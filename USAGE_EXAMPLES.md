# Usage Examples - Purple Team Validation Framework

Quick reference guide with practical examples for common use cases.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Common Workflows](#common-workflows)
3. [Advanced Usage](#advanced-usage)
4. [Troubleshooting](#troubleshooting)

---

## Quick Start

### 1. First-Time Setup

```bash
# Clone and setup
git clone <repository-url>
cd TEDVA

# Validate environment
python automation_scripts/validate_environment.py

# Install dependencies
pip install -r automation_scripts/requirements.txt

# Edit configuration
nano config.yaml  # Update SIEM settings
```

### 2. Run Complete Workflow

```bash
# Execute all phases automatically
python automation_scripts/run_all.py
```

**What this does:**
- Builds MITRE ATT&CK test matrix
- Assesses baseline detection coverage
- Executes atomic tests (if not skipped)
- Analyzes detection gaps
- Generates Sigma rules
- Creates visualizations

---

## Common Workflows

### Workflow 1: Full Validation with Test Execution

```bash
# Run everything (recommended for first time)
python automation_scripts/run_all.py
```

### Workflow 2: Analysis Only (No Test Execution)

```bash
# Skip actual test execution, use existing results
python automation_scripts/run_all.py --skip-execution
```

**Use case:** When you have test results and want to re-analyze

### Workflow 3: Quick Assessment (Skip Baseline & Visualization)

```bash
# Fast mode - core analysis only
python automation_scripts/run_all.py --skip-baseline --skip-visualization
```

**Use case:** Quick gap analysis during iterative development

### Workflow 4: Manual Step-by-Step

```bash
cd automation_scripts

# Step 1: Build test matrix
python attack_matrix_builder.py

# Step 2: Assess current coverage
python baseline_assessment.py

# Step 3: Execute tests
python atomic_test_executor.py

# Step 4: Analyze gaps
python gap_analysis_generator.py

# Step 5: Build detection rules
python sigma_rule_builder.py

# Step 6: Visualize results
python maturity_heatmap.py
```

**Use case:** Fine-grained control, debugging, educational

---

## Advanced Usage

### Custom Configuration

```yaml
# config.yaml - customize for your environment
siem:
  type: "wazuh"      # Change to: splunk, elk
  host: "10.0.0.20"  # Your SIEM IP
  port: 55000

execution:
  dry_run: false     # Set to true for simulation
  wait_time: 5       # Seconds between tests

detection:
  min_events_detected: 3       # Adjust threshold
  min_confidence_detected: 80  # Detection confidence
```

### Environment Variables

```bash
# Set SIEM credentials via environment
export SIEM_USERNAME="atomic_user"
export SIEM_PASSWORD="SecurePassword123"

# Run with env vars
python automation_scripts/run_all.py
```

### Filtering Specific Techniques

Edit `config.yaml`:

```yaml
priority_techniques:
  - T1059.001  # PowerShell only
  - T1548      # UAC bypass only
```

Then run:

```bash
python automation_scripts/attack_matrix_builder.py
python automation_scripts/atomic_test_executor.py
```

### Custom Output Directories

```yaml
output:
  test_matrix_dir: "custom/test_results"
  gap_analysis_dir: "custom/analysis"
  detection_rules_dir: "custom/sigma_rules"
  visualizations_dir: "custom/charts"
```

---

## Example: Weekly Automated Testing

### Using Cron (Linux)

```bash
# Add to crontab
crontab -e

# Run every Monday at 2 AM
0 2 * * 1 cd /path/to/TEDVA && python automation_scripts/run_all.py --skip-baseline >> /var/log/purple_team.log 2>&1
```

### Using Windows Task Scheduler

```powershell
# Create scheduled task
$action = New-ScheduledTaskAction -Execute 'python.exe' -Argument 'C:\TEDVA\automation_scripts\run_all.py'
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 2am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "PurpleTeamValidation" -Description "Weekly atomic test validation"
```

### Using Kubernetes CronJob

```bash
# Deploy to Kubernetes
kubectl apply -f siem_integration/atomic_test_scheduler.yaml

# Check job status
kubectl get cronjobs -n security-testing

# View logs
kubectl logs -n security-testing -l app=atomic-red-team
```

---

## Troubleshooting

### Issue: Module Import Errors

```bash
# Verify Python path
python -c "import sys; print(sys.path)"

# Install missing modules
pip install -r automation_scripts/requirements.txt

# Run from project root
cd /path/to/TEDVA
python automation_scripts/run_all.py
```

### Issue: SIEM Connection Failed

```bash
# Test SIEM connectivity
ping 10.0.0.20

# Check config
cat config.yaml | grep -A 5 "siem:"

# Test with curl (Wazuh example)
curl -u user:pass -k -X GET "https://10.0.0.20:55000/"
```

### Issue: Permission Denied

```bash
# Make scripts executable
chmod +x automation_scripts/*.py

# Or run with python explicitly
python automation_scripts/run_all.py
```

### Issue: No Test Results

```bash
# Check if test matrix exists
ls -lh test_matrix/attack_test_matrix.json

# Re-build matrix
python automation_scripts/attack_matrix_builder.py

# Check dry_run mode
grep "dry_run:" config.yaml
# Should be: dry_run: false
```

### Issue: Visualizations Not Generated

```bash
# Install visualization dependencies
pip install matplotlib seaborn

# Verify installation
python -c "import matplotlib; import seaborn; print('OK')"

# Generate manually
python automation_scripts/maturity_heatmap.py
```

---

## Example: Integrating with CI/CD

### GitHub Actions

```yaml
name: Purple Team Validation
on:
  schedule:
    - cron: '0 2 * * 1'  # Weekly Monday 2 AM

jobs:
  validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      
      - name: Install dependencies
        run: pip install -r automation_scripts/requirements.txt
      
      - name: Validate environment
        run: python automation_scripts/validate_environment.py
      
      - name: Run validation
        run: python automation_scripts/run_all.py --skip-execution
        env:
          SIEM_USERNAME: ${{ secrets.SIEM_USERNAME }}
          SIEM_PASSWORD: ${{ secrets.SIEM_PASSWORD }}
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v2
        with:
          name: purple-team-results
          path: |
            gap_analysis/
            visualizations/
```

---

## Example Outputs

### Successful Run

```
======================================================================
PURPLE TEAM VALIDATION FRAMEWORK - FULL WORKFLOW
======================================================================
Started: 2025-01-15 02:00:00

======================================================================
▶  PHASE 1: Build MITRE ATT&CK Test Matrix
======================================================================
🔨 Building MITRE ATT&CK test matrix...
✓ Test matrix generated: 45 techniques
✅ PHASE 1: Build MITRE ATT&CK Test Matrix - COMPLETED

[... more phases ...]

======================================================================
WORKFLOW EXECUTION SUMMARY
======================================================================
Duration:    00:15:32

Phase Results:
  ✅ PASS       | Test Matrix Generation
  ✅ PASS       | Baseline Assessment
  ⊙ SKIPPED    | Atomic Test Execution
  ✅ PASS       | Gap Analysis
  ✅ PASS       | Sigma Rule Generation
  ✅ PASS       | Visualization Generation

Total: 5 completed, 1 skipped, 0 failed

✅ Workflow completed successfully!
```

---

## Performance Tips

1. **Skip phases you don't need** using CLI arguments
2. **Use dry_run mode** for testing without execution
3. **Filter techniques** in config.yaml to reduce scope
4. **Run baseline once** then skip with --skip-baseline
5. **Cache SIEM queries** to reduce load

---

## Best Practices

1. **Always validate environment first**
   ```bash
   python automation_scripts/validate_environment.py
   ```

2. **Review config.yaml before running**
   - Check SIEM connection details
   - Verify output directories
   - Adjust thresholds as needed

3. **Start with dry-run**
   ```yaml
   execution:
     dry_run: true
   ```

4. **Version control your config**
   ```bash
   git add config.yaml
   git commit -m "Update SIEM configuration"
   ```

5. **Monitor resource usage**
   ```bash
   # Check disk space before running
   df -h
   
   # Monitor during execution
   watch -n 5 'du -sh test_matrix/ gap_analysis/ visualizations/'
   ```

---

**For more information:**
- README.md - Project overview
- METHODOLOGY.md - Testing framework details
- documentation/QUICK_START.md - Lab setup guide

