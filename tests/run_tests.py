#!/usr/bin/env python3
"""
RepoKit Test Runner

Run all tests or specific test suites with organized test runs and cleanup.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --unit             # Run only unit tests
    python run_tests.py --integration      # Run only integration tests
    python run_tests.py --github           # Run only GitHub tests (requires token)
    python run_tests.py --deployment       # Run only deployment tests (requires token)
    python run_tests.py --no-cleanup       # Skip test repository cleanup
    python run_tests.py --keep-run         # Keep test run directory for debugging
    python run_tests.py --verbose          # Verbose output
    python run_tests.py --test-dir DIR     # Specify custom test run directory
"""

import sys
import os
import unittest
import argparse
import shutil
import datetime
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import test modules
from test_core_functionality import (
    TestProjectAnalyzer,
    TestGitManager,
    TestConfigManager,
    TestTemplateEngine,
    TestDirectoryAnalyzer
)
from test_cli_integration import (
    TestCLICommands,
    TestComplexWorkflows,
    TestErrorHandling
)
from test_github_integration import (
    TestGitHubIntegration,
    TestGitHubAPIMocking,
    TestCredentialManagement
)
from test_deployment_scenarios import TestDeploymentScenarios

# Test suite categories
UNIT_TESTS = [
    TestProjectAnalyzer,
    TestGitManager,
    TestConfigManager,
    TestTemplateEngine,
    TestDirectoryAnalyzer,
    TestGitHubAPIMocking
]

INTEGRATION_TESTS = [
    TestCLICommands,
    TestComplexWorkflows,
    TestErrorHandling,
    TestCredentialManagement
]

GITHUB_TESTS = [
    TestGitHubIntegration,
    TestDeploymentScenarios
]

ALL_TESTS = UNIT_TESTS + INTEGRATION_TESTS + GITHUB_TESTS


class TestRunManager:
    """Manages test run directories and cleanup."""
    
    def __init__(self, keep_run=False, custom_dir=None):
        self.keep_run = keep_run
        self.custom_dir = custom_dir
        self.test_run_dir = None
        self.created_dirs = []
        
    def setup_test_run(self):
        """Set up organized test run directory."""
        # Create test_runs base directory
        test_runs_base = Path(__file__).parent.parent / "test_runs"
        test_runs_base.mkdir(exist_ok=True)
        
        if self.custom_dir:
            self.test_run_dir = Path(self.custom_dir)
            self.test_run_dir.mkdir(parents=True, exist_ok=True)
        else:
            # Create timestamped directory
            timestamp = datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S")
            self.test_run_dir = test_runs_base / f"test_run_{timestamp}"
            self.test_run_dir.mkdir(exist_ok=True)
        
        # Set environment variable for tests to use
        os.environ['REPOKIT_TEST_RUN_DIR'] = str(self.test_run_dir)
        
        print(f"Test run directory: {self.test_run_dir}")
        return self.test_run_dir
    
    def cleanup_test_run(self):
        """Clean up test run directory unless keep_run is True."""
        if self.keep_run:
            print(f"Keeping test run directory: {self.test_run_dir}")
            return
            
        if self.test_run_dir and self.test_run_dir.exists():
            try:
                shutil.rmtree(self.test_run_dir)
                print(f"Cleaned up test run directory: {self.test_run_dir}")
            except Exception as e:
                print(f"Warning: Failed to clean up {self.test_run_dir}: {e}")
    
    def cleanup_old_test_runs(self, keep_recent=5):
        """Clean up old test run directories, keeping only the most recent ones."""
        test_runs_base = Path(__file__).parent.parent / "test_runs"
        if not test_runs_base.exists():
            return
            
        # Get all test run directories
        test_dirs = []
        for item in test_runs_base.iterdir():
            if item.is_dir() and item.name.startswith("test_run_"):
                test_dirs.append(item)
        
        # Sort by creation time (newest first)
        test_dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Remove old directories
        for old_dir in test_dirs[keep_recent:]:
            try:
                shutil.rmtree(old_dir)
                print(f"Cleaned up old test run: {old_dir.name}")
            except Exception as e:
                print(f"Warning: Failed to clean up {old_dir}: {e}")


def create_test_suite(test_classes):
    """Create a test suite from a list of test classes."""
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
        
    return suite


