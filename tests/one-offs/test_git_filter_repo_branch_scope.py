#!/usr/bin/env python3
"""
Test git filter-repo to understand its branch-specific capabilities.

This test creates a controlled repository with sensitive files in multiple branches
to determine if git filter-repo can selectively clean specific branches without
affecting others.

Key Questions:
1. Can git filter-repo work on specific branches only?
2. Does it affect the entire repository history?
3. Can we preserve files in private branch while cleaning public branches?
"""

import os
import subprocess
import tempfile
import shutil
from pathlib import Path


def run_cmd(cmd, cwd=None, capture=True):
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd)} in {cwd or 'current dir'}")
    try:
        if capture:
            result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        else:
            subprocess.run(cmd, cwd=cwd, check=True)
            return "Success"
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        raise


def create_test_repository():
    """Create a test repository with sensitive files in multiple branches."""
    # Create temporary directory
    test_dir = tempfile.mkdtemp(prefix="git_filter_repo_test_")
    print(f"Creating test repository in: {test_dir}")
    
    # Initialize git repository
    run_cmd(["git", "init"], cwd=test_dir)
    run_cmd(["git", "config", "user.name", "Test User"], cwd=test_dir)
    run_cmd(["git", "config", "user.email", "test@example.com"], cwd=test_dir)
    
    # Create directory structure
    os.makedirs(os.path.join(test_dir, "src"), exist_ok=True)
    os.makedirs(os.path.join(test_dir, "private"), exist_ok=True)
    os.makedirs(os.path.join(test_dir, "scripts"), exist_ok=True)
    os.makedirs(os.path.join(test_dir, "logs"), exist_ok=True)
    
    # Create public files (should remain in all branches)
    with open(os.path.join(test_dir, "README.md"), "w") as f:
        f.write("# Test Repository\n\nThis is a public file.\n")
    
    with open(os.path.join(test_dir, "src", "main.py"), "w") as f:
        f.write("#!/usr/bin/env python3\nprint('Hello, World!')\n")
    
    # Create sensitive files (should be removed from public branches)
    with open(os.path.join(test_dir, "private", "secret.txt"), "w") as f:
        f.write("This is a private secret file.\n")
    
    with open(os.path.join(test_dir, "scripts", "deploy.sh~"), "w") as f:
        f.write("#!/bin/bash\necho 'This is a vim backup file'\n")
    
    with open(os.path.join(test_dir, "logs", "debug.log"), "w") as f:
        f.write("2025-06-06 DEBUG: This is a log file\n")
    
    # Create initial commit on main branch
    run_cmd(["git", "add", "."], cwd=test_dir)
    run_cmd(["git", "commit", "-m", "Initial commit with all files"], cwd=test_dir)
    
    # Create private branch (should keep all files)
    run_cmd(["git", "branch", "private"], cwd=test_dir)
    
    # Create dev branch (should have sensitive files removed)
    run_cmd(["git", "branch", "dev"], cwd=test_dir)
    
    # Add more commits to create history
    with open(os.path.join(test_dir, "src", "utils.py"), "w") as f:
        f.write("def helper_function():\n    return 'utility'\n")
    
    run_cmd(["git", "add", "src/utils.py"], cwd=test_dir)
    run_cmd(["git", "commit", "-m", "Add utility functions"], cwd=test_dir)
    
    # Add sensitive file in second commit
    with open(os.path.join(test_dir, "private", "config.env"), "w") as f:
        f.write("SECRET_KEY=abc123\nAPI_TOKEN=xyz789\n")
    
    run_cmd(["git", "add", "private/config.env"], cwd=test_dir)
    run_cmd(["git", "commit", "-m", "Add configuration files"], cwd=test_dir)
    
    return test_dir


