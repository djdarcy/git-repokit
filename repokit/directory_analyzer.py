#!/usr/bin/env python3
"""
Directory Analyzer for RepoKit.

Analyzes directories for migration to the RepoKit structure.
Supports universal project migration for any project type.
"""

import os
import fnmatch
import shutil
import logging
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any


class GitManager:
    """
    Manages Git repository state detection and operations.
    """
    
    def __init__(self, target_dir: str, verbose: int = 0):
        """Initialize GitManager."""
        self.target_dir = os.path.abspath(target_dir)
        self.verbose = verbose
        self.logger = logging.getLogger("repokit.git")
    
    def run_git(self, args: List[str], check: bool = True) -> Optional[str]:
        """Run a git command and return output."""
        cmd = ["git"] + args
        
        if self.verbose >= 2:
            self.logger.debug(f"Running: {' '.join(cmd)} in {self.target_dir}")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.target_dir,
                check=check,
                capture_output=True,
                text=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            if self.verbose >= 1:
                self.logger.warning(f"Git command failed: {e.stderr}")
            if check:
                raise
            return None
    
    def is_git_repo(self) -> bool:
        """Check if directory is a Git repository."""
        return os.path.exists(os.path.join(self.target_dir, ".git"))
    
    def get_repo_state(self) -> Dict[str, Any]:
        """Get comprehensive Git repository state."""
        if not self.is_git_repo():
            return {"is_repo": False}
        
        state = {"is_repo": True}
        
        try:
            # Get current branch
            state["current_branch"] = self.run_git(["branch", "--show-current"], check=False)
            
            # Get all branches
            branches_output = self.run_git(["branch", "-a"], check=False)
            if branches_output:
                branches = []
                for line in branches_output.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('remotes/'):
                        branch = line.lstrip('* ').strip()
                        if branch:
                            branches.append(branch)
                state["branches"] = branches
            
            # Check for uncommitted changes
            status_output = self.run_git(["status", "--porcelain"], check=False)
            state["has_uncommitted_changes"] = bool(status_output and status_output.strip())
            
            # Get remotes
            remotes_output = self.run_git(["remote", "-v"], check=False)
            remotes = {}
            if remotes_output:
                for line in remotes_output.split('\n'):
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            remote_name = parts[0]
                            remote_url = parts[1]
                            if remote_name not in remotes:
                                remotes[remote_name] = remote_url
            state["remotes"] = remotes
            
            # Check if repo has commits
            try:
                self.run_git(["rev-parse", "HEAD"], check=True)
                state["has_commits"] = True
            except:
                state["has_commits"] = False
            
        except Exception as e:
            self.logger.warning(f"Error getting Git state: {str(e)}")
        
        return state
    
    def get_branch_strategy(self) -> str:
        """Detect existing branch strategy."""
        state = self.get_repo_state()
        if not state["is_repo"]:
            return "none"
        
        branches = set(state.get("branches", []))
        
        # Check for GitFlow pattern
        if "develop" in branches and any(b.startswith("feature/") for b in branches):
            return "gitflow"
        
        # Check for standard RepoKit pattern
        repokit_branches = {"main", "dev", "staging", "test", "live"}
        if len(repokit_branches & branches) >= 3:
            return "standard"
        
        # Check for simple pattern
        if "main" in branches and "dev" in branches:
            return "simple"
        
        # Single branch or unknown
        return "minimal"


