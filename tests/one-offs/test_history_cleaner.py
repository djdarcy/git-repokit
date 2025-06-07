#!/usr/bin/env python3
"""
Test script for history cleaner functionality.

This script tests the new clean-history and analyze-history commands.
"""

import os
import sys
import tempfile
import shutil
import subprocess

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from repokit.history_cleaner import HistoryCleaner, CleaningConfig, CleaningRecipe


def run_git(args, cwd=None, check=True):
    """Helper to run git commands."""
    cmd = ['git'] + args
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=check)
    return result.stdout.strip()


def create_test_repo_with_history():
    """Create a test repository with problematic history."""
    # Create temporary directory
    temp_dir = tempfile.mkdtemp(prefix='repokit_cleaner_test_')
    print(f"Created test repo at: {temp_dir}")
    
    # Initialize git repo
    run_git(['init', '-b', 'main'], cwd=temp_dir)
    run_git(['config', 'user.name', 'Test User'], cwd=temp_dir)
    run_git(['config', 'user.email', 'test@example.com'], cwd=temp_dir)
    
    # Create initial commit
    with open(os.path.join(temp_dir, 'README.md'), 'w') as f:
        f.write("# Test Project\n")
    run_git(['add', 'README.md'], cwd=temp_dir)
    run_git(['commit', '-m', 'Initial commit'], cwd=temp_dir)
    
    # Add private files
    os.makedirs(os.path.join(temp_dir, 'private'), exist_ok=True)
    with open(os.path.join(temp_dir, 'private', 'secrets.txt'), 'w') as f:
        f.write("API_KEY=super-secret-key\n")
    with open(os.path.join(temp_dir, 'CLAUDE.md'), 'w') as f:
        f.write("# AI Instructions\n")
    run_git(['add', '.'], cwd=temp_dir)
    run_git(['commit', '-m', 'Add private files'], cwd=temp_dir)
    
    # Add logs
    os.makedirs(os.path.join(temp_dir, 'logs'), exist_ok=True)
    with open(os.path.join(temp_dir, 'logs', 'debug.log'), 'w') as f:
        f.write("Debug information\n")
    run_git(['add', '.'], cwd=temp_dir)
    run_git(['commit', '-m', 'Add logs'], cwd=temp_dir)
    
    # Add Windows problematic file (if not on Windows)
    if os.name != 'nt':
        with open(os.path.join(temp_dir, 'nul'), 'w') as f:
            f.write("This file has a Windows reserved name\n")
        run_git(['add', 'nul'], cwd=temp_dir)
        run_git(['commit', '-m', 'Add Windows problematic file'], cwd=temp_dir)
    
    # Add some normal files
    with open(os.path.join(temp_dir, 'app.py'), 'w') as f:
        f.write("print('Hello, World!')\n")
    run_git(['add', 'app.py'], cwd=temp_dir)
    run_git(['commit', '-m', 'Add application'], cwd=temp_dir)
    
    # Create dev branch with more changes
    run_git(['checkout', '-b', 'dev'], cwd=temp_dir)
    with open(os.path.join(temp_dir, 'feature.py'), 'w') as f:
        f.write("def feature():\n    pass\n")
    run_git(['add', 'feature.py'], cwd=temp_dir)
    run_git(['commit', '-m', 'Add feature'], cwd=temp_dir)
    
    # Go back to main
    run_git(['checkout', 'main'], cwd=temp_dir)
    
    return temp_dir


def test_analyzer():
    """Test repository analysis."""
    print("\n=== Testing Repository Analysis ===")
    
    repo_dir = create_test_repo_with_history()
    
    try:
        cleaner = HistoryCleaner(repo_path=repo_dir, check_filter_repo=False)
        analysis = cleaner.analyze_repository()
        
        print(f"\nAnalysis Results:")
        print(f"  Total commits: {analysis['total_commits']}")
        print(f"  Branches: {analysis['branches']}")
        print(f"  Private paths found: {len(analysis['private_paths'])}")
        for path in analysis['private_paths']:
            print(f"    - {path}")
        
        if analysis['windows_issues']:
            print(f"  Windows issues: {len(analysis['windows_issues'])}")
            for path in analysis['windows_issues']:
                print(f"    - {path}")
        
        # Verify expected results
        assert analysis['total_commits'] >= 4, "Should have at least 4 commits"
        assert 'main' in analysis['branches'], "Should have main branch"
        assert 'dev' in analysis['branches'], "Should have dev branch"
        assert any('private/' in p for p in analysis['private_paths']), "Should find private directory"
        assert 'CLAUDE.md' in analysis['private_paths'], "Should find CLAUDE.md"
        
        print("\n✓ Analysis test passed!")
        
    except Exception as e:
        print(f"\n✗ Analysis test failed: {e}")
        raise
    finally:
        shutil.rmtree(repo_dir)


