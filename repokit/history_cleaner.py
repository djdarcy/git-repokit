#!/usr/bin/env python3
"""
History Cleaner for RepoKit.

Provides safe, user-friendly tools to clean sensitive data from git history
using git filter-repo. Includes pre-built recipes for common scenarios and
comprehensive safety features.
"""

import os
import sys
import shutil
import logging
import subprocess
import tempfile
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass
from enum import Enum


class CleaningRecipe(Enum):
    """Pre-built recipes for common cleaning scenarios."""
    PRE_OPEN_SOURCE = "pre-open-source"
    REMOVE_SECRETS = "remove-secrets"
    WINDOWS_SAFE = "windows-safe"
    CUTOFF_DATE = "cutoff-date"
    CUSTOM = "custom"


@dataclass
class CleaningConfig:
    """Configuration for a cleaning operation."""
    recipe: CleaningRecipe
    paths_to_remove: List[str] = None
    patterns_to_remove: List[str] = None
    cutoff_sha: Optional[str] = None
    cutoff_date: Optional[str] = None
    preserve_recent: bool = True
    backup_location: Optional[str] = None
    force: bool = False
    dry_run: bool = False


class HistoryCleanerError(Exception):
    """Base exception for history cleaner errors."""
    pass


class GitFilterRepoNotFound(HistoryCleanerError):
    """Raised when git filter-repo is not available."""
    pass


