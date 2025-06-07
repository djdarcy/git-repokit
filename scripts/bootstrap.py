#!/usr/bin/env python3
"""
RepoKit Bootstrap Script

This script demonstrates how to use RepoKit to set up itself as a new repository
and publish it to a remote service like GitHub or GitLab.

Usage:
    python bootstrap.py [options]

Examples:
    python bootstrap.py --name git-repokit --publish-to github
    python bootstrap.py --name my-repokit --private --organization my-org
"""

import os
import sys
import json
import argparse
import subprocess
import shutil
import fnmatch
import logging
from pathlib import Path
from typing import List, Set, Dict, Any, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("repokit.bootstrap")

# Files and directories to always exclude when copying
ALWAYS_EXCLUDE = [
    # Git and version control
    ".git", ".gitignore", ".gitattributes",
    # Python bytecode and cache
    "__pycache__", "*.py[cod]", "*$py.class", "*.so",
    # Build artifacts
    "dist", "build", "*.egg-info",
    # Virtual environments
    "venv", ".env", ".venv", "env",
    # IDE files
    ".vscode", ".idea", "*.sublime-*",
    # Temp files
    "*.bak", "*.swp", "*.tmp", "*~", "*.*~",
    # Test directories
    "test*",
    # Credentials and secrets
    "credentials.json", "*token*", ".env",
    # Logs
    "logs", "*.log",
]

# Essential directories to copy
ESSENTIAL_DIRS = [
    "repokit", "docs", "scripts", "templates"
]

# Essential files to copy
ESSENTIAL_FILES = [
    "setup.py", "README.md", "pyproject.toml", "config-template.json"
]

def parse_args():
    """Parse command-line arguments for the bootstrap script."""
    parser = argparse.ArgumentParser(
        description="Bootstrap RepoKit into a new Git repository"
    )
    parser.add_argument(
        "--name", 
        default="git-repokit",
        help="Repository name (default: git-repokit)"
    )
    parser.add_argument(
        "--description",
        default="Tool for creating standardized Git repositories with complex branching strategies",
        help="Repository description"
    )
    parser.add_argument(
        "--publish-to", 
        choices=["github", "gitlab"], 
        default="github",
        help="Remote service to publish to (default: github)"
    )
    parser.add_argument(
        "--private", 
        action="store_true",
        help="Create a private repository"
    )
    parser.add_argument(
        "--token", 
        help="Authentication token for the remote service"
    )
    parser.add_argument(
        "--token-command", 
        help="Command to retrieve token (e.g., 'pass show github/token')"
    )
    parser.add_argument(
        "--organization", 
        help="GitHub organization or GitLab group name"
    )
    parser.add_argument(
        "--config-path",
        default="bootstrap_config.json",
        help="Path to save the generated configuration file (default: bootstrap_config.json)"
    )
    parser.add_argument(
        "--git-user-name",
        help="Git user name (default: from GIT_USER_NAME environment variable)"
    )
    parser.add_argument(
        "--git-user-email",
        help="Git user email (default: from GIT_USER_EMAIL environment variable)"
    )
    parser.add_argument(
        "--credentials-file",
        help="Path to credentials file (default: ~/.repokit/credentials.json)"
    )
    parser.add_argument(
        "--source-dir",
        default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        help="Source directory containing the RepoKit code to copy (default: parent of script dir)"
    )
    parser.add_argument(
        "--verbose", "-v", 
        action="count", 
        default=0,
        help="Increase verbosity (use -v, -vv, or -vvv for more detail)"
    )
    parser.add_argument(
        "--no-publish",
        action="store_true",
        help="Skip publishing to remote service"
    )
    parser.add_argument(
        "--set-default-branch",
        default="main",
        help="Set the default branch (default: main)"
    )
    parser.add_argument(
        "--only-copy-essential",
        action="store_true",
        help="Only copy essential files and directories (recommended)"
    )
    
    return parser.parse_args()

def set_verbosity(verbose: int):
    """Set verbosity level for logging."""
    if verbose >= 3:
        logger.setLevel(logging.DEBUG)
    elif verbose >= 2:
        logger.setLevel(logging.INFO)
    elif verbose >= 1:
        logger.setLevel(logging.WARNING)
    else:
        logger.setLevel(logging.ERROR)

