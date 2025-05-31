#!/usr/bin/env python3
"""
Directory Analyzer for RepoKit.

Analyzes directories for migration to the RepoKit structure.
"""

import os
import fnmatch
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any


class DirectoryAnalyzer:
    """
    Analyzes directories for migration to RepoKit structure.
    
    This class helps identify existing files and directories that match
    RepoKit's expected structure, detects conflicts, and provides migration
    strategies.
    """
    
    # Standard RepoKit directories
    STANDARD_DIRS = [
        "convos", "docs", "logs", "private", "revisions", "scripts", "tests"
    ]
    
    # Private directories that shouldn't be checked in
    PRIVATE_DIRS = ["private", "convos", "logs"]
    
    # Special directories that need special handling
    SPECIAL_DIRS = [".git", ".github", ".vscode"]
    
    # Template directories to look for in the target
    TEMPLATE_DIRS = [".github"]
    
    def __init__(self, target_dir: str, verbose: int = 0):
        """
        Initialize the directory analyzer.
        
        Args:
            target_dir: Directory to analyze
            verbose: Verbosity level (0=normal, 1=info, 2=debug)
        """
        self.target_dir = os.path.abspath(target_dir)
        self.verbose = verbose
        self.logger = logging.getLogger("repokit.analyzer")
        
        # Analysis results
        self.existing_dirs = set()
        self.missing_dirs = set()
        self.special_dirs = {}
        self.template_conflicts = {}
        
        # Scan target directory
        self._scan_directory()
    
    def _scan_directory(self) -> None:
        """Scan the target directory and categorize content."""
        if not os.path.exists(self.target_dir):
            self.logger.warning(f"Target directory does not exist: {self.target_dir}")
            return
        
        self.logger.info(f"Scanning directory: {self.target_dir}")
        
        # Check for standard directories
        for dirname in self.STANDARD_DIRS:
            dirpath = os.path.join(self.target_dir, dirname)
            if os.path.exists(dirpath) and os.path.isdir(dirpath):
                self.existing_dirs.add(dirname)
            else:
                self.missing_dirs.add(dirname)
        
        # Check for special directories
        for dirname in self.SPECIAL_DIRS:
            dirpath = os.path.join(self.target_dir, dirname)
            if os.path.exists(dirpath) and os.path.isdir(dirpath):
                self.special_dirs[dirname] = dirpath
        
        # Check for template conflicts
        for template_dir in self.TEMPLATE_DIRS:
            dirpath = os.path.join(self.target_dir, template_dir)
            if os.path.exists(dirpath) and os.path.isdir(dirpath):
                self.template_conflicts[template_dir] = self._scan_template_conflicts(template_dir)
        
        if self.verbose >= 1:
            self._log_scan_results()
    
    def _scan_template_conflicts(self, template_dir: str) -> Dict[str, str]:
        """
        Scan a template directory for potential conflicts.
        
        Args:
            template_dir: Template directory name (e.g., ".github")
            
        Returns:
            Dictionary of {filename: path} for conflicting files
        """
        conflicts = {}
        dirpath = os.path.join(self.target_dir, template_dir)
        
        if not os.path.exists(dirpath):
            return conflicts
        
        for root, dirs, files in os.walk(dirpath):
            for file in files:
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, dirpath)
                conflicts[rel_path] = filepath
        
        return conflicts
    
    def _log_scan_results(self) -> None:
        """Log the results of the directory scan."""
        self.logger.info(f"Existing standard directories: {', '.join(self.existing_dirs) or 'None'}")
        self.logger.info(f"Missing standard directories: {', '.join(self.missing_dirs) or 'None'}")
        self.logger.info(f"Special directories found: {', '.join(self.special_dirs.keys()) or 'None'}")
        
        if self.template_conflicts:
            for template_dir, conflicts in self.template_conflicts.items():
                self.logger.info(f"Potential conflicts in {template_dir}: {len(conflicts)} files")
                
                if self.verbose >= 2:
                    for rel_path in conflicts:
                        self.logger.debug(f"  - {rel_path}")
    
    def has_git_repository(self) -> bool:
        """Check if the target directory is a Git repository."""
        return ".git" in self.special_dirs
    
    def has_template_conflicts(self) -> bool:
        """Check if there are any template conflicts."""
        return any(len(conflicts) > 0 for conflicts in self.template_conflicts.values())
    
    def get_migration_plan(self, strategy: str = "safe") -> Dict[str, Any]:
        """
        Generate a migration plan based on the analysis.
        
        Args:
            strategy: Migration strategy ("safe", "replace", "merge")
            
        Returns:
            Dictionary with migration plan details
        """
        plan = {
            "target_dir": self.target_dir,
            "create_dirs": list(self.missing_dirs),
            "move_dirs": {},
            "special_dirs": {k: {"path": v, "action": self._get_special_dir_action(k, strategy)} 
                           for k, v in self.special_dirs.items()},
            "template_conflicts": {k: {"conflicts": len(v), "action": self._get_template_conflict_action(k, strategy)} 
                                for k, v in self.template_conflicts.items()},
            "strategy": strategy
        }
        
        return plan
    
    def _get_special_dir_action(self, dirname: str, strategy: str) -> str:
        """
        Determine action for a special directory based on strategy.
        
        Args:
            dirname: Directory name
            strategy: Migration strategy
            
        Returns:
            Action to take ("keep", "backup", "replace", "merge")
        """
        if strategy == "safe":
            if dirname == ".git":
                return "keep"
            else:
                return "backup"
        elif strategy == "replace":
            return "replace"
        elif strategy == "merge":
            return "merge"
        else:
            return "keep"
    
    def _get_template_conflict_action(self, template_dir: str, strategy: str) -> str:
        """
        Determine action for template conflicts based on strategy.
        
        Args:
            template_dir: Template directory name
            strategy: Migration strategy
            
        Returns:
            Action to take ("keep", "backup", "replace", "merge")
        """
        if strategy == "safe":
            return "backup"
        elif strategy == "replace":
            return "replace"
        elif strategy == "merge":
            return "merge"
        else:
            return "keep"
    
    def execute_migration_plan(self, plan: Dict[str, Any], dry_run: bool = False) -> bool:
        """
        Execute a migration plan.
        
        Args:
            plan: Migration plan from get_migration_plan()
            dry_run: If True, only log actions without executing
            
        Returns:
            True if successful, False otherwise
        """
        self.logger.info(f"Executing migration plan (dry_run={dry_run})")
        
        # Create missing directories
        for dirname in plan["create_dirs"]:
            dirpath = os.path.join(self.target_dir, dirname)
            self.logger.info(f"Creating directory: {dirpath}")
            if not dry_run:
                os.makedirs(dirpath, exist_ok=True)
        
        # Handle special directories
        for dirname, info in plan["special_dirs"].items():
            action = info["action"]
            path = info["path"]
            
            if action == "keep":
                self.logger.info(f"Keeping {dirname} as is")
            elif action == "backup":
                backup_path = f"{path}_backup"
                self.logger.info(f"Backing up {dirname} to {backup_path}")
                if not dry_run:
                    if os.path.exists(backup_path):
                        shutil.rmtree(backup_path)
                    shutil.copytree(path, backup_path)
            elif action == "replace":
                self.logger.info(f"Replacing {dirname}")
                if not dry_run:
                    shutil.rmtree(path)
            elif action == "merge":
                self.logger.info(f"Marking {dirname} for merge (requires template content)")
        
        # Handle template conflicts
        for template_dir, info in plan["template_conflicts"].items():
            action = info["action"]
            conflicts = self.template_conflicts[template_dir]
            
            if action == "keep":
                self.logger.info(f"Keeping existing {template_dir} files")
            elif action == "backup":
                backup_dir = os.path.join(self.target_dir, f"{template_dir}_backup")
                self.logger.info(f"Backing up {len(conflicts)} files from {template_dir} to {backup_dir}")
                if not dry_run:
                    if not os.path.exists(backup_dir):
                        os.makedirs(backup_dir, exist_ok=True)
                    for rel_path, filepath in conflicts.items():
                        backup_path = os.path.join(backup_dir, rel_path)
                        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                        shutil.copy2(filepath, backup_path)
            elif action == "replace":
                self.logger.info(f"Replacing {len(conflicts)} files in {template_dir}")
                dirpath = os.path.join(self.target_dir, template_dir)
                if not dry_run:
                    shutil.rmtree(dirpath)
            elif action == "merge":
                self.logger.info(f"Marking {template_dir} for merge (requires template content)")
        
        return True
    
    def categorize_files(self, path: str = None) -> Dict[str, List[str]]:
        """
        Categorize files in a directory by type.
        
        Args:
            path: Directory path to categorize (default: target_dir)
            
        Returns:
            Dictionary with categorized files
        """
        path = path or self.target_dir
        
        categories = {
            "python": [],     # Python source files
            "javascript": [], # JavaScript source files
            "html": [],       # HTML files
            "css": [],        # CSS files
            "markdown": [],   # Markdown files
            "images": [],     # Image files
            "documents": [],  # Document files
            "data": [],       # Data files
            "config": [],     # Configuration files
            "other": []       # Other files
        }
        
        for root, dirs, files in os.walk(path):
            # Skip .git directory
            if ".git" in root.split(os.sep):
                continue
                
            for file in files:
                filepath = os.path.join(root, file)
                
                # Categorize by extension
                if file.endswith((".py", ".pyw")):
                    categories["python"].append(filepath)
                elif file.endswith((".js", ".jsx", ".ts", ".tsx")):
                    categories["javascript"].append(filepath)
                elif file.endswith((".html", ".htm")):
                    categories["html"].append(filepath)
                elif file.endswith((".css", ".scss", ".sass")):
                    categories["css"].append(filepath)
                elif file.endswith((".md", ".markdown")):
                    categories["markdown"].append(filepath)
                elif file.endswith((".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico")):
                    categories["images"].append(filepath)
                elif file.endswith((".doc", ".docx", ".pdf", ".txt", ".rtf")):
                    categories["documents"].append(filepath)
                elif file.endswith((".csv", ".json", ".xml", ".yaml", ".yml")):
                    categories["data"].append(filepath)
                elif file.endswith((".ini", ".cfg", ".conf", ".config", ".toml")):
                    categories["config"].append(filepath)
                else:
                    categories["other"].append(filepath)
        
        return categories
    
    def suggest_language(self) -> str:
        """
        Suggest a programming language based on the file categories.
        
        Returns:
            Suggested language ("python", "javascript", or "generic")
        """
        categories = self.categorize_files()
        
        # Count files by language
        python_count = len(categories["python"])
        javascript_count = len(categories["javascript"])
        
        if python_count > javascript_count:
            return "python"
        elif javascript_count > python_count:
            return "javascript"
        else:
            return "generic"
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the directory analysis.
        
        Returns:
            Summary dictionary
        """
        categories = self.categorize_files()
        
        summary = {
            "target_dir": self.target_dir,
            "existing_dirs": sorted(list(self.existing_dirs)),
            "missing_dirs": sorted(list(self.missing_dirs)),
            "special_dirs": list(self.special_dirs.keys()),
            "has_git_repository": self.has_git_repository(),
            "has_template_conflicts": self.has_template_conflicts(),
            "suggested_language": self.suggest_language(),
            "file_counts": {
                category: len(files) for category, files in categories.items()
            },
            "total_files": sum(len(files) for files in categories.values())
        }
        
        return summary


class MigrationManager:
    """
    Manages migration of directories to RepoKit structure.
    """
    
    def __init__(self, source_dir: str, target_dir: str = None, verbose: int = 0):
        """
        Initialize the migration manager.
        
        Args:
            source_dir: Source directory
            target_dir: Target directory (default: source_dir)
            verbose: Verbosity level (0=normal, 1=info, 2=debug)
        """
        self.source_dir = os.path.abspath(source_dir)
        self.target_dir = os.path.abspath(target_dir) if target_dir else self.source_dir
        self.verbose = verbose
        self.logger = logging.getLogger("repokit.migration")
        
        # Initialize analyzer
        self.analyzer = DirectoryAnalyzer(self.source_dir, verbose)
    
    def analyze(self) -> Dict[str, Any]:
        """
        Analyze the source directory.
        
        Returns:
            Analysis summary
        """
        return self.analyzer.get_summary()
    
    def plan_migration(self, strategy: str = "safe") -> Dict[str, Any]:
        """
        Plan migration from source to target.
        
        Args:
            strategy: Migration strategy ("safe", "replace", "merge")
            
        Returns:
            Migration plan
        """
        return self.analyzer.get_migration_plan(strategy)
    
    def execute_migration(self, plan: Dict[str, Any], dry_run: bool = False) -> bool:
        """
        Execute a migration plan.
        
        Args:
            plan: Migration plan from plan_migration()
            dry_run: If True, only log actions without executing
            
        Returns:
            True if successful, False otherwise
        """
        return self.analyzer.execute_migration_plan(plan, dry_run)
    
    def migrate(self, strategy: str = "safe", dry_run: bool = False) -> bool:
        """
        Analyze, plan, and execute migration in one step.
        
        Args:
            strategy: Migration strategy ("safe", "replace", "merge")
            dry_run: If True, only log actions without executing
            
        Returns:
            True if successful, False otherwise
        """
        plan = self.plan_migration(strategy)
        return self.execute_migration(plan, dry_run)


def analyze_directory(directory: str, verbose: int = 0) -> Dict[str, Any]:
    """
    Analyze a directory for RepoKit compatibility.
    
    Args:
        directory: Directory to analyze
        verbose: Verbosity level (0=normal, 1=info, 2=debug)
        
    Returns:
        Analysis summary
    """
    analyzer = DirectoryAnalyzer(directory, verbose)
    return analyzer.get_summary()


def plan_migration(directory: str, strategy: str = "safe", verbose: int = 0) -> Dict[str, Any]:
    """
    Plan migration for a directory.
    
    Args:
        directory: Directory to analyze
        strategy: Migration strategy ("safe", "replace", "merge")
        verbose: Verbosity level (0=normal, 1=info, 2=debug)
        
    Returns:
        Migration plan
    """
    analyzer = DirectoryAnalyzer(directory, verbose)
    return analyzer.get_migration_plan(strategy)


def migrate_directory(directory: str, strategy: str = "safe", dry_run: bool = False, verbose: int = 0) -> bool:
    """
    Migrate a directory to RepoKit structure.
    
    Args:
        directory: Directory to migrate
        strategy: Migration strategy ("safe", "replace", "merge")
        dry_run: If True, only log actions without executing
        verbose: Verbosity level (0=normal, 1=info, 2=debug)
        
    Returns:
        True if successful, False otherwise
    """
    migration = MigrationManager(directory, verbose=verbose)
    return migration.migrate(strategy, dry_run)
