#!/usr/bin/env python3
"""
Debug vim backup pattern matching specifically for files like 'listall.cmd~'.

This test reproduces the exact pattern matching logic used in deployment
to understand why '*.*~' patterns work in tests but fail in actual deployment.
"""

import os
import fnmatch
from pathlib import Path
import tempfile
import shutil

def test_vim_backup_patterns():
    """Test vim backup patterns against specific problematic files."""
    print("=" * 80)
    print("VIM BACKUP PATTERN MATCHING DEBUG")
    print("=" * 80)
    
    # Test patterns from DEFAULT_SENSITIVE_PATTERNS
    patterns = [
        "*.*~",          # Primary vim backup pattern (multiple extensions)
        "*~",            # Fallback vim backup pattern
        "*.cmd~",        # Specific pattern for .cmd~ files
        "scripts/*~",    # Directory + vim backup pattern
        "scripts/*.*~",  # Directory + multiple extension vim backup
    ]
    
    # Test files - including the exact problematic file
    test_files = [
        "listall.cmd~",                           # The exact file causing issues
        "scripts/listall.cmd~",                   # With directory path
        "test.py~",                              # Simple vim backup
        "config.json~",                          # Another extension + backup
        "README.md~",                            # Markdown backup
        "data.tar.gz~",                          # Multiple extensions + backup
        "nul",                                   # Windows reserved (different pattern type)
        "logs/test.log",                         # Regular log file
        "private/secret.txt",                    # Private directory file
    ]
    
    print(f"Testing {len(patterns)} patterns against {len(test_files)} files:\n")
    
    # Test each pattern against each file
    results = {}
    for pattern in patterns:
        results[pattern] = {}
        print(f"Pattern: '{pattern}'")
        print("-" * 40)
        
        for test_file in test_files:
            # Test multiple matching approaches (same as repo_manager.py)
            
            # Approach 1: Direct fnmatch
            match1 = fnmatch.fnmatch(test_file, pattern)
            
            # Approach 2: Basename only
            match2 = fnmatch.fnmatch(os.path.basename(test_file), pattern)
            
            # Approach 3: Path normalization (cross-platform)
            normalized_file = str(Path(test_file)).replace('\\', '/')
            normalized_pattern = pattern.replace('\\', '/')
            match3 = fnmatch.fnmatch(normalized_file, normalized_pattern)
            
            # Approach 4: Basename with normalization
            match4 = fnmatch.fnmatch(os.path.basename(test_file), normalized_pattern)
            
            # Combined result (any match = True, same logic as cleanup)
            any_match = any([match1, match2, match3, match4])
            
            results[pattern][test_file] = {
                'direct': match1,
                'basename': match2, 
                'normalized': match3,
                'basename_normalized': match4,
                'any_match': any_match
            }
            
            # Print result with details
            status = "✅ MATCH" if any_match else "❌ NO MATCH"
            details = f"direct={match1}, basename={match2}, norm={match3}, base_norm={match4}"
            print(f"  {test_file:<25} {status} ({details})")
        
        print()
    
    # Focus on the problematic file
    print("=" * 80)
    print("FOCUS: listall.cmd~ PATTERN ANALYSIS")
    print("=" * 80)
    
    problem_file = "listall.cmd~"
    problem_file_path = "scripts/listall.cmd~"
    
    print(f"File: {problem_file}")
    print(f"Path: {problem_file_path}")
    print()
    
    for pattern in patterns:
        result1 = results[pattern].get(problem_file, {})
        result2 = results[pattern].get(problem_file_path, {})
        
        print(f"Pattern '{pattern}':")
        print(f"  Filename only: {result1.get('any_match', False)} - {result1}")
        print(f"  With path:     {result2.get('any_match', False)} - {result2}")
        print()
    
    # Test the actual problematic scenario from the test deployment
    print("=" * 80) 
    print("DEPLOYMENT SCENARIO SIMULATION")
    print("=" * 80)
    
    # Create a temporary directory structure matching the real deployment
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Creating test repository structure in: {temp_dir}")
        
        # Create directory structure
        scripts_dir = os.path.join(temp_dir, "scripts")
        os.makedirs(scripts_dir, exist_ok=True)
        
        # Create the problematic file
        problem_file_full = os.path.join(scripts_dir, "listall.cmd~")
        with open(problem_file_full, "w") as f:
            f.write("@echo off\nlistall.py -d . -xd .git %*\n")
        
        print(f"Created file: {problem_file_full}")
        print(f"File exists: {os.path.exists(problem_file_full)}")
        
        # Test os.walk logic (same as cleanup function)
        print("\nTesting os.walk detection logic:")
        
        from repokit.defaults import DEFAULT_SENSITIVE_PATTERNS
        
        for root, dirs, files in os.walk(temp_dir):
            # Skip .git directory (same as cleanup)
            if ".git" in root.split(os.sep):
                continue
                
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, temp_dir)
                
                print(f"\nFound file: {relative_path}")
                print(f"  Full path: {file_path}")
                print(f"  Basename: {file}")
                
                # Test each pattern
                for pattern in DEFAULT_SENSITIVE_PATTERNS:
                    # Use exact same logic as _cleanup_sensitive_files
                    normalized_relative = str(Path(relative_path)).replace('\\', '/')
                    normalized_pattern = pattern.replace('\\', '/')
                    
                    matches = [
                        fnmatch.fnmatch(normalized_relative, normalized_pattern),  # Full path
                        fnmatch.fnmatch(file, normalized_pattern),                 # Filename only  
                        fnmatch.fnmatch(str(Path(file)), normalized_pattern),     # Filename as Path
                    ]
                    
                    if any(matches):
                        print(f"  ✅ MATCHED by pattern '{pattern}' (norm: '{normalized_pattern}')")
                        print(f"     Match details: full={matches[0]}, file={matches[1]}, path={matches[2]}")
                        break
                else:
                    print(f"  ❌ NO PATTERN MATCHED")
                    
                    # Show what each key pattern would produce
                    key_patterns = ["*.*~", "*~", "*.cmd~"]
                    for kp in key_patterns:
                        normalized_kp = kp.replace('\\', '/')
                        km = [
                            fnmatch.fnmatch(normalized_relative, normalized_kp),
                            fnmatch.fnmatch(file, normalized_kp),
                            fnmatch.fnmatch(str(Path(file)), normalized_kp),
                        ]
                        print(f"     Pattern '{kp}': {km}")
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    
    # Summary of findings
    critical_patterns = ["*.*~", "*~"]
    critical_file = "listall.cmd~"
    
    print(f"\nKey findings for file '{critical_file}':")
    for pattern in critical_patterns:
        if pattern in results and critical_file in results[pattern]:
            match_result = results[pattern][critical_file]['any_match']
            print(f"  Pattern '{pattern}': {'✅ SHOULD MATCH' if match_result else '❌ PROBLEMATIC'}")
        else:
            print(f"  Pattern '{pattern}': ❓ NOT TESTED")

if __name__ == "__main__":
    test_vim_backup_patterns()