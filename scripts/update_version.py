#!/usr/bin/env python3
"""
Script to update version numbers across all RepoKit files.

This updates the version in:
- repokit/__version__.py (source of truth)
- pyproject.toml
- README.md
- Any other files that contain version strings
"""

import re
import sys
import os
from pathlib import Path


def update_version_file(new_version: str) -> None:
    """Update the main version file."""
    version_file = Path("repokit/__version__.py")
    content = version_file.read_text()
    
    # Update version string
    content = re.sub(
        r'__version__ = "[^"]*"',
        f'__version__ = "{new_version}"',
        content
    )
    
    version_file.write_text(content)
    print(f"Updated {version_file}")


def update_pyproject_toml(new_version: str) -> None:
    """Update version in pyproject.toml."""
    pyproject_file = Path("pyproject.toml")
    if not pyproject_file.exists():
        print(f"Warning: {pyproject_file} not found")
        return
        
    content = pyproject_file.read_text()
    
    # Update version in [tool.poetry] or [project] section
    content = re.sub(
        r'^version = "[^"]*"',
        f'version = "{new_version}"',
        content,
        flags=re.MULTILINE
    )
    
    pyproject_file.write_text(content)
    print(f"Updated {pyproject_file}")


def update_readme(new_version: str) -> None:
    """Update version in README.md."""
    readme_file = Path("README.md")
    if not readme_file.exists():
        print(f"Warning: {readme_file} not found")
        return
        
    content = readme_file.read_text()
    
    # Update version in badge URLs
    content = re.sub(
        r'(version-)([\d.]+)(-blue)',
        rf'\g<1>{new_version}\g<3>',
        content
    )
    
    # Update version in text (e.g., "RepoKit v0.3.0")
    content = re.sub(
        r'(RepoKit v)([\d.]+)',
        rf'\g<1>{new_version}',
        content
    )
    
    # Update version at bottom of README (e.g., "Current Version: 0.2.0")
    content = re.sub(
        r'(\*\*Current Version\*\*: )([\d.]+)',
        rf'\g<1>{new_version}',
        content
    )
    
    # Update version in installation instructions if any
    content = re.sub(
        r'(repokit==)([\d.]+)',
        rf'\g<1>{new_version}',
        content
    )
    
    readme_file.write_text(content)
    print(f"Updated {readme_file}")


def get_current_version() -> str:
    """Get the current version from __version__.py."""
    version_file = Path("repokit/__version__.py")
    content = version_file.read_text()
    
    match = re.search(r'__version__ = "([^"]*)"', content)
    if match:
        return match.group(1)
    else:
        raise ValueError("Could not find version in __version__.py")


def main():
    """Main function."""
    # Change to repository root
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    os.chdir(repo_root)
    
    if len(sys.argv) != 2:
        current = get_current_version()
        print(f"Current version: {current}")
        print(f"Usage: {sys.argv[0]} <new_version>")
        print(f"Example: {sys.argv[0]} 0.4.1")
        sys.exit(1)
    
    new_version = sys.argv[1]
    
    # Validate version format
    if not re.match(r'^\d+\.\d+\.\d+$', new_version):
        print(f"Error: Invalid version format '{new_version}'")
        print("Version must be in format: X.Y.Z (e.g., 0.4.0)")
        sys.exit(1)
    
    print(f"Updating version to {new_version}...")
    
    # Update all files
    update_version_file(new_version)
    update_pyproject_toml(new_version)
    update_readme(new_version)
    
    print(f"\nVersion updated to {new_version}")
    print("\nDon't forget to:")
    print("1. Update CHANGELOG.md with the new version changes")
    print("2. Commit the changes: git add -A && git commit -m 'chore: bump version to " + new_version + "'")
    print("3. Tag the release: git tag v" + new_version)


if __name__ == "__main__":
    main()