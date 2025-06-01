#!/usr/bin/env python3
"""
Configuration management for RepoKit.

Handles loading, validating, and merging configurations from
multiple sources (defaults, config files, environment, CLI).
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Union

from .directory_profiles import DirectoryProfileManager


class ConfigManager:
    """
    Manages configuration loading and validation for RepoKit.

    The configuration hierarchy (from lowest to highest precedence):
    1. Default values
    2. Global config file (~/.repokit/config.json)
    3. Project config file (./.repokit.json)
    4. Environment variables (REPOKIT_*)
    5. Command line arguments
    """

    def __init__(self, verbose: int = 0):
        """
        Initialize the configuration manager.

        Args:
            verbose: Verbosity level (0=normal, 1=info, 2=debug)
        """
        self.verbose = verbose
        self.logger = logging.getLogger("repokit.config")
        
        # Initialize directory profile manager
        self.directory_manager = DirectoryProfileManager(verbose=verbose)

        # Default configuration
        self.default_config = {
            "name": "my-project",
            "description": "A new project repository",
            "language": "generic",
            "default_branch": "main",
            "branches": ["main", "dev", "staging", "test", "live"],
            "worktrees": ["main", "dev"],
            "directories": [
                "convos",
                "docs",
                "logs",
                "private",
                "revisions",
                "scripts",
                "tests",
            ],
            "private_dirs": ["private", "convos", "logs"],
            "private_branch": "private",
            "github": True,
            "use_github_noreply": True,  # Add GitHub no-reply setting
            "user": {"name": "", "email": ""},
            # Branch configuration enhancements
            "branch_config": {
                # Default mapping between branch names and directory names
                "branch_directories": {
                    "main": "github",  # main branch maps to github directory by default
                    "dev": "dev",  # dev branch maps to dev directory
                    # Other branches use the branch name as directory name by default
                },
                # Define branch purposes and relationships
                "branch_roles": {
                    "main": "production",  # Main production branch
                    "dev": "development",  # Development branch
                    "staging": "pre-release",  # Pre-production testing
                    "test": "testing",  # Testing branch
                    "live": "live",  # Live deployment branch
                    "private": "personal",  # Personal/local development
                },
                # Define branch flow (which branches can be merged to which)
                "branch_flow": {
                    "private": ["dev"],  # Private can merge to dev
                    "dev": ["staging", "test"],  # Dev can merge to staging or test
                    "test": ["staging"],  # Test can merge to staging
                    "staging": ["main"],  # Staging can merge to main
                    "main": ["live"],  # Main can merge to live
                },
            },
            # Branch strategy templates
            "branch_strategy": "standard",  # Default strategy
            "branch_strategies": {
                "standard": {
                    "branches": ["main", "dev", "staging", "test", "live"],
                    "worktrees": ["main", "dev"],
                    "private_branch": "private",
                },
                "simple": {
                    "branches": ["main", "dev"],
                    "worktrees": ["main"],
                    "private_branch": "private",
                },
                "gitflow": {
                    "branches": ["main", "develop", "release", "hotfix"],
                    "worktrees": ["main", "develop"],
                    "private_branch": "private",
                },
                "github-flow": {
                    "branches": ["main"],
                    "worktrees": ["main"],
                    "private_branch": "private",
                },
                "minimal": {
                    "branches": ["main"],
                    "worktrees": [],
                    "private_branch": "main",
                },
            },
        }

        # Load configurations
        self.global_config = self._load_global_config()
        self.project_config = self._load_project_config()
        self.env_config = self._load_env_config()
        self.cli_config = {}  # Will be set later

        # The merged, final configuration
        self.config = self._merge_configs()

    def apply_branch_strategy(self) -> None:
        """
        Apply the selected branch strategy to the configuration.

        This updates branches, worktrees, and other settings based on the
        selected branch strategy.
        """
        # Get the selected strategy
        strategy_name = self.config.get("branch_strategy", "standard")
        strategies = self.config.get("branch_strategies", {})

        if strategy_name in strategies:
            strategy = strategies[strategy_name]

            # Only update if not explicitly set in config
            if "branches" not in self.cli_config:
                self.config["branches"] = strategy.get("branches", ["main", "dev"])

            if "worktrees" not in self.cli_config:
                self.config["worktrees"] = strategy.get("worktrees", ["main"])

            if "private_branch" not in self.cli_config:
                self.config["private_branch"] = strategy.get(
                    "private_branch", "private"
                )

            # Ensure default_branch aligns
            if "default_branch" not in self.cli_config:
                self.config["default_branch"] = self.config.get(
                    "default_branch", "main"
                )

            if self.verbose >= 1:
                self.logger.info(f"Applied branch strategy '{strategy_name}'")

    def get_branch_directory(self, branch_name: str) -> str:
        """
        Get the directory name for a branch.

        Args:
            branch_name: Name of the branch

        Returns:
            Directory name for the branch
        """
        # Check branch_directories mapping first
        branch_dirs = self.config.get("branch_config", {}).get("branch_directories", {})

        if branch_name in branch_dirs:
            return branch_dirs[branch_name]

        # Default: use branch name as directory name
        return branch_name

    def load_branch_config_file(self, path: str) -> bool:
        """
        Load branch configuration from a file.

        Args:
            path: Path to branch configuration file

        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            with open(path, "r") as f:
                branch_config = json.load(f)

            # Update branch configuration
            if "branch_config" in branch_config:
                self.project_config["branch_config"] = branch_config["branch_config"]

            if "branch_strategy" in branch_config:
                self.project_config["branch_strategy"] = branch_config[
                    "branch_strategy"
                ]

            if "branch_strategies" in branch_config:
                self.project_config["branch_strategies"] = branch_config[
                    "branch_strategies"
                ]

            # Remerge configs
            self.config = self._merge_configs()

            # Apply branch strategy
            self.apply_branch_strategy()

            if self.verbose >= 1:
                self.logger.info(f"Loaded branch configuration from {path}")

            return True
        except Exception as e:
            self.logger.error(
                f"Failed to load branch configuration from {path}: {str(e)}"
            )
            return False

    def _load_global_config(self) -> Dict[str, Any]:
        """
        Load global configuration from ~/.repokit/config.json.

        Returns:
            Global configuration or empty dict if not found
        """
        home_dir = os.path.expanduser("~")
        global_config_path = os.path.join(home_dir, ".repokit", "config.json")

        if os.path.exists(global_config_path):
            try:
                with open(global_config_path, "r") as f:
                    config = json.load(f)
                if self.verbose >= 1:
                    self.logger.info(f"Loaded global config from {global_config_path}")
                return config
            except Exception as e:
                self.logger.warning(f"Error loading global config: {str(e)}")

        return {}

    def _load_project_config(self) -> Dict[str, Any]:
        """
        Load project-specific configuration from ./.repokit.json.

        Returns:
            Project configuration or empty dict if not found
        """
        project_config_path = os.path.join(os.getcwd(), ".repokit.json")

        if os.path.exists(project_config_path):
            try:
                with open(project_config_path, "r") as f:
                    config = json.load(f)
                if self.verbose >= 1:
                    self.logger.info(
                        f"Loaded project config from {project_config_path}"
                    )
                return config
            except Exception as e:
                self.logger.warning(f"Error loading project config: {str(e)}")

        return {}

    def _load_env_config(self) -> Dict[str, Any]:
        """
        Load configuration from environment variables (REPOKIT_*).

        Returns:
            Environment configuration
        """
        config = {}

        # Look for environment variables with REPOKIT_ prefix
        for key, value in os.environ.items():
            if key.startswith("REPOKIT_"):
                # Convert REPOKIT_SNAKE_CASE to camelCase or underscore
                config_key = key[8:].lower()  # Remove REPOKIT_ and lowercase

                # Handle nested keys (e.g., REPOKIT_USER_NAME -> user.name)
                parts = config_key.split("_")
                current = config

                for i, part in enumerate(parts):
                    if i == len(parts) - 1:  # Last part
                        current[part] = value
                    else:
                        if part not in current:
                            current[part] = {}
                        current = current[part]

        # Special handling for list-type values
        for key in ["branches", "worktrees", "directories", "private_dirs"]:
            env_key = f"REPOKIT_{key.upper()}"
            if env_key in os.environ:
                config[key] = os.environ[env_key].split(",")

        if config and self.verbose >= 1:
            self.logger.info(f"Loaded configuration from environment variables")

        return config

    def set_cli_config(self, cli_config: Dict[str, Any]) -> None:
        """
        Set the command-line configuration.

        Args:
            cli_config: Configuration from command-line arguments
        """
        self.cli_config = cli_config

        # Remerge configs with the new CLI config
        self.config = self._merge_configs()

        # Apply branch strategy
        self.apply_branch_strategy()
        
        # Resolve directory profiles
        self.resolve_directory_profiles()

    def _merge_configs(self) -> Dict[str, Any]:
        """
        Merge configurations from all sources.

        Returns:
            Merged configuration
        """
        # Start with default config
        config = self.default_config.copy()

        # Recursively update with each config source in order of precedence
        self._recursive_update(config, self.global_config)
        self._recursive_update(config, self.project_config)
        self._recursive_update(config, self.env_config)
        self._recursive_update(config, self.cli_config)

        return config

    def _recursive_update(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        Recursively update a target dictionary with values from a source dictionary.

        Args:
            target: Target dictionary to update
            source: Source dictionary with new values
        """
        for key, value in source.items():
            if (
                key in target
                and isinstance(target[key], dict)
                and isinstance(value, dict)
            ):
                # Recursively update nested dictionaries
                self._recursive_update(target[key], value)
            elif value is not None:  # Only update if value is not None
                target[key] = value

    def get_config(self) -> Dict[str, Any]:
        """
        Get the merged configuration.

        Returns:
            Merged configuration
        """
        return self.config

    def save_config(self, path: str) -> bool:
        """
        Save the current configuration to a file.

        Args:
            path: Path to save the configuration

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(path), exist_ok=True)

            with open(path, "w") as f:
                json.dump(self.config, f, indent=4)

            if self.verbose >= 1:
                self.logger.info(f"Saved configuration to {path}")

            return True
        except Exception as e:
            self.logger.error(f"Failed to save configuration to {path}: {str(e)}")
            return False

    def load_config_file(self, path: str) -> bool:
        """
        Load configuration from a file.

        Args:
            path: Path to the configuration file

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(path, "r") as f:
                config = json.load(f)

            # Update project_config with the loaded config
            self.project_config = config

            # Remerge configs with the new project config
            self.config = self._merge_configs()

            if self.verbose >= 1:
                self.logger.info(f"Loaded configuration from {path}")

            return True
        except Exception as e:
            self.logger.error(f"Failed to load configuration from {path}: {str(e)}")
            return False

    def validate_config(self) -> List[str]:
        """
        Validate the configuration.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Basic validation
        if not self.config.get("name"):
            errors.append("Project name is required")

        # More validation rules can be added here

        return errors

    def create_bootstrap_config(
        self,
        name: str,
        description: str = None,
        language: str = "python",
        user_info: Dict[str, str] = None,
    ) -> Dict[str, Any]:
        """
        Create a configuration specifically for bootstrapping a project.

        Args:
            name: Project name
            description: Project description
            language: Programming language
            user_info: Dictionary with user name and email

        Returns:
            Bootstrap configuration dictionary
        """
        # Start with default config
        config = self.default_config.copy()

        # Update with provided values
        config["name"] = name

        if description:
            config["description"] = description

        if language:
            config["language"] = language

        # Handle user information
        if user_info and isinstance(user_info, dict):
            if "name" in user_info or "email" in user_info:
                config["user"] = user_info.copy()

        return config

    def create_config_from_environment(self) -> Dict[str, Any]:
        """
        Create a configuration from environment variables.

        Environment variables:
            REPOKIT_NAME: Project name
            REPOKIT_DESCRIPTION: Project description
            REPOKIT_LANGUAGE: Programming language
            GIT_USER_NAME: Git user name
            GIT_USER_EMAIL: Git user email

        Returns:
            Configuration dictionary from environment
        """
        config = {}

        # Get basic project info
        name = os.environ.get("REPOKIT_NAME")
        if name:
            config["name"] = name

        description = os.environ.get("REPOKIT_DESCRIPTION")
        if description:
            config["description"] = description

        language = os.environ.get("REPOKIT_LANGUAGE")
        if language:
            config["language"] = language

        # Get user info
        user_name = os.environ.get("GIT_USER_NAME")
        user_email = os.environ.get("GIT_USER_EMAIL")

        if user_name or user_email:
            config["user"] = {}
            if user_name:
                config["user"]["name"] = user_name
            if user_email:
                config["user"]["email"] = user_email

        return config

    def get_git_user_info(self) -> Dict[str, str]:
        """
        Get Git user information from environment or global Git config.

        Returns:
            Dictionary with user name and email
        """
        user_info = {"name": "", "email": ""}

        # Try environment variables first
        user_name = os.environ.get("GIT_USER_NAME")
        user_email = os.environ.get("GIT_USER_EMAIL")

        if user_name:
            user_info["name"] = user_name

        if user_email:
            user_info["email"] = user_email

        # If not in environment, try Git global config
        if not user_name or not user_email:
            try:
                import subprocess

                if not user_name:
                    try:
                        result = subprocess.run(
                            ["git", "config", "--global", "user.name"],
                            capture_output=True,
                            text=True,
                            check=False,
                        )
                        if result.returncode == 0 and result.stdout.strip():
                            user_info["name"] = result.stdout.strip()
                    except Exception:
                        pass

                if not user_email:
                    try:
                        result = subprocess.run(
                            ["git", "config", "--global", "user.email"],
                            capture_output=True,
                            text=True,
                            check=False,
                        )
                        if result.returncode == 0 and result.stdout.strip():
                            user_info["email"] = result.stdout.strip()
                    except Exception:
                        pass
            except Exception as e:
                self.logger.warning(f"Could not get Git user info: {str(e)}")

        return user_info

    def apply_github_email_privacy(self, user_info: Dict[str, str]) -> Dict[str, str]:
        """
        Apply GitHub email privacy protection to user email.

        Args:
            user_info: Dictionary with user name and email

        Returns:
            Updated user info dictionary
        """
        updated_info = user_info.copy()

        # Apply GitHub privacy protection if enabled and pushing to GitHub
        if self.config.get("use_github_noreply", True) and self.config.get(
            "github", True
        ):
            email = updated_info.get("email", "")

            # If email isn't already a no-reply format
            if email and "@users.noreply.github.com" not in email:
                # Extract username from email or use first part
                username = email.split("@")[0]

                # If no username from email, try to use name
                if not username and "name" in updated_info:
                    # Convert name to a username-like format
                    username = updated_info["name"].lower().replace(" ", "-")

                # Create GitHub no-reply email if we have a username
                if username:
                    github_email = f"{username}@users.noreply.github.com"
                    self.logger.info(
                        f"Using GitHub no-reply email format: {github_email}"
                    )
                    updated_info["email"] = github_email

        return updated_info
    
    def resolve_directory_profiles(self) -> None:
        """
        Resolve directory profiles into actual directory lists.
        
        This method converts directory profile names, groups, and explicit directories
        into a final list of directories to create.
        """
        # Load custom directory profiles from config if available
        if "directory_profiles" in self.config:
            self.directory_manager.profiles.update(self.config["directory_profiles"])
        
        if "directory_groups" in self.config and isinstance(self.config["directory_groups"], dict):
            self.directory_manager.groups.update(self.config["directory_groups"])
        
        if "directory_types" in self.config:
            self.directory_manager.type_mapping.update(self.config["directory_types"])
        
        # Check if we're using a directory profile
        profile = self.config.get("directory_profile")
        groups = self.config.get("directory_groups", [])
        private_set = self.config.get("private_set", "standard")
        
        # If we have a profile or groups, use the directory manager
        if profile or groups:
            # Get all directories from the profile manager
            all_dirs = self.directory_manager.get_all_directories(
                profile=profile or "standard",
                groups=groups,
                private_set=private_set,
                package_name=self.config.get("name")
            )
            
            # Convert to flat lists
            directories = all_dirs["standard"]
            private_dirs = all_dirs["private"]
            
            # Only add explicit additional directories from CLI, not from default config
            if "directories" in self.cli_config:
                existing_dirs = set(directories)
                for d in self.cli_config["directories"]:
                    if d not in existing_dirs:
                        directories.append(d)
            
            # Update config with resolved directories
            self.config["directories"] = directories
            self.config["private_dirs"] = private_dirs
            
            if self.verbose >= 1:
                self.logger.info(f"Resolved directory profile '{profile}' to {len(directories)} directories")
        
        # Ensure private_dirs is always set
        if "private_dirs" not in self.config:
            self.config["private_dirs"] = ["private", "convos", "logs"]
