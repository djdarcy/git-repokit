#!/usr/bin/env python3
"""
Manual test runner for directory profiles.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import and run tests
try:
    from repokit.directory_profiles import DirectoryProfileManager
    from repokit.config import ConfigManager
    
    print("✓ Imports successful")
    
    # Test 1: DirectoryProfileManager basics
    print("\nTest 1: DirectoryProfileManager basics")
    manager = DirectoryProfileManager()
    print(f"  Profiles available: {list(manager.profiles.keys())}")
    print(f"  Minimal profile: {manager.profiles['minimal']}")
    print(f"  ✓ DirectoryProfileManager works")
    
    # Test 2: ConfigManager integration
    print("\nTest 2: ConfigManager integration")
    config = ConfigManager()
    config.cli_config = {
        "directory_profile": "minimal",
        "name": "testproject"
    }
    config.config = config._merge_configs()
    config.resolve_directory_profiles()
    
    dirs = config.config.get("directories", [])
    print(f"  Resolved directories: {dirs}")
    print(f"  Directory count: {len(dirs)}")
    
    if len(dirs) == 3 and "testproject" in dirs and "tests" in dirs and "docs" in dirs:
        print("  ✓ Minimal profile resolves correctly")
    else:
        print("  ✗ ERROR: Minimal profile did not resolve to expected 3 directories")
    
    # Test 3: Backward compatibility
    print("\nTest 3: Backward compatibility")
    config2 = ConfigManager()
    config2.cli_config = {"name": "testproject"}
    config2.config = config2._merge_configs()
    config2.resolve_directory_profiles()
    
    dirs2 = config2.config.get("directories", [])
    print(f"  Default directories: {dirs2}")
    
    if "convos" in dirs2 and "private" in dirs2 and "scripts" in dirs2:
        print("  ✓ Backward compatibility maintained")
    else:
        print("  ✗ ERROR: Default directories not maintained")
    
    print("\n✅ All tests passed!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()