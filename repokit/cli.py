#!/usr/bin/env python3
"""
RepoKit: Repository Template Generator

Command-line interface for creating standardized Git repositories.
"""

import os
import sys
import json
import argparse
import logging
from typing import Dict, Any, Optional

from .config import ConfigManager
from .repo_manager import RepoManager
from .template_engine import TemplateEngine
from .directory_analyzer import analyze_directory, plan_migration, migrate_directory, analyze_project, adopt_project

def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Create a standardized Git repository with branches, worktrees, and templates."
    )
    
    # Required for 'create' command
    parser.add_argument(
        "command",
        choices=["create", "list-templates", "init-config", "publish", "bootstrap", "store-credentials", "analyze", "migrate", "adopt"],
        help="Command to execute (create a repository, list templates, initialize configuration, publish to remote, generate bootstrap script, or store credentials)"
    )
    
    parser.add_argument(
        "name",
        nargs="?",
        help="Name of the repository to create (required for 'create' command), or path to existing repository (for 'publish' command)"
    )
    
    parser.add_argument(
        "--config", "-c",
        help="Path to configuration file (JSON)"
    )
    
    parser.add_argument(
        "--language", "-l",
        choices=["python", "javascript", "generic"],
        help="Programming language for language-specific templates"
    )
    
    parser.add_argument(
        "--description", "-d",
        help="Short description of the repository"
    )
    
    parser.add_argument(
        "--branches", "-b",
        help="Comma-separated list of branches to create (default: main,dev,staging,test,live)"
    )
    
    parser.add_argument(
        "--worktrees", "-w",
        help="Comma-separated list of branches to create worktrees for (default: main,dev)"
    )
    
    parser.add_argument(
        "--directories", "-dir",
        help="Comma-separated list of directories to create"
    )
    
    parser.add_argument(
        "--private-dirs", "-pd",
        help="Comma-separated list of directories to mark as private"
    )
    
    parser.add_argument(
        "--private-branch",
        help="Name of the private branch (default: private)"
    )

    # Default branch override
    parser.add_argument(
        "--default-branch",
        help="Name of the default branch (default: main)"
    )
    
    # Branch strategy options
    parser.add_argument(
        "--branch-strategy",
        choices=["standard", "simple", "gitflow", "github-flow", "minimal"],
        help="Predefined branch strategy to use (default: standard)"
    )
    
    parser.add_argument(
        "--branch-config",
        help="Path to branch configuration file (JSON)"
    )
    
    # Branch directory mapping
    parser.add_argument(
        "--branch-dir-main",
        help="Directory name for main branch (default: github)"
    )
    
    parser.add_argument(
        "--branch-dir-dev",
        help="Directory name for dev branch (default: dev)"
    )
    
    # Migration options
    parser.add_argument(
        "--migration-strategy",
        choices=["safe", "replace", "merge"],
        default="safe",
        help="Strategy for migration (safe: keep existing files, replace: use templates, merge: try to combine)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Analyze migration actions without executing them"
    )

    # Git user configuration
    parser.add_argument(
        "--user-name",
        help="Git user name for commits"
    )
    
    parser.add_argument(
        "--user-email",
        help="Git user email for commits"
    )
    
    # Remote integration options
    parser.add_argument(
        "--publish-to",
        choices=["github", "gitlab"],
        help="Publish repository to a remote service (GitHub or GitLab)"
    )
    
    parser.add_argument(
        "--remote-name",
        default="origin",
        help="Name for the remote (default: origin)"
    )
    
    parser.add_argument(
        "--private-repo",
        action="store_true",
        help="Create a private repository on remote service"
    )
    
    parser.add_argument(
        "--organization",
        help="GitHub organization or GitLab group name"
    )
    
    parser.add_argument(
        "--no-push",
        action="store_true",
        help="Don't push branches after creating remote repository"
    )
    
    # Authentication options
    parser.add_argument(
        "--token",
        help="Authentication token for remote service"
    )
    
    parser.add_argument(
        "--token-command",
        help="Command to retrieve token (e.g., 'pass show github/token')"
    )
    
    parser.add_argument(
        "--credentials-file",
        help="Path to credentials file"
    )
    
    # Bootstrap command options
    parser.add_argument(
        "--output", "-o",
        help="Output file for bootstrap script (default: bootstrap_repokit.py)"
    )
    
    # Template customization
    parser.add_argument(
        "--templates-dir",
        help="Path to custom templates directory"
    )
    
    # AI integration
    parser.add_argument(
        "--ai",
        choices=["none", "claude"],
        default="claude",
        help="AI tool integration to include (default: claude)"
    )
    
    # Enhanced verbosity control
    verbosity_group = parser.add_mutually_exclusive_group()
    verbosity_group.add_argument(
        "--verbose", "-v",
        action="count",
        default=0,
        help="Increase verbosity level (use -v, -vv, or -vvv for more detail)"
    )
    verbosity_group.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress all output except errors"
    )
    
    # Save configuration
    parser.add_argument(
        "--save-config",
        help="Save the configuration to the specified file"
    )
    
    return parser.parse_args()

