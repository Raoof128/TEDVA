# Contributing to Purple Team Validation Framework

First off, thank you for considering contributing to the Purple Team Validation Framework! It's people like you that make this tool better for the security community.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)

---

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

---

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected behavior** vs actual behavior
- **Environment details** (OS, Python version, SIEM platform)
- **Logs and error messages**
- **Screenshots** if applicable

**Example Bug Report:**

```markdown
**Bug:** Sigma rule builder fails with YAML parsing error

**Environment:**
- OS: Ubuntu 22.04
- Python: 3.10.2
- Framework Version: v1.0.0

**Steps to Reproduce:**
1. Run `python sigma_rule_builder.py`
2. Error occurs when processing T1548

**Error Message:**
```
yaml.scanner.ScannerError: mapping values not allowed
```

**Expected:** Rule should generate successfully
**Actual:** Script crashes with YAML error
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear and descriptive title**
- **Detailed description** of the proposed functionality
- **Use case** and rationale
- **Examples** of how it would work
- **Mockups or diagrams** if applicable

### Adding New Detection Rules

We welcome contributions of new Sigma detection rules! To contribute:

1. **Research the technique** thoroughly using MITRE ATT&CK
2. **Create the Sigma rule** following the template in `detection_rules/sigma_rules/`
3. **Test the rule** against sample data
4. **Document false positives** and tuning recommendations
5. **Submit a PR** with the rule and test results

**Rule Template:**

```yaml
title: [Technique Name] Detection
id: [UUID]
status: experimental
description: |
  [Detailed description]
  Developed for Purple Team Validation Framework
author: [Your Name]
date: YYYY/MM/DD
references:
  - https://attack.mitre.org/techniques/[TECHNIQUE_ID]
logsource:
  product: windows
  service: [sysmon/security/etc]
detection:
  selection:
    # Detection logic
  condition: selection
falsepositives:
  - [Known FP scenario 1]
  - [Known FP scenario 2]
level: [low/medium/high/critical]
tags:
  - attack.[technique_id]
  - purple_team_validation
```

### Adding MITRE ATT&CK Techniques

To add new techniques to the test matrix:

1. **Add to `PRIORITY_TACTICS`** in `attack_matrix_builder.py`
2. **Define expected detections** in `_define_expected_detections()`
3. **Update `config.yaml`** priority_techniques list
4. **Test end-to-end** workflow
5. **Update documentation**

---

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment tool (venv, virtualenv, or conda)

### Setup Steps

```bash
# Clone repository
git clone https://github.com/your-org/TEDVA.git
cd TEDVA

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r automation_scripts/requirements.txt
pip install -r requirements-dev.txt  # Development dependencies

# Validate environment
python automation_scripts/validate_environment.py

