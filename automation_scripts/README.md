# Automation Scripts

Python automation scripts for the Purple Team Validation Framework.

## Scripts Overview

| Script | Purpose | Input | Output |
|--------|---------|-------|--------|
| **validate_environment.py** | Environment validation | - | Validation report |
| **run_all.py** | Master orchestrator | config.yaml | All outputs |
| **attack_matrix_builder.py** | Build test matrix | config.yaml | test_matrix/*.json |
| **baseline_assessment.py** | Assess coverage | test_matrix/*.json | gap_analysis/*.json |
| **atomic_test_executor.py** | Execute tests | test_matrix/*.json | test_matrix/*.json |
| **gap_analysis_generator.py** | Analyze gaps | test_matrix/*.json | gap_analysis/* |
| **sigma_rule_builder.py** | Generate rules | gap_analysis/*.json | detection_rules/sigma_rules/* |
| **maturity_heatmap.py** | Create visualizations | test_matrix/*.json | visualizations/*.png |

## Quick Start

### 1. Validate Environment

```bash
python validate_environment.py
```

Checks:
- Python version (3.8+)
- Required dependencies
- Directory structure
- Configuration files
- Script syntax

### 2. Run Complete Workflow

```bash
# Full workflow
python run_all.py

# Skip certain phases
python run_all.py --skip-baseline --skip-execution
```

### 3. Run Individual Scripts

```bash
# Build test matrix
python attack_matrix_builder.py

# Assess baseline
python baseline_assessment.py

# Execute tests
python atomic_test_executor.py

# Analyze gaps
python gap_analysis_generator.py

# Build Sigma rules
python sigma_rule_builder.py

# Generate visualizations
python maturity_heatmap.py
```

## Dependencies

Install all dependencies:

```bash
pip install -r requirements.txt
```

**Required:**
- pandas (data processing)
- numpy (numerical operations)
- matplotlib (visualization)
- seaborn (statistical visualization)
- pyyaml (configuration)

**Optional:**
- colorama (colored output)
- tabulate (table formatting)
- tqdm (progress bars)

## Configuration

Edit `../config.yaml` to customize:

- SIEM connection settings
- Test execution parameters
- Detection thresholds
- Output directories
- Visualization settings
- Priority techniques

## Execution Flow

```
validate_environment.py
        ↓
run_all.py (orchestrates all scripts)
        ↓
        ├── attack_matrix_builder.py
        ├── baseline_assessment.py
        ├── atomic_test_executor.py
        ├── gap_analysis_generator.py
        ├── sigma_rule_builder.py
        └── maturity_heatmap.py
```

## Error Handling

All scripts include:
- ✅ Input validation
- ✅ Error handling and recovery
- ✅ Detailed logging
- ✅ Graceful degradation
- ✅ User-friendly error messages

## Logging

Logs are written to:
- **Console:** INFO level and above
- **File:** `atomic_execution.log` (all levels)

Configure log level in `config.yaml`:
```yaml
output:
  log_level: "INFO"  # DEBUG, INFO, WARNING, ERROR
```

## Output Directories

```
../
├── test_matrix/           # Test execution data
├── gap_analysis/          # Analysis results
├── detection_rules/       # Sigma rules
├── visualizations/        # Charts and graphs
└── automation_scripts/    # These scripts
```

## Common Issues

### Import Error

```bash
# Install missing packages
pip install -r requirements.txt
```

### Permission Error

```bash
# Ensure output directories exist
mkdir -p ../test_matrix ../gap_analysis ../detection_rules/sigma_rules ../visualizations
```

### SIEM Connection Error

Check `config.yaml`:
- Correct SIEM type (wazuh, splunk, elk)
- Valid host and port
- Set environment variables for credentials

## Development

### Code Style
- PEP 8 compliant
- Type hints used throughout
- Docstrings for all functions
- Error handling in all critical paths

### Testing

```bash
# Validate syntax
python -m py_compile *.py

# Run validation
python validate_environment.py
```

## Support

For issues or questions:
- See parent README.md
- Check METHODOLOGY.md for workflow details
- Review config.yaml for configuration options

---

**Version:** 1.0.0
**Python:** 3.8+
**Platform:** Cross-platform (Windows, Linux, macOS)