def test_recipe_configs():
    """Test recipe configurations."""
    print("\n=== Testing Recipe Configurations ===")
    
    # Create cleaner without checking for git filter-repo
    cleaner = HistoryCleaner(check_filter_repo=False)
    
    # Test pre-open-source recipe
    config = cleaner.get_recipe_config(CleaningRecipe.PRE_OPEN_SOURCE)
    print(f"\nPre-open-source recipe:")
    print(f"  Paths to remove: {config.paths_to_remove[:5]}...")
    assert 'private/' in config.paths_to_remove
    assert 'CLAUDE.md' in config.paths_to_remove
    
    # Test windows-safe recipe
    config = cleaner.get_recipe_config(CleaningRecipe.WINDOWS_SAFE)
    print(f"\nWindows-safe recipe:")
    print(f"  Recipe type: {config.recipe.value}")
    assert config.recipe == CleaningRecipe.WINDOWS_SAFE
    
    print("\n✓ Recipe configuration test passed!")


def test_cli_commands():
    """Test CLI command availability."""
    print("\n=== Testing CLI Commands ===")
    
    # Test analyze-history help
    result = subprocess.run(
        [sys.executable, '-m', 'repokit', 'analyze-history', '--help'],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✓ analyze-history command available")
    else:
        print("✗ analyze-history command failed")
        print(f"Error: {result.stderr}")
    
    # Test clean-history help
    result = subprocess.run(
        [sys.executable, '-m', 'repokit', 'clean-history', '--help'],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✓ clean-history command available")
        print("\nHelp preview:")
        print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
    else:
        print("✗ clean-history command failed")
        print(f"Error: {result.stderr}")


def test_preview_mode():
    """Test preview functionality."""
    print("\n=== Testing Preview Mode ===")
    
    repo_dir = create_test_repo_with_history()
    
    try:
        cleaner = HistoryCleaner(repo_path=repo_dir, check_filter_repo=False)
        
        # Get pre-open-source config
        config = cleaner.get_recipe_config(CleaningRecipe.PRE_OPEN_SOURCE)
        
        # Preview cleaning
        preview = cleaner.preview_cleaning(config)
        
        print(f"\nPreview Results:")
        print(f"  Recipe: {preview['recipe']}")
        print(f"  Paths to remove: {len(preview['paths_to_remove'])}")
        print(f"  Warnings: {preview['warnings']}")
        
        assert preview['recipe'] == 'pre-open-source'
        assert len(preview['paths_to_remove']) > 0
        
        print("\n✓ Preview test passed!")
        
    except Exception as e:
        print(f"\n✗ Preview test failed: {e}")
        raise
    finally:
        shutil.rmtree(repo_dir)


def main():
    """Run all tests."""
    print("Testing RepoKit History Cleaner")
    print("=" * 50)
    
    # Check if git filter-repo is available
    try:
        result = subprocess.run(
            ['git', 'filter-repo', '--version'],
            capture_output=True,
            text=True,
            check=False
        )
        has_filter_repo = result.returncode == 0
    except:
        has_filter_repo = False
    
    if not has_filter_repo:
        print("\n⚠️  git filter-repo not installed")
        print("Some tests will be skipped")
        print("To install: pip install git-filter-repo")
    
    # Run tests that don't require git filter-repo
    test_recipe_configs()
    test_cli_commands()
    
    # Run tests that need a git repo but not filter-repo
    try:
        test_analyzer()
        test_preview_mode()
    except Exception as e:
        print(f"\nError in tests: {e}")
        return 1
    
    print("\n" + "=" * 50)
    print("All available tests completed!")
    
    if not has_filter_repo:
        print("\n💡 Install git filter-repo to test actual cleaning functionality")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())