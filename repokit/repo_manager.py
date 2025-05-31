#!/usr/bin/env python3
"""
RepoKit: Repository Template Generator

Core repository manager that handles repository initialization,
branch creation, worktree setup, and template generation.
"""

import os
import subprocess
import json
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

from .template_engine import TemplateEngine

class RepoManager:
    """Manages repository setup and configuration."""
    
    def __init__(self, config: Dict[str, Any], templates_dir: Optional[str] = None, verbose: int = 0):
        """
        Initialize the repository manager.
        
        Args:
            config: Dictionary containing repository configuration
            templates_dir: Optional path to custom templates directory
            verbose: Verbosity level (0=normal, 1=info, 2=debug)
        """
        self.config = config
        self.verbose = verbose
        self.project_name = config.get('name')
        self.project_root = os.path.abspath(self.project_name)
        self.repo_root = os.path.join(self.project_root, "local")
        self.github_root = os.path.join(self.project_root, "github")
        
        # Get logger for repokit
        self.logger = logging.getLogger("repokit")
        
        # Initialize template engine with same verbosity
        self.template_engine = TemplateEngine(templates_dir=templates_dir, verbose=verbose)
    
    def run_git(self, args: List[str], cwd: Optional[str] = None, check: bool = True) -> Optional[str]:
        """
        Run a git command and return its output.
        
        Args:
            args: List of git command arguments
            cwd: Working directory for the command
            check: Whether to check for command success
            
        Returns:
            Command output as string
        """
        cwd = cwd or self.repo_root
        cmd = ["git"] + args
        
        if self.verbose >= 2:
            self.logger.debug(f"Running: {' '.join(cmd)} in {cwd}")
            
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                check=check,
                capture_output=True,
                text=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Git command failed: {e.stderr}")
            if check:
                raise
            return None
    
    def setup_repository(self) -> bool:
        """
        Set up the repository structure according to configuration.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"Setting up repository: {self.project_name}")
            
            # Create project directory structure
            self._create_directory_structure()
            
            # Initialize git repositories
            self._init_git_repos()
            
            # Set up branches
            self._setup_branches()
            
            # Generate template files
            self._generate_template_files()
            
            # Create initial commit
            self._create_initial_commit()
            
            # Generate AI integration files if requested (only in private branch, after initial commit)
            if self.config.get('ai_integration'):
                self._generate_ai_templates()
            
            # Set up private content protection
            self._setup_protection()
            
            # Set up worktrees AFTER initial commits and branch updates
            # This is the key change - moved worktree setup to the end
            self._setup_worktrees()
            
            # Set up GitHub integration (copy files to GitHub worktree)
            self._setup_github_integration()
            
            self.logger.info(f"Repository setup complete: {self.project_name}")
            self._print_next_steps()
            
            return True
        except Exception as e:
            self.logger.error(f"Error setting up repository: {str(e)}")
            if self.verbose >= 2:
                import traceback
                traceback.print_exc()
            return False
    
    def _create_directory_structure(self) -> None:
        """Create the basic directory structure."""
        self.logger.info("Creating directory structure")
        
        # Create main project directory
        os.makedirs(self.project_root, exist_ok=True)
        
        # Create local repository directory
        os.makedirs(self.repo_root, exist_ok=True)
        
        # Create github directory for worktree
        os.makedirs(self.github_root, exist_ok=True)
        
        # Create standard subdirectories
        standard_dirs = self.config.get('directories', [
            'convos', 'docs', 'logs', 'private', 'revisions', 'scripts', 'tests'
        ])
        
        for directory in standard_dirs:
            dir_path = os.path.join(self.repo_root, directory)
            os.makedirs(dir_path, exist_ok=True)
            
            # Create .gitkeep file to ensure empty directories are tracked
            with open(os.path.join(dir_path, '.gitkeep'), 'w') as f:
                f.write('# This file ensures the directory is tracked by Git\n')
    
    def _init_git_repos(self) -> None:
        """Initialize git repositories."""
        self.logger.info("Initializing git repositories")
        
        # Initialize main repository
        self.run_git(["init"], cwd=self.repo_root)
        
        # Configure user information if provided
        user = self.config.get('user', {})
        if user:
            # Get user name
            if user.get('name'):
                self.run_git(["config", "user.name", user['name']], cwd=self.repo_root)
                self.logger.info(f"Set Git user.name to: {user['name']}")
            
            # Get user email with GitHub privacy protection
            if user.get('email'):
                email = user['email']
                
                # Apply GitHub privacy protection if enabled and pushing to GitHub
                if self.config.get('use_github_noreply', True) and self.config.get('github', True):
                    # If email isn't already a no-reply format
                    if '@users.noreply.github.com' not in email:
                        # Extract username from email or use first part
                        username = email.split('@')[0]
                        
                        # Create GitHub no-reply email
                        github_email = f"{username}@users.noreply.github.com"
                        self.logger.info(f"Using GitHub no-reply email format: {github_email}")
                        email = github_email
                
                self.run_git(["config", "user.email", email], cwd=self.repo_root)
                self.logger.info(f"Set Git user.email to: {email}")
            
    
    def _setup_branches(self) -> None:
        """Set up repository branches."""
        self.logger.info("Setting up branches")
        
        # Create an initial commit on main to allow branch creation
        readme_path = os.path.join(self.repo_root, "README.md")
        
        # Generate README from template
        context = {
            'project_name': self.project_name,
            'description': self.config.get('description', 'A new project'),
            'author': self.config.get('user', {}).get('name', ''),
            'author_email': self.config.get('user', {}).get('email', '')
        }
        
        # Try to render from template, fall back to simple content
        if not self.template_engine.render_template_to_file("README.md", readme_path, context):
            with open(readme_path, "w") as f:
                f.write(f"# {self.project_name}\n\n")
                f.write(f"{self.config.get('description', 'A new project')}\n")
        
        self.run_git(["add", "README.md"], cwd=self.repo_root)
        self.run_git(["commit", "-m", "Initial commit"], cwd=self.repo_root)
        
        # Create branches
        branches = self.config.get('branches', ['main', 'dev', 'staging', 'test', 'live'])
        
        # Ensure the configured default branch exists
        default_branch = self.config.get('default_branch', 'main')
        current_branch = self.run_git(["branch", "--show-current"], cwd=self.repo_root)
        
        if current_branch != default_branch:
            if default_branch not in branches:
                branches.append(default_branch)
            self.run_git(["branch", "-m", default_branch], cwd=self.repo_root)
        
        # Create other branches
        for branch in branches:
            if branch != default_branch:  # Skip default branch which already exists
                self.run_git(["branch", branch], cwd=self.repo_root)
        
        # Create private branch for personal work
        private_branch = self.config.get('private_branch', 'private')
        if private_branch not in branches:
            self.run_git(["branch", private_branch], cwd=self.repo_root)
        
        # Switch to private branch (we stay on private in the main repo)
        self.run_git(["checkout", private_branch], cwd=self.repo_root)
    
    def _setup_worktrees(self) -> None:
        """Set up git worktrees for branches."""
        self.logger.info("Setting up worktrees")
        
        # Get branches to create worktrees for
        worktree_branches = self.config.get('worktrees', [self.config.get('default_branch', 'main'), 'dev'])

        # Always add GitHub directory as worktree with the default branch if it�s in the list
        main_branch = self.config.get('default_branch', 'main')
        if main_branch in worktree_branches:
            # Get directory name for main branch from branch_config
            github_dir = self.config.get('branch_config', {}).get('branch_directories', {}).get(main_branch, 'github')
            github_path = os.path.join(os.path.dirname(self.repo_root), github_dir)
            
            try:
                self.run_git(["worktree", "add", github_path, main_branch], cwd=self.repo_root)
                self.logger.info(f"Created worktree for branch '{main_branch}' at {github_path}")
            except Exception as e:
                self.logger.error(f"Failed to create worktree for branch '{main_branch}': {str(e)}")
            
            # Configure Git for the GitHub worktree if user information is provided
            user = self.config.get('user', {})
            if user:
                if user.get('name'):
                    self.run_git(["config", "user.name", user['name']], cwd=github_path)
                
                if user.get('email'):
                    self.run_git(["config", "user.email", user['email']], cwd=github_path)
        
        # Add additional worktrees as configured
        worktree_base = os.path.dirname(self.repo_root)
        for branch in worktree_branches:
            if branch == main_branch and main_branch in self.config.get('branch_config', {}).get('branch_directories', {}):
                # Skip main branch if it has a custom directory mapping (already handled above)
                continue
                
            # Get directory name for this branch
            branch_dir = self.config.get('branch_config', {}).get('branch_directories', {}).get(branch, branch)
            worktree_path = os.path.join(worktree_base, branch_dir)
            
            # Skip if already exists (might be the main branch worktree we already created)
            if os.path.exists(worktree_path):
                continue
                
            try:
                self.run_git(["worktree", "add", worktree_path, branch], cwd=self.repo_root)
                self.logger.info(f"Created worktree for branch '{branch}' at {worktree_path}")
                
                # Configure Git for this worktree if user information is provided
                if user:
                    if user.get('name'):
                        self.run_git(["config", "user.name", user['name']], cwd=worktree_path)
                    
                    if user.get('email'):
                        self.run_git(["config", "user.email", user['email']], cwd=worktree_path)
            except Exception as e:
                self.logger.warning(f"Failed to create worktree for branch '{branch}': {str(e)}")
    
    def _generate_template_files(self) -> None:
        """Generate template files for the repository."""
        self.logger.info("Generating template files")
        
        # Get language to determine specific templates
        language = self.config.get('language', 'generic')
        
        # Context for template rendering
        context = {
            'project_name': self.project_name,
            'language': language,
            'description': self.config.get('description', ''),
            'author': self.config.get('user', {}).get('name', ''),
            'author_email': self.config.get('user', {}).get('email', '')
        }
        
        # Create .github directory
        github_dir = os.path.join(self.repo_root, ".github")
        os.makedirs(github_dir, exist_ok=True)
        
        # Create workflow directory
        workflow_dir = os.path.join(github_dir, "workflows")
        os.makedirs(workflow_dir, exist_ok=True)
        
        # Create ISSUE_TEMPLATE directory
        issue_dir = os.path.join(github_dir, "ISSUE_TEMPLATE")
        os.makedirs(issue_dir, exist_ok=True)
        
        # Generate GitHub workflow file
        self.template_engine.render_template_to_file(
            "main.yml",
            os.path.join(workflow_dir, "main.yml"),
            context,
            category="github/workflows"
        )
        
        # Generate issue templates
        self.template_engine.render_template_to_file(
            "bug-report.md",
            os.path.join(issue_dir, "bug-report.md"),
            context,
            category="github/ISSUE_TEMPLATE"
        )
        
        self.template_engine.render_template_to_file(
            "feature-request.md",
            os.path.join(issue_dir, "feature-request.md"),
            context,
            category="github/ISSUE_TEMPLATE"
        )
        
        # Generate CODEOWNERS file
        self.template_engine.render_template_to_file(
            "CODEOWNERS",
            os.path.join(github_dir, "CODEOWNERS"),
            context,
            category="github"
        )
        
        # Generate other common files
        self.template_engine.render_template_to_file(
            "CONTRIBUTING.md",
            os.path.join(self.repo_root, "CONTRIBUTING.md"),
            context,
            category="common"
        )
        
        # Create language-specific configuration files
        self._create_language_specific_files(language, context)
    
    def _create_language_specific_files(self, language: str, context: Dict[str, Any]) -> None:
        """
        Create language-specific configuration files.
        
        Args:
            language: Programming language
            context: Template context variables
        """
        if language == 'python':
            # Create setup.py
            self.template_engine.render_template_to_file(
                "setup.py",
                os.path.join(self.repo_root, "setup.py"),
                context,
                category="languages/python"
            )
            
            # Create requirements.txt
            self.template_engine.render_template_to_file(
                "requirements.txt",
                os.path.join(self.repo_root, "requirements.txt"),
                context,
                category="languages/python"
            )
            
            # Create Python .gitignore
            self.template_engine.render_template_to_file(
                "gitignore",
                os.path.join(self.repo_root, ".gitignore"),
                context,
                category="languages/python"
            )
                
        elif language == 'javascript':
            # Create package.json
            self.template_engine.render_template_to_file(
                "package.json",
                os.path.join(self.repo_root, "package.json"),
                context,
                category="languages/javascript"
            )
            
            # Create .npmrc
            self.template_engine.render_template_to_file(
                "npmrc",
                os.path.join(self.repo_root, ".npmrc"),
                context,
                category="languages/javascript"
            )
            
            # Create JavaScript .gitignore
            self.template_engine.render_template_to_file(
                "gitignore",
                os.path.join(self.repo_root, ".gitignore"),
                context,
                category="languages/javascript"
            )
        else:
            # Create generic .gitignore
            self.template_engine.render_template_to_file(
                "gitignore",
                os.path.join(self.repo_root, ".gitignore"),
                context,
                category="common"
            )
        
        # Add VS Code launch.json for all languages
        vscode_dir = os.path.join(self.repo_root, ".vscode")
        os.makedirs(vscode_dir, exist_ok=True)
        
        self.template_engine.render_template_to_file(
            "launch.json",
            os.path.join(vscode_dir, "launch.json"),
            context,
            category="common"
        )
    
    def _setup_github_integration(self) -> None:
        """Set up GitHub integration."""
        self.logger.info("Setting up GitHub integration")
        
        # Skip if GitHub integration is disabled
        if not self.config.get('github', True):
            self.logger.info("GitHub integration is disabled, skipping")
            return
        
        # Only proceed if the GitHub worktree exists
        if not os.path.exists(self.github_root):
            self.logger.warning("GitHub worktree not found, skipping GitHub integration")
            return
            
        # Copy .github directory to github worktree
        github_src = os.path.join(self.repo_root, ".github")
        github_dst = os.path.join(self.github_root, ".github")
        
        if os.path.exists(github_src):
            if os.path.exists(github_dst):
                shutil.rmtree(github_dst)
            shutil.copytree(github_src, github_dst)
            
            # Check if there are changes to commit before trying
            if self._has_changes(self.github_root):
                try:
                    self.run_git(["add", ".github"], cwd=self.github_root)
                    self.run_git(["commit", "-m", "Add GitHub configuration files"], cwd=self.github_root)
                    self.logger.info("Committed GitHub configuration files")
                except Exception as e:
                    self.logger.warning(f"Failed to commit GitHub files: {str(e)}")
            else:
                self.logger.info("No GitHub files to commit")
        else:
            self.logger.warning("No .github directory found in repository, skipping GitHub integration")
    
    def _setup_protection(self) -> None:
        """Set up protection for private content."""
        self.logger.info("Setting up private content protection")
        
        # Append to .gitignore for private content
        gitignore_path = os.path.join(self.repo_root, ".gitignore")
        
        with open(gitignore_path, "a") as f:
            f.write("\n# Private content\n")
            
            # Get private directories from config
            private_dirs = self.config.get("private_dirs", ["private", "convos", "logs"])
            for private_dir in private_dirs:
                f.write(f"/{private_dir}/\n")
            
            f.write("**/__private__*\n\n")
        
        # Create pre-commit hook
        hooks_dir = os.path.join(self.repo_root, ".git", "hooks")
        os.makedirs(hooks_dir, exist_ok=True)
        
        # Generate the pattern string for private directories
        private_dirs_patterns = ""
        for dir_name in self.config.get("private_dirs", ["private", "convos", "logs"]):
            pattern = f"^{dir_name}/"
            private_dirs_patterns += f'    "{pattern}"\n'
        
        # Render pre-commit hook from template
        context = {
            'private_dirs_patterns': private_dirs_patterns
        }
        
        pre_commit_path = os.path.join(hooks_dir, "pre-commit")
        if not self.template_engine.render_template_to_file(
            "pre-commit",
            pre_commit_path,
            context,
            category="hooks"
        ):
            # Fallback to creating a simple hook
            with open(pre_commit_path, "w") as f:
                f.write("""#!/bin/sh
