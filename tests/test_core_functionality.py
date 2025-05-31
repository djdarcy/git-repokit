"""
Test core RepoKit functionality.

Unit tests for core components without GitHub deployment.
"""

import unittest
import os
import tempfile
import shutil
import json
from pathlib import Path

from test_utils import RepoKitTestCase

# Import RepoKit modules
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repokit.directory_analyzer import (
    ProjectAnalyzer, 
    GitManager,
    DirectoryAnalyzer
)
from repokit.config import ConfigManager
from repokit.template_engine import TemplateEngine


class TestProjectAnalyzer(unittest.TestCase):
    """Test ProjectAnalyzer functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp(prefix="test_analyzer_")
        self.analyzer = ProjectAnalyzer(self.test_dir)
        
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)
            
    def test_detect_empty_project(self):
        """Test detection of empty project."""
        result = self.analyzer.get_comprehensive_summary()
        
        self.assertEqual(result['project_type'], 'empty')
        self.assertEqual(result['detected_language'], 'generic')
        self.assertFalse(result['has_git_repository'])
        self.assertEqual(result['migration_complexity'], 'low')
        
    def test_detect_python_project(self):
        """Test Python project detection."""
        # Create Python files
        with open(os.path.join(self.test_dir, "main.py"), "w") as f:
            f.write("print('Hello')")
        with open(os.path.join(self.test_dir, "requirements.txt"), "w") as f:
            f.write("requests>=2.0.0")
            
        # Re-analyze after adding files
        self.analyzer = ProjectAnalyzer(self.test_dir)
        result = self.analyzer.get_comprehensive_summary()
        
        self.assertEqual(result['project_type'], 'source_no_git')
        self.assertEqual(result['detected_language'], 'python')
        self.assertGreater(result['total_files'], 0)
        
    def test_detect_javascript_project(self):
        """Test JavaScript project detection."""
        # Create JS files
        with open(os.path.join(self.test_dir, "index.js"), "w") as f:
            f.write("console.log('Hello');")
        with open(os.path.join(self.test_dir, "package.json"), "w") as f:
            f.write('{"name": "test", "version": "1.0.0"}')
            
        # Re-analyze after adding files
        self.analyzer = ProjectAnalyzer(self.test_dir)
        result = self.analyzer.get_comprehensive_summary()
        
        self.assertEqual(result['detected_language'], 'javascript')
        
    def test_migration_recommendation(self):
        """Test migration recommendations."""
        # Empty project
        result = self.analyzer.get_comprehensive_summary()
        
        # For empty projects, it recommends 'create_new'
        self.assertEqual(result['recommended_strategy'], 'create_new')
        self.assertEqual(result['recommended_branch_strategy'], 'standard')


class TestGitManager(unittest.TestCase):
    """Test GitManager functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp(prefix="test_git_")
        self.git_manager = GitManager(self.test_dir)
        
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)
            
    def test_detect_no_git(self):
        """Test detection of non-Git directory."""
        self.assertFalse(self.git_manager.is_git_repo())
        
    def test_detect_git_repo(self):
        """Test detection of Git repository."""
        # Initialize Git repo
        import subprocess
        subprocess.run(["git", "init"], cwd=self.test_dir, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], 
                      cwd=self.test_dir, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], 
                      cwd=self.test_dir, capture_output=True)
        
        # Create initial commit
        with open(os.path.join(self.test_dir, "test.txt"), "w") as f:
            f.write("test")
        subprocess.run(["git", "add", "."], cwd=self.test_dir, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial"], 
                      cwd=self.test_dir, capture_output=True)
        
        self.assertTrue(self.git_manager.is_git_repo())
        
        info = self.git_manager.get_repo_state()
        self.assertTrue(info['is_repo'])
        # Git creates 'master' by default on older systems
        branches = info['branches'] + [info['current_branch']]
        self.assertTrue(any(b in ['master', 'main'] for b in branches))
        
    def test_branch_strategy(self):
        """Test branch strategy detection."""
        # No Git
        strategy = self.git_manager.get_branch_strategy()
        # For non-git repos, it returns 'none'
        self.assertEqual(strategy, 'none')


