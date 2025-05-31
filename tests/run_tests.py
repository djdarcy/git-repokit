#!/usr/bin/env python3
"""
RepoKit Test Runner

Run all tests or specific test suites.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --unit             # Run only unit tests
    python run_tests.py --integration      # Run only integration tests
    python run_tests.py --github           # Run only GitHub tests (requires token)
    python run_tests.py --deployment       # Run only deployment tests (requires token)
    python run_tests.py --no-cleanup       # Skip test repository cleanup
    python run_tests.py --verbose          # Verbose output
"""

import sys
import os
import unittest
import argparse
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


def create_test_suite(test_classes):
    """Create a test suite from a list of test classes."""
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
        
    return suite


def run_tests(args):
    """Run the selected tests."""
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
    
    # Run tests
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("\nAll tests passed! ✅")
        return 0
    else:
        print("\nSome tests failed! ❌")
        return 1


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
    return run_tests(args)


if __name__ == "__main__":
    sys.exit(main())