def run_tests(args):
    """Run the selected tests with organized test run management."""
    # Set up test run manager
    test_run_manager = TestRunManager(
        keep_run=args.keep_run,
        custom_dir=getattr(args, 'test_dir', None)
    )
    
    try:
        # Set up test run directory
        test_run_dir = test_run_manager.setup_test_run()
        
        # Clean up old test runs
        if not args.keep_run:
            test_run_manager.cleanup_old_test_runs()
        
        # Determine which tests to run
        if args.unit:
            test_classes = UNIT_TESTS
            print("Running unit tests...")
        elif args.integration:
            test_classes = INTEGRATION_TESTS
            print("Running integration tests...")
        elif args.github:
            test_classes = GITHUB_TESTS
            print("Running GitHub tests (requires token)...")
        elif args.deployment:
            test_classes = [TestDeploymentScenarios]
            print("Running deployment scenario tests...")
        else:
            test_classes = ALL_TESTS
            print("Running all tests...")
            
        # Set cleanup environment variable
        if args.no_cleanup:
            os.environ['REPOKIT_TEST_CLEANUP'] = 'false'
            print("Test cleanup disabled - repositories will remain on GitHub")
            
        # Create and run test suite
        suite = create_test_suite(test_classes)
        
        # Configure runner
        verbosity = 2 if args.verbose else 1
        runner = unittest.TextTestRunner(verbosity=verbosity)
        
        print(f"\nStarting tests in: {test_run_dir}")
        print("=" * 70)
        
        # Run tests
        result = runner.run(suite)
        
        print("=" * 70)
        print(f"Test run completed. Directory: {test_run_dir}")
        
        # Print summary
        print("\n" + "="*70)
        print("Test Summary:")
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        print(f"Skipped: {len(result.skipped)}")
        
        if result.wasSuccessful():
            print("\nAll tests passed! ✅")
            return_code = 0
        else:
            print("\nSome tests failed! ❌")
            return_code = 1
            
        return result, return_code
        
    finally:
        # Clean up test run unless keeping it
        test_run_manager.cleanup_test_run()


def check_environment():
    """Check test environment setup."""
    print("Checking test environment...")
    
    # Check for test token
    env_file = Path(__file__).parent.parent / '.env.test'
    if env_file.exists():
        print("✓ Found .env.test file")
        
        # Load and check token
        from dotenv import load_dotenv
        load_dotenv(env_file)
        
        if os.environ.get('REPOKIT_TEST_GITHUB_TOKEN'):
            print("✓ GitHub token configured")
        else:
            print("✗ No GitHub token found in .env.test")
            print("  GitHub tests will be skipped")
    else:
        print("✗ No .env.test file found")
        print("  Create .env.test with REPOKIT_TEST_GITHUB_TOKEN to run GitHub tests")
        
    # Check Python version
    print(f"✓ Python version: {sys.version.split()[0]}")
    
    # Check if RepoKit is installed
    try:
        import repokit
        print("✓ RepoKit module found")
    except ImportError:
        print("✗ RepoKit not installed")
        print("  Run: pip install -e .")
        
    print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run RepoKit test suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # Test selection
    parser.add_argument(
        "--unit", 
        action="store_true",
        help="Run only unit tests"
    )
    parser.add_argument(
        "--integration",
        action="store_true", 
        help="Run only integration tests"
    )
    parser.add_argument(
        "--github",
        action="store_true",
        help="Run only GitHub API tests (requires token)"
    )
    parser.add_argument(
        "--deployment",
        action="store_true",
        help="Run only deployment scenario tests"
    )
    
    # Options
    parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Skip cleanup of test repositories on GitHub"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose test output"
    )
    parser.add_argument(
        "--keep-run",
        action="store_true",
        help="Keep test run directory for debugging"
    )
    parser.add_argument(
        "--test-dir",
        help="Specify custom test run directory"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check test environment setup"
    )
    
    args = parser.parse_args()
    
    # Check environment if requested
    if args.check:
        check_environment()
        return 0
        
    # Run tests
    check_environment()
    test_result, exit_code = run_tests(args)
    
    # Return the exit code from test execution
    return exit_code


if __name__ == "__main__":
    sys.exit(main())