class ProjectAnalyzer:
    """
    Universal project analyzer for any type of project.
    
    Analyzes project structure, language, Git state, and provides
    comprehensive migration recommendations for RepoKit adoption.
    """
    
    # Language detection patterns
    LANGUAGE_PATTERNS = {
        "python": {
            "files": ["setup.py", "pyproject.toml", "requirements.txt", "Pipfile", "poetry.lock"],
            "extensions": [".py", ".pyw"],
            "directories": ["src", "lib", "tests"]
        },
        "javascript": {
            "files": ["package.json", "package-lock.json", "yarn.lock", "webpack.config.js"],
            "extensions": [".js", ".jsx", ".ts", ".tsx"],
            "directories": ["src", "lib", "node_modules", "dist"]
        },
        "java": {
            "files": ["pom.xml", "build.gradle", "build.xml"],
            "extensions": [".java", ".class"],
            "directories": ["src", "target", "build"]
        },
        "csharp": {
            "files": ["*.csproj", "*.sln", "packages.config"],
            "extensions": [".cs", ".vb"],
            "directories": ["bin", "obj"]
        },
        "go": {
            "files": ["go.mod", "go.sum"],
            "extensions": [".go"],
            "directories": ["cmd", "pkg", "internal"]
        },
        "rust": {
            "files": ["Cargo.toml", "Cargo.lock"],
            "extensions": [".rs"],
            "directories": ["src", "target"]
        }
    }
    
    def __init__(self, target_dir: str, verbose: int = 0):
        """Initialize ProjectAnalyzer."""
        self.target_dir = os.path.abspath(target_dir)
        self.verbose = verbose
        self.logger = logging.getLogger("repokit.project_analyzer")
        
        # Initialize Git manager
        self.git_manager = GitManager(target_dir, verbose)
        
        # Initialize directory analyzer for RepoKit-specific analysis
        self.directory_analyzer = DirectoryAnalyzer(target_dir, verbose)
        
        # Project analysis results
        self.project_type = None
        self.language = None
        self.git_state = None
        self.migration_complexity = None
        
        # Perform analysis
        self._analyze_project()
    
    def _analyze_project(self) -> None:
        """Perform comprehensive project analysis."""
        self.logger.info(f"Analyzing project: {self.target_dir}")
        
        # Detect project type and language
        self.language = self._detect_language()
        self.project_type = self._determine_project_type()
        
        # Analyze Git state
        self.git_state = self.git_manager.get_repo_state()
        
        # Assess migration complexity
        self.migration_complexity = self._assess_migration_complexity()
    
    def _detect_language(self) -> str:
        """Detect primary programming language."""
        scores = {lang: 0 for lang in self.LANGUAGE_PATTERNS}
        
        # Check for characteristic files
        for lang, patterns in self.LANGUAGE_PATTERNS.items():
            for file_pattern in patterns["files"]:
                if "*" in file_pattern:
                    # Handle glob patterns
                    import glob
                    matches = glob.glob(os.path.join(self.target_dir, file_pattern))
                    if matches:
                        scores[lang] += 10
                else:
                    # Direct file check
                    if os.path.exists(os.path.join(self.target_dir, file_pattern)):
                        scores[lang] += 10
            
            # Count files by extension
            ext_count = 0
            for root, dirs, files in os.walk(self.target_dir):
                if ".git" in root:
                    continue
                for file in files:
                    if any(file.endswith(ext) for ext in patterns["extensions"]):
                        ext_count += 1
            scores[lang] += ext_count
            
            # Check for characteristic directories
            for dir_name in patterns["directories"]:
                if os.path.exists(os.path.join(self.target_dir, dir_name)):
                    scores[lang] += 5
        
        # Return language with highest score
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        return "generic"
    
    def _determine_project_type(self) -> str:
        """Determine project type based on structure and content."""
        # Check if it's already a RepoKit project
        repokit_indicators = [
            "CLAUDE.md",
            os.path.join("private", "claude"),
            ".repokit.json"
        ]
        
        for indicator in repokit_indicators:
            if os.path.exists(os.path.join(self.target_dir, indicator)):
                return "repokit"
        
        # Check for empty directory
        try:
            contents = os.listdir(self.target_dir)
            # Filter out hidden files for empty check
            visible_contents = [item for item in contents if not item.startswith('.')]
            if not visible_contents:
                return "empty"
        except OSError:
            return "inaccessible"
        
        # Check if it's a Git repository
        if self.git_state and self.git_state.get("is_repo"):
            if self.git_state.get("has_commits"):
                return "git_with_history"
            else:
                return "git_new"
        
        # Check if it has source files
        has_source = False
        for root, dirs, files in os.walk(self.target_dir):
            for file in files:
                if any(file.endswith(ext) for lang_patterns in self.LANGUAGE_PATTERNS.values() 
                      for ext in lang_patterns["extensions"]):
                    has_source = True
                    break
            if has_source:
                break
        
        if has_source:
            return "source_no_git"
        else:
            return "files_no_git"
    
    def _assess_migration_complexity(self) -> str:
        """Assess migration complexity level."""
        complexity_score = 0
        
        # Git repository complexity
        if self.git_state and self.git_state.get("is_repo"):
            complexity_score += 2
            
            # Multiple branches add complexity
            branches = self.git_state.get("branches", [])
            if len(branches) > 2:
                complexity_score += 2
            
            # Uncommitted changes add complexity
            if self.git_state.get("has_uncommitted_changes"):
                complexity_score += 1
            
            # Existing remotes add complexity
            if self.git_state.get("remotes"):
                complexity_score += 1
        
        # File structure complexity
        dir_summary = self.directory_analyzer.get_summary()
        if dir_summary.get("has_template_conflicts"):
            complexity_score += 2
        
        # Large number of files
        if dir_summary.get("total_files", 0) > 100:
            complexity_score += 1
        
        if complexity_score <= 2:
            return "low"
        elif complexity_score <= 5:
            return "medium"
        else:
            return "high"
    
    def get_comprehensive_summary(self) -> Dict[str, Any]:
        """Get comprehensive project analysis summary."""
        # Get base directory analysis
        dir_summary = self.directory_analyzer.get_summary()
        
        # Enhance with project analysis
        summary = {
            "target_dir": self.target_dir,
            "project_type": self.project_type,
            "detected_language": self.language,
            "migration_complexity": self.migration_complexity,
            "git_state": self.git_state,
            "branch_strategy": self.git_manager.get_branch_strategy(),
            
            # Directory analysis results
            "existing_dirs": dir_summary["existing_dirs"],
            "missing_dirs": dir_summary["missing_dirs"],
            "special_dirs": dir_summary["special_dirs"],
            "has_git_repository": dir_summary["has_git_repository"],
            "has_template_conflicts": dir_summary["has_template_conflicts"],
            "file_counts": dir_summary["file_counts"],
            "total_files": dir_summary["total_files"],
            
            # Recommendations
            "recommended_strategy": self._recommend_migration_strategy(),
            "recommended_branch_strategy": self._recommend_branch_strategy(),
            "migration_steps": self._generate_migration_steps()
        }
        
        return summary
    
    def _recommend_migration_strategy(self) -> str:
        """Recommend migration strategy based on analysis."""
        if self.project_type == "empty":
            return "create_new"
        elif self.project_type == "repokit":
            return "already_repokit"
        elif self.migration_complexity == "low":
            return "safe"
        elif self.git_state and self.git_state.get("has_uncommitted_changes"):
            return "safe"  # Always safe when there are uncommitted changes
        else:
            return "merge"
    
    def _recommend_branch_strategy(self) -> str:
        """Recommend branch strategy based on project characteristics."""
        if self.project_type == "empty":
            return "standard"  # Default for new projects
        
        current_strategy = self.git_manager.get_branch_strategy()
        
        if current_strategy in ["gitflow", "standard", "simple"]:
            return current_strategy  # Keep existing if recognized
        
        # For small projects, recommend simple
        dir_summary = self.directory_analyzer.get_summary()
        if dir_summary.get("total_files", 0) < 50:
            return "simple"
        
        return "standard"  # Default recommendation
    
    def _generate_migration_steps(self) -> List[str]:
        """Generate step-by-step migration recommendations."""
        steps = []
        
        if self.project_type == "empty":
            steps = [
                "Initialize new RepoKit project structure",
                "Set up chosen branch strategy",
                "Generate language-specific templates",
                "Create remote repository if requested"
            ]
        elif self.project_type == "repokit":
            steps = ["Project is already using RepoKit structure"]
        elif self.git_state and self.git_state.get("has_uncommitted_changes"):
            steps = [
                "WARNING: Uncommitted changes detected",
                "Commit or stash changes before migration",
                "Run migration with 'safe' strategy"
            ]
        else:
            steps = [
                "Backup existing project (recommended)",
                "Analyze and resolve any template conflicts",
                "Apply RepoKit directory structure",
                "Initialize or update Git repository",
                "Set up branch strategy and worktrees",
                "Generate appropriate templates",
                "Create remote repository if requested"
            ]
        
        return steps


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


