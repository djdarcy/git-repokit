#!/usr/bin/env python3
"""
Debug Helper for RepoKit Bootstrap

This script helps diagnose issues with the RepoKit bootstrap process by:
1. Running the bootstrap script with debugging enabled
2. Checking the repository structure
3. Validating GitHub authentication
4. Monitoring file copying

Usage:
    python debug_bootstrap.py [options]
"""

import os
import sys
import json
import subprocess
import argparse
import time
from pathlib import Path

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Debug the RepoKit bootstrap process"
    )
    parser.add_argument(
        "--name",
        default="git-repokit-debug",
        help="Repository name (default: git-repokit-debug)"
    )
    parser.add_argument(
        "--bootstrap-script",
        default="../scripts/bootstrap.py",
        help="Path to bootstrap script (default: ../scripts/bootstrap.py)"
    )
    parser.add_argument(
        "--credentials-file",
        default="credentials.json",
        help="Path to credentials file (default: credentials.json)"
    )
    parser.add_argument(
        "--only-essential",
        action="store_true",
        help="Only copy essential files (recommended)"
    )
    parser.add_argument(
        "--no-publish",
        action="store_true",
        help="Skip GitHub publishing step"
    )
    return parser.parse_args()

def check_credentials(credentials_file):
    """Check if credentials file exists and contains valid GitHub token."""
    print(f"\n--- Checking credentials file: {credentials_file} ---")
    
    if not os.path.exists(credentials_file):
        print(f"ERROR: Credentials file not found: {credentials_file}")
        return False
    
    try:
        with open(credentials_file, 'r') as f:
            creds = json.load(f)
        
        if 'github' not in creds:
            print("ERROR: No 'github' section in credentials file")
            return False
        
        if 'token' not in creds['github']:
            print("ERROR: No 'token' found in github section")
            return False
        
        token = creds['github']['token']
        print(f"Found GitHub token: {token[:4]}...{token[-4:]} ({len(token)} chars)")
        
        # Set environment variable for bootstrap script
        os.environ['GITHUB_TOKEN'] = token
        print("Set GITHUB_TOKEN environment variable")
        
        return True
    except json.JSONDecodeError:
        print(f"ERROR: Invalid JSON in credentials file")
        return False
    except Exception as e:
        print(f"ERROR: Failed to read credentials: {str(e)}")
        return False

def run_bootstrap(args):
    """Run the bootstrap script with maximum verbosity."""
    print(f"\n--- Running bootstrap script with debug options ---")
    
    # Build command
    cmd = [
        sys.executable,
        args.bootstrap_script,
        "--name", args.name,
        "--publish-to", "github",
        "--credentials-file", args.credentials_file,
        "--verbose", "--verbose", "--verbose"  # Maximum verbosity
    ]
    
    if args.only_essential:
        cmd.append("--only-copy-essential")
    
    if args.no_publish:
        cmd.append("--no-publish")
    
    # Print command
    print(f"Running command: {' '.join(cmd)}")
    
    # Execute
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    end_time = time.time()
    
    # Print results
    print(f"\n--- Bootstrap completed in {end_time - start_time:.2f} seconds ---")
    print(f"Exit code: {result.returncode}")
    
    # Save output to files for analysis
    with open("bootstrap_stdout.log", "w") as f:
        f.write(result.stdout)
    with open("bootstrap_stderr.log", "w") as f:
        f.write(result.stderr)
    
    print(f"Output saved to bootstrap_stdout.log and bootstrap_stderr.log")
    
    # Display output
    print("\n--- Bootstrap Output ---")
    print(result.stdout)
    
    if result.stderr:
        print("\n--- Bootstrap Errors ---")
        print(result.stderr)
    
    return result.returncode == 0

