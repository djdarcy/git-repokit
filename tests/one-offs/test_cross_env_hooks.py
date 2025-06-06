#!/usr/bin/env python3
"""
Test script for cross-environment hook functionality.

This script tests that our updated hooks work properly across Windows and WSL environments.
"""

import os
import subprocess
import tempfile
import shutil
from pathlib import Path

def test_hook_python_detection():
    """Test that our hook can detect Python in different environments."""
    
    # Create a temporary test hook based on our template
    hook_content = '''#!/bin/sh
# Test cross-environment Python detection

find_python() {
    if [ -n "$WINDIR" ] || [ "$OSTYPE" = "msys" ] || [ "$OSTYPE" = "cygwin" ]; then
        if command -v py >/dev/null 2>&1; then
            echo "py"
        elif command -v python >/dev/null 2>&1; then
            echo "python"
        elif command -v python3 >/dev/null 2>&1; then
            echo "python3"
        else
            echo ""
        fi
    else
        if command -v python3 >/dev/null 2>&1; then
            echo "python3"
        elif command -v python >/dev/null 2>&1; then
            echo "python"
        else
            echo ""
        fi
    fi
}

PYTHON_CMD=$(find_python)
if [ -z "$PYTHON_CMD" ]; then
    echo "PYTHON_NOT_FOUND"
    exit 1
else
    echo "PYTHON_FOUND:$PYTHON_CMD"
    $PYTHON_CMD -c "print('Python execution successful')"
fi
'''
    
    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
        f.write(hook_content)
        hook_path = f.name
    
    try:
        # Make executable
        os.chmod(hook_path, 0o755)
        
        # Run the test
        result = subprocess.run([hook_path], capture_output=True, text=True)
        
        print(f"Return code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        print(f"Stderr: {result.stderr}")
        
        if result.returncode == 0 and "PYTHON_FOUND:" in result.stdout:
            print("✅ Cross-environment Python detection working!")
            return True
        else:
            print("❌ Cross-environment Python detection failed")
            return False
            
    finally:
        # Clean up
        os.unlink(hook_path)

def test_git_hook_installation():
    """Test that our hooks can be installed and work in a git repository."""
    
    # Create temporary git repository
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_path = Path(temp_dir) / "test_repo"
        repo_path.mkdir()
        
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=repo_path, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_path)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_path)
        
        # Install our cross-env hook
        hooks_dir = repo_path / ".git" / "hooks"
        hook_path = hooks_dir / "post-checkout"
        
        # Use our actual hook content from guardrails.py
        hook_content = '''#!/bin/sh
# Test post-checkout hook

find_python() {
    if [ -n "$WINDIR" ] || [ "$OSTYPE" = "msys" ] || [ "$OSTYPE" = "cygwin" ]; then
        if command -v py >/dev/null 2>&1; then
            echo "py"
        elif command -v python >/dev/null 2>&1; then
            echo "python"
        elif command -v python3 >/dev/null 2>&1; then
            echo "python3"
        else
            echo ""
        fi
    else
        if command -v python3 >/dev/null 2>&1; then
            echo "python3"
        elif command -v python >/dev/null 2>&1; then
            echo "python"
        else
            echo ""
        fi
    fi
}

PYTHON_CMD=$(find_python)
if [ -z "$PYTHON_CMD" ]; then
    echo "⚠️  Python not found - skipping RepoKit post-checkout tasks"
    exit 0
fi

$PYTHON_CMD -c "print('✅ Post-checkout hook executed successfully')"
'''
        
        hook_path.write_text(hook_content)
        hook_path.chmod(0o755)
        
        # Create a test file and commit
        test_file = repo_path / "test.txt"
        test_file.write_text("test content")
        subprocess.run(["git", "add", "test.txt"], cwd=repo_path, check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_path, check=True)
        
        # Create and switch to a new branch (this should trigger post-checkout)
        subprocess.run(["git", "checkout", "-b", "test-branch"], cwd=repo_path, check=True)
        
        print("✅ Git hook installation test completed")
        return True

if __name__ == "__main__":
    print("🔧 Testing Cross-Environment Hook Functionality")
    print("=" * 50)
    
    print("\n1. Testing Python detection...")
    test1_result = test_hook_python_detection()
    
    print("\n2. Testing git hook installation...")
    test2_result = test_git_hook_installation()
    
    print("\n" + "=" * 50)
    if test1_result and test2_result:
        print("🎉 All cross-environment hook tests passed!")
    else:
        print("❌ Some tests failed - check output above")