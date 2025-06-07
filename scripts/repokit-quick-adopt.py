#!/usr/bin/env python3
"""
RepoKit Quick Adopt - Interactive launcher for easy project adoption

This script provides a simple, interactive way to adopt projects with RepoKit
without needing to know all the command-line options.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def print_header():
    """Print welcome header."""
    print("=" * 60)
    print("🚀 RepoKit Quick Adopt - Interactive Project Setup")
    print("=" * 60)
    print()
    print("This tool helps you quickly adopt your existing project with RepoKit")
    print("professional structure and optionally deploy to GitHub.")
    print()


def get_user_input(prompt, default=None, choices=None):
    """Get user input with validation."""
    while True:
        if default:
            user_prompt = f"{prompt} (default: {default}): "
        else:
            user_prompt = f"{prompt}: "
            
        if choices:
            user_prompt = f"{prompt} ({'/'.join(choices)}): "
            
        response = input(user_prompt).strip()
        
        if not response and default:
            return default
            
        if choices and response and response.lower() not in [c.lower() for c in choices]:
            print(f"Please choose from: {', '.join(choices)}")
            continue
            
        if response or default:
            return response or default
        else:
            print("This field is required.")


def yes_no(prompt, default="n"):
    """Get yes/no input from user."""
    response = get_user_input(f"{prompt} (y/n)", default).lower()
    return response in ['y', 'yes', 'true', '1']


def get_project_info():
    """Gather basic project information."""
    print("📁 PROJECT INFORMATION")
    print("-" * 30)
    
    # Project path
    default_path = "."
    project_path = get_user_input("Project folder path", default_path)
    
    # Verify path exists
    if not os.path.exists(project_path):
        print(f"❌ Error: Path '{project_path}' does not exist")
        sys.exit(1)
        
    # Project name (for GitHub)
    default_name = os.path.basename(os.path.abspath(project_path))
    project_name = get_user_input("Project name (for GitHub)", default_name)
    
    # Description
    description = get_user_input("Project description (optional)", "")
    
    # Language
    language = get_user_input("Programming language", "generic", 
                             ["python", "javascript", "generic"])
    
    return {
        "path": project_path,
        "name": project_name,
        "description": description,
        "language": language
    }


def get_github_info():
    """Gather GitHub deployment information."""
    print("\n🌐 GITHUB DEPLOYMENT")
    print("-" * 30)
    
    deploy_github = yes_no("Deploy to GitHub?", "y")
    
    if not deploy_github:
        return {"deploy": False}
    
    # Repository visibility
    is_private = yes_no("Make repository private?", "y")
    
    # Organization (optional)
    organization = get_user_input("GitHub organization (optional)", "")
    
    return {
        "deploy": True,
        "private": is_private,
        "organization": organization
    }


def get_advanced_options():
    """Gather advanced configuration options."""
    print("\n⚙️ ADVANCED OPTIONS")
    print("-" * 30)
    
    show_advanced = yes_no("Configure advanced options?", "n")
    
    if not show_advanced:
        return {
            "branch_strategy": "simple",
            "dir_profile": "standard",
            "backup": True,
            "ai": "claude"
        }
    
    # Branch strategy
    branch_strategy = get_user_input(
        "Branch strategy", "simple",
        ["simple", "gitflow", "github-flow", "minimal"]
    )
    
    # Directory profile
    dir_profile = get_user_input(
        "Directory profile", "standard",
        ["minimal", "standard", "complete"]
    )
    
    # Backup
    backup = yes_no("Create backup before adoption?", "y")
    
    # AI integration
    ai = get_user_input("AI integration", "claude", ["claude", "none"])
    
    # Clean history
    clean_history = yes_no("Clean git history for open source?", "n")
    
    return {
        "branch_strategy": branch_strategy,
        "dir_profile": dir_profile,
        "backup": backup,
        "ai": ai,
        "clean_history": clean_history
    }


def build_command(project_info, github_info, advanced_options):
    """Build the repokit adopt command."""
    cmd = ["repokit", "adopt", project_info["path"]]
    
    # Basic options
    cmd.extend(["--language", project_info["language"]])
    
    if project_info["description"]:
        cmd.extend(["--description", project_info["description"]])
    
    # Advanced options
    cmd.extend(["--branch-strategy", advanced_options["branch_strategy"]])
    cmd.extend(["--dir-profile", advanced_options["dir_profile"]])
    cmd.extend(["--ai", advanced_options["ai"]])
    
    if advanced_options["backup"]:
        cmd.append("--backup")
        
    if advanced_options.get("clean_history"):
        cmd.extend(["--clean-history", "--cleaning-recipe", "pre-open-source"])
    
    # GitHub options
    if github_info["deploy"]:
        cmd.extend(["--publish-to", "github"])
        cmd.extend(["--repo-name", project_info["name"]])
        
        if github_info["private"]:
            cmd.append("--private-repo")
            
        if github_info["organization"]:
            cmd.extend(["--organization", github_info["organization"]])
    
    return cmd


def preview_command(cmd):
    """Show the command that will be executed."""
    print("\n📋 COMMAND PREVIEW")
    print("-" * 30)
    print("The following command will be executed:")
    print()
    print(" ".join(cmd))
    print()


def confirm_execution():
    """Confirm user wants to proceed."""
    print("⚠️  IMPORTANT:")
    print("- This will modify your project structure")
    print("- A backup will be created if you enabled it")
    print("- You can stop with Ctrl+C at any time")
    print()
    
    return yes_no("Proceed with adoption?", "y")


def execute_command(cmd):
    """Execute the repokit command."""
    print("\n🚀 EXECUTING ADOPTION")
    print("-" * 30)
    print("Running RepoKit adoption...")
    print()
    
    try:
        # Execute with real-time output
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Print output in real-time
        for line in process.stdout:
            print(line.rstrip())
            
        process.wait()
        
        if process.returncode == 0:
            print("\n✅ SUCCESS! Your project has been adopted with RepoKit.")
            return True
        else:
            print(f"\n❌ ERROR: Command failed with exit code {process.returncode}")
            return False
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Adoption cancelled by user.")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False


def show_success_info(project_info, github_info):
    """Show information about what was created."""
    print("\n🎉 ADOPTION COMPLETE!")
    print("-" * 30)
    
    project_path = os.path.abspath(project_info["path"])
    print(f"📁 Project location: {project_path}")
    print()
    
    print("📂 Directory structure:")
    print(f"  {project_path}/local/     - Your private development workspace")
    print(f"  {project_path}/dev/       - Development and testing")
    
    if github_info["deploy"]:
        print(f"  {project_path}/github/   - Clean version for GitHub")
        print()
        print("🌐 GitHub deployment:")
        repo_url = f"https://github.com/{github_info.get('organization', 'YOUR_USERNAME')}/{project_info['name']}"
        print(f"  Repository: {repo_url}")
        if github_info["private"]:
            print("  Visibility: Private")
        else:
            print("  Visibility: Public")
    else:
        print(f"  {project_path}/github/   - Ready for GitHub deployment")
    
    print()
    print("🔄 Next steps:")
    print("1. Explore your new directory structure")
    print("2. Review the generated documentation")
    print("3. Start developing in the 'local' directory")
    
    if github_info["deploy"]:
        print("4. Check your GitHub repository")
        print("5. Collaborate with others using the new structure")
    else:
        print("4. Deploy to GitHub when ready with: repokit adopt --publish-to github")


def main():
    """Main interactive adoption flow."""
    parser = argparse.ArgumentParser(
        description="Interactive RepoKit project adoption"
    )
    parser.add_argument(
        "--non-interactive", 
        action="store_true",
        help="Skip interactive prompts and use defaults"
    )
    args = parser.parse_args()
    
    if not args.non_interactive:
        print_header()
    
    try:
        # Gather information
        project_info = get_project_info()
        github_info = get_github_info()
        advanced_options = get_advanced_options()
        
        # Build and preview command
        cmd = build_command(project_info, github_info, advanced_options)
        preview_command(cmd)
        
        # Confirm and execute
        if confirm_execution():
            success = execute_command(cmd)
            
            if success:
                show_success_info(project_info, github_info)
            else:
                print("\n❌ Adoption failed. Check the error messages above.")
                sys.exit(1)
        else:
            print("\n⚠️ Adoption cancelled by user.")
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Adoption cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()