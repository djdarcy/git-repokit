#!/usr/bin/env python3
"""
Git Configuration Manager for RepoKit

Enhanced git configuration detection with multi-level cascade support.
Provides comprehensive user.name and user.email detection across different
git config levels.
"""

import os
import subprocess
import logging
from typing import Dict, Optional, Any


class GitConfigManager:
    """
    Manages git configuration detection with multi-level cascade support.

    Detection levels (in order of precedence):
    1. Repository-specific config (.git/config)
    2. Global user config (~/.gitconfig)
    3. System config (/etc/gitconfig)
    4. Environment variables
    5. Interactive prompts (if enabled)
    """

    def __init__(self, repo_path: Optional[str] = None, verbose: int = 0):
        """
        Initialize GitConfigManager.

        Args:
            repo_path: Path to git repository (for repo-specific config)
            verbose: Verbosity level for logging
        """
        self.repo_path = repo_path
        self.verbose = verbose
        self.logger = logging.getLogger("repokit.git_config")

    def get_comprehensive_user_info(self, interactive: bool = True) -> Dict[str, str]:
        """
        Get git user information using comprehensive detection cascade.

        Args:
            interactive: Whether to prompt user if information is missing

        Returns:
            Dictionary with 'name' and 'email' keys
        """
        user_info = {}

        # Level 1: Repository-specific config
        if self.repo_path:
            repo_config = self._get_repo_git_config()
            user_info.update(repo_config)
            if self.verbose >= 2:
                self.logger.debug(f"Repository config: {repo_config}")

        # Level 2: Global git config (if missing data)
        if not user_info.get('name') or not user_info.get('email'):
            global_config = self._get_global_git_config()
            for key, value in global_config.items():
                if not user_info.get(key):
                    user_info[key] = value
            if self.verbose >= 2:
                self.logger.debug(f"Global config: {global_config}")

        # Level 3: System git config (if still missing data)
        if not user_info.get('name') or not user_info.get('email'):
            system_config = self._get_system_git_config()
            for key, value in system_config.items():
                if not user_info.get(key):
                    user_info[key] = value
            if self.verbose >= 2:
                self.logger.debug(f"System config: {system_config}")

        # Level 4: Environment variables
        if not user_info.get('name') or not user_info.get('email'):
            env_config = self._get_env_git_config()
            for key, value in env_config.items():
                if not user_info.get(key):
                    user_info[key] = value
            if self.verbose >= 2:
                self.logger.debug(f"Environment config: {env_config}")

        # Level 5: Interactive prompts (if enabled and data still missing)
        missing_info = (not user_info.get('name') or
                        not user_info.get('email'))
        if interactive and missing_info:
            interactive_config = self._prompt_for_git_config(user_info)
            user_info.update(interactive_config)
            if self.verbose >= 2:
                self.logger.debug(f"Interactive config: {interactive_config}")

        # Log final result
        if self.verbose >= 1:
            name = user_info.get('name', 'NOT SET')
            email = user_info.get('email', 'NOT SET')
            self.logger.info(f"Final git user config: name='{name}', "
                            f"email='{email}'")

        return user_info

    def _get_repo_git_config(self) -> Dict[str, str]:
        """Get user config from repository-specific .git/config."""
        if not self.repo_path:
            return {}
        
        git_path = os.path.join(self.repo_path, ".git")
        if not os.path.exists(git_path):
            return {}

        config = {}

        # Get user.name from repo config
        try:
            result = subprocess.run(
                ["git", "config", "--local", "user.name"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0 and result.stdout.strip():
                config["name"] = result.stdout.strip()
        except Exception as e:
            if self.verbose >= 3:
                self.logger.debug(f"Failed to get repo user.name: {e}")

        # Get user.email from repo config
        try:
            result = subprocess.run(
                ["git", "config", "--local", "user.email"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0 and result.stdout.strip():
                config["email"] = result.stdout.strip()
        except Exception as e:
            if self.verbose >= 3:
                self.logger.debug(f"Failed to get repo user.email: {e}")

        return config

    def _get_global_git_config(self) -> Dict[str, str]:
        """Get user config from global ~/.gitconfig."""
        config = {}

        # Get user.name from global config
        try:
            result = subprocess.run(
                ["git", "config", "--global", "user.name"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0 and result.stdout.strip():
                config["name"] = result.stdout.strip()
        except Exception as e:
            if self.verbose >= 3:
                self.logger.debug(f"Failed to get global user.name: {e}")

        # Get user.email from global config
        try:
            result = subprocess.run(
                ["git", "config", "--global", "user.email"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0 and result.stdout.strip():
                config["email"] = result.stdout.strip()
        except Exception as e:
            if self.verbose >= 3:
                self.logger.debug(f"Failed to get global user.email: {e}")

        return config

    def _get_system_git_config(self) -> Dict[str, str]:
        """Get user config from system /etc/gitconfig."""
        config = {}

        # Get user.name from system config
        try:
            result = subprocess.run(
                ["git", "config", "--system", "user.name"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0 and result.stdout.strip():
                config["name"] = result.stdout.strip()
        except Exception as e:
            if self.verbose >= 3:
                self.logger.debug(f"Failed to get system user.name: {e}")

        # Get user.email from system config
        try:
            result = subprocess.run(
                ["git", "config", "--system", "user.email"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0 and result.stdout.strip():
                config["email"] = result.stdout.strip()
        except Exception as e:
            if self.verbose >= 3:
                self.logger.debug(f"Failed to get system user.email: {e}")

        return config

    def _get_env_git_config(self) -> Dict[str, str]:
        """Get user config from environment variables."""
        config = {}

        # Check for git-specific environment variables
        if os.environ.get('GIT_AUTHOR_NAME'):
            config["name"] = os.environ['GIT_AUTHOR_NAME']
        elif os.environ.get('GIT_COMMITTER_NAME'):
            config["name"] = os.environ['GIT_COMMITTER_NAME']

        if os.environ.get('GIT_AUTHOR_EMAIL'):
            config["email"] = os.environ['GIT_AUTHOR_EMAIL']
        elif os.environ.get('GIT_COMMITTER_EMAIL'):
            config["email"] = os.environ['GIT_COMMITTER_EMAIL']

        # Check for RepoKit-specific environment variables
        if os.environ.get('REPOKIT_USER_NAME'):
            config["name"] = os.environ['REPOKIT_USER_NAME']

        if os.environ.get('REPOKIT_USER_EMAIL'):
            config["email"] = os.environ['REPOKIT_USER_EMAIL']

        return config

    def _prompt_for_git_config(self, existing_config: Dict[str, str]) -> Dict[str, str]:
        """
        Interactively prompt user for missing git configuration.

        Args:
            existing_config: Already detected configuration

        Returns:
            Dictionary with user-provided values
        """
        config = {}

        try:
            # Prompt for name if missing
            if not existing_config.get('name'):
                print("\n" + "="*60)
                print("Git User Configuration Required")
                print("="*60)
                print("RepoKit needs your git user information for commits "
                      "and templates.")
                print("This will be saved to your project's .repokit.json file.")
                print()

                name = input("Enter your full name (for git commits): ").strip()
                if name:
                    config["name"] = name

            # Prompt for email if missing
            if not existing_config.get('email'):
                if not existing_config.get('name'):
                    print()  # Add spacing if we already prompted for name

                email = input("Enter your email address (for git commits): ").strip()
                if email:
                    config["email"] = email

            if config:
                print()
                print("✓ Configuration collected. This will be saved for future use.")
                print("="*60)

        except (KeyboardInterrupt, EOFError):
            # User cancelled input
            if self.verbose >= 1:
                self.logger.info("User cancelled git config input")

        return config

    def get_template_context(self, base_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get enhanced template context with git user information.

        Args:
            base_context: Existing template context to enhance

        Returns:
            Enhanced context dictionary with git user info
        """
        context = base_context.copy() if base_context else {}

        # Get comprehensive user info
        user_info = self.get_comprehensive_user_info(interactive=False)

        # Add git-specific template variables
        context.update({
            'author': user_info.get('name', 'Unknown Author'),
            'author_email': user_info.get('email', 'unknown@example.com'),
            'git_user_name': user_info.get('name'),
            'git_user_email': user_info.get('email'),

            # Backwards compatibility
            'user_name': user_info.get('name'),
            'user_email': user_info.get('email'),
        })

        return context

    def configure_repo_git_user(self, user_info: Optional[Dict[str, str]] = None) -> bool:
        """
        Configure git user settings in the repository.

        Args:
            user_info: User info dict, or None to detect automatically

        Returns:
            True if configuration was successful
        """
        if not self.repo_path:
            self.logger.warning("Cannot configure git user: no repository path")
            return False
        
        git_path = os.path.join(self.repo_path, ".git")
        if not os.path.exists(git_path):
            self.logger.warning("Cannot configure git user: not a git repository")
            return False

        if not user_info:
            user_info = self.get_comprehensive_user_info(interactive=True)

        success = True

        # Configure user.name
        if user_info.get('name'):
            try:
                subprocess.run(
                    ["git", "config", "user.name", user_info['name']],
                    cwd=self.repo_path,
                    check=True,
                    capture_output=True
                )
                if self.verbose >= 1:
                    self.logger.info(f"Set git user.name to: {user_info['name']}")
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Failed to set git user.name: {e}")
                success = False

        # Configure user.email
        if user_info.get('email'):
            try:
                subprocess.run(
                    ["git", "config", "user.email", user_info['email']],
                    cwd=self.repo_path,
                    check=True,
                    capture_output=True
                )
                if self.verbose >= 1:
                    self.logger.info(f"Set git user.email to: {user_info['email']}")
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Failed to set git user.email: {e}")
                success = False

        return success