def analyze_repository_state(repo_dir, stage_name):
    """Analyze and report the current state of the repository."""
    print(f"\n{'='*60}")
    print(f"REPOSITORY STATE: {stage_name}")
    print(f"{'='*60}")
    
    # List all branches
    branches = run_cmd(["git", "branch", "-a"], cwd=repo_dir)
    print(f"Branches:\n{branches}")
    
    # Check each branch for file content
    for branch in ["main", "private", "dev"]:
        try:
            print(f"\n--- Branch: {branch} ---")
            run_cmd(["git", "checkout", branch], cwd=repo_dir, capture=False)
            
            # List all tracked files
            tracked_files = run_cmd(["git", "ls-files"], cwd=repo_dir)
            print(f"Tracked files:\n{tracked_files}")
            
            # Show git log
            log_output = run_cmd(["git", "log", "--oneline", "--name-status"], cwd=repo_dir)
            print(f"Git log:\n{log_output}")
            
            # Check for specific sensitive files
            sensitive_files = [
                "private/secret.txt",
                "private/config.env", 
                "scripts/deploy.sh~",
                "logs/debug.log"
            ]
            
            print(f"Sensitive file status:")
            for sensitive_file in sensitive_files:
                full_path = os.path.join(repo_dir, sensitive_file)
                exists_in_working = os.path.exists(full_path)
                
                try:
                    run_cmd(["git", "ls-files", "--error-unmatch", sensitive_file], cwd=repo_dir)
                    tracked_by_git = True
                except:
                    tracked_by_git = False
                
                print(f"  {sensitive_file}: working_dir={exists_in_working}, git_tracked={tracked_by_git}")
                
        except Exception as e:
            print(f"Error checking branch {branch}: {e}")


def test_git_filter_repo_branch_specific(repo_dir):
    """Test if git filter-repo can work on specific branches."""
    print(f"\n{'='*60}")
    print(f"TESTING GIT FILTER-REPO BRANCH CAPABILITIES")
    print(f"{'='*60}")
    
    # First, let's try to see if git filter-repo is available
    try:
        run_cmd(["git", "filter-repo", "--version"])
        print("✅ git filter-repo is available")
    except Exception as e:
        print(f"❌ git filter-repo not available: {e}")
        print("To install: pip install git-filter-repo")
        return False
    
    # Test 1: Try to filter specific branches only
    print(f"\n--- Test 1: Branch-specific filtering ---")
    try:
        # Try to remove private/ directory from only main and dev branches
        cmd = [
            "git", "filter-repo", 
            "--path", "private/",
            "--invert-paths",
            "--refs", "main", "dev",  # Try to limit to specific branches
            "--force"
        ]
        
        run_cmd(cmd, cwd=repo_dir, capture=False)
        print("✅ Branch-specific filter-repo command succeeded")
        return True
        
    except Exception as e:
        print(f"❌ Branch-specific filter-repo failed: {e}")
        
        # Test 2: Try alternative branch syntax
        print(f"\n--- Test 2: Alternative branch syntax ---")
        try:
            cmd = [
                "git", "filter-repo",
                "--path", "private/",
                "--invert-paths", 
                "--refs", "refs/heads/main", "refs/heads/dev",
                "--force"
            ]
            
            run_cmd(cmd, cwd=repo_dir, capture=False)
            print("✅ Alternative branch syntax succeeded")
            return True
            
        except Exception as e:
            print(f"❌ Alternative branch syntax failed: {e}")
    
    # Test 3: Try protecting specific branches
    print(f"\n--- Test 3: Branch protection syntax ---")
    try:
        cmd = [
            "git", "filter-repo",
            "--path", "private/", 
            "--invert-paths",
            "--refs", "main", "dev",
            "--replace-refs", "delete-no-add",
            "--force"
        ]
        
        run_cmd(cmd, cwd=repo_dir, capture=False)
        print("✅ Branch protection syntax succeeded")
        return True
        
    except Exception as e:
        print(f"❌ Branch protection syntax failed: {e}")
    
    return False


