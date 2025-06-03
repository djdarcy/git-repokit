#!/usr/bin/env python3
"""
Test the history protection feature with a UNCtools-like scenario.

This demonstrates how the history protection would have helped with the
UNCtools deployment where prototype and feature/clean-up branches contained
detailed implementation history.
"""

import os
import sys
import tempfile
import shutil
import subprocess

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from repokit.history_protection import HistoryProtectionManager


def run_git(args, cwd=None, check=True):
    """Helper to run git commands."""
    cmd = ['git'] + args
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=check)
    return result.stdout.strip()


def create_unctools_like_repo():
    """Create a repo similar to the UNCtools scenario."""
    # Create temporary directory
    temp_dir = tempfile.mkdtemp(prefix='unctools_history_test_')
    print(f"Created test repo at: {temp_dir}")
    
    # Initialize git repo
    run_git(['init', '-b', 'main'], cwd=temp_dir)
    run_git(['config', 'user.name', 'Developer'], cwd=temp_dir)
    run_git(['config', 'user.email', 'dev@example.com'], cwd=temp_dir)
    
    # Create initial structure
    os.makedirs(os.path.join(temp_dir, 'unctools'), exist_ok=True)
    with open(os.path.join(temp_dir, 'README.md'), 'w') as f:
        f.write("# UNCtools\n")
    with open(os.path.join(temp_dir, 'unctools', '__init__.py'), 'w') as f:
        f.write("__version__ = '0.1.0'\n")
    run_git(['add', '.'], cwd=temp_dir)
    run_git(['commit', '-m', 'Initial commit'], cwd=temp_dir)
    
    # Create prototype branch with messy history
    run_git(['checkout', '-b', 'prototype'], cwd=temp_dir)
    
    # Simulate prototype development with sensitive commits
    prototype_commits = [
        ("Hack: hardcoded path for testing", "unctools/config.py", 
         "# TODO: HACK - remove before release\nPATH = '/home/dev/private/data'\n"),
        ("Experimenting with Windows registry", "unctools/windows/registry.py",
         "# TEMP: Direct registry access - DO NOT COMMIT\nimport winreg\n"),
        ("Added debug prints everywhere", "unctools/converter.py",
         "def convert(path):\n    print('DEBUG:', path)  # REMOVE\n    return path\n"),
        ("Testing with private customer data", "tests/test_private.py",
         "# Testing with CompanyX private paths\ntest_path = '//companyX/private/share'\n"),
        ("Fixed the actual issue", "unctools/converter.py",
         "def convert(path):\n    # Proper implementation\n    return path.replace('\\\\', '/')\n"),
        ("Cleaned up some code", "unctools/converter.py",
         "def convert(path):\n    '''Convert UNC paths'''\n    return path.replace('\\\\', '/')\n"),
    ]
    
    for msg, filename, content in prototype_commits:
        filepath = os.path.join(temp_dir, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(content)
        run_git(['add', filename], cwd=temp_dir)
        run_git(['commit', '-m', msg], cwd=temp_dir)
    
    # Create feature/clean-up branch from prototype
    run_git(['checkout', '-b', 'feat/clean-up'], cwd=temp_dir)
    
    # More commits in cleanup (with actual changes)
    cleanup_commits = [
        ("Removed debug statements", "unctools/utils.py",
         "def log(msg):\n    '''Simple logger'''\n    pass\n"),
        ("Updated tests", "tests/test_converter.py",
         "def test_convert():\n    assert convert('\\\\\\\\server\\\\share') == '//server/share'\n"),
        ("Added documentation", "unctools/converter.py",
         "def convert(path):\n    '''Convert UNC paths.\n    \n    Args:\n        path: UNC path to convert\n    '''\n    return path.replace('\\\\', '/')\n"),
    ]
    
    for msg, filename, content in cleanup_commits:
        filepath = os.path.join(temp_dir, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(content)
        run_git(['add', filename], cwd=temp_dir)
        run_git(['commit', '-m', msg], cwd=temp_dir)
    
    # Go to private branch
    run_git(['checkout', '-b', 'private', 'main'], cwd=temp_dir)
    
    return temp_dir


def demonstrate_history_protection():
    """Demonstrate how history protection would work with UNCtools."""
    print("\n=== UNCtools History Protection Scenario ===\n")
    
    # Create the repo
    repo_dir = create_unctools_like_repo()
    
    # Initialize history protection
    config = {
        'history_protection': {
            'branch_rules': {
                'prototype/*': {'action': 'squash', 'auto': True},
                'prototype': {'action': 'squash', 'auto': True},  # Also match exact
                'feat/*': {'action': 'interactive', 'auto': False},
            }
        }
    }
    
    manager = HistoryProtectionManager(repo_path=repo_dir, config=config)
    
    # Show current state
    print("Current branch: private")
    print("\nBranches with sensitive history:")
    
    # Analyze prototype branch
    print("\n1. Prototype branch:")
    prototype_commits = manager.get_branch_commits("prototype", "private")
    print(f"   Total commits: {len(prototype_commits)}")
    print("   Commit messages:")
    for commit in prototype_commits:
        print(f"   - {commit.message}")
    
    # Show what would happen with safe-merge-dev
    print("\n2. Using safe-merge-dev on prototype:")
    commits, message = manager.preview_squash("prototype", "private")
    print(f"   Would squash {len(commits)} commits")
    print(f"\n   Generated safe message:\n{message}")
    
    # Analyze feat/clean-up branch
    print("\n\n3. Feature cleanup branch:")
    feat_commits = manager.get_branch_commits("feat/clean-up", "private")
    print(f"   Total commits: {len(feat_commits)}")
    print("   Commit messages:")
    for commit in feat_commits:
        print(f"   - {commit.message}")
    
    # Show interactive mode
    print("\n4. Using safe-merge-dev on feat/clean-up:")
    print("   This would trigger INTERACTIVE mode")
    print("   User would see:")
    print("   - All 9 commits (6 from prototype + 3 new)")
    print("   - Option to squash or preserve")
    print("   - Suggested squash message")
    
    # Show the difference
    print("\n\n=== Without History Protection ===")
    print("If these branches were merged normally and pushed to GitHub:")
    print("- All 9 detailed commits would be visible")
    print("- Sensitive information exposed:")
    print("  - Hardcoded private paths")
    print("  - Customer names (CompanyX)")  
    print("  - Debug statements and hacks")
    print("  - Internal development notes")
    
    print("\n=== With History Protection ===")
    print("After using safe-merge-dev:")
    print("- Prototype: 1 clean commit with sanitized message")
    print("- Feature: User choice (likely squashed to 1-3 commits)")
    print("- No sensitive information in public history")
    print("- Clean, professional commit history")
    
    # Cleanup
    shutil.rmtree(repo_dir)


def main():
    """Run the demonstration."""
    print("UNCtools History Protection Demonstration")
    print("=" * 50)
    
    demonstrate_history_protection()
    
    print("\n" + "=" * 50)
    print("Demonstration completed!")
    print("\nKey Takeaway: History protection would have prevented the")
    print("detailed development history from being pushed to GitHub while")
    print("still preserving the meaningful changes in a clean format.")


if __name__ == "__main__":
    main()