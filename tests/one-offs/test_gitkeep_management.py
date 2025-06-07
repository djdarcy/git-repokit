#!/usr/bin/env python3
"""
Test script for .gitkeep management functionality.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the repokit module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from repokit.directory_profiles import DirectoryProfileManager


def test_gitkeep_management():
    """Test the .gitkeep management functionality."""
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Testing in temporary directory: {temp_dir}")
        
        # Create test directory structure
        test_dirs = [
            "empty_dir1",
            "empty_dir2", 
            "non_empty_dir1",
            "non_empty_dir2",
            "nested/empty_nested",
            "nested/non_empty_nested"
        ]
        
        for dir_path in test_dirs:
            full_path = os.path.join(temp_dir, dir_path)
            os.makedirs(full_path, exist_ok=True)
        
        # Add content to some directories
        with open(os.path.join(temp_dir, "non_empty_dir1", "file1.txt"), "w") as f:
            f.write("test content")
        
        with open(os.path.join(temp_dir, "non_empty_dir2", "file2.txt"), "w") as f:
            f.write("test content")
            
        with open(os.path.join(temp_dir, "nested", "non_empty_nested", "file3.txt"), "w") as f:
            f.write("test content")
        
        # Add .gitkeep to a non-empty directory (should be removed)
        with open(os.path.join(temp_dir, "non_empty_dir1", ".gitkeep"), "w") as f:
            f.write("# Should be removed")
        
        print("\nInitial directory structure:")
        for root, dirs, files in os.walk(temp_dir):
            level = root.replace(temp_dir, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                print(f"{subindent}{file}")
        
        # Initialize directory profile manager
        profile_manager = DirectoryProfileManager(verbose=1)
        
        # Test .gitkeep management
        print("\nManaging .gitkeep files...")
        result = profile_manager.manage_gitkeep_files(temp_dir, recursive=True)
        
        print(f"\nResults:")
        print(f"Added: {result['added']}")
        print(f"Removed: {result['removed']}")
        
        print("\nFinal directory structure:")
        for root, dirs, files in os.walk(temp_dir):
            level = root.replace(temp_dir, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                print(f"{subindent}{file}")
        
        # Verify expected results
        expected_gitkeeps = [
            os.path.join(temp_dir, "empty_dir1", ".gitkeep"),
            os.path.join(temp_dir, "empty_dir2", ".gitkeep"),
            os.path.join(temp_dir, "nested", "empty_nested", ".gitkeep")
        ]
        
        unexpected_gitkeeps = [
            os.path.join(temp_dir, "non_empty_dir1", ".gitkeep"),
            os.path.join(temp_dir, "non_empty_dir2", ".gitkeep"),
            os.path.join(temp_dir, "nested", "non_empty_nested", ".gitkeep")
        ]
        
        print("\nVerification:")
        all_good = True
        
        for gitkeep_path in expected_gitkeeps:
            if os.path.exists(gitkeep_path):
                print(f"✓ Found expected .gitkeep: {gitkeep_path}")
            else:
                print(f"✗ Missing expected .gitkeep: {gitkeep_path}")
                all_good = False
        
        for gitkeep_path in unexpected_gitkeeps:
            if not os.path.exists(gitkeep_path):
                print(f"✓ Correctly removed .gitkeep: {gitkeep_path}")
            else:
                print(f"✗ Unexpected .gitkeep found: {gitkeep_path}")
                all_good = False
        
        if all_good:
            print("\n🎉 All tests passed!")
            return True
        else:
            print("\n❌ Some tests failed!")
            return False


if __name__ == "__main__":
    success = test_gitkeep_management()
    sys.exit(0 if success else 1)