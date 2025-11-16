#!/usr/bin/env python3
"""
Installation Test Script
Verifies that all components are properly installed and working
"""

import sys
import os
from pathlib import Path


def test_python_version():
    """Test Python version"""
    print("Testing Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"  ✗ Python {version.major}.{version.minor} (Need 3.8+)")
        return False


def test_dependencies():
    """Test required dependencies"""
    print("\nTesting dependencies...")
    dependencies = {
        'pandas': 'pandas',
        'requests': 'requests',
        'yaml': 'pyyaml',
        'dotenv': 'python-dotenv',
        'tqdm': 'tqdm',
        'openpyxl': 'openpyxl'
    }

    all_ok = True
    for module, package in dependencies.items():
        try:
            __import__(module)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} (Not installed)")
            all_ok = False

    return all_ok


def test_modules():
    """Test project modules"""
    print("\nTesting project modules...")

    # Add src to path
    sys.path.insert(0, str(Path(__file__).parent / 'src'))

    modules_ok = True

    try:
        from extractor import DataExtractor
        print("  ✓ extractor.py")
    except Exception as e:
        print(f"  ✗ extractor.py ({e})")
        modules_ok = False

    try:
        from filters import DataFilter
        print("  ✓ filters.py")
    except Exception as e:
        print(f"  ✗ filters.py ({e})")
        modules_ok = False

    try:
        from validator import DataValidator
        print("  ✓ validator.py")
    except Exception as e:
        print(f"  ✗ validator.py ({e})")
        modules_ok = False

    try:
        import cli
        print("  ✓ cli.py")
    except Exception as e:
        print(f"  ✗ cli.py ({e})")
        modules_ok = False

    return modules_ok


def test_directories():
    """Test directory structure"""
    print("\nTesting directory structure...")

    directories = ['input', 'output', 'logs', 'config', 'src']
    all_ok = True

    for directory in directories:
        path = Path(directory)
        if path.exists() and path.is_dir():
            print(f"  ✓ {directory}/")
        else:
            print(f"  ✗ {directory}/ (Missing)")
            all_ok = False

    return all_ok


def test_config_files():
    """Test configuration files"""
    print("\nTesting configuration files...")

    files = {
        'config/filters.yaml': 'Filter configuration',
        '.env.example': 'Environment template',
        'requirements.txt': 'Dependencies list'
    }

    all_ok = True

    for filepath, description in files.items():
        path = Path(filepath)
        if path.exists() and path.is_file():
            print(f"  ✓ {filepath} ({description})")
        else:
            print(f"  ✗ {filepath} ({description}) - Missing")
            all_ok = False

    return all_ok


def test_basic_functionality():
    """Test basic functionality"""
    print("\nTesting basic functionality...")

    sys.path.insert(0, str(Path(__file__).parent / 'src'))

    try:
        from extractor import DataExtractor
        from filters import DataFilter
        from validator import DataValidator

        # Test initialization
        extractor = DataExtractor()
        print("  ✓ DataExtractor initialization")

        validator = DataValidator()
        print("  ✓ DataValidator initialization")

        filter_config = {
            'filters': {
                'entity_types': {'enabled': False, 'values': []},
                'status': {'enabled': False, 'values': []}
            },
            'output': {}
        }
        data_filter = DataFilter(filter_config)
        print("  ✓ DataFilter initialization")

        return True

    except Exception as e:
        print(f"  ✗ Functionality test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 70)
    print("BUSINESS DATA EXTRACTION TOOL - INSTALLATION TEST")
    print("=" * 70)

    tests = [
        ("Python Version", test_python_version),
        ("Dependencies", test_dependencies),
        ("Project Modules", test_modules),
        ("Directory Structure", test_directories),
        ("Configuration Files", test_config_files),
        ("Basic Functionality", test_basic_functionality)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\nError in {test_name}: {e}")
            results.append((test_name, False))

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} {test_name}")

    print("-" * 70)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ Installation successful! All tests passed.")
        print("\nNext steps:")
        print("1. Review README.md for usage instructions")
        print("2. Configure config/filters.yaml for your needs")
        print("3. Run: python -m src.cli --help")
        return 0
    else:
        print(f"\n✗ Installation incomplete. {total - passed} test(s) failed.")
        print("\nPlease:")
        print("1. Install missing dependencies: pip install -r requirements.txt")
        print("2. Check file permissions")
        print("3. Review error messages above")
        return 1


if __name__ == '__main__':
    sys.exit(main())
