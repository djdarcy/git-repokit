#!/usr/bin/env python3
"""
Test script for history protection functionality.

This script tests the new safe-merge-dev command and history protection features.
"""

import os
import sys
import tempfile
import shutil
import subprocess

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from repokit.history_protection import HistoryProtectionManager, MergeAction, BranchRule


def run_git(args, cwd=None, check=True):
    """Helper to run git commands."""
    cmd = ['git'] + args
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=check)
    return result.stdout.strip()


def create_test_repo():
    """Create a test git repository with branches and commits."""
    # Create temporary directory
    temp_dir = tempfile.mkdtemp(prefix='repokit_history_test_')
    print(f"Created test repo at: {temp_dir}")
    
    # Initialize git repo
    run_git(['init', '-b', 'main'], cwd=temp_dir)
    run_git(['config', 'user.name', 'Test User'], cwd=temp_dir)
    run_git(['config', 'user.email', 'test@example.com'], cwd=temp_dir)
    
    # Create initial commit on main
    with open(os.path.join(temp_dir, 'README.md'), 'w') as f:
        f.write("# Test Repository\n")
    run_git(['add', 'README.md'], cwd=temp_dir)
    run_git(['commit', '-m', 'Initial commit'], cwd=temp_dir)
    
    # Create a prototype branch with messy history
    run_git(['checkout', '-b', 'prototype/new-feature'], cwd=temp_dir)
    
    # Add multiple commits with sensitive content
    commits = [
        ("Added secret key", "config.py", "SECRET_KEY = 'do-not-commit-this'\n"),
        ("WIP: temp hack", "hack.py", "# TODO: hack - remove before production\n"),
        ("Experimented with private API", "private/api.py", "# Uses private internal API\n"),
        ("Fixed typo", "README.md", "# Test Repository\n\nFixed.\n"),
        ("TEMP: debugging print statements", "debug.py", "print('DEBUGGING')\n"),
        ("Implemented feature", "feature.py", "def feature():\n    return True\n"),
    ]
    
    for msg, filename, content in commits:
        filepath = os.path.join(temp_dir, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(content)
        run_git(['add', filename], cwd=temp_dir)
        run_git(['commit', '-m', msg], cwd=temp_dir)
    
    # Switch back to main
    run_git(['checkout', 'main'], cwd=temp_dir)
    
    return temp_dir


def test_branch_rules():
    """Test branch rule matching."""
    print("\n=== Testing Branch Rules ===")
    
    manager = HistoryProtectionManager()
    
    test_cases = [
        ("prototype/new-feature", MergeAction.SQUASH),
        ("experiment/ml-model", MergeAction.SQUASH),
        ("feature/oauth", MergeAction.INTERACTIVE),
        ("bugfix/critical-fix", MergeAction.PRESERVE),
        ("hotfix/security-patch", MergeAction.PRESERVE),
        ("random-branch", MergeAction.INTERACTIVE),  # Default
    ]
    
    for branch_name, expected_action in test_cases:
        rule = manager.get_branch_rule(branch_name)
        status = "✓" if rule.action == expected_action else "✗"
        print(f"{status} {branch_name}: {rule.action.value} (expected: {expected_action.value})")


def test_commit_analysis():
    """Test commit analysis and message generation."""
    print("\n=== Testing Commit Analysis ===")
    
    repo_dir = create_test_repo()
    manager = HistoryProtectionManager(repo_path=repo_dir)
    
    # Get commits from prototype branch
    commits = manager.get_branch_commits("prototype/new-feature", "main")
    print(f"\nFound {len(commits)} commits in prototype/new-feature")
    
    for commit in commits:
        print(f"  {commit.hash[:8]} {commit.message}")
    
    # Test message sanitization
    print("\n--- Testing Message Sanitization ---")
    test_messages = [
        "Added secret key",
        "TODO: hack this needs fixing",
        "Updated private/config.py",
        "Normal commit message",
    ]
    
    for msg in test_messages:
        sanitized = manager.sanitize_message(msg)
        if sanitized != msg:
            print(f"  '{msg}' → '{sanitized}'")
        else:
            print(f"  '{msg}' (unchanged)")
    
    # Test squash message generation
    print("\n--- Testing Squash Message Generation ---")
    squash_msg = manager.generate_squash_message(commits, "prototype/new-feature")
    print(f"\nGenerated squash message:\n{squash_msg}")
    
    # Cleanup
    shutil.rmtree(repo_dir)


def test_safe_merge_preview():
    """Test safe merge preview functionality."""
    print("\n=== Testing Safe Merge Preview ===")
    
    repo_dir = create_test_repo()
    manager = HistoryProtectionManager(repo_path=repo_dir)
    
    # Preview squash
    commits, message = manager.preview_squash("prototype/new-feature", "main")
    
    print(f"\nPreview for merging prototype/new-feature:")
    print(f"Commits to squash: {len(commits)}")
    print(f"\nGenerated message:\n{message}")
    
    # Cleanup
    shutil.rmtree(repo_dir)


def test_cli_command():
    """Test the CLI command."""
    print("\n=== Testing CLI Command ===")
    
    # Test help
    result = subprocess.run(
        [sys.executable, '-m', 'repokit', 'safe-merge-dev', '--help'],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✓ CLI command is available")
        print("\nHelp output preview:")
        print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
    else:
        print("✗ CLI command failed")
        print(f"Error: {result.stderr}")


def main():
    """Run all tests."""
    print("Testing RepoKit History Protection")
    print("=" * 50)
    
    test_branch_rules()
    test_commit_analysis()
    test_safe_merge_preview()
    test_cli_command()
    
    print("\n" + "=" * 50)
    print("All tests completed!")


if __name__ == "__main__":
    main()