# Run tests
python -m pytest tests/
```

### Development Tools

We recommend using:
- **IDE:** VS Code, PyCharm, or similar
- **Linting:** pylint, flake8
- **Formatting:** black, autopep8
- **Type Checking:** mypy

---

## Coding Standards

### Python Style Guide

We follow **PEP 8** with these additions:

- **Line length:** 100 characters maximum
- **Indentation:** 4 spaces (no tabs)
- **Docstrings:** Google-style docstrings for all public functions
- **Type hints:** Use type hints for function parameters and returns
- **Imports:** Organized alphabetically, grouped by standard/third-party/local

**Example:**

```python
#!/usr/bin/env python3
"""
Module description.

This module provides...
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd


def process_data(input_file: Path, threshold: int = 10) -> Dict[str, List]:
    """
    Process data from input file.

    Args:
        input_file: Path to input JSON file
        threshold: Minimum threshold for filtering (default: 10)

    Returns:
        Dictionary containing processed results with keys:
        - 'valid': List of valid entries
        - 'invalid': List of invalid entries

    Raises:
        FileNotFoundError: If input_file doesn't exist
        ValueError: If threshold is negative
    """
    if threshold < 0:
        raise ValueError("Threshold must be non-negative")

    # Implementation
    pass
```

### YAML Style Guide

- **Indentation:** 2 spaces
- **Quotes:** Use single quotes for strings (except when double quotes needed)
- **Comments:** Add comments for complex logic
- **Keys:** Use lowercase with underscores (snake_case)

### Sigma Rule Guidelines

- **Follow Sigma specification:** https://github.com/SigmaHQ/sigma-specification
- **Test rules:** Against sample data before submitting
- **Document false positives:** Be comprehensive
- **Use appropriate log sources:** Prefer widely available sources
- **Tag properly:** Include ATT&CK tags and framework tags

---

## Commit Guidelines

We follow the **Conventional Commits** specification.

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat:** New feature
- **fix:** Bug fix
- **docs:** Documentation changes
- **style:** Code style changes (formatting, no logic change)
- **refactor:** Code refactoring
- **perf:** Performance improvements
- **test:** Adding or updating tests
- **chore:** Maintenance tasks

### Examples

```bash
# New feature
feat(sigma): Add T1003 credential dumping detection rule

Added Sigma rule for detecting LSASS credential dumping.
Includes detection for common tools: Mimikatz, ProcDump, Task Manager.
Tested against sample data with <2% FP rate.

Closes #42

# Bug fix
fix(executor): Handle timeout gracefully in atomic_test_executor.py

Previously, timeouts would crash the script. Now catches
TimeoutExpired exception and logs appropriately.

Fixes #38

# Documentation
docs(readme): Update installation instructions for Windows

Clarified PowerShell execution policy requirements and
added troubleshooting section for common Windows issues.
```

### Commit Best Practices

- **One logical change per commit**
- **Write descriptive commit messages**
- **Reference issues** when applicable
- **Keep commits atomic** and reversible
- **Test before committing**

---

## Pull Request Process

### Before Submitting

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow coding standards
   - Add tests for new functionality
   - Update documentation

3. **Test thoroughly**
   ```bash
   python automation_scripts/validate_environment.py
   python -m pytest tests/
   ```

4. **Update CHANGELOG.md**
   Add entry under "Unreleased" section

5. **Commit your changes**
   Follow commit guidelines

### Submitting Pull Request

1. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create PR** on GitHub with:
   - **Clear title** following conventional commits
   - **Description** of changes
   - **Issue reference** if applicable
   - **Testing performed**
   - **Screenshots** if UI changes

3. **PR Template** (auto-filled):

```markdown
## Description
[Describe your changes]

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing Performed
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added for new functionality
- [ ] All tests passing
- [ ] CHANGELOG.md updated
```

### Review Process

- Maintainers will review within **3-5 business days**
- Address review comments promptly
- Ensure CI checks pass
- Squash commits if requested
- Once approved, maintainers will merge

### After Merge

- Delete your feature branch
- Pull latest main branch
- Close related issues if applicable

---

## Development Workflow

### Typical Development Cycle

```bash
# 1. Sync with main
git checkout main
git pull origin main

# 2. Create feature branch
git checkout -b feature/add-linux-support

# 3. Make changes
vim automation_scripts/atomic_test_executor.py

# 4. Test changes
python automation_scripts/validate_environment.py
python -m pytest tests/

# 5. Commit
git add automation_scripts/atomic_test_executor.py
git commit -m "feat(executor): Add Linux platform support"

# 6. Push and create PR
git push origin feature/add-linux-support
# Create PR on GitHub

# 7. Address review comments
# Make changes, commit, push

# 8. After merge, cleanup
git checkout main
git pull origin main
git branch -d feature/add-linux-support
```

---

## Questions?

- **GitHub Issues:** For bugs and feature requests
- **GitHub Discussions:** For questions and general discussion
- **Email:** [maintainer email] for private concerns

---

## Recognition

Contributors will be recognized in:
- **CHANGELOG.md** for each release
- **README.md** contributors section (coming soon)
- **Release notes** on GitHub

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License that covers this project.

---

**Thank you for contributing to Purple Team Validation Framework!** 🎉
