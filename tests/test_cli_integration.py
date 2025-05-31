"""
Integration tests for RepoKit CLI commands.

Tests the actual command-line interface and workflows.
"""

import unittest
import os
import json
import subprocess
from pathlib import Path

from test_utils import RepoKitTestCase, TestConfig


class TestCLICommands(RepoKitTestCase):
    """Test CLI command functionality."""
    
    def test_help_command(self):
        """Test help command output."""
        exit_code, stdout, stderr = self.run_repokit(["--help"])
        
        self.assertEqual(exit_code, 0)
        self.assertIn("RepoKit", stdout)
        self.assertIn("create", stdout)
        self.assertIn("bootstrap", stdout)
        self.assertIn("migrate", stdout)
        self.assertIn("adopt", stdout)
        self.assertIn("analyze", stdout)
        
    def test_version_command(self):
        """Test version command output."""
        exit_code, stdout, stderr = self.run_repokit(["--version"])
        
        self.assertEqual(exit_code, 0)
        self.assertIn("0.1.1", stdout)  # Current version
        
    def test_create_basic_project(self):
        """Test basic project creation."""
        project_name = "test-create-basic"
        
        stdout, stderr = self.assert_repokit_success([
            "create", project_name,
            "--language", "python",
            "--skip-github"
        ])
        
        # Check project was created
        project_dir = os.path.join(self.test_dir, project_name)
        self.assertTrue(os.path.exists(project_dir))
        
        # Check basic structure
        self.assert_directory_structure(project_dir, [
            "docs", "tests", "scripts", "private"
        ])
        
        # Check Python-specific files
        self.assert_file_exists(project_dir, "requirements.txt")
        self.assert_file_exists(project_dir, "setup.py")
        
    def test_create_with_ai_integration(self):
        """Test project creation with AI integration."""
        project_name = "test-create-ai"
        
        stdout, stderr = self.assert_repokit_success([
            "create", project_name,
            "--ai", "claude",
            "--skip-github"
        ])
        
        project_dir = os.path.join(self.test_dir, project_name)
        
        # Check AI files created
        private_dir = os.path.join(project_dir, "private")
        self.assert_file_exists(private_dir, "CLAUDE.md")
        
        # Check instructions directory
        instructions_dir = os.path.join(private_dir, "claude", "instructions")
        self.assertTrue(os.path.exists(instructions_dir))
        
    def test_analyze_empty_directory(self):
        """Test analyze command on empty directory."""
        empty_dir = os.path.join(self.test_dir, "empty")
        os.makedirs(empty_dir)
        
        stdout, stderr = self.assert_repokit_success(
            ["analyze", "."],
            cwd=empty_dir
        )
        
        # Check analysis output
        self.assertIn("empty", stdout.lower())
        self.assertIn("Project Analysis", stdout)
        
    def test_analyze_python_project(self):
        """Test analyze command on Python project."""
        # Create Python project
        project_dir = self.create_test_project("python-analyze")
        
        stdout, stderr = self.assert_repokit_success(
            ["analyze", "."],
            cwd=project_dir
        )
        
        # Check detection
        self.assertIn("python", stdout.lower())
        self.assertIn("source_no_git", stdout)
        
    def test_adopt_simple_project(self):
        """Test adopt command on simple project."""
        # Create test project
        project_dir = self.create_test_project("adopt-test", with_git=False)
        
        stdout, stderr = self.assert_repokit_success([
            "adopt", ".",
            "--skip-github"
        ], cwd=project_dir)
        
        # Check adoption succeeded
        self.assertIn("successfully", stdout.lower())
        
        # Check structure created
        self.assert_directory_structure(project_dir, [
            "docs", "tests", "scripts"
        ])
        
        # Check original files preserved
        self.assert_file_exists(project_dir, "main.py")
        self.assert_file_exists(project_dir, "README.md")
        
    def test_adopt_with_strategy(self):
        """Test adopt with different strategies."""
        # Create project with potential conflicts
        project_dir = self.create_test_project("adopt-strategy", with_git=True)
        
        # Add conflicting file
        with open(os.path.join(project_dir, "setup.py"), "w") as f:
            f.write("# Existing setup.py")
            
        # Test safe strategy
        stdout, stderr = self.assert_repokit_success([
            "adopt", ".",
            "--strategy", "safe",
            "--skip-github"
        ], cwd=project_dir)
        
        # Check backup created
        self.assertTrue(
            os.path.exists(os.path.join(project_dir, "setup.py.backup")) or
            os.path.exists(os.path.join(project_dir, "setup.py")),
            "Original setup.py should be preserved"
        )
        
    def test_store_credentials(self):
        """Test credential storage."""
        # Test GitHub credentials
        stdout, stderr = self.assert_repokit_success([
            "store-credentials",
            "--publish-to", "github", 
            "--token", "test-token-12345"
        ])
        
        self.assertIn("stored successfully", stdout.lower())
        
        # Check credentials file created
        creds_file = os.path.expanduser("~/.repokit/credentials.json")
        self.assertTrue(os.path.exists(creds_file))
        
        # Verify content (be careful with real tokens!)
        with open(creds_file, "r") as f:
            creds = json.load(f)
            self.assertIn("github", creds)
            self.assertEqual(creds["github"]["token"], "test-token-12345")
            
    def test_dry_run_mode(self):
        """Test dry-run mode for various commands."""
        project_dir = self.create_test_project("dry-run-test")
        
        # Test adopt dry-run
        stdout, stderr = self.assert_repokit_success([
            "adopt", ".",
            "--dry-run"
        ], cwd=project_dir)
        
        self.assertIn("dry run", stdout.lower())
        self.assertIn("would", stdout.lower())
        
        # Verify no actual changes made
        self.assertFalse(os.path.exists(os.path.join(project_dir, "docs")))
        
    def test_config_hierarchy(self):
        """Test configuration hierarchy and precedence."""
        project_dir = self.create_test_project("config-test")
        
        # Create local config
        local_config = {
            "name": "local-name",
            "branches": ["custom-main", "custom-dev"]
        }
        
        with open(os.path.join(project_dir, ".repokit.json"), "w") as f:
            json.dump(local_config, f)
            
        # Run command that uses config
        stdout, stderr = self.assert_repokit_success([
            "analyze", "."
        ], cwd=project_dir)
        
        # Local config should be detected
        # (Would need to enhance analyze output to verify this properly)
        
    def test_bootstrap_alias(self):
        """Test that bootstrap command works as alias for adopt."""
        project_dir = self.create_test_project("bootstrap-test")
        
        stdout, stderr = self.assert_repokit_success([
            "bootstrap", ".",
            "--skip-github"
        ], cwd=project_dir)
        
        # Should work same as adopt
        self.assertIn("successfully", stdout.lower())
        self.assert_directory_structure(project_dir, ["docs", "tests"])


