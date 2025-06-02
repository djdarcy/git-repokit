#!/usr/bin/env python3
"""Debug private set configuration."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from repokit.directory_profiles import DirectoryProfileManager
from repokit.config import ConfigManager

print("=== Testing Private Set Configuration ===")

# Test DirectoryProfileManager directly
manager = DirectoryProfileManager()
print(f"Standard private dirs: {manager.get_private_directories('standard')}")
print(f"Enhanced private dirs: {manager.get_private_directories('enhanced')}")

# Test through ConfigManager
config = ConfigManager()
config.cli_config = {
    "directory_profile": "standard",
    "private_set": "enhanced",
    "name": "testproject"
}
config.config = config._merge_configs()
print(f"Config private_set: {config.config.get('private_set')}")

config.resolve_directory_profiles()
private_dirs = config.config.get("private_dirs", [])
print(f"Resolved private dirs: {private_dirs}")

if "secrets" in private_dirs and "local" in private_dirs:
    print("✓ Enhanced private set working correctly")
else:
    print("✗ Enhanced private set not working")