def ensure_repokit_installed():
    """Ensure RepoKit is installed, installing it if necessary."""
    try:
        import repokit
        logger.info("RepoKit is already installed.")
        return True
    except ImportError:
        logger.warning("RepoKit is not installed. Attempting to install it...")
        try:
            current_dir = os.getcwd()
            
            # Check if we're in a RepoKit development directory
            potential_setup = os.path.join(current_dir, "setup.py")
            if os.path.exists(potential_setup):
                logger.info(f"Found setup.py in current directory, installing in development mode...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."])
                logger.info("RepoKit installed successfully in development mode.")
                return True
            
            # Try looking up one directory
            parent_dir = os.path.dirname(current_dir)
            potential_setup = os.path.join(parent_dir, "setup.py")
            if os.path.exists(potential_setup):
                logger.info(f"Found setup.py in parent directory, installing in development mode...")
                os.chdir(parent_dir)
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."])
                os.chdir(current_dir)  # Change back to original directory
                logger.info("RepoKit installed successfully in development mode.")
                return True
            
            logger.error("No setup.py found. Please run this script from a RepoKit development directory.")
            return False
        except subprocess.CalledProcessError:
            logger.error("Failed to install RepoKit.")
            return False

def create_config(args):
    """Create a configuration dictionary based on command-line arguments."""
    git_user_name = args.git_user_name or os.environ.get("GIT_USER_NAME", "")
    git_user_email = args.git_user_email or os.environ.get("GIT_USER_EMAIL", "")
    
    config = {
        "name": args.name,
        "description": args.description,
        "language": "python",
        "branches": ["main", "dev", "staging", "test", "live"],
        "worktrees": ["main", "dev"],
        "directories": [
            "convos", "docs", "logs", "private", "revisions", "scripts", "tests"
        ],
        "private_dirs": ["private", "convos", "logs"],
        "private_branch": "private",
        "github": True,
        "user": {
            "name": git_user_name,
            "email": git_user_email
        }
    }
    
    return config

def save_config(config, config_path):
    """Save configuration to a JSON file."""
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)
    logger.info(f"Configuration saved to {config_path}")

def build_repokit_command(args, config_path):
    """Build the RepoKit command line arguments."""
    # First, just create the repository locally without publishing
    repokit_args = [
        "create",
        args.name,
        "--config", config_path
    ]
    
    # Add --no-push to prevent automatic pushing
    repokit_args.append("--no-push")
    
    # Add verbosity flags
    for _ in range(args.verbose):
        repokit_args.append("-v")
    
    return repokit_args

def build_publish_command(args):
    """Build the RepoKit publish command."""
    # Important: Use the repository root, not 'local'
    repo_path = os.path.abspath(args.name)
    
    # The repository has a structure like:
    # repo_name/
    #   ├── local/    # Main repository (private branch)
    #   ├── github/   # GitHub worktree (main branch)
    #   └── dev/      # dev branch worktree
    
    # This is the root cause of the repo being named "local" on GitHub
    repo_path = os.path.abspath(os.path.join(args.name, "local"))
    
    publish_args = [
        "publish",
        repo_path,
        "--publish-to", args.publish_to,
        # Add the repository name explicitly to ensure correct naming
        "--name", args.name
    ]
    
    if args.private:
        publish_args.append("--private-repo")
    
    if args.organization:
        publish_args.extend(["--organization", args.organization])
        
    if args.credentials_file:
        publish_args.extend(["--credentials-file", args.credentials_file])
    
    if args.token:
        publish_args.extend(["--token", args.token])
    
    # Add verbosity flags
    for _ in range(args.verbose):
        publish_args.append("-v")
    
    return publish_args

def run_repokit(repokit_args):
    """Run RepoKit with the given arguments."""
    try:
        from repokit.cli import main
        
        logger.info(f"Running: repokit {' '.join(repokit_args)}")
        
        # Use sys.argv to pass arguments to RepoKit
        old_argv = sys.argv
        sys.argv = ["repokit"] + repokit_args
        
        try:
            exit_code = main()
            # Restore original sys.argv
            sys.argv = old_argv
            
            if exit_code == 0:
                logger.info("Command completed successfully!")
                return True
            else:
                logger.error(f"Command failed with exit code: {exit_code}")
                return False
        except Exception as e:
            logger.error(f"An error occurred while running RepoKit: {str(e)}")
            # Restore original sys.argv
            sys.argv = old_argv
            return False
    except ImportError:
        logger.error("Failed to import repokit.cli. Please check your installation.")
        return False

