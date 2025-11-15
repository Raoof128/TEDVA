#!/usr/bin/env python3
"""
Master Orchestration Script
Runs the complete purple team validation workflow
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path
from datetime import datetime


class WorkflowOrchestrator:
    """Orchestrates the complete validation workflow"""

    def __init__(self, skip_baseline=False, skip_execution=False, skip_visualization=False):
        self.skip_baseline = skip_baseline
        self.skip_execution = skip_execution
        self.skip_visualization = skip_visualization
        self.script_dir = Path(__file__).parent
        self.start_time = datetime.now()

    def run_script(self, script_name, description):
        """Run a Python script and handle errors"""
        print("\n" + "=" * 70)
        print(f"▶  {description}")
        print("=" * 70)

        script_path = self.script_dir / script_name

        if not script_path.exists():
            print(f"❌ ERROR: {script_name} not found")
            return False

        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout per script
            )

            # Print output
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)

            if result.returncode == 0:
                print(f"✅ {description} - COMPLETED")
                return True
            else:
                print(f"❌ {description} - FAILED (exit code: {result.returncode})")
                return False

        except subprocess.TimeoutExpired:
            print(f"❌ {description} - TIMEOUT (exceeded 5 minutes)")
            return False
        except Exception as e:
            print(f"❌ {description} - ERROR: {e}")
            return False

    def run_workflow(self):
        """Execute complete workflow"""
        print("=" * 70)
        print("PURPLE TEAM VALIDATION FRAMEWORK - FULL WORKFLOW")
        print("=" * 70)
        print(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        results = {}

        # Phase 1: Build Test Matrix
        results['test_matrix'] = self.run_script(
            'attack_matrix_builder.py',
            'PHASE 1: Build MITRE ATT&CK Test Matrix'
        )

        if not results['test_matrix']:
            print("\n❌ CRITICAL: Cannot proceed without test matrix")
            return False

        # Phase 2: Baseline Assessment (optional)
        if not self.skip_baseline:
            results['baseline'] = self.run_script(
                'baseline_assessment.py',
                'PHASE 2: Assess Baseline Detection Coverage'
            )
        else:
            print("\n⊙ PHASE 2: Baseline Assessment - SKIPPED")
            results['baseline'] = None

        # Phase 3: Execute Atomic Tests (optional)
        if not self.skip_execution:
            results['execution'] = self.run_script(
                'atomic_test_executor.py',
                'PHASE 3: Execute Atomic Red Team Tests'
            )

            if not results['execution']:
                print("\n⚠️  WARNING: Test execution failed - continuing with analysis")
        else:
            print("\n⊙ PHASE 3: Test Execution - SKIPPED")
            results['execution'] = None

        # Phase 4: Gap Analysis
        results['gap_analysis'] = self.run_script(
            'gap_analysis_generator.py',
            'PHASE 4: Analyze Detection Gaps'
        )

        # Phase 5: Build Sigma Rules
        results['sigma_rules'] = self.run_script(
            'sigma_rule_builder.py',
            'PHASE 5: Generate Sigma Detection Rules'
        )

        # Phase 6: Generate Visualizations (optional)
        if not self.skip_visualization:
            results['visualization'] = self.run_script(
                'maturity_heatmap.py',
                'PHASE 6: Generate Detection Maturity Visualizations'
            )
        else:
            print("\n⊙ PHASE 6: Visualization - SKIPPED")
            results['visualization'] = None

        # Print final summary
        self.print_summary(results)

        # Return overall success
        critical_tasks = ['test_matrix', 'gap_analysis']
        return all(results.get(task, False) for task in critical_tasks)

    def print_summary(self, results):
        """Print workflow execution summary"""
        end_time = datetime.now()
        duration = end_time - self.start_time

        print("\n" + "=" * 70)
        print("WORKFLOW EXECUTION SUMMARY")
        print("=" * 70)

        print(f"\nStart Time:  {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"End Time:    {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Duration:    {duration}")

        print("\nPhase Results:")
        phase_names = {
            'test_matrix': 'Test Matrix Generation',
            'baseline': 'Baseline Assessment',
            'execution': 'Atomic Test Execution',
            'gap_analysis': 'Gap Analysis',
            'sigma_rules': 'Sigma Rule Generation',
            'visualization': 'Visualization Generation'
        }

        for phase, name in phase_names.items():
            result = results.get(phase)
            if result is None:
                status = "⊙ SKIPPED"
            elif result:
                status = "✅ PASS"
            else:
                status = "❌ FAIL"
            print(f"  {status:12} | {name}")

        # Overall status
        completed = sum(1 for v in results.values() if v is True)
        skipped = sum(1 for v in results.values() if v is None)
        failed = sum(1 for v in results.values() if v is False)

        print(f"\nTotal: {completed} completed, {skipped} skipped, {failed} failed")

        print("\n" + "=" * 70)

        # Output locations
        print("\n📁 Output Locations:")
        outputs = [
            ('test_matrix/attack_test_matrix.json', 'Test Matrix'),
            ('gap_analysis/baseline_assessment.json', 'Baseline Assessment'),
            ('test_matrix/test_execution_results.json', 'Test Results'),
            ('gap_analysis/gap_analysis_report.json', 'Gap Analysis'),
            ('detection_rules/sigma_rules/', 'Sigma Rules'),
            ('visualizations/detection_maturity_heatmap.png', 'Heatmap')
        ]

        for path, description in outputs:
            if Path(path).exists():
                print(f"   ✓ {description:25} → {path}")
            else:
                print(f"   ⊙ {description:25} → {path} (not generated)")

        print("\n" + "=" * 70)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Purple Team Validation Framework - Complete Workflow',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Run complete workflow
  python run_all.py

  # Skip test execution (use existing results)
  python run_all.py --skip-execution

  # Skip baseline and visualization (fast mode)
  python run_all.py --skip-baseline --skip-visualization
        '''
    )

    parser.add_argument(
        '--skip-baseline',
        action='store_true',
        help='Skip baseline assessment phase'
    )

    parser.add_argument(
        '--skip-execution',
        action='store_true',
        help='Skip atomic test execution (use existing results)'
    )

    parser.add_argument(
        '--skip-visualization',
        action='store_true',
        help='Skip visualization generation'
    )

    args = parser.parse_args()

    # Change to repo root if in automation_scripts
    if Path.cwd().name == 'automation_scripts':
        os.chdir('..')

    # Run workflow
    orchestrator = WorkflowOrchestrator(
        skip_baseline=args.skip_baseline,
        skip_execution=args.skip_execution,
        skip_visualization=args.skip_visualization
    )

    success = orchestrator.run_workflow()

    if success:
        print("\n✅ Workflow completed successfully!")
        print("\nNext steps:")
        print("  1. Review gap_analysis/gap_analysis_report.json")
        print("  2. Deploy Sigma rules from detection_rules/sigma_rules/")
        print("  3. Share visualizations with stakeholders")
        return 0
    else:
        print("\n❌ Workflow completed with errors")
        print("  Review output above for details")
        return 1


if __name__ == "__main__":
    sys.exit(main())
