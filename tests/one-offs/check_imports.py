#!/usr/bin/env python3
"""Check if all imports work correctly."""

import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

print("Checking imports...")

try:
    import repokit
    print("✓ repokit")
except Exception as e:
    print(f"✗ repokit: {e}")

try:
    from repokit import cli
    print("✓ repokit.cli")
except Exception as e:
    print(f"✗ repokit.cli: {e}")

try:
    from repokit import config
    print("✓ repokit.config")
except Exception as e:
    print(f"✗ repokit.config: {e}")

try:
    from repokit import directory_profiles
    print("✓ repokit.directory_profiles")
except Exception as e:
    print(f"✗ repokit.directory_profiles: {e}")

try:
    from repokit import repo_manager
    print("✓ repokit.repo_manager")
except Exception as e:
    print(f"✗ repokit.repo_manager: {e}")

print("\nDone!")