def check_repository_structure(args):
    """Check the structure of the created repository."""
    print(f"\n--- Checking repository structure: {args.name} ---")
    
    repo_path = os.path.abspath(args.name)
    if not os.path.exists(repo_path):
        print(f"ERROR: Repository directory not found: {repo_path}")
        return False
    
    # Check for expected subdirectories
    expected_dirs = ["local", "github", "dev"]
    for dirname in expected_dirs:
        dir_path = os.path.join(repo_path, dirname)
        if not os.path.exists(dir_path):
            print(f"ERROR: Expected directory not found: {dirname}")
            return False
        print(f"Found directory: {dirname}")
    
    # Check local repository
    local_path = os.path.join(repo_path, "local")
    
    # Check for Git repository
    git_dir = os.path.join(local_path, ".git")
    if not os.path.exists(git_dir):
        print(f"ERROR: Git repository not found in {local_path}")
        return False
    print(f"Found Git repository in local/")
    
    # Check for essential files
    essential_files = ["README.md", "setup.py"]
    for filename in essential_files:
        file_path = os.path.join(local_path, filename)
        if not os.path.exists(file_path):
            print(f"WARNING: Essential file not found: {filename}")
        else:
            print(f"Found essential file: {filename}")
    
    # Check for repokit module
    repokit_dir = os.path.join(local_path, "repokit")
    if not os.path.exists(repokit_dir):
        print(f"ERROR: repokit module directory not found")
        return False
    print(f"Found repokit module directory")
    
    # Check Git branches
    result = subprocess.run(
        ["git", "branch"], 
        cwd=local_path,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"ERROR: Failed to check Git branches")
        return False
    
    branches = result.stdout.strip().split('\n')
    branches = [b.strip('* \t') for b in branches if b.strip()]
    
    expected_branches = ["main", "dev", "test", "staging", "live", "private"]
    missing_branches = [b for b in expected_branches if b not in branches]
    
    if missing_branches:
        print(f"WARNING: Missing branches: {', '.join(missing_branches)}")
    else:
        print(f"Found all expected branches: {', '.join(branches)}")
    
    # Check remotes
    result = subprocess.run(
        ["git", "remote", "-v"], 
        cwd=local_path,
        capture_output=True,
        text=True
    )
    
    if "origin" in result.stdout:
        print(f"Found remote: origin")
        # Extract URL
        for line in result.stdout.split('\n'):
            if line.startswith('origin') and '(fetch)' in line:
                url = line.split()[1]
                print(f"Remote URL: {url}")
                break
    else:
        print(f"WARNING: No remote named 'origin' found")
    
    return True

def check_for_credentials_in_repo(args):
    """Check if credentials file was accidentally copied to the repository."""
    print(f"\n--- Checking for sensitive files in repository ---")
    
    repo_path = os.path.join(os.path.abspath(args.name), "local")
    
    # Check for credentials file
    sensitive_files = [
        "credentials.json",
        ".env",
        "*token*",
        "*secret*",
        "*password*"
    ]
    
    found_sensitive = False
    
    for pattern in sensitive_files:
        result = subprocess.run(
            ["find", ".", "-name", pattern], 
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        
        if result.stdout.strip():
            files = result.stdout.strip().split('\n')
            print(f"WARNING: Found potentially sensitive files matching '{pattern}':")
            for file in files:
                if file.strip():
                    found_sensitive = True
                    print(f"  - {file}")
    
    if not found_sensitive:
        print("No sensitive files found in repository. Good!")
    
    return not found_sensitive

def suggest_fixes(success):
    """Suggest fixes based on the debug results."""
    if success:
        print("\n--- Suggested Next Steps ---")
        print("1. Verify the GitHub repository was created correctly")
        print("2. Check that all necessary files were copied")
        print("3. Ensure correct branch is set as default on GitHub")
        print("4. Consider implementing these bootstrap improvements in the core RepoKit code")
    else:
        print("\n--- Suggested Fixes ---")
        print("1. Check credentials file format and validity")
        print("2. Ensure GitHub token has sufficient permissions")
        print("3. Verify RepoKit installation")
        print("4. Try running with --only-essential flag to reduce file copying issues")
        print("5. Try running with --no-publish flag to focus on local repository creation first")
        print("6. Check logs for specific error messages")

def main():
    """Main entry point for the debug script."""
    args = parse_args()
    
    print("=== RepoKit Bootstrap Debugging ===")
    print(f"Repository name: {args.name}")
    print(f"Bootstrap script: {args.bootstrap_script}")
    print(f"Credentials file: {args.credentials_file}")
    print(f"Only essential files: {args.only_essential}")
    print(f"Skip publishing: {args.no_publish}")
    
    # Check credentials
    creds_ok = check_credentials(args.credentials_file)
    if not creds_ok and not args.no_publish:
        print("WARNING: Credentials issues detected but continuing...")
    
    # Run bootstrap
    bootstrap_ok = run_bootstrap(args)
    
    # Check repository structure
    structure_ok = False
    if bootstrap_ok:
        structure_ok = check_repository_structure(args)
        
        # Check for accidentally included credentials
        creds_check = check_for_credentials_in_repo(args)
    
    # Suggest fixes
    suggest_fixes(bootstrap_ok and structure_ok)
    
    # Return status
    return 0 if bootstrap_ok and structure_ok else 1

if __name__ == "__main__":
    sys.exit(main())