def load_credentials(args):
    """
    Try to load credentials from default locations or environment variables.
    
    If args.token is provided, it takes precedence.
    """
    if args.token:
        # Token provided via command line
        os.environ[f"{args.publish_to.upper()}_TOKEN"] = args.token
        logger.info(f"Using token provided via command line")
        return True
    
    # Check if token is already in environment
    if os.environ.get(f"{args.publish_to.upper()}_TOKEN"):
        logger.info(f"Using {args.publish_to} token from environment variable")
        return True

    # Check if credentials file exists
    credentials_file = args.credentials_file
    if not credentials_file:
        # Default location
        home_dir = Path.home()
        credentials_file = os.path.join(home_dir, ".repokit", "credentials.json")
    
    if os.path.exists(credentials_file):
        try:
            with open(credentials_file, 'r') as f:
                credentials = json.load(f)
                
            # Try to get token from credentials file
            service = args.publish_to.lower()
            if service in credentials and "token" in credentials[service]:
                token = credentials[service]["token"]
                os.environ[f"{service.upper()}_TOKEN"] = token
                logger.info(f"Loaded {service} token from credentials file: {credentials_file}")
                
                # Also get organization if present
                if not args.organization:
                    org_key = "organization" if service == "github" else "group"
                    if org_key in credentials[service]:
                        args.organization = credentials[service][org_key]
                        logger.info(f"Using {service} organization from credentials file: {args.organization}")
                
                return True
        except Exception as e:
            logger.error(f"Error loading credentials: {str(e)}")
    
    logger.warning(f"No {args.publish_to} token found. Remote publishing will likely fail.")
    print(f"\nNo {args.publish_to.upper()}_TOKEN found. You can provide one with:")
    print(f"  1. --token parameter")
    print(f"  2. --credentials-file parameter")
    print(f"  3. Setting {args.publish_to.upper()}_TOKEN environment variable")
    return False

def is_excluded(path: str, rel_path: str, exclude_patterns: List[str]) -> bool:
    """
    Check if a path should be excluded based on patterns.
    
    Args:
        path: Full path to check
        rel_path: Relative path from source directory
        exclude_patterns: List of patterns to exclude

    Returns:
        True if the path should be excluded, False otherwise
    """
    # Check if path matches any exclude pattern
    for pattern in exclude_patterns:
        # Handle directory patterns (ending with /)
        if pattern.endswith('/'):
            dir_pattern = pattern[:-1]
            path_parts = rel_path.split(os.sep)
            if any(fnmatch.fnmatch(part, dir_pattern) for part in path_parts):
                return True
        # Check if any part of the path matches the pattern
        elif any(fnmatch.fnmatch(part, pattern) for part in rel_path.split(os.sep)):
            return True
        # Check if the filename matches the pattern
        elif os.path.isfile(path) and fnmatch.fnmatch(os.path.basename(path), pattern):
            return True
    
    return False

def is_essential(path: str, rel_path: str) -> bool:
    """
    Check if a path is considered essential.
    
    Args:
        path: Full path to check
        rel_path: Relative path from source directory

    Returns:
        True if the path is essential, False otherwise
    """
    # Root directory is always essential
    if rel_path == ".":
        return True
    
    # Check if it's a directory that's essential
    path_parts = rel_path.split(os.sep)
    if path_parts[0] in ESSENTIAL_DIRS:
        return True
    
    # Check if it's a file that's essential
    if os.path.isfile(path) and os.path.basename(path) in ESSENTIAL_FILES:
        return True
    
    return False