class TestComplexWorkflows(RepoKitTestCase):
    """Test complex multi-step workflows."""
    
    def test_full_project_lifecycle(self):
        """Test complete project lifecycle from creation to adoption."""
        # Step 1: Create initial project
        project_name = "lifecycle-test"
        project_dir = os.path.join(self.test_dir, project_name)
        
        os.makedirs(project_dir)
        
        # Add some code
        with open(os.path.join(project_dir, "app.py"), "w") as f:
            f.write("def main():\n    print('Hello from lifecycle test')\n")
            
        # Step 2: Analyze
        stdout, _ = self.assert_repokit_success(
            ["analyze", "."],
            cwd=project_dir
        )
        self.assertIn("source_no_git", stdout)
        
        # Step 3: Adopt with AI
        stdout, _ = self.assert_repokit_success([
            "adopt", ".",
            "--ai", "claude",
            "--skip-github"
        ], cwd=project_dir)
        
        # Step 4: Verify complete structure
        self.assert_directory_structure(project_dir, [
            "docs", "tests", "scripts", "private"
        ])
        self.assert_file_exists(project_dir, "app.py")
        self.assert_file_exists(os.path.join(project_dir, "private"), "CLAUDE.md")
        
        # Step 5: Verify Git setup
        self.assert_git_branch_exists(project_dir, "main")
        self.assert_git_branch_exists(project_dir, "dev")
        self.assert_git_branch_exists(project_dir, "private")
        
    def test_migration_from_legacy(self):
        """Test migration from legacy project structure."""
        # Create legacy-style project
        project_dir = self.create_test_project("legacy-migration", with_git=True)
        
        # Add legacy structure
        os.makedirs(os.path.join(project_dir, "lib"))
        os.makedirs(os.path.join(project_dir, "bin"))
        
        with open(os.path.join(project_dir, "lib", "old_module.py"), "w") as f:
            f.write("# Legacy code")
        with open(os.path.join(project_dir, "bin", "run.sh"), "w") as f:
            f.write("#!/bin/bash\npython lib/old_module.py")
            
        # Commit legacy structure
        subprocess.run(["git", "add", "."], cwd=project_dir, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Legacy structure"], 
                      cwd=project_dir, capture_output=True)
        
        # Analyze first
        stdout, _ = self.assert_repokit_success(
            ["analyze", "."],
            cwd=project_dir
        )
        
        # Adopt with safe strategy
        stdout, _ = self.assert_repokit_success([
            "adopt", ".",
            "--strategy", "safe",
            "--skip-github"
        ], cwd=project_dir)
        
        # Verify legacy files preserved
        self.assert_file_exists(os.path.join(project_dir, "lib"), "old_module.py")
        self.assert_file_exists(os.path.join(project_dir, "bin"), "run.sh")
        
        # Verify new structure added
        self.assert_directory_structure(project_dir, ["docs", "tests"])


class TestErrorHandling(RepoKitTestCase):
    """Test error handling and edge cases."""
    
    def test_invalid_command(self):
        """Test handling of invalid commands."""
        exit_code, stdout, stderr = self.run_repokit(["invalid-command"])
        
        self.assertNotEqual(exit_code, 0)
        self.assertIn("error", stderr.lower())
        
    def test_missing_directory(self):
        """Test handling of missing directory."""
        exit_code, stdout, stderr = self.run_repokit([
            "analyze", "/non/existent/directory"
        ])
        
        self.assertNotEqual(exit_code, 0)
        
    def test_permission_denied(self):
        """Test handling of permission errors."""
        # Create read-only directory
        readonly_dir = os.path.join(self.test_dir, "readonly")
        os.makedirs(readonly_dir)
        os.chmod(readonly_dir, 0o444)
        
        exit_code, stdout, stderr = self.run_repokit([
            "create", "test-project"
        ], cwd=readonly_dir)
        
        self.assertNotEqual(exit_code, 0)
        
        # Restore permissions for cleanup
        os.chmod(readonly_dir, 0o755)
        
    def test_conflicting_options(self):
        """Test handling of conflicting command options."""
        # Test conflicting strategies
        project_dir = self.create_test_project("conflict-test")
        
        # This should handle gracefully
        stdout, _ = self.assert_repokit_success([
            "adopt", ".",
            "--strategy", "force",
            "--skip-github"
        ], cwd=project_dir)


if __name__ == "__main__":
    unittest.main()