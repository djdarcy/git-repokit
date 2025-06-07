#!/usr/bin/env python3
"""
Directory Profiles for RepoKit.

Implements a flexible directory structure system with profiles, groups, and types.
This allows for customized directory setups based on project needs.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Set, Any, Optional

from .defaults import (
    DEFAULT_PRIVATE_DIRS as CENTRALIZED_PRIVATE_DIRS,
    DEFAULT_DIRECTORY_PROFILES,
    DEFAULT_DIRECTORY_GROUPS,
    DEFAULT_DIRECTORY_TYPE_MAPPING,
    DEFAULT_PRIVATE_DIR_SETS
)

# Set up logging
logger = logging.getLogger("repokit.directories")

# Use centralized configurations from defaults.py
# These are now imported directly, eliminating duplication


class DirectoryProfileManager:
    """Manages directory profiles, groups, and types for project setup."""

    def __init__(self, config_file: Optional[str] = None, verbose: int = 0):
        """
        Initialize the directory profile manager.

        Args:
            config_file: Optional path to configuration file
            verbose: Verbosity level
        """
        self.verbose = verbose

        # Initialize defaults using centralized configurations
        self.profiles = DEFAULT_DIRECTORY_PROFILES.copy()
        self.groups = DEFAULT_DIRECTORY_GROUPS.copy()
        self.private_dirs = DEFAULT_PRIVATE_DIR_SETS.copy()
        self.type_mapping = DEFAULT_DIRECTORY_TYPE_MAPPING.copy()

        # Load custom configuration if provided
        if config_file:
            self.load_config(config_file)

    def load_config(self, config_file: str) -> bool:
        """
        Load directory configuration from a file.

        Args:
            config_file: Path to configuration file

        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            with open(config_file, "r") as f:
                config = json.load(f)

            # Update with custom configuration
            if "directory_profiles" in config:
                self.profiles.update(config["directory_profiles"])

            if "directory_groups" in config:
                self.groups.update(config["directory_groups"])

            if "private_dirs" in config:
                self.private_dirs.update(config["private_dirs"])

            if "directory_types" in config:
                self.type_mapping.update(config["directory_types"])

            logger.info(f"Loaded directory configuration from {config_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to load directory configuration: {str(e)}")
            return False

    def save_config(self, config_file: str) -> bool:
        """
        Save directory configuration to a file.

        Args:
            config_file: Path to configuration file

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            config = {
                "directory_profiles": self.profiles,
                "directory_groups": self.groups,
                "private_dirs": self.private_dirs,
                "directory_types": self.type_mapping,
            }

            # Create parent directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(config_file)), exist_ok=True)

            with open(config_file, "w") as f:
                json.dump(config, f, indent=4)

            logger.info(f"Saved directory configuration to {config_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save directory configuration: {str(e)}")
            return False

    def get_directories_for_profile(self, profile: str) -> List[str]:
        """
        Get directory types for a specific profile.

        Args:
            profile: Profile name (minimal, standard, complete, or custom)

        Returns:
            List of directory types in the profile
        """
        return self.profiles.get(profile, self.profiles["standard"]).copy()

    def get_directories_for_groups(self, groups: List[str]) -> List[str]:
        """
        Get directory types for specific groups.

        Args:
            groups: List of group names

        Returns:
            List of directory types in the groups
        """
        result = set()
        for group in groups:
            if group in self.groups:
                result.update(self.groups[group])
        return sorted(list(result))

    def get_private_directories(self, private_set: str = "standard") -> List[str]:
        """
        Get list of private directories.

        Args:
            private_set: Private directory set name

        Returns:
            List of private directory types
        """
        return self.private_dirs.get(private_set, self.private_dirs["standard"]).copy()

    def get_actual_directory_name(
        self, dir_type: str, package_name: Optional[str] = None
    ) -> str:
        """
        Get actual directory name for a directory type.

        Args:
            dir_type: Directory type (src, tests, etc.)
            package_name: Optional package name to use for src directory

        Returns:
            Actual directory name to create
        """
        # Special handling for source directory
        if dir_type == "src" and package_name:
            return package_name

        return self.type_mapping.get(dir_type, dir_type)

    def get_all_directories(
        self,
        profile: str,
        groups: Optional[List[str]] = None,
        private_set: str = "standard",
        package_name: Optional[str] = None,
    ) -> Dict[str, List[str]]:
        """
        Get all directories to create, mapped to actual names.

        Args:
            profile: Profile name
            groups: Optional additional groups
            private_set: Private directory set name
            package_name: Optional package name for src directory

        Returns:
            Dictionary with categories and actual directory names
        """
        # Start with profile directories
        dir_types = set(self.get_directories_for_profile(profile))

        # Add group directories if specified
        if groups:
            dir_types.update(self.get_directories_for_groups(groups))

        # Get private directories
        private_types = set(self.get_private_directories(private_set))

        # Convert types to actual directory names
        standard_dirs = []
        private_dirs = []

        for dir_type in dir_types:
            actual_name = self.get_actual_directory_name(dir_type, package_name)
            if dir_type in private_types:
                private_dirs.append(actual_name)
            else:
                standard_dirs.append(actual_name)
        
        # Add all private directories from the private set (even if not in profile)
        for private_type in private_types:
            actual_name = self.get_actual_directory_name(private_type, package_name)
            if actual_name not in private_dirs:
                private_dirs.append(actual_name)

        return {"standard": sorted(standard_dirs), "private": sorted(private_dirs)}

    def create_directories(
        self,
        base_path: str,
        profile: str,
        groups: Optional[List[str]] = None,
        private_set: str = "standard",
        package_name: Optional[str] = None,
    ) -> Dict[str, List[str]]:
        """
        Create all directories for a project.

        Args:
            base_path: Base path to create directories in
            profile: Profile name
            groups: Optional additional groups
            private_set: Private directory set name
            package_name: Optional package name for src directory

        Returns:
            Dictionary with created directories by category
        """
        directories = self.get_all_directories(
            profile, groups, private_set, package_name
        )

        created_dirs = {"standard": [], "private": []}

        # Create standard directories
        for dirname in directories["standard"]:
            dir_path = os.path.join(base_path, dirname)
            os.makedirs(dir_path, exist_ok=True)
            created_dirs["standard"].append(dirname)

            # Create .gitkeep file
            gitkeep_path = os.path.join(dir_path, ".gitkeep")
            if not os.path.exists(gitkeep_path):
                with open(gitkeep_path, "w") as f:
                    f.write("# This file ensures the directory is tracked by Git\n")

        # Create private directories
        for dirname in directories["private"]:
            dir_path = os.path.join(base_path, dirname)
            os.makedirs(dir_path, exist_ok=True)
            created_dirs["private"].append(dirname)

            # Create .gitkeep file (will be ignored in .gitignore)
            gitkeep_path = os.path.join(dir_path, ".gitkeep")
            if not os.path.exists(gitkeep_path):
                with open(gitkeep_path, "w") as f:
                    f.write("# This file ensures the directory exists\n")

        logger.info(f"Created {len(created_dirs['standard'])} standard directories")
        logger.info(f"Created {len(created_dirs['private'])} private directories")

        return created_dirs

    def validate_directories(self, base_path: str) -> Dict[str, List[str]]:
        """
        Validate existing directories against all known directory types.

        Args:
            base_path: Base path to check

        Returns:
            Dictionary with existing, missing, and unknown directories
        """
        # Get all known directory types
        all_known_types = set()
        for profile in self.profiles.values():
            all_known_types.update(profile)

        # Get all directory names that could exist
        all_possible_names = set()
        for dir_type in all_known_types:
            # Add with default name
            all_possible_names.add(self.get_actual_directory_name(dir_type))
            # Also add common package names for src
            if dir_type == "src":
                all_possible_names.update(["src", "app", "lib", "pkg"])

        # Check existing directories
        existing_dirs = []
        for item in os.listdir(base_path):
            item_path = os.path.join(base_path, item)
            if os.path.isdir(item_path) and not item.startswith("."):
                existing_dirs.append(item)

        # Categorize directories
        known_dirs = [d for d in existing_dirs if d in all_possible_names]
        unknown_dirs = [d for d in existing_dirs if d not in all_possible_names]
        missing_dirs = [d for d in all_possible_names if d not in existing_dirs]

        return {
            "existing": sorted(known_dirs),
            "unknown": sorted(unknown_dirs),
            "missing": sorted(missing_dirs),
        }

    def suggest_profile(self, base_path: str) -> str:
        """
        Suggest a profile based on existing directories.

        Args:
            base_path: Base path to check

        Returns:
            Suggested profile name
        """
        validation = self.validate_directories(base_path)
        existing_dirs = set(validation["existing"])

        # Check each profile to see how many directories match
        profile_matches = {}
        for profile_name, profile_dirs in self.profiles.items():
            # Convert profile types to actual directory names
            profile_names = set(self.get_actual_directory_name(d) for d in profile_dirs)
            # Count matches
            matches = len(existing_dirs.intersection(profile_names))
            profile_matches[profile_name] = matches

        # Find the profile with the most matches
        best_profile = max(profile_matches.items(), key=lambda x: x[1])

        # If minimal matches, default to standard
        if best_profile[1] <= 1:
            return "standard"

        return best_profile[0]

    def manage_gitkeep_files(self, base_path: str, recursive: bool = True) -> Dict[str, List[str]]:
        """
        Manage .gitkeep files based on directory contents.
        
        Adds .gitkeep to empty directories and removes .gitkeep from non-empty directories.
        
        Args:
            base_path: Base path to manage
            recursive: Whether to process subdirectories recursively
            
        Returns:
            Dictionary with added and removed .gitkeep files
        """
        result = {"added": [], "removed": []}
        
        def process_directory(dir_path: str, relative_path: str = ""):
            """Process a single directory for .gitkeep management."""
            if not os.path.isdir(dir_path):
                return
                
            gitkeep_path = os.path.join(dir_path, ".gitkeep")
            gitkeep_exists = os.path.exists(gitkeep_path)
            
            # Get all items in directory (excluding .gitkeep itself)
            try:
                items = [item for item in os.listdir(dir_path) if item != ".gitkeep"]
            except PermissionError:
                logger.warning(f"Permission denied accessing directory: {dir_path}")
                return
            
            # Filter out hidden files and directories that should be ignored
            non_hidden_items = [item for item in items if not item.startswith(".")]
            
            # Check if directory is effectively empty (only has hidden files or .gitkeep)
            is_empty = len(non_hidden_items) == 0
            
            # Manage .gitkeep based on directory state
            if is_empty and not gitkeep_exists:
                # Add .gitkeep to empty directory
                try:
                    with open(gitkeep_path, "w") as f:
                        f.write("# This file ensures the directory is tracked by Git\n")
                    result["added"].append(os.path.join(relative_path, ".gitkeep") if relative_path else ".gitkeep")
                    logger.debug(f"Added .gitkeep to empty directory: {dir_path}")
                except PermissionError:
                    logger.warning(f"Permission denied creating .gitkeep in: {dir_path}")
            elif not is_empty and gitkeep_exists:
                # Remove .gitkeep from non-empty directory
                try:
                    os.remove(gitkeep_path)
                    result["removed"].append(os.path.join(relative_path, ".gitkeep") if relative_path else ".gitkeep")
                    logger.debug(f"Removed .gitkeep from non-empty directory: {dir_path}")
                except PermissionError:
                    logger.warning(f"Permission denied removing .gitkeep from: {dir_path}")
                    
            # Process subdirectories recursively if requested
            if recursive:
                for item in items:
                    item_path = os.path.join(dir_path, item)
                    if os.path.isdir(item_path) and not item.startswith("."):
                        item_relative = os.path.join(relative_path, item) if relative_path else item
                        process_directory(item_path, item_relative)
        
        # Start processing from base path
        process_directory(base_path)
        
        if result["added"] or result["removed"]:
            logger.info(f"Managed .gitkeep files: {len(result['added'])} added, {len(result['removed'])} removed")
        else:
            logger.debug("No .gitkeep file changes needed")
            
        return result
