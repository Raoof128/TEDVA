#!/usr/bin/env python3
"""
Environment Validation Script
Checks that all dependencies and configuration are correct before running tests
"""

import sys
import os
from pathlib import Path


def check_python_version():
    """Check Python version"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✓ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"   ✗ Python {version.major}.{version.minor}.{version.micro} (Need 3.8+)")
        return False


def check_dependencies():
    """Check required Python packages"""
    print("\n📦 Checking Python dependencies...")

    required_packages = {
        'pandas': 'pandas',
        'numpy': 'numpy',
        'matplotlib': 'matplotlib',
        'seaborn': 'seaborn',
        'yaml': 'pyyaml'
    }

    all_ok = True
    for module_name, package_name in required_packages.items():
        try:
            __import__(module_name)
            print(f"   ✓ {package_name}")
        except ImportError:
            print(f"   ✗ {package_name} (Missing - run: pip install {package_name})")
            all_ok = False

    return all_ok


def check_directory_structure():
    """Check required directories exist"""
    print("\n📁 Checking directory structure...")

    required_dirs = [
        'automation_scripts',
        'test_matrix',
        'gap_analysis',
        'detection_rules/sigma_rules',
        'siem_integration',
        'documentation',
        'visualizations'
    ]

    all_ok = True
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"   ✓ {dir_path}")
        else:
            print(f"   ✗ {dir_path} (Missing)")
            all_ok = False

    return all_ok


def check_config_file():
    """Check config file exists and is valid"""
    print("\n⚙️  Checking configuration file...")

    config_path = Path("config.yaml")
    if not config_path.exists():
        print("   ⚠️  config.yaml not found (optional)")
        return True

    try:
        import yaml
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        required_keys = ['siem', 'execution', 'detection', 'output']
        missing = [k for k in required_keys if k not in config]

        if missing:
            print(f"   ⚠️  config.yaml missing keys: {', '.join(missing)}")
            return True  # Non-fatal
        else:
            print("   ✓ config.yaml (Valid)")
            return True
    except Exception as e:
        print(f"   ⚠️  config.yaml error: {e}")
        return True  # Non-fatal


def check_scripts():
    """Check all main scripts exist"""
    print("\n📜 Checking automation scripts...")

    required_scripts = [
        'automation_scripts/attack_matrix_builder.py',
        'automation_scripts/baseline_assessment.py',
        'automation_scripts/atomic_test_executor.py',
        'automation_scripts/gap_analysis_generator.py',
        'automation_scripts/sigma_rule_builder.py',
        'automation_scripts/maturity_heatmap.py'
    ]

    all_ok = True
    for script_path in required_scripts:
        if Path(script_path).exists():
            print(f"   ✓ {Path(script_path).name}")
        else:
            print(f"   ✗ {script_path} (Missing)")
            all_ok = False

    return all_ok


def check_syntax():
    """Check Python syntax of all scripts"""
    print("\n🔍 Checking Python syntax...")

    import py_compile

    script_dir = Path('automation_scripts')
    py_files = list(script_dir.glob('*.py'))
    py_files = [f for f in py_files if f.name != '__pycache__']

    all_ok = True
    for py_file in py_files:
        if py_file.name.startswith('__'):
            continue
        try:
            py_compile.compile(str(py_file), doraise=True)
            print(f"   ✓ {py_file.name}")
        except py_compile.PyCompileError as e:
            print(f"   ✗ {py_file.name}: {e}")
            all_ok = False

    return all_ok


def print_summary(results):
    """Print validation summary"""
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)

    passed = sum(results.values())
    total = len(results)

    for check, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} | {check}")

    print("=" * 70)
    print(f"Result: {passed}/{total} checks passed")

    if passed == total:
        print("\n✅ Environment validation PASSED - Ready to run!")
        print("\nNext steps:")
        print("  1. Review config.yaml and customize for your environment")
        print("  2. Run: python automation_scripts/attack_matrix_builder.py")
        print("  3. Run: python automation_scripts/run_all.py")
        return 0
    else:
        print("\n❌ Environment validation FAILED - Fix issues above")
        print("\nCommon fixes:")
        print("  • Install dependencies: pip install -r automation_scripts/requirements.txt")
        print("  • Check directory structure matches repository layout")
        return 1


def main():
    """Run all validation checks"""
    print("=" * 70)
    print("PURPLE TEAM VALIDATION FRAMEWORK - ENVIRONMENT CHECK")
    print("=" * 70)

    # Change to repo root if in automation_scripts
    if Path.cwd().name == 'automation_scripts':
        os.chdir('..')

    results = {
        'Python Version': check_python_version(),
        'Dependencies': check_dependencies(),
        'Directory Structure': check_directory_structure(),
        'Configuration': check_config_file(),
        'Scripts Present': check_scripts(),
        'Syntax Check': check_syntax()
    }

    return print_summary(results)


if __name__ == "__main__":
    sys.exit(main())