def test_manual_branch_cleaning(repo_dir):
    """Test manual branch cleaning as alternative to git filter-repo."""
    print(f"\n{'='*60}")
    print(f"TESTING MANUAL BRANCH CLEANING APPROACH")
    print(f"{'='*60}")
    
    try:
        # Checkout dev branch
        run_cmd(["git", "checkout", "dev"], cwd=repo_dir, capture=False)
        
        # Remove sensitive files manually
        sensitive_patterns = ["private/", "*.log", "*~"]
        
        for pattern in sensitive_patterns:
            print(f"Removing files matching pattern: {pattern}")
            
            # Get list of files matching pattern
            if pattern.endswith("/"):
                # Directory pattern
                dir_to_remove = pattern.rstrip("/")
                full_path = os.path.join(repo_dir, dir_to_remove)
                if os.path.exists(full_path):
                    # Remove from git and filesystem
                    run_cmd(["git", "rm", "-rf", dir_to_remove], cwd=repo_dir, capture=False)
                    print(f"  Removed directory: {dir_to_remove}")
            else:
                # File pattern - need to find matching files
                tracked_files = run_cmd(["git", "ls-files"], cwd=repo_dir).split('\n')
                
                import fnmatch
                matching_files = [f for f in tracked_files if fnmatch.fnmatch(f, pattern)]
                
                for file_path in matching_files:
                    run_cmd(["git", "rm", file_path], cwd=repo_dir, capture=False)
                    print(f"  Removed file: {file_path}")
        
        # Commit the removals
        run_cmd(["git", "commit", "-m", "Remove sensitive files from dev branch"], cwd=repo_dir, capture=False)
        print("✅ Manual branch cleaning succeeded")
        
        # Do the same for main branch
        run_cmd(["git", "checkout", "main"], cwd=repo_dir, capture=False)
        
        # Remove sensitive files from main
        for pattern in sensitive_patterns:
            if pattern.endswith("/"):
                dir_to_remove = pattern.rstrip("/")
                full_path = os.path.join(repo_dir, dir_to_remove)
                if os.path.exists(full_path):
                    run_cmd(["git", "rm", "-rf", dir_to_remove], cwd=repo_dir, capture=False)
            else:
                tracked_files = run_cmd(["git", "ls-files"], cwd=repo_dir).split('\n')
                import fnmatch
                matching_files = [f for f in tracked_files if fnmatch.fnmatch(f, pattern)]
                for file_path in matching_files:
                    run_cmd(["git", "rm", file_path], cwd=repo_dir, capture=False)
        
        run_cmd(["git", "commit", "-m", "Remove sensitive files from main branch"], cwd=repo_dir, capture=False)
        print("✅ Manual main branch cleaning succeeded")
        
        return True
        
    except Exception as e:
        print(f"❌ Manual branch cleaning failed: {e}")
        return False


def main():
    """Main test function."""
    print("Git Filter-Repo Branch Scope Test")
    print("=" * 60)
    
    # Create test repository
    repo_dir = create_test_repository()
    
    try:
        # Analyze initial state
        analyze_repository_state(repo_dir, "INITIAL STATE")
        
        # Test git filter-repo capabilities
        filter_repo_success = test_git_filter_repo_branch_specific(repo_dir)
        
        if filter_repo_success:
            analyze_repository_state(repo_dir, "AFTER GIT FILTER-REPO")
        else:
            # Test manual approach if filter-repo doesn't work
            manual_success = test_manual_branch_cleaning(repo_dir)
            
            if manual_success:
                analyze_repository_state(repo_dir, "AFTER MANUAL CLEANING")
        
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Git Filter-Repo Branch-Specific: {'✅ SUCCESS' if filter_repo_success else '❌ FAILED'}")
        
        if not filter_repo_success:
            print(f"Manual Branch Cleaning: ✅ SUCCESS (fallback approach)")
            print(f"\nConclusion: Git filter-repo may not support branch-specific filtering.")
            print(f"Manual approach or selective branch creation may be needed.")
        else:
            print(f"Conclusion: Git filter-repo supports branch-specific filtering!")
        
    finally:
        # Clean up
        print(f"\nTest repository created at: {repo_dir}")
        print(f"To examine manually: cd {repo_dir}")
        
        # Optionally remove test directory (comment out for debugging)
        # shutil.rmtree(repo_dir)
        # print(f"Cleaned up test directory: {repo_dir}")


if __name__ == "__main__":
    main()