# Pre-commit hook to prevent committing private content

# Check for private directories
for file in $(git diff --cached --name-only); do
    if echo "$file" | grep -q -E "^private/|^convos/|^logs/|__private__"; then
        echo "ERROR: Attempting to commit private content: $file"
        echo "Private content should not be committed to the repository."
        exit 1
    fi
done

exit 0
""")
        
        # Make hook executable on Unix-like systems
        if os.name != 'nt':  # not Windows
            os.chmod(pre_commit_path, 0o755)
    
    def _create_initial_commit(self) -> None:
        """Create initial commit in repository."""
        self.logger.info("Creating initial commit")
        
        # Add all files
        self.run_git(["add", "."], cwd=self.repo_root)
        
        # Create commit
        self.run_git(["commit", "-m", "Initial repository setup with RepoKit"], cwd=self.repo_root)
        
        # Push to branches WITHOUT checking them out directly
        # This avoids the worktree conflict issue
        branches = self.config.get('branches', ['main', 'dev', 'staging', 'test', 'live'])
        private_branch = self.config.get('private_branch', 'private')
        
        for branch in branches:
            if branch != private_branch:  # Skip private branch
                try:
                    # Use git push to update branches without checking out
                    self.run_git(["push", ".", f"{private_branch}:{branch}"], cwd=self.repo_root)
                    if self.verbose >= 2:
                        self.logger.debug(f"Updated branch '{branch}' from {private_branch}")
                except Exception as e:
                    self.logger.warning(f"Failed to update branch '{branch}': {str(e)}")
        
        # We stay on private branch
        # No need to check out private branch again as we're already on it
    
    def _has_changes(self, directory: str) -> bool:
        """
        Check if there are uncommitted changes in the repository.
        
        Args:
            directory: Directory to check
            
        Returns:
            True if there are changes, False otherwise
        """
        try:
            # Check for any changes (staged or unstaged)
            output = self.run_git(["status", "--porcelain"], cwd=directory, check=False)
            return bool(output and output.strip())
        except Exception:
            # In case of error, assume there are changes
            return True
    
    def _print_next_steps(self) -> None:
        """Print next steps for the user."""
        print("\n" + "="*80)
        print(f"Repository {self.project_name} has been set up successfully!")
        print("\nDirectory structure:")
        print(f"  {self.project_name}/")
        
        # Use ASCII characters instead of Unicode box-drawing characters
        # This avoids encoding errors on Windows command prompt
        print(f"  |-- local/          # Main repository ({self.config.get('private_branch', 'private')} branch)")
        
        if self.config.get('github', True):
            print(f"  |-- github/         # GitHub worktree (main branch)")
        
        worktree_branches = self.config.get('worktrees', ['main', 'dev'])
        for branch in worktree_branches:
            if branch != 'main' or not self.config.get('github', True):  # Skip main if github is enabled
                print(f"  |-- {branch}/           # {branch} branch worktree")
        
        print("\nNext steps:")
        print("1. Set up a remote GitHub repository")
        print("2. Add it as a remote:")
        print(f"   cd {self.repo_root}")
        print("   git remote add origin https://github.com/username/repo.git")
        print("3. Push your branches:")
        print("   git push -u origin main")
        print("   git push -u origin dev")
        
        private_branch = self.config.get('private_branch', 'private')
        print(f"\nRemember: The '{private_branch}' branch is for your local work only and should not be pushed!")
        print("="*80)

    def bootstrap_repository(self, source_dir: Optional[str] = None) -> bool:
        """
        Bootstrap a repository with essential files from a source directory.
        
        This is used to set up the repository with existing code, typically
        used to bootstrap RepoKit itself or to convert an existing project
        to use RepoKit's structure.
        
        Args:
            source_dir: Source directory containing the files to copy
                    (default: current directory)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"Bootstrapping repository from {source_dir}")
            
            # Default to current directory if not specified
            if not source_dir:
                source_dir = os.getcwd()
            
            # First set up the repository structure
            if not self.setup_repository():
                self.logger.error("Failed to set up repository structure")
                return False
            
            # Import utils module (avoid circular imports)
            from .utils import copy_files, get_essential_file_patterns
            
            # Get essential file patterns
            patterns = get_essential_file_patterns()
            
            # Copy essential files to repository
            copied = copy_files(
                source_dir,
                self.repo_root,
                include_patterns=patterns["include"],
                exclude_patterns=patterns["exclude"]
            )
            
            if copied == 0:
                self.logger.warning("No files were copied during bootstrap")
                return False
            
            # Create a commit with the copied files
            try:
                self.run_git(["add", "."], cwd=self.repo_root)
                self.run_git(["commit", "-m", "Bootstrap repository with source files"], cwd=self.repo_root)
                self.logger.info("Committed bootstrap files")
                
                # Update branches from private
                self._update_branches_from_private()
                
                # Update worktrees to match their branches
                self._update_worktrees()
            except Exception as e:
                self.logger.error(f"Error committing bootstrap files: {str(e)}")
                return False
            
            self.logger.info("Repository bootstrap complete")
            return True
        except Exception as e:
            self.logger.error(f"Error bootstrapping repository: {str(e)}")
            return False

    def _update_branches_from_private(self) -> None:
        """
        Update all branches from the private branch.
        
        This is used after committing bootstrap files to ensure all branches
        have the same content.
        """
        private_branch = self.config.get("private_branch", "private")
        branches = self.config.get("branches", ["main", "dev", "staging", "test", "live"])
        
        # Get current branch
        current_branch = self.run_git(["branch", "--show-current"], cwd=self.repo_root)
        
        # Get the commit hash of the private branch for reset operations
        private_hash = self.run_git(["rev-parse", private_branch], cwd=self.repo_root)
        
        for branch in branches:
            if branch != private_branch:
                try:
                    # Check if the branch is checked out in a worktree
                    if self._is_branch_in_worktree(branch):
                        # For branches in worktrees, we need to update them directly in the worktree
                        worktree_path = self._get_worktree_path(branch)
                        if worktree_path:
                            # Use a more forceful update approach
                            self.logger.info(f"Updating branch '{branch}' in worktree {worktree_path}")
                            
                            # First fetch the changes from the main repository
                            self.run_git(["fetch", "..", private_branch], cwd=worktree_path, check=False)
                            
                            # Then hard reset to the private branch commit
                            self.run_git(["reset", "--hard", private_hash], cwd=worktree_path, check=False)
                            
                            # Verify the update worked
                            current_hash = self.run_git(["rev-parse", "HEAD"], cwd=worktree_path, check=False)
                            if current_hash == private_hash:
                                self.logger.info(f"Updated branch '{branch}' from {private_branch}")
                            else:
                                self.logger.warning(f"Failed to update branch '{branch}' to match {private_branch}")
                    else:
                        # For branches not in worktrees, we can update them directly
                        self.run_git(["checkout", branch], cwd=self.repo_root)
                        self.run_git(["reset", "--hard", private_branch], cwd=self.repo_root)
                        self.logger.info(f"Updated branch '{branch}' from {private_branch}")
                except Exception as e:
                    self.logger.warning(f"Failed to update branch '{branch}': {str(e)}")
        
        # Return to original branch
        if current_branch != self.run_git(["branch", "--show-current"], cwd=self.repo_root):
            self.run_git(["checkout", current_branch], cwd=self.repo_root)

    def _update_worktrees(self) -> None:
        """
        Update all worktrees to match their corresponding branches.
        
        This ensures that all worktree directories reflect the latest state
        of their branches.
        """
        # Check if we have worktrees
        worktree_output = self.run_git(["worktree", "list"], cwd=self.repo_root, check=False)
        if not worktree_output:
            return
        
        # Parse worktree list
        worktrees = {}
        for line in worktree_output.split('\n'):
            if not line.strip():
                continue
            
            # Parse worktree line (format: "/path/to/worktree  abcd1234 [branch]")
            parts = line.split()
            if len(parts) >= 3 and '[' in parts[2] and ']' in parts[2]:
                path = parts[0]
                branch = parts[2].strip('[]')
                worktrees[branch] = path
        
        # Update each worktree
        for branch, path in worktrees.items():
            if branch == self.config.get("private_branch", "private"):
                # Skip private branch
                continue
            
            try:
                # Force synchronization with the branch from the main repository
                branch_hash = self.run_git(["rev-parse", branch], cwd=self.repo_root)
                
                # Make sure worktree has latest changes from its branch
                self.run_git(["reset", "--hard", branch_hash], cwd=path, check=False)
                self.run_git(["clean", "-fd"], cwd=path, check=False)
                
                # Verify the update worked
                current_hash = self.run_git(["rev-parse", "HEAD"], cwd=path, check=False)
                if current_hash == branch_hash:
                    self.logger.info(f"Updated worktree for branch '{branch}' at {path}")
                else:
                    self.logger.warning(f"Failed to update worktree for branch '{branch}' at {path}")
            except Exception as e:
                self.logger.warning(f"Failed to update worktree for branch '{branch}': {str(e)}")

    def _is_branch_in_worktree(self, branch: str) -> bool:
        """
        Check if a branch is currently checked out in a worktree.
        
        Args:
            branch: Branch name to check
            
        Returns:
            True if the branch is checked out in a worktree, False otherwise
        """
        try:
            # Get worktree list
            worktree_output = self.run_git(["worktree", "list"], cwd=self.repo_root, check=False)
            
            # Check if branch is in any worktree
            for line in worktree_output.split('\n'):
                if f"[{branch}]" in line:
                    return True
            
            return False
        except Exception:
            # If we can't determine, assume it's not in a worktree
            return False

    def _get_worktree_path(self, branch: str) -> Optional[str]:
        """
        Get the path to the worktree containing a branch.
        
        Args:
            branch: Branch name
            
        Returns:
            Path to the worktree or None if the branch is not in a worktree
        """
        try:
            # Get worktree list
            worktree_output = self.run_git(["worktree", "list"], cwd=self.repo_root, check=False)
            
            # Find worktree with this branch
            for line in worktree_output.split('\n'):
                if f"[{branch}]" in line:
                    # Extract path from line (it's the first part)
                    return line.split()[0]
            
            return None
        except Exception:
            # If we can't determine, return None
            return None

    def publish_repository(self, service: str = "github", remote_name: str = "origin",
                        private: bool = False, push_branches: bool = True,
                        organization: Optional[str] = None,
                        token_command: Optional[str] = None,
                        credentials_file: Optional[str] = None) -> bool:
        """
        Set up remote repository and push branches.
        
        This is a convenience method that wraps RemoteIntegration functionality
        directly in the RepoManager class.
        
        Args:
            service: Remote service ("github" or "gitlab")
            remote_name: Name for the remote
            private: Whether the repository should be private
            push_branches: Whether to push branches
            organization: Organization or group name
            token_command: Command to retrieve token
            credentials_file: Path to credentials file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Import RemoteIntegration (avoid circular imports)
            from .remote_integration import RemoteIntegration
            
            # Initialize remote integration
            remote_integration = RemoteIntegration(
                self,
                credentials_file=credentials_file,
                verbose=self.verbose
            )
            
            # Set up remote repository
            success = remote_integration.setup_remote_repository(
                service=service,
                remote_name=remote_name,
                private=private,
                push_branches=push_branches,
                organization=organization,
                token_command=token_command
            )
            
            if not success:
                self.logger.error(f"Failed to publish repository to {service}")
                return False
            
            self.logger.info(f"Successfully published repository to {service}")
            return True
        except Exception as e:
            self.logger.error(f"Error publishing repository: {str(e)}")
            return False
    
    def _generate_ai_templates(self) -> None:
        """Generate AI integration templates (only in private branch)."""
        ai_provider = self.config.get('ai_integration', '').lower()
        if not ai_provider or ai_provider == 'none':
            return
            
        self.logger.info(f"Generating AI integration files for: {ai_provider}")
        
        # Create private/claude directory structure
        if ai_provider == 'claude':
            claude_dir = os.path.join(self.repo_root, "private", "claude")
            instructions_dir = os.path.join(claude_dir, "instructions")
            os.makedirs(instructions_dir, exist_ok=True)
            
            # Context for AI templates
            import datetime
            context = {
                'project_name': self.project_name,
                'description': self.config.get('description', 'A new project'),
                'language': self.config.get('language', 'generic'),
                'date': datetime.datetime.now().strftime('%Y-%m-%d'),
                'test_command': self._get_test_command(),
                'lint_command': self._get_lint_command(),
                'build_command': self._get_build_command()
            }
            
            # Generate CLAUDE.md
            self.template_engine.render_template_to_file(
                "CLAUDE.md",
                os.path.join(self.repo_root, "CLAUDE.md"),
                context,
                category=f"ai/{ai_provider}"
            )
            
            # Copy instruction files
            instruction_files = [
                "step1_context_rebuilder.md",
                "step2_dev_workflow_process.md",
                "step3_context_bridge.md"
            ]
            
            for instruction_file in instruction_files:
                # Try to get template path - for instruction files, try without .template extension first
                src_path = os.path.join(self.template_engine.templates_dir, f"ai/{ai_provider}/instructions", instruction_file)
                if not os.path.exists(src_path):
                    # Try with template engine's path finding
                    src_path = self.template_engine.get_template_path(
                        instruction_file, 
                        category=f"ai/{ai_provider}/instructions"
                    )
                
                if src_path and os.path.exists(src_path):
                    dest_path = os.path.join(instructions_dir, instruction_file)
                    shutil.copy2(src_path, dest_path)
                    self.logger.debug(f"Copied instruction file: {instruction_file}")
            
            # Add files to git (use -f for private directory since it's in .gitignore)
            self.run_git(["add", "CLAUDE.md"], cwd=self.repo_root)
            self.run_git(["add", "-f", "private/claude/"], cwd=self.repo_root)
            
            # Commit AI integration files
            self.run_git(["commit", "-m", "Add Claude AI integration files"], cwd=self.repo_root)
            
            self.logger.info("AI integration files generated successfully")
    
    def _get_test_command(self) -> str:
        """Get the appropriate test command for the language."""
        language = self.config.get('language', 'generic')
        commands = {
            'python': 'pytest',
            'javascript': 'npm test',
            'generic': '# Add your test command here'
        }
        return commands.get(language, commands['generic'])
    
    def _get_lint_command(self) -> str:
        """Get the appropriate lint command for the language."""
        language = self.config.get('language', 'generic')
        commands = {
            'python': 'black . && flake8',
            'javascript': 'npm run lint',
            'generic': '# Add your lint command here'
        }
        return commands.get(language, commands['generic'])
    
    def _get_build_command(self) -> str:
        """Get the appropriate build command for the language."""
        language = self.config.get('language', 'generic')
        commands = {
            'python': 'python setup.py build',
            'javascript': 'npm run build',
            'generic': '# Add your build command here'
        }
        return commands.get(language, commands['generic'])