def setup_logging(verbosity: int, quiet: bool = False) -> None:
    """
    Set up logging based on verbosity level.
    
    Args:
        verbosity: Verbosity level (0-3)
        quiet: Whether to suppress all output except errors
    """
    if quiet:
        log_level = logging.ERROR
    else:
        # Map verbosity levels to logging levels
        log_levels = {
            0: logging.WARNING,  # Default
            1: logging.INFO,     # -v
            2: logging.DEBUG,    # -vv
            3: logging.DEBUG     # -vvv (more detailed debug)
        }
        # Cap at maximum level
        capped_verbosity = min(verbosity, 3)
        log_level = log_levels[capped_verbosity]
    
    # Configure basic logging
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # For highest verbosity, adjust formatter to include more details
    if verbosity >= 3:
        for handler in logging.root.handlers:
            handler.setFormatter(logging.Formatter(
                "%(asctime)s - %(levelname)s - %(name)s - %(filename)s:%(lineno)d - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            ))
    
    # Get logger for repokit
    logger = logging.getLogger("repokit")
    
    # Log verbosity level for debugging
    if verbosity >= 1:
        logger.info(f"Verbosity level: {verbosity}")

def args_to_config(args: argparse.Namespace) -> Dict[str, Any]:
    """
    Convert command-line arguments to configuration dictionary.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Configuration dictionary
    """
    # Base configuration from CLI arguments
    cli_config = {
        "name": args.name,
        "language": args.language,
        "description": args.description,
        "private_branch": args.private_branch,
        "user": {
            "name": args.user_name,
            "email": args.user_email
        } if args.user_name or args.user_email else None
    }
    
    # Handle list-type arguments
    if args.branches:
        cli_config["branches"] = [branch.strip() for branch in args.branches.split(',')]
    
    if args.worktrees:
        cli_config["worktrees"] = [worktree.strip() for worktree in args.worktrees.split(',')]
    
    if args.directories:
        cli_config["directories"] = [directory.strip() for directory in args.directories.split(',')]
    
    if args.private_dirs:
        cli_config["private_dirs"] = [dir.strip() for dir in args.private_dirs.split(',')]
    
    # Handle branch strategy
    if args.branch_strategy:
        cli_config["branch_strategy"] = args.branch_strategy
    
    # Handle AI integration
    if args.ai and args.ai != "none":
        cli_config["ai_integration"] = args.ai
    
    # Handle branch directory mappings
    branch_directories = {}
    
    if args.branch_dir_main:
        branch_directories["main"] = args.branch_dir_main
    
    if args.branch_dir_dev:
        branch_directories["dev"] = args.branch_dir_dev
    
    if branch_directories:
        cli_config["branch_config"] = {"branch_directories": branch_directories}

    # default branch from CLI
    if args.default_branch:
        cli_config["default_branch"] = args.default_branch
    
    # Remove None values from config
    return {k: v for k, v in cli_config.items() if v is not None}

def main() -> int:
    """
    Main entry point.
    
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    args = parse_arguments()
    
    # Set up logging based on verbosity
    setup_logging(args.verbose, args.quiet)
    logger = logging.getLogger("repokit")
    
    # Initialize configuration manager
    config_manager = ConfigManager(verbose=args.verbose)
    
    # Load config file if provided
    if args.config and os.path.exists(args.config):
        config_manager.load_config_file(args.config)
    
    # Load branch configuration file if provided
    if args.branch_config and os.path.exists(args.branch_config):
        config_manager.load_branch_config_file(args.branch_config)
    
    # Add CLI arguments to configuration
    cli_config = args_to_config(args)
    config_manager.set_cli_config(cli_config)
    
    # Get the final, merged configuration
    config = config_manager.get_config()
    
    # Add remote integration configuration
    if args.publish_to:
        service_config = config.get(args.publish_to, {})
        if args.organization:
            if args.publish_to == "github":
                service_config["organization"] = args.organization
            else:
                service_config["group"] = args.organization
        config[args.publish_to] = service_config
    
    # Validate configuration
    errors = config_manager.validate_config()
    if errors:
        for error in errors:
            logger.error(f"Configuration error: {error}")
        return 1
    
    # Save configuration if requested
    if args.save_config:
        config_manager.save_config(args.save_config)
    
    # Handle commands
    if args.command == "list-templates":
        template_engine = TemplateEngine(
            templates_dir=args.templates_dir,
            verbose=args.verbose
        )
        templates = template_engine.list_templates()
        print("Available templates:")
        for template in sorted(templates):
            print(f"  {template}")
        return 0
    
    elif args.command == "init-config":
        # Create a default configuration file in the current directory
        config_path = os.path.join(os.getcwd(), ".repokit.json")
        if os.path.exists(config_path):
            logger.error(f"Configuration file already exists at {config_path}")
            return 1
        
        config_manager.save_config(config_path)
        logger.info(f"Created default configuration at {config_path}")
        print(f"Created default configuration at {config_path}")
        print("Edit this file to customize your repository settings.")
        return 0
    
    elif args.command == "store-credentials":
        from .remote_integration import RemoteIntegration
        from .auth_integration import AuthenticationHandler
        
        if not args.publish_to:
            logger.error("Please specify a service with --publish-to (github or gitlab)")
            return 1
        
        if not args.token and not args.token_command:
            logger.error("Please provide either --token or --token-command")
            return 1
        
        auth_handler = AuthenticationHandler(verbose=args.verbose)
        
        # If token_command is provided, use it to get the token
        if args.token_command:
            token = auth_handler.get_token(args.publish_to, args.token_command)
            if not token:
                logger.error(f"Failed to retrieve token using command: {args.token_command}")
                return 1
        else:
            token = args.token
        
        # Store the credentials
        success = auth_handler.store_credentials(
            args.publish_to,
            token,
            args.organization,
            args.credentials_file
        )
        
        if success:
            logger.info(f"Successfully stored credentials for {args.publish_to}")
            return 0
        else:
            logger.error(f"Failed to store credentials for {args.publish_to}")
            return 1
    
    elif args.command == "bootstrap":
        bootstrap_script = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            "scripts", 
            "bootstrap.py"
        )
        
        if not os.path.exists(bootstrap_script):
            logger.error(f"Bootstrap script not found at {bootstrap_script}")
            return 1
        
        # Build arguments for bootstrap script
        bootstrap_args = [sys.executable, bootstrap_script]
        
        # Pass through relevant arguments
        if args.name:
            bootstrap_args.extend(["--name", args.name])
        
        if args.publish_to:
            bootstrap_args.extend(["--service", args.publish_to])
        
        if args.private_repo:
            bootstrap_args.append("--private")
        
        if args.organization:
            bootstrap_args.extend(["--organization", args.organization])
        
        if args.output:
            bootstrap_args.extend(["--config-path", args.output])
        
        if args.user_name:
            bootstrap_args.extend(["--git-user-name", args.user_name])
        
        if args.user_email:
            bootstrap_args.extend(["--git-user-email", args.user_email])
        
        # Add verbosity flags
        for _ in range(args.verbose):
            bootstrap_args.append("-v")
        
        # Execute the bootstrap script
        logger.info(f"Running bootstrap script: {' '.join(bootstrap_args)}")
        
        try:
            exit_code = subprocess.call(bootstrap_args)
            return exit_code
        except Exception as e:
            logger.error(f"Error running bootstrap script: {str(e)}")
            return 1
    
    elif args.command == "analyze":
        if not args.name:
            logger.error("Directory path is required for 'analyze' command")
            return 1
        
        try:
            # Analyze the directory
            dir_path = os.path.abspath(args.name)
            if not os.path.exists(dir_path):
                logger.error(f"Directory not found: {dir_path}")
                return 1
            
            # Use comprehensive project analysis
            summary = analyze_project(dir_path, verbose=args.verbose)
            
            # Display the enhanced analysis results
            print(f"\n=== PROJECT ANALYSIS: {dir_path} ===")
            print(f"  Project type: {summary['project_type']}")
            print(f"  Detected language: {summary['detected_language']}")
            print(f"  Migration complexity: {summary['migration_complexity']}")
            print(f"  Recommended strategy: {summary['recommended_strategy']}")
            print(f"  Recommended branch strategy: {summary['recommended_branch_strategy']}")
            
            # Git state information
            git_state = summary.get('git_state', {})
            if git_state.get('is_repo'):
                print(f"\n  Git repository:")
                print(f"    Current branch: {git_state.get('current_branch', 'Unknown')}")
                print(f"    Branches: {', '.join(git_state.get('branches', []))}")
                print(f"    Has uncommitted changes: {'Yes' if git_state.get('has_uncommitted_changes') else 'No'}")
                print(f"    Remotes: {', '.join(git_state.get('remotes', {}).keys()) or 'None'}")
                print(f"    Branch strategy: {summary['branch_strategy']}")
            else:
                print(f"  Git repository: No")
            
            # Directory structure
            print(f"\n  Directory structure:")
            print(f"    Existing standard directories: {', '.join(summary['existing_dirs']) or 'None'}")
            print(f"    Missing standard directories: {', '.join(summary['missing_dirs']) or 'None'}")
            print(f"    Special directories: {', '.join(summary['special_dirs']) or 'None'}")
            print(f"    Has template conflicts: {'Yes' if summary['has_template_conflicts'] else 'No'}")
            
            # File information
            print(f"\n  File counts:")
            for category, count in summary['file_counts'].items():
                if count > 0:
                    print(f"    {category}: {count}")
            print(f"    Total: {summary['total_files']}")
            
            # Migration recommendations
            print(f"\n  Migration steps:")
            for i, step in enumerate(summary['migration_steps'], 1):
                print(f"    {i}. {step}")
            
            # Command suggestions
            print(f"\n=== NEXT STEPS ===")
            if summary['project_type'] == 'repokit':
                print("  Project is already using RepoKit structure.")
            elif summary['project_type'] == 'empty':
                print("  Create new RepoKit project:")
                print(f"    repokit create {os.path.basename(dir_path)} --language {summary['detected_language']}")
            else:
                print("  Migrate to RepoKit structure:")
                print(f"    repokit migrate {args.name} --migration-strategy {summary['recommended_strategy']}")
                print("  Or adopt in-place:")
                print(f"    repokit adopt {args.name} --strategy {summary['recommended_strategy']}")
                if args.publish_to:
                    print(f"  With publishing:")
                    print(f"    repokit adopt {args.name} --publish-to {args.publish_to}")
            
            return 0
        except Exception as e:
            logger.error(f"Error analyzing directory: {str(e)}")
            if args.verbose >= 2:
                import traceback
                traceback.print_exc()
            return 1

    elif args.command == "migrate":
        if not args.name:
            logger.error("Directory path is required for 'migrate' command")
            return 1
        
        try:
            # Analyze and migrate the directory
            dir_path = os.path.abspath(args.name)
            if not os.path.exists(dir_path):
                logger.error(f"Directory not found: {dir_path}")
                return 1
            
            # First show the analysis
            summary = analyze_directory(dir_path, verbose=args.verbose)
            
            print(f"\nAnalysis of {dir_path}:")
            print(f"  Existing standard directories: {', '.join(summary['existing_dirs']) or 'None'}")
            print(f"  Missing standard directories: {', '.join(summary['missing_dirs']) or 'None'}")
            print(f"  Special directories: {', '.join(summary['special_dirs']) or 'None'}")
            print(f"  Has Git repository: {'Yes' if summary['has_git_repository'] else 'No'}")
            print(f"  Has template conflicts: {'Yes' if summary['has_template_conflicts'] else 'No'}")
            
            # Get migration plan
            plan = plan_migration(
                dir_path, 
                strategy=args.migration_strategy, 
                verbose=args.verbose
            )
            
            # Show migration plan
            print("\nMigration plan:")
            print(f"  Strategy: {plan['strategy']}")
            print(f"  Directories to create: {', '.join(plan['create_dirs']) or 'None'}")
            
            for dirname, info in plan['special_dirs'].items():
                print(f"  Special directory '{dirname}': {info['action']}")
            
            for template_dir, info in plan['template_conflicts'].items():
                print(f"  Template conflicts in '{template_dir}' ({info['conflicts']} files): {info['action']}")
            
            # Confirm migration
            if not args.dry_run and not args.quiet:
                confirm = input("\nProceed with migration? [y/N]: ")
                if confirm.lower() != "y":
                    print("Migration cancelled.")
                    return 0
            
            # Execute migration
            success = migrate_directory(
                dir_path, 
                strategy=args.migration_strategy, 
                dry_run=args.dry_run, 
                verbose=args.verbose
            )
            
            if success:
                msg = "Migration analysis completed (dry run)" if args.dry_run else "Migration completed successfully"
                print(f"\n{msg}")
                print("\nNext steps:")
                
                if summary['has_git_repository']:
                    print("  - Your directory already has a Git repository.")
                    print("  - You may want to update templates and configuration.")
                else:
                    print("  - Initialize a Git repository (if not already done):")
                    print("    git init")
                    print("  - Set up your initial branches:")
                    print("    git branch dev")
                    print("    git branch staging")
                    print("    git branch test")
                    print("    git branch live")
                
                if args.publish_to:
                    print(f"  - Publish to {args.publish_to}:")
                    print(f"    repokit publish {dir_path} --publish-to {args.publish_to}")
                
                return 0
            else:
                logger.error("Migration failed.")
                return 1
        except Exception as e:
            logger.error(f"Error migrating directory: {str(e)}")
            if args.verbose >= 2:
                import traceback
                traceback.print_exc()
            return 1
    
    elif args.command == "adopt":
        # Use current directory if no name provided
        dir_path = os.path.abspath(args.name) if args.name else os.getcwd()
        
        if not os.path.exists(dir_path):
            logger.error(f"Directory not found: {dir_path}")
            return 1
        
        try:
            # First analyze the project
            summary = analyze_project(dir_path, verbose=args.verbose)
            
            print(f"\n=== ADOPTING PROJECT: {dir_path} ===")
            print(f"  Project type: {summary['project_type']}")
            print(f"  Detected language: {summary['detected_language']}")
            print(f"  Migration complexity: {summary['migration_complexity']}")
            
            # Check if already RepoKit
            if summary['project_type'] == 'repokit':
                print("  Project is already using RepoKit structure.")
                return 0
            
            # Warn about uncommitted changes
            git_state = summary.get('git_state', {})
            if git_state.get('has_uncommitted_changes'):
                print("  WARNING: Uncommitted changes detected!")
                if not args.dry_run and not args.quiet:
                    confirm = input("  Continue with adoption? Changes should be committed first. [y/N]: ")
                    if confirm.lower() != "y":
                        print("  Adoption cancelled.")
                        return 0
            
            # Determine strategies
            strategy = args.migration_strategy if hasattr(args, 'migration_strategy') else summary['recommended_strategy']
            branch_strategy = getattr(args, 'branch_strategy', None)
            if not branch_strategy:
                branch_strategy = summary['recommended_branch_strategy']
            
            print(f"  Using migration strategy: {strategy}")
            print(f"  Using branch strategy: {branch_strategy}")
            
            if args.dry_run:
                print(f"  DRY RUN - No changes will be made")
            
            # Execute adoption
            success = adopt_project(
                directory=dir_path,
                strategy=strategy,
                branch_strategy=branch_strategy,
                publish_to=args.publish_to,
                dry_run=args.dry_run,
                verbose=args.verbose
            )
            
            if success:
                msg = "Adoption analysis completed (dry run)" if args.dry_run else "Project adopted successfully!"
                print(f"\n{msg}")
                
                if not args.dry_run:
                    print("\nNext steps:")
                    print(f"  - Your project now uses RepoKit structure")
                    print(f"  - Check the generated templates and configuration")
                    print(f"  - Commit any new files to your repository")
                    
                    if args.publish_to:
                        print(f"  - Repository will be published to {args.publish_to}")
                    elif not git_state.get('remotes'):
                        print(f"  - Consider publishing to a remote service:")
                        print(f"    repokit publish {dir_path} --publish-to github")
                
                return 0
            else:
                logger.error("Project adoption failed.")
                return 1
                
        except Exception as e:
            logger.error(f"Error adopting project: {str(e)}")
            if args.verbose >= 2:
                import traceback
                traceback.print_exc()
            return 1
    
    elif args.command == "create":
        if not args.name:
            logger.error("Repository name is required for 'create' command")
            return 1
        
        try:
            # Initialize RepoManager with the merged configuration
            repo_manager = RepoManager(
                config,
                templates_dir=args.templates_dir,
                verbose=args.verbose
            )
            
            # Set up repository
            success = repo_manager.setup_repository()
            if not success:
                return 1
            
            # Publish to remote if requested
            if args.publish_to:
                from .remote_integration import RemoteIntegration
                
                remote_integration = RemoteIntegration(
                    repo_manager, 
                    credentials_file=args.credentials_file,
                    verbose=args.verbose
                )
                
                publish_success = remote_integration.setup_remote_repository(
                    service=args.publish_to,
                    remote_name=args.remote_name,
                    private=args.private_repo,
                    push_branches=not args.no_push,
                    organization=args.organization,
                    token_command=args.token_command
                )
                
                if not publish_success:
                    logger.error(f"Failed to publish repository to {args.publish_to}")
                    return 1
                
                logger.info(f"Successfully published repository to {args.publish_to}")
            
            return 0
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            if args.verbose >= 2:
                import traceback
                traceback.print_exc()
            return 1
    
    elif args.command == "publish":
        if not args.name:
            logger.error("Repository path is required for 'publish' command")
            return 1
        
        if not args.publish_to:
            logger.error("--publish-to is required for 'publish' command")
            return 1
        
        try:
            # Use the provided path as the repository root
            repo_path = os.path.abspath(args.name)
            if not os.path.exists(repo_path):
                logger.error(f"Repository not found at {repo_path}")
                return 1
            
            # Update configuration with the correct path
            config["name"] = os.path.basename(repo_path)
            
            # Initialize RepoManager with the repository path
            repo_manager = RepoManager(
                config,
                templates_dir=args.templates_dir,
                verbose=args.verbose
            )
            
            # Override the project_root and repo_root
            repo_manager.project_root = os.path.dirname(repo_path)
            repo_manager.repo_root = repo_path
            
            # Publish to remote
            from .remote_integration import RemoteIntegration
            
            remote_integration = RemoteIntegration(
                repo_manager, 
                credentials_file=args.credentials_file,
                verbose=args.verbose
            )
            
            publish_success = remote_integration.setup_remote_repository(
                service=args.publish_to,
                remote_name=args.remote_name,
                private=args.private_repo,
                push_branches=not args.no_push,
                organization=args.organization,
                token_command=args.token_command
            )
            
            if not publish_success:
                logger.error(f"Failed to publish repository to {args.publish_to}")
                return 1
            
            logger.info(f"Successfully published repository to {args.publish_to}")
            return 0
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            if args.verbose >= 2:
                import traceback
                traceback.print_exc()
            return 1
    
    # Unknown command (should not happen due to choices in argparse)
    logger.error(f"Unknown command: {args.command}")
    return 1

if __name__ == "__main__":
    sys.exit(main())