class TestConfigManager(unittest.TestCase):
    """Test ConfigManager functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp(prefix="test_config_")
        self.config_file = os.path.join(self.test_dir, "test_config.json")
        
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)
            
    def test_default_config(self):
        """Test default configuration values."""
        config_manager = ConfigManager()
        config = config_manager.get_config()
        
        self.assertEqual(config.get("private_branch"), "private")
        self.assertIn("main", config.get("branches"))
        self.assertIn("dev", config.get("branches"))
        
    def test_load_config_file(self):
        """Test loading configuration from file."""
        # Create test config
        test_config = {
            "name": "test-project",
            "branches": ["master", "develop"],
            "custom_value": "test"
        }
        
        with open(self.config_file, "w") as f:
            json.dump(test_config, f)
            
        config_manager = ConfigManager()
        config_manager.load_config_file(self.config_file)
        config = config_manager.get_config()
        
        self.assertEqual(config.get("name"), "test-project")
        self.assertEqual(config.get("branches"), ["master", "develop"])
        self.assertEqual(config.get("custom_value"), "test")
        
    def test_config_merge(self):
        """Test configuration merging."""
        config_manager = ConfigManager()
        
        # Default value
        config = config_manager.get_config()
        self.assertEqual(config.get("private_branch"), "private")
        
        # Override with custom value using set_cli_config
        config_manager.set_cli_config({"private_branch": "secret"})
        config = config_manager.get_config()
        self.assertEqual(config.get("private_branch"), "secret")


class TestTemplateEngine(unittest.TestCase):
    """Test TemplateEngine functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp(prefix="test_template_")
        self.context = {
            "name": "test-project",
            "description": "Test project",
            "language": "python",
            "branches": ["main", "dev"]
        }
        self.engine = TemplateEngine()
        
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)
            
    def test_render_template(self):
        """Test basic template rendering."""
        # TemplateEngine uses string.Template which uses $variable syntax
        template = "Project: $name\nDescription: $description"
        result = self.engine.render_template(template, self.context)
        
        self.assertIn("test-project", result)
        self.assertIn("Test project", result)
        
    def test_template_with_braces(self):
        """Test template rendering with braces."""
        template = "Project: ${name}\nLanguage: ${language}"
        result = self.engine.render_template(template, self.context)
        
        self.assertIn("test-project", result)
        self.assertIn("python", result)
        
    def test_missing_variable(self):
        """Test template with missing variable."""
        # safe_substitute leaves missing variables as-is
        template = "Project: $name\nMissing: $nonexistent"
        result = self.engine.render_template(template, self.context)
        
        self.assertIn("test-project", result)
        self.assertIn("$nonexistent", result)


class TestDirectoryAnalyzer(unittest.TestCase):
    """Test DirectoryAnalyzer functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp(prefix="test_dir_analyzer_")
        
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)
            
    def test_analyze_empty_directory(self):
        """Test analyzing empty directory."""
        from repokit.directory_analyzer import analyze_directory
        stats = analyze_directory(self.test_dir)
        
        # Check that analysis returns expected structure
        self.assertIn("existing_dirs", stats)
        self.assertIn("missing_dirs", stats)
        self.assertIn("has_template_conflicts", stats)
        
    def test_analyze_with_files(self):
        """Test analyzing directory with files."""
        # Create test structure
        os.makedirs(os.path.join(self.test_dir, "src"))
        os.makedirs(os.path.join(self.test_dir, "tests"))
        
        with open(os.path.join(self.test_dir, "README.md"), "w") as f:
            f.write("# Test")
        with open(os.path.join(self.test_dir, "src", "main.py"), "w") as f:
            f.write("print('test')")
        with open(os.path.join(self.test_dir, "tests", "test_main.py"), "w") as f:
            f.write("import unittest")
            
        from repokit.directory_analyzer import analyze_directory
        stats = analyze_directory(self.test_dir)
        
        # Verify the directory was analyzed
        self.assertIn("existing_dirs", stats)
        # tests directory should be detected as existing
        self.assertIn("tests", stats["existing_dirs"])
        
    def test_directory_detection(self):
        """Test detection of RepoKit standard directories."""
        # Create some standard RepoKit directories
        os.makedirs(os.path.join(self.test_dir, "docs"))
        os.makedirs(os.path.join(self.test_dir, "scripts"))
        
        analyzer = DirectoryAnalyzer(self.test_dir)
        
        # Check that standard dirs were detected
        self.assertIn("docs", analyzer.existing_dirs)
        self.assertIn("scripts", analyzer.existing_dirs)
        self.assertIn("private", analyzer.missing_dirs)


if __name__ == "__main__":
    unittest.main()