class HistoryCleaner:
    """
    Manages safe history cleaning operations using git filter-repo.
    
    This class provides:
    - Pre-built recipes for common scenarios
    - Safety checks and backups
    - Windows compatibility
    - Dry-run previews
    - Progress tracking
    """
    
    # Default paths to remove for pre-open-source recipe
    DEFAULT_PRIVATE_PATHS = [
        'private/',
        'revisions/',
        'convos/',
        'logs/',
        'credentials/',
        'secrets/',
        '.env',
        'CLAUDE.md',
        '.claude',
        '__private__',
        '*~',  # Vim backup files
    ]
    
    # Windows reserved names that cause issues
    WINDOWS_RESERVED_NAMES = [
        'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4',
        'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2',
        'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9',
    ]
    
    # Common secret patterns
    SECRET_PATTERNS = [
        r'["\']?api[_-]?key["\']?\s*[:=]\s*["\'][^"\']+["\']',
        r'["\']?secret[_-]?key["\']?\s*[:=]\s*["\'][^"\']+["\']',
        r'["\']?password["\']?\s*[:=]\s*["\'][^"\']+["\']',
        r'["\']?token["\']?\s*[:=]\s*["\'][^"\']+["\']',
        r'["\']?auth["\']?\s*[:=]\s*["\'][^"\']+["\']',
        r'BEGIN (RSA|DSA|EC|OPENSSH) PRIVATE KEY',
        r'ssh-rsa AAAA[0-9A-Za-z+/]+[=]{0,2}',
    ]
    
    def __init__(self, repo_path: str = ".", verbose: int = 0, check_filter_repo: bool = True):
        """
        Initialize the history cleaner.
        
        Args:
            repo_path: Path to the git repository
            verbose: Verbosity level
            check_filter_repo: Whether to check for git filter-repo availability
        """
        self.repo_path = os.path.abspath(repo_path)
        self.verbose = verbose
        self.logger = logging.getLogger("repokit.history_cleaner")
        self._filter_repo_checked = False
        
        # Only check if git filter-repo is available when needed
        if check_filter_repo:
            self._ensure_filter_repo_available()
        
        # Ensure we're in a git repository if path is not current directory
        if repo_path != "." and not os.path.exists(os.path.join(self.repo_path, '.git')):
            raise HistoryCleanerError(f"Not a git repository: {self.repo_path}")
    
    def _ensure_filter_repo_available(self):
        """Ensure git filter-repo is available, checking only once."""
        if self._filter_repo_checked:
            return
        
        self._check_filter_repo_availability()
        self._filter_repo_checked = True
    
    def _check_filter_repo_availability(self):
        """Check if git filter-repo is installed and available."""
        try:
            result = subprocess.run(
                ['git', 'filter-repo', '--version'],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode != 0:
                raise GitFilterRepoNotFound()
        except (subprocess.SubprocessError, FileNotFoundError):
            raise GitFilterRepoNotFound(
                "git filter-repo is not installed. "
                "Install it with: pip install git-filter-repo"
            )
    
    def run_command(self, cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Run a command and return the result."""
        if self.verbose >= 2:
            self.logger.debug(f"Running: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            check=False
        )
        
        if check and result.returncode != 0:
            raise HistoryCleanerError(
                f"Command failed: {' '.join(cmd)}\n"
                f"Error: {result.stderr}"
            )
        
        return result
    
    def create_backup(self, backup_location: Optional[str] = None) -> str:
        """
        Create a backup of the repository.
        
        Args:
            backup_location: Where to create the backup
            
        Returns:
            Path to the backup
        """
        if not backup_location:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_location = f"{self.repo_path}_backup_{timestamp}"
        
        self.logger.info(f"Creating backup at: {backup_location}")
        
        # Use git clone --mirror for a complete backup
        self.run_command([
            'git', 'clone', '--mirror',
            self.repo_path, backup_location
        ])
        
        return backup_location
    
    def analyze_repository(self) -> Dict[str, Any]:
        """
        Analyze repository for potential issues and cleaning candidates.
        
        Returns:
            Analysis results
        """
        analysis = {
            'private_paths': [],
            'large_files': [],
            'windows_issues': [],
            'potential_secrets': [],
            'branches': [],
            'total_commits': 0,
        }
        
        # Get all file paths in history
        result = self.run_command([
            'git', 'log', '--all', '--name-only', '--format='
        ])
        
        all_paths = set(result.stdout.strip().split('\n'))
        all_paths.discard('')  # Remove empty strings
        
        # Check for private paths
        for path in all_paths:
            for private_pattern in self.DEFAULT_PRIVATE_PATHS:
                if path.startswith(private_pattern) or f"/{private_pattern}" in path:
                    analysis['private_paths'].append(path)
                    break
        
        # Check for Windows reserved names
        for path in all_paths:
            filename = os.path.basename(path).upper()
            base_name = filename.split('.')[0] if '.' in filename else filename
            if base_name in self.WINDOWS_RESERVED_NAMES:
                analysis['windows_issues'].append(path)
        
        # Get branch list
        result = self.run_command(['git', 'branch', '-a'])
        analysis['branches'] = [
            line.strip().lstrip('* ')
            for line in result.stdout.strip().split('\n')
            if line.strip()
        ]
        
        # Count commits
        result = self.run_command(['git', 'rev-list', '--all', '--count'])
        analysis['total_commits'] = int(result.stdout.strip())
        
        return analysis
    
    def get_recipe_config(self, recipe: CleaningRecipe) -> CleaningConfig:
        """
        Get default configuration for a recipe.
        
        Args:
            recipe: The recipe to get config for
            
        Returns:
            CleaningConfig for the recipe
        """
        if recipe == CleaningRecipe.PRE_OPEN_SOURCE:
            return CleaningConfig(
                recipe=recipe,
                paths_to_remove=self.DEFAULT_PRIVATE_PATHS.copy(),
                preserve_recent=True
            )
        elif recipe == CleaningRecipe.WINDOWS_SAFE:
            # Will be determined by analysis
            return CleaningConfig(
                recipe=recipe,
                paths_to_remove=[],
                preserve_recent=True
            )
        elif recipe == CleaningRecipe.REMOVE_SECRETS:
            return CleaningConfig(
                recipe=recipe,
                patterns_to_remove=self.SECRET_PATTERNS.copy(),
                preserve_recent=True
            )
        else:
            return CleaningConfig(recipe=recipe)
    
    def preview_cleaning(self, config: CleaningConfig) -> Dict[str, Any]:
        """
        Preview what would be cleaned without making changes.
        
        Args:
            config: Cleaning configuration
            
        Returns:
            Preview information
        """
        preview = {
            'recipe': config.recipe.value,
            'paths_to_remove': config.paths_to_remove or [],
            'patterns_to_remove': config.patterns_to_remove or [],
            'estimated_impact': {},
            'warnings': [],
        }
        
        # Analyze repository
        analysis = self.analyze_repository()
        
        # Calculate impact
        if config.paths_to_remove:
            affected_files = []
            for path in analysis['private_paths']:
                for remove_path in config.paths_to_remove:
                    if path.startswith(remove_path) or f"/{remove_path}" in path:
                        affected_files.append(path)
                        break
            
            preview['estimated_impact']['files_to_remove'] = len(set(affected_files))
        
        # Add warnings
        if analysis['windows_issues'] and config.recipe != CleaningRecipe.WINDOWS_SAFE:
            preview['warnings'].append(
                f"Found {len(analysis['windows_issues'])} Windows reserved names. "
                "Consider using --recipe windows-safe"
            )
        
        if len(analysis['branches']) > 5:
            preview['warnings'].append(
                f"Repository has {len(analysis['branches'])} branches. "
                "Cleaning will affect all branches."
            )
        
        return preview
    
    def clean_history(self, config: CleaningConfig) -> bool:
        """
        Clean repository history according to configuration.
        
        Args:
            config: Cleaning configuration
            
        Returns:
            True if successful
        """
        # Ensure git filter-repo is available
        self._ensure_filter_repo_available()
        
        # Safety checks
        if not config.force and not config.dry_run:
            # Check for uncommitted changes
            result = self.run_command(['git', 'status', '--porcelain'], check=False)
            if result.stdout.strip():
                raise HistoryCleanerError(
                    "Uncommitted changes detected. Commit or stash them first."
                )
            
            # Confirm with user
            print("\n⚠️  WARNING: This will rewrite repository history!")
            print("This operation:")
            print("- Cannot be undone (except by restoring from backup)")
            print("- Will require force-push to update remotes")
            print("- Will break existing clones")
            
            response = input("\nContinue? [y/N]: ")
            if response.lower() != 'y':
                print("Operation cancelled.")
                return False
        
        # Create backup unless skipped
        if not config.dry_run and config.backup_location != 'skip':
            backup_path = self.create_backup(config.backup_location)
            print(f"✓ Backup created at: {backup_path}")
        
        # Execute the appropriate recipe
        if config.recipe == CleaningRecipe.PRE_OPEN_SOURCE:
            return self._clean_pre_open_source(config)
        elif config.recipe == CleaningRecipe.WINDOWS_SAFE:
            return self._clean_windows_safe(config)
        elif config.recipe == CleaningRecipe.REMOVE_SECRETS:
            return self._clean_remove_secrets(config)
        elif config.recipe == CleaningRecipe.CUTOFF_DATE:
            return self._clean_cutoff_date(config)
        else:
            raise HistoryCleanerError(f"Recipe not implemented: {config.recipe}")
    
    def _clean_pre_open_source(self, config: CleaningConfig) -> bool:
        """Execute pre-open-source cleaning recipe."""
        self.logger.info("Executing pre-open-source recipe")
        
        # Build filter-repo command
        cmd = ['git', 'filter-repo', '--force']
        
        if config.dry_run:
            cmd.append('--dry-run')
        
        # Add paths to remove
        for path in config.paths_to_remove:
            cmd.extend(['--path', path, '--invert-paths'])
        
        # Execute
        result = self.run_command(cmd, check=False)
        
        if result.returncode != 0:
            self.logger.error(f"Cleaning failed: {result.stderr}")
            return False
        
        if not config.dry_run:
            self.logger.info("Successfully cleaned repository")
            print("\n✓ Repository cleaned successfully!")
            print("\nNext steps:")
            print("1. Review the changes with: git log --oneline")
            print("2. Force push to remote: git push --force-with-lease origin <branch>")
            print("3. Notify team members to re-clone the repository")
        
        return True
    
    def _clean_windows_safe(self, config: CleaningConfig) -> bool:
        """Execute Windows-safe cleaning recipe."""
        self.logger.info("Executing Windows-safe recipe")
        
        # Find Windows reserved names
        analysis = self.analyze_repository()
        windows_issues = analysis['windows_issues']
        
        if not windows_issues:
            print("No Windows reserved names found.")
            return True
        
        print(f"\nFound {len(windows_issues)} Windows reserved names:")
        for path in windows_issues[:10]:
            print(f"  - {path}")
        if len(windows_issues) > 10:
            print(f"  ... and {len(windows_issues) - 10} more")
        
        # Build filter-repo command
        cmd = ['git', 'filter-repo', '--force']
        
        if config.dry_run:
            cmd.append('--dry-run')
        
        # Remove each problematic file
        for path in windows_issues:
            cmd.extend(['--path', path, '--invert-paths'])
        
        # Execute
        result = self.run_command(cmd, check=False)
        
        return result.returncode == 0
    
    def _clean_remove_secrets(self, config: CleaningConfig) -> bool:
        """Execute remove-secrets cleaning recipe."""
        # TODO: Implement secret removal using regex patterns
        raise NotImplementedError("Remove secrets recipe not yet implemented")
    
    def _clean_cutoff_date(self, config: CleaningConfig) -> bool:
        """Execute cutoff-date cleaning recipe."""
        # TODO: Implement cutoff date cleaning
        raise NotImplementedError("Cutoff date recipe not yet implemented")