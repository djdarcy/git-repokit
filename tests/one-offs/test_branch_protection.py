#!/usr/bin/env python3
"""
Test script for branch protection functionality with our configuration consolidation fixes.
"""

import os
import sys
import tempfile
import shutil

# Add the repokit module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from repokit.repo_manager import RepoManager


def test_branch_protection():
    """Test that branch protection works with custom sensitive files and patterns."""
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Testing in temporary directory: {temp_dir}")
        
        # Create test project structure
        project_dir = os.path.join(temp_dir, "test-protection")
        os.makedirs(project_dir)
        
        # Create various files that should and shouldn't be in public branches
        test_files = {
            "README.md": "# Test Project",
            "main.py": "print('hello world')",
            "CLAUDE.md": "# Claude instructions - should be private",
            "Clipboard Text.txt": "Some clipboard content - should be private",
            "temp_file.tmp": "Temporary file - should be private",
            "private/secret.txt": "Private content",
            "revisions/old_version.py": "Old version",
            "logs/debug.log": "Debug information",
            "docs/guide.md": "User guide - should be public"
        }
        
        for file_path, content in test_files.items():
            full_path = os.path.join(project_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w") as f:
                f.write(content)
        
        print("\nCreated test files:")
        for file_path in test_files.keys():
            print(f"  {file_path}")
        
        # Configure RepoManager with custom sensitive patterns
        config = {
            "name": "test-protection",
            "description": "Test project for branch protection",
            "language": "python",
            "default_branch": "main",
            "branches": ["main", "dev"],
            "private_branch": "private",
            # Test our custom configuration
            "sensitive_files": ["CLAUDE.md", "secrets.json"],
            "sensitive_patterns": ["Clipboard Text*", "*.tmp", "temp_*"]
        }
        
        # Initialize RepoManager
        repo_manager = RepoManager(config, verbose=2)
        
        # Override paths to work in our test directory
        repo_manager.project_root = temp_dir
        repo_manager.repo_root = project_dir
        repo_manager.github_root = os.path.join(temp_dir, "github")
        
        print(f"\nInitializing repository in {project_dir}")
        
        # Initialize git repository
        repo_manager.run_git(["init"], cwd=project_dir)
        repo_manager.run_git(["config", "user.name", "Test User"], cwd=project_dir)
        repo_manager.run_git(["config", "user.email", "test@example.com"], cwd=project_dir)
        
        # Add all files to private branch
        repo_manager.run_git(["add", "."], cwd=project_dir)
        repo_manager.run_git(["commit", "-m", "Initial commit with all files"], cwd=project_dir)
        repo_manager.run_git(["branch", "-m", "private"], cwd=project_dir)
        
        print("\nTesting clean branch creation...")
        
        # Test creating clean main branch
        try:
            repo_manager._create_clean_public_branch("main", "private")
            print("✓ Created clean main branch")
            
            # Verify the main branch is clean
            if repo_manager._verify_clean_branch("main"):
                print("✓ Main branch verified clean")
            else:
                print("✗ Main branch failed verification")
                return False
                
        except Exception as e:
            print(f"✗ Failed to create clean main branch: {str(e)}")
            return False
        
        # Test creating clean dev branch
        try:
            repo_manager._create_clean_public_branch("dev", "private")
            print("✓ Created clean dev branch")
            
            # Verify the dev branch is clean
            if repo_manager._verify_clean_branch("dev"):
                print("✓ Dev branch verified clean")
            else:
                print("✗ Dev branch failed verification")
                return False
                
        except Exception as e:
            print(f"✗ Failed to create clean dev branch: {str(e)}")
            return False
        
        # Check what files exist in the main branch
        repo_manager.run_git(["checkout", "main"], cwd=project_dir)
        main_files = []
        for root, dirs, files in os.walk(project_dir):
            if ".git" in root:
                continue
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), project_dir)
                main_files.append(rel_path)
        
        print(f"\nFiles in main branch: {sorted(main_files)}")
        
        # Expected files in public branch (should NOT contain private content)
        expected_public_files = {"README.md", "main.py", "docs/guide.md", ".gitignore"}
        unexpected_files = {"CLAUDE.md", "Clipboard Text.txt", "temp_file.tmp", 
                           "private/secret.txt", "revisions/old_version.py", "logs/debug.log"}
        
        # Check that public files are present
        missing_public = expected_public_files - set(main_files)
        if missing_public:
            print(f"✗ Missing expected public files: {missing_public}")
            return False
        
        # Check that private files are absent
        leaked_private = set(main_files) & unexpected_files
        if leaked_private:
            print(f"✗ Private files leaked to public branch: {leaked_private}")
            return False
        
        print("✓ All branch protection tests passed!")
        return True


if __name__ == "__main__":
    try:
        if test_branch_protection():
            print("\n🎉 Branch protection test successful!")
            sys.exit(0)
        else:
            print("\n❌ Branch protection test failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)