def copy_repokit_files(args, repo_path):
    """
    Copy RepoKit files from source directory to repository.
    
    Args:
        args: Command-line arguments
        repo_path: Path to the target repository
    """
    source_dir = args.source_dir
    logger.info(f"Copying RepoKit files from {source_dir} to repository...")
    
    # Local repository path
    local_repo = os.path.join(repo_path, "local")
    
    # Collect files to copy
    files_to_copy = []
    dirs_to_create = set()
    
    # Exclude patterns
    exclude_patterns = ALWAYS_EXCLUDE + [
        # Exclude the target directory itself
        args.name, 
        # Exclude temporary files
        "temp", "tmp"
    ]
    
    logger.debug(f"Exclude patterns: {exclude_patterns}")
    
    # Walk through the source directory
    for dirpath, dirnames, filenames in os.walk(source_dir):
        # Get relative path
        rel_path = os.path.relpath(dirpath, source_dir)
        
        # Skip excluded directories
        if is_excluded(dirpath, rel_path, exclude_patterns):
            logger.debug(f"Skipping excluded directory: {rel_path}")
            # Remove these directories from dirnames to prevent walk from descending into them
            for exclude in exclude_patterns:
                dirnames[:] = [d for d in dirnames if not fnmatch.fnmatch(d, exclude)]
            continue
        
        # If only copying essential files, check if this directory is essential
        if args.only_copy_essential and not is_essential(dirpath, rel_path):
            logger.debug(f"Skipping non-essential directory: {rel_path}")
            continue
        
        # Add directory to create
        if rel_path != ".":
            target_dir = os.path.join(local_repo, rel_path)
            dirs_to_create.add(target_dir)
        
        # Process files in this directory
        for filename in filenames:
            src_file = os.path.join(dirpath, filename)
            file_rel_path = os.path.join(rel_path, filename) if rel_path != "." else filename
            
            # Skip excluded files
            if is_excluded(src_file, file_rel_path, exclude_patterns):
                logger.debug(f"Skipping excluded file: {file_rel_path}")
                continue
            
            # If only copying essential files, check if this file is essential
            if args.only_copy_essential and not is_essential(src_file, file_rel_path):
                logger.debug(f"Skipping non-essential file: {file_rel_path}")
                continue
            
            # Determine target file path
            if rel_path == ".":
                dst_file = os.path.join(local_repo, filename)
            else:
                dst_file = os.path.join(local_repo, rel_path, filename)
            
            # Add to files to copy
            files_to_copy.append((src_file, dst_file))
    
    # Create directories
    for directory in sorted(dirs_to_create):
        os.makedirs(directory, exist_ok=True)
        logger.debug(f"Created directory: {os.path.relpath(directory, local_repo)}")
    
    # Copy files
    for src_file, dst_file in files_to_copy:
        try:
            shutil.copy2(src_file, dst_file)
            logger.debug(f"Copied: {os.path.relpath(dst_file, local_repo)}")
        except Exception as e:
            logger.error(f"Error copying {src_file} to {dst_file}: {str(e)}")
    
    logger.info(f"Copied {len(files_to_copy)} files to repository")
    
    # Commit the changes
    try:
        # Check if there are changes to commit
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=local_repo,
            check=True,
            capture_output=True,
            text=True
        )
        
        if result.stdout.strip():
            # Changes exist, commit them
            logger.info("Committing changes to repository...")
            subprocess.run(["git", "add", "."], cwd=local_repo, check=True)
            subprocess.run(
                ["git", "commit", "-m", "Add RepoKit source files"],
                cwd=local_repo,
                check=True
            )
            logger.info("Changes committed to repository")
            
            # Push to branches, but NOT using the worktree approach as it doesn't work
            # Instead, we'll update branches after pushing to remote
            return True
        else:
            logger.info("No changes to commit")
            return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error committing changes: {str(e)}")
        return False

def push_repository(args, repo_path):
    """
    Push repository to remote service.
    
    Args:
        args: Command-line arguments
        repo_path: Path to the repository
    """
    if args.no_publish:
        logger.info("Skipping remote publishing as requested")
        return True
    
    # Ensure we have credentials
    if not load_credentials(args):
        logger.warning("No credentials found for remote publishing")
    
    # Run the publish command
    publish_args = build_publish_command(args)
    success = run_repokit(publish_args)
    
    if not success:
        logger.error("Failed to publish repository")
        return False
    
    logger.info("Repository published successfully!")
    return True

def main():
    """Main entry point for the bootstrap script."""
    args = parse_args()
    
    # Set verbosity level
    set_verbosity(args.verbose)
    
    print(f"Bootstrapping RepoKit as '{args.name}'...")
    
    # Ensure RepoKit is installed
    if not ensure_repokit_installed():
        print("Failed to ensure RepoKit is installed")
        sys.exit(1)
    
    # Create and save configuration
    config = create_config(args)
    save_config(config, args.config_path)
    
    # Build and run RepoKit command to create local repository
    repokit_args = build_repokit_command(args, args.config_path)
    if not run_repokit(repokit_args):
        print("Failed to create repository structure")
        sys.exit(1)
    
    # Copy RepoKit files to repository
    repo_path = os.path.abspath(args.name)
    if not copy_repokit_files(args, repo_path):
        print("Failed to copy RepoKit files to repository")
        sys.exit(1)
    
    # Now publish to remote if requested
    if not args.no_publish:
        if not push_repository(args, repo_path):
            print("Failed to publish repository to remote service")
            sys.exit(1)
    
    print(f"\nSuccessfully bootstrapped RepoKit as '{args.name}'!")
    print(f"You can find your new repository in the '{args.name}' directory")
    print("\nNext steps:")
    print(f"  1. Explore the repository: cd {args.name}")
    print(f"  2. Check the GitHub repository (if published)")
    print(f"  3. Make changes in the {args.name}/local directory (on private branch)")
    print(f"  4. Merge changes to dev/main branches as needed")

if __name__ == "__main__":
    main()