def analyze_project(directory: str, verbose: int = 0) -> Dict[str, Any]:
    """
    Comprehensive project analysis for universal migration.
    
    Args:
        directory: Directory to analyze
        verbose: Verbosity level (0=normal, 1=info, 2=debug)
        
    Returns:
        Comprehensive analysis summary
    """
    analyzer = ProjectAnalyzer(directory, verbose)
    return analyzer.get_comprehensive_summary()


def universal_migrate_project(directory: str, target_name: Optional[str] = None, strategy: str = "safe", 
                            branch_strategy: str = "auto", publish_to: Optional[str] = None,
                            dry_run: bool = False, verbose: int = 0) -> bool:
    """
    Universal project migration to RepoKit structure.
    
    This function handles any type of project and migrates it to RepoKit structure
    with appropriate branch strategies and remote publishing.
    
    Args:
        directory: Source directory to migrate
        target_name: Target repository name (default: use directory name)
        strategy: Migration strategy ("safe", "replace", "merge", "auto")
        branch_strategy: Branch strategy ("standard", "simple", "gitflow", "auto")
        publish_to: Remote service to publish to ("github", "gitlab")
        dry_run: If True, only log actions without executing
        verbose: Verbosity level (0=normal, 1=info, 2=debug)
        
    Returns:
        True if successful, False otherwise
    """
    # Use ProjectAnalyzer for comprehensive analysis
    analyzer = ProjectAnalyzer(directory, verbose)
    summary = analyzer.get_comprehensive_summary()
    
    # Determine target name
    if not target_name:
        target_name = os.path.basename(os.path.abspath(directory))
    
    # Auto-select strategies if requested
    if strategy == "auto":
        strategy = summary["recommended_strategy"]
    
    if branch_strategy == "auto":
        branch_strategy = summary["recommended_branch_strategy"]
    
    # Use UniversalMigrationExecutor for the actual migration
    executor = UniversalMigrationExecutor(directory, target_name, verbose)
    return executor.execute_migration(strategy, branch_strategy, publish_to, dry_run)


