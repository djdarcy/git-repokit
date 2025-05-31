#!/usr/bin/env python3
"""
Streamlined RepoKit Bootstrap Script for Testing

A simpler version that uses RepoKit's core functionality to bootstrap
itself into a new repository and publish it to GitHub.
"""

import os
import sys
import argparse
import logging
import shutil
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("repokit.bootstrap")

# Add parent directory to path so we can import RepoKit modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Bootstrap RepoKit into a new Git repository using core RepoKit functionality"
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
        "--credentials-file",
        help="Path to credentials file (default: ~/.repokit/credentials.json)"
    )
    parser.add_argument(
        "--private",
        action="store_true",
        help="Create a private repository"
    )
    parser.add_argument(
        "--organization",
        help="GitHub organization or GitLab group name"
    )
    parser.add_argument(
        "--source-dir",
        default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        help="Source directory containing the RepoKit code (default: parent of script dir)"
    )
    parser.add_argument(
        "--verbose", "-v", 
        action="count", 
        default=0,
        help="Increase verbosity (use -v, -vv, or -vvv for more detail)"
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Clean up existing repository if it exists"
    )
    
    return parser.parse_args()

def set_verbosity(verbose):
    """Set logging verbosity level."""
    if verbose >= 3:
        logger.setLevel(logging.DEBUG)
    elif verbose >= 2:
        logger.setLevel(logging.INFO)
    elif verbose >= 1:
        logger.setLevel(logging.WARNING)
    else:
        logger.setLevel(logging.ERROR)

def cleanup_existing_repo(repo_path):
    """Remove an existing repository if it exists."""
    if os.path.exists(repo_path):
        logger.info(f"Cleaning up existing repository: {repo_path}")
        try:
            shutil.rmtree(repo_path)
            logger.info(f"Removed existing repository: {repo_path}")
        except Exception as e:
            logger.error(f"Failed to remove existing repository: {e}")
            return False
    return True

def main():
    """Main function."""
    args = parse_args()
    set_verbosity(args.verbose)
    
    # Check for existing repository and clean up if requested
    repo_path = os.path.abspath(args.name)
    if os.path.exists(repo_path):
        if args.cleanup:
            if not cleanup_existing_repo(repo_path):
                sys.exit(1)
        else:
            logger.error(f"Repository already exists: {repo_path}")
            logger.error("Use --cleanup to remove it or choose a different name")
            sys.exit(1)
    
    print(f"Bootstrapping RepoKit as '{args.name}'...")
    
    try:
        # Import RepoKit modules
        from repokit.config import ConfigManager
        from repokit.repo_manager import RepoManager
        logger.info("Successfully imported RepoKit modules")
        
        # Create configuration
        config_manager = ConfigManager(verbose=args.verbose)
        
        # Get user info from Git
        user_info = config_manager.get_git_user_info()
        
        # Apply GitHub email privacy if needed
        if args.publish_to == "github":
            user_info = config_manager.apply_github_email_privacy(user_info)
        
        # Create bootstrap config
        bootstrap_config = config_manager.create_bootstrap_config(
            name=args.name,
            description=args.description,
            language="python",
            user_info=user_info
        )
        
        # Set CLI config
        config_manager.set_cli_config(bootstrap_config)
        
        # Initialize repository manager
        repo_manager = RepoManager(
            config_manager.get_config(),
            verbose=args.verbose
        )
        
        # Bootstrap repository
        success = repo_manager.bootstrap_repository(args.source_dir)
        if not success:
            logger.error("Failed to bootstrap repository")
            sys.exit(1)
        
        # Publish to remote if requested
        if args.publish_to:
            success = repo_manager.publish_repository(
                service=args.publish_to,
                private=args.private,
                organization=args.organization,
                credentials_file=args.credentials_file
            )
            
            if not success:
                logger.error(f"Failed to publish to {args.publish_to}")
                sys.exit(1)
        
        print(f"\nSuccessfully bootstrapped RepoKit as '{args.name}'!")
        print(f"You can find your new repository at {os.path.abspath(args.name)}")
        
    except ImportError as e:
        logger.error(f"Failed to import RepoKit modules: {e}")
        logger.error("Please make sure you're running this script from the RepoKit repository")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error bootstrapping RepoKit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
