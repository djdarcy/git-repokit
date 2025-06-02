#!/usr/bin/env python3
"""
Branch utilities for RepoKit.

Provides branch detection and validation for private content protection.
"""

import subprocess
import os
from typing import Set, List, Dict, Optional, Tuple


class BranchContext:
    """Manages branch context and security rules."""
    
    # Branches that can contain private content
    PRIVATE_BRANCHES = {'private', 'local'}
    
    # Branches that must never contain private content
    PUBLIC_BRANCHES = {'main', 'master', 'dev', 'test', 'staging', 'live', 'prod', 'production'}
    
    # Files/directories that should only exist in private branches
    PRIVATE_PATTERNS = {
        'CLAUDE.md',
        'private/',
        'convos/',
        'logs/',
        'credentials/',
        'secrets/',
        '.env.local',
        '.env.private',
        '**/__private__*',
        '**/private_*',
    }
    
    # Files that should be excluded from public branches during merges
    EXCLUDE_FROM_PUBLIC = {
        'CLAUDE.md',
        'private/claude/',
        'private/docs/',
        'private/notes/',
        'private/temp/',
        'revisions/',
        'test-runs/',
        'test_runs/',
    }
    
    def __init__(self, repo_path: str = '.'):
        """Initialize branch context for given repository."""
        self.repo_path = os.path.abspath(repo_path)
        self._current_branch = None
        self._branch_type = None
    
    @property
    def current_branch(self) -> str:
        """Get current branch name."""
        if self._current_branch is None:
            self._current_branch = self._get_current_branch()
        return self._current_branch
    
    @property
    def branch_type(self) -> str:
        """Get branch type: 'private', 'public', or 'unknown'."""
        if self._branch_type is None:
            self._branch_type = self._determine_branch_type()
        return self._branch_type
    
    def _get_current_branch(self) -> str:
        """Get current git branch name."""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return 'unknown'
    
    def _determine_branch_type(self) -> str:
        """Determine if current branch is private, public, or unknown."""
        branch = self.current_branch.lower()
        
        # Check explicit private branches
        if branch in self.PRIVATE_BRANCHES:
            return 'private'
        
        # Check explicit public branches
        if branch in self.PUBLIC_BRANCHES:
            return 'public'
        
        # Check patterns
        if branch.startswith('private/') or branch.startswith('local/'):
            return 'private'
        
        if branch.startswith('feature/') or branch.startswith('feat/'):
            return 'private'  # Feature branches can have private content
        
        # Default to public for safety
        return 'public'
    
    def is_private_branch(self) -> bool:
        """Check if current branch allows private content."""
        return self.branch_type == 'private'
    
    def is_public_branch(self) -> bool:
        """Check if current branch must not have private content."""
        return self.branch_type == 'public'
    
    def get_staged_files(self) -> List[str]:
        """Get list of files staged for commit."""
        try:
            result = subprocess.run(
                ['git', 'diff', '--cached', '--name-only'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
        except subprocess.CalledProcessError:
            return []
    
    def check_private_files(self, files: List[str]) -> List[Tuple[str, str]]:
        """
        Check if files contain private content.
        
        Returns list of (file, reason) tuples for files that are private.
        """
        private_files = []
        
        for file in files:
            # Check exact matches
            if file in self.PRIVATE_PATTERNS:
                private_files.append((file, "Exact match to private pattern"))
                continue
            
            # Check directory prefixes
            for pattern in self.PRIVATE_PATTERNS:
                if pattern.endswith('/') and file.startswith(pattern):
                    private_files.append((file, f"Inside private directory: {pattern}"))
                    break
            
            # Check file patterns
            if 'private' in file.lower() or '__private__' in file:
                private_files.append((file, "Contains 'private' in path"))
            
            # Check specific files that should be excluded
            for exclude in self.EXCLUDE_FROM_PUBLIC:
                if file == exclude or file.startswith(exclude):
                    private_files.append((file, f"Matches exclude pattern: {exclude}"))
                    break
        
        return private_files
    
    def validate_commit(self) -> Tuple[bool, List[str]]:
        """
        Validate if current commit is safe for the branch.
        
        Returns (is_valid, error_messages).
        """
        if self.is_private_branch():
            # Private branches can have any content
            return True, []
        
        # Public branch - check for private content
        staged_files = self.get_staged_files()
        private_files = self.check_private_files(staged_files)
        
        if private_files:
            errors = [
                f"ERROR: Attempting to commit private files to public branch '{self.current_branch}':",
                ""
            ]
            for file, reason in private_files:
                errors.append(f"  - {file}: {reason}")
            
            errors.extend([
                "",
                "These files should only exist in private branches.",
                "To fix this:",
                "  1. Switch to private branch: git checkout private",
                "  2. Or unstage these files: git reset HEAD <file>",
                "  3. Or remove from working directory: rm <file>",
            ])
            return False, errors
        
        return True, []
    
    def get_merge_excludes(self, source_branch: str, target_branch: str) -> Set[str]:
        """Get list of files to exclude when merging between branches."""
        # If merging from private to public, exclude private files
        if source_branch in self.PRIVATE_BRANCHES and target_branch in self.PUBLIC_BRANCHES:
            return self.EXCLUDE_FROM_PUBLIC
        
        return set()
    
    def setup_branch_excludes(self) -> None:
        """Set up .git/info/exclude for current branch."""
        exclude_file = os.path.join(self.repo_path, '.git', 'info', 'exclude')
        
        if self.is_public_branch():
            # Add private patterns to exclude file
            excludes = [
                "# RepoKit: Branch-conditional excludes for public branch",
                "# These files are tracked in 'private' branch but ignored in public branches",
                "",
                "# AI integration files",
                "CLAUDE.md",
                "",
                "# Development conversation logs", 
                "private/claude/",
                "",
                "# Private development documentation",
                "private/docs/",
                "",
                "# Development notes and temporary files",
                "private/notes/",
                "private/temp/",
                "",
                "# Revision history (private branch only)",
                "revisions/",
                "",
                "# Test artifacts",
                "test-runs/",
                "test_runs/",
            ]
            
            with open(exclude_file, 'w') as f:
                f.write('\n'.join(excludes))
                
            print(f"✓ Set up branch excludes for public branch '{self.current_branch}'")
        else:
            # Private branch - minimal excludes
            excludes = [
                "# RepoKit: Minimal excludes for private branch",
                "# Private branches can contain all content",
                "",
                "# Test artifacts (not needed in git)",
                "test-runs/",
                "test_runs/",
            ]
            
            with open(exclude_file, 'w') as f:
                f.write('\n'.join(excludes))
                
            print(f"✓ Set up branch excludes for private branch '{self.current_branch}'")


def check_branch_safety() -> bool:
    """Quick check if current operations are safe."""
    context = BranchContext()
    is_valid, errors = context.validate_commit()
    
    if not is_valid:
        for error in errors:
            print(error)
        return False
    
    return True


if __name__ == "__main__":
    # Quick test when run directly
    context = BranchContext()
    print(f"Current branch: {context.current_branch}")
    print(f"Branch type: {context.branch_type}")
    print(f"Is private: {context.is_private_branch()}")
    print(f"Is public: {context.is_public_branch()}")
    
    staged = context.get_staged_files()
    if staged:
        print(f"\nStaged files: {staged}")
        private = context.check_private_files(staged)
        if private:
            print("\nPrivate files detected:")
            for file, reason in private:
                print(f"  - {file}: {reason}")