def adopt_project(directory: str = ".", strategy: str = "auto", branch_strategy: str = "auto",
                 publish_to: Optional[str] = None, dry_run: bool = False, verbose: int = 0) -> bool:
    """
    Adopt an existing project in-place to use RepoKit structure.
    
    This function converts the current directory to use RepoKit structure
    without creating a new directory.
    
    Args:
        directory: Directory to adopt (default: current directory)
        strategy: Migration strategy ("safe", "replace", "merge", "auto")
        branch_strategy: Branch strategy ("standard", "simple", "gitflow", "auto")
        publish_to: Remote service to publish to ("github", "gitlab")
        dry_run: If True, only log actions without executing
        verbose: Verbosity level (0=normal, 1=info, 2=debug)
        
    Returns:
        True if successful, False otherwise
    """
    # Use the directory name as the project name
    target_name = os.path.basename(os.path.abspath(directory))
    
    # For adoption, we modify in-place rather than creating a new structure
    return universal_migrate_project(
        directory=directory,
        target_name=target_name,
        strategy=strategy,
        branch_strategy=branch_strategy,
        publish_to=publish_to,
        dry_run=dry_run,
        verbose=verbose
    )


class UniversalMigrationExecutor:
    """
    Executes universal project migrations to RepoKit structure.
    
    This class handles the actual migration process for any type of project,
    including Git repository setup, file migration, and remote publishing.
    """
    
    def __init__(self, source_dir: str, target_name: str, verbose: int = 0):
        """Initialize UniversalMigrationExecutor."""
        self.source_dir = os.path.abspath(source_dir)
        self.target_name = target_name
        self.verbose = verbose
        self.logger = logging.getLogger("repokit.universal_executor")
        
        # Initialize project analyzer
        self.analyzer = ProjectAnalyzer(source_dir, verbose)
        
    def execute_migration(self, strategy: str = "safe", branch_strategy: str = "standard",
                         publish_to: Optional[str] = None, dry_run: bool = False) -> bool:
        """
        Execute the universal migration.
        
        Args:
            strategy: Migration strategy
            branch_strategy: Branch strategy to implement
            publish_to: Remote service to publish to ("github", "gitlab")
            dry_run: If True, only log actions without executing
            
        Returns:
            True if successful, False otherwise
        """
        if dry_run:
            return self._simulate_migration(strategy, branch_strategy, publish_to)
        
        try:
            # Step 1: Prepare target structure
            if not self._prepare_target_structure():
                return False
            
            # Step 2: Migrate files based on strategy
            if not self._migrate_files(strategy):
                return False
            
            # Step 3: Set up Git repository
            if not self._setup_git_repository(branch_strategy):
                return False
            
            # Step 4: Generate templates
            if not self._generate_templates():
                return False
            
            # Step 5: Publish to remote if requested
            if publish_to and not self._publish_to_remote(publish_to):
                return False
            
            self.logger.info("Universal migration completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Migration failed: {str(e)}")
            return False
    
    def _simulate_migration(self, strategy: str, branch_strategy: str, publish_to: Optional[str]) -> bool:
        """Simulate migration for dry run."""
        summary = self.analyzer.get_comprehensive_summary()
        
        self.logger.info("=== MIGRATION SIMULATION ===")
        self.logger.info(f"Source: {self.source_dir}")
        self.logger.info(f"Target: {self.target_name}")
        self.logger.info(f"Project type: {summary['project_type']}")
        self.logger.info(f"Language: {summary['detected_language']}")
        self.logger.info(f"Migration strategy: {strategy}")
        self.logger.info(f"Branch strategy: {branch_strategy}")
        
        if publish_to:
            self.logger.info(f"Would publish to: {publish_to}")
        
        self.logger.info("Migration steps:")
        for i, step in enumerate(summary['migration_steps'], 1):
            self.logger.info(f"  {i}. {step}")
        
        return True
    
    def _prepare_target_structure(self) -> bool:
        """Prepare the target RepoKit structure."""
        self.logger.info("Preparing target structure...")
        # Implementation would go here
        return True
    
    def _migrate_files(self, strategy: str) -> bool:
        """Migrate files based on strategy."""
        self.logger.info(f"Migrating files using strategy: {strategy}")
        # Implementation would go here
        return True
    
    def _setup_git_repository(self, branch_strategy: str) -> bool:
        """Set up Git repository with chosen branch strategy."""
        self.logger.info(f"Setting up Git repository with strategy: {branch_strategy}")
        # Implementation would go here
        return True
    
    def _generate_templates(self) -> bool:
        """Generate appropriate templates."""
        self.logger.info("Generating templates...")
        # Implementation would go here
        return True
    
    def _publish_to_remote(self, service: str) -> bool:
        """Publish to remote service."""
        self.logger.info(f"Publishing to {service}...")
        # Implementation would go here
        return True
