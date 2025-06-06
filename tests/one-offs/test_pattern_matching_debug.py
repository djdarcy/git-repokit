#!/usr/bin/env python3
"""
Test pattern matching for sensitive file cleanup.

This test validates the enhanced pattern matching logic and debugging
capabilities added to fix the listall.cmd~ cleanup issues.
"""

import os
import sys
import tempfile
import shutil
import fnmatch
from pathlib import Path

# Add the repokit package to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from repokit.defaults import DEFAULT_SENSITIVE_PATTERNS


def test_pattern_matching():
    """Test pattern matching against problematic files."""
    
    print("=== PATTERN MATCHING DEBUG TEST ===")
    print(f"Default sensitive patterns: {DEFAULT_SENSITIVE_PATTERNS}")
    
    # Test files that should be caught
    test_files = [
        "listall.cmd~",           # The problematic vim backup file
        "script.py~",             # Single extension vim backup
        "config.json~",           # Another single extension
        "test.html~",             # Web file backup
        "data.csv~",              # Data file backup
        "logs/test.log",          # Log file in logs directory
        "run_tests_stdout_stderr.txt",  # The other problematic file
        "Clipboard Text.txt",     # Clipboard files
        "Clipboard Text (1).txt", # Numbered clipboard files
        "nul",                    # Windows reserved name
        "temp.tmp",               # Temp files
        "backup.backup",          # Backup files
        "test.bak",               # Bak files
        ".env.local",             # Environment files
    ]
    
    print("\n=== TESTING PATTERN MATCHING ===")
    
    for test_file in test_files:
        print(f"\nTesting file: '{test_file}'")
        matched = False
        matching_patterns = []
        
        for pattern in DEFAULT_SENSITIVE_PATTERNS:
            # Test different matching approaches
            matches = []
            
            # Full path match
            if fnmatch.fnmatch(test_file, pattern):
                matches.append(f"full_path({pattern})")
                
            # Filename only match  
            if fnmatch.fnmatch(os.path.basename(test_file), pattern):
                matches.append(f"basename({pattern})")
                
            # Path object match
            if fnmatch.fnmatch(str(Path(test_file)), pattern):
                matches.append(f"pathlib({pattern})")
            
            if matches:
                matched = True
                matching_patterns.extend(matches)
                print(f"  ✓ Matched by: {', '.join(matches)}")
        
        if not matched:
            print(f"  ❌ NOT MATCHED - This is a problem!")
        else:
            print(f"  ✅ MATCHED by {len(matching_patterns)} pattern checks")
    
    print("\n=== TESTING SPECIFIC PROBLEMATIC CASES ===")
    
    # Test the specific files that failed in deployment
    problematic_files = [
        "scripts/listall.cmd~",
        "logs/2025.03.22_4/run_tests_stdout_stderr.txt"
    ]
    
    for test_file in problematic_files:
        print(f"\nTesting problematic file: '{test_file}'")
        
        for pattern in DEFAULT_SENSITIVE_PATTERNS:
            # Test all matching methods
            full_match = fnmatch.fnmatch(test_file, pattern)
            base_match = fnmatch.fnmatch(os.path.basename(test_file), pattern)
            path_match = fnmatch.fnmatch(str(Path(test_file)), pattern)
            
            if full_match or base_match or path_match:
                print(f"  ✓ Pattern '{pattern}' matches:")
                if full_match:
                    print(f"    - Full path match: {test_file}")
                if base_match:
                    print(f"    - Basename match: {os.path.basename(test_file)}")
                if path_match:
                    print(f"    - Path object match: {str(Path(test_file))}")


def test_create_sample_files():
    """Create sample files and test cleanup detection."""
    
    print("\n=== CREATING SAMPLE FILES FOR TESTING ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Creating test files in: {temp_dir}")
        
        # Create the problematic files
        test_files = [
            "scripts/listall.cmd~",
            "logs/2025.03.22_4/run_tests_stdout_stderr.txt",
            "private/convos/00. pre-start.md",
            "CLAUDE.md",
            "Clipboard Text.txt"
        ]
        
        created_files = []
        
        for file_path in test_files:
            full_path = os.path.join(temp_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w') as f:
                f.write(f"Test content for {file_path}")
            
            created_files.append(file_path)
            print(f"  Created: {file_path}")
        
        print(f"\nCreated {len(created_files)} test files")
        
        # Now test pattern matching on actual files
        print("\n=== TESTING PATTERN MATCHING ON ACTUAL FILES ===")
        
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, temp_dir)
                
                matched_patterns = []
                
                for pattern in DEFAULT_SENSITIVE_PATTERNS:
                    if (fnmatch.fnmatch(relative_path, pattern) or 
                        fnmatch.fnmatch(file, pattern) or
                        fnmatch.fnmatch(str(Path(relative_path)), pattern)):
                        matched_patterns.append(pattern)
                
                if matched_patterns:
                    print(f"  ✓ {relative_path} -> matched by: {matched_patterns}")
                else:
                    print(f"  ❌ {relative_path} -> NOT MATCHED")


if __name__ == "__main__":
    test_pattern_matching()
    test_create_sample_files()
    
    print("\n=== PATTERN MATCHING TEST COMPLETE ===")
    print("Review the output above to verify that all expected files are matched.")
    print("Any files showing 'NOT MATCHED' indicate pattern issues that need fixing.")