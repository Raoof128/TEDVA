# Examples

Sample outputs and example files for the Purple Team Validation Framework.

## Contents

### Sample Data Files

- **`sample_test_matrix.json`**: Example test matrix with 2 techniques
- **`sample_gap_analysis.json`**: Example gap analysis report
- **`outputs/`**: Sample visualization outputs (screenshots)

## Using Example Files

### Testing the Framework

Use example files to test the framework without running actual atomic tests:

```bash
# Copy example file to test_matrix directory
cp examples/sample_test_matrix.json test_matrix/attack_test_matrix.json

# Run gap analysis using sample data
python automation_scripts/gap_analysis_generator.py
```

### Understanding Output Format

Example files show the expected output format for each phase:

1. **Test Matrix** (`sample_test_matrix.json`)
   - Technique definitions
   - Expected detections
   - Priority and tactic mappings

2. **Gap Analysis** (`sample_gap_analysis.json`)
   - Detected/undetected/partial techniques
   - Risk assessment
   - Remediation recommendations

### Visualizations

The `outputs/` directory contains example visualizations:

- Detection maturity heatmap
- Coverage breakdown charts
- Gap severity analysis

## Creating Your Own Examples

To generate your own example outputs:

```bash
# Run complete workflow
python automation_scripts/run_all.py

# Copy outputs to examples
cp test_matrix/test_execution_results.json examples/my_execution_results.json
cp gap_analysis/gap_analysis_report.json examples/my_gap_analysis.json
cp visualizations/*.png examples/outputs/
```

## Example Configurations

See `../config.yaml` for example configuration settings.

## Example Sigma Rules

See `../detection_rules/sigma_rules/` for example detection rules:

- T1059.001 - PowerShell execution
- T1548 - UAC bypass
- T1562 - Impair defenses

## Questions?

For questions about examples or output formats, see:
- [README.md](../README.md) - Main documentation
- [USAGE_EXAMPLES.md](../USAGE_EXAMPLES.md) - Usage examples
- [METHODOLOGY.md](../METHODOLOGY.md) - Testing methodology
