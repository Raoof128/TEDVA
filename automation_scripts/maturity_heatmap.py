#!/usr/bin/env python3
"""
Detection Maturity Heatmap Generator
Generate visual detection coverage maturity matrix based on MITRE ATT&CK framework
"""

import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List
from datetime import datetime
import numpy as np


class DetectionMaturityMatrix:
    """Map techniques across tactics showing detection coverage"""

    TACTICS = [
        'Initial Access',
        'Execution',
        'Persistence',
        'Privilege Escalation',
        'Defense Evasion',
        'Credential Access',
        'Discovery',
        'Lateral Movement',
        'Collection',
        'Command and Control',
        'Exfiltration',
        'Impact'
    ]

    MATURITY_LEVELS = {
        0: 'Not Tested',
        1: 'Detected (Basic)',
        2: 'Detected (Validated)',
        3: 'Detected (Tuned)',
        4: 'Detected + Auto Response'
    }

    MATURITY_COLORS = {
        0: '#f0f0f0',  # Gray - Not tested
        1: '#FFB6C1',  # Light red - Basic detection
        2: '#FFD700',  # Gold - Validated
        3: '#90EE90',  # Light green - Tuned
        4: '#00CC00'   # Dark green - Automated
    }

    def __init__(self, test_results_path: str, output_dir: str = "visualizations"):
        self.test_results_path = Path(test_results_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.test_results = self._load_results()
        self.matrix_data = None

    def _load_results(self) -> Dict:
        """Load test execution results"""
        try:
            with open(self.test_results_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Results not found: {self.test_results_path}")
            return {}

    def generate_heatmap(self) -> Path:
        """Create MITRE ATT&CK-style coverage matrix"""

        print("\n📊 Generating Detection Maturity Heatmap...")
        print("=" * 70)

        # Build matrix data
        self.matrix_data = self._build_matrix_data()

        # Create figure
        fig, ax = plt.subplots(figsize=(16, 8))

        # Create heatmap
        sns.heatmap(
            self.matrix_data,
            cmap=[self.MATURITY_COLORS[i] for i in range(5)],
            annot=True,
            fmt='d',
            cbar_kws={'label': 'Detection Maturity Level'},
            linewidths=0.5,
            linecolor='white',
            ax=ax,
            vmin=0,
            vmax=4
        )

        # Customize plot
        plt.title('Detection Coverage Maturity Matrix - Purple Team Validation\n' +
                 f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}',
                 fontsize=14, fontweight='bold', pad=20)
        plt.xlabel('Techniques', fontsize=12, fontweight='bold')
        plt.ylabel('Tactics', fontsize=12, fontweight='bold')
        plt.tight_layout()

        # Save
        output_path = self.output_dir / 'detection_maturity_heatmap.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"✓ Heatmap generated: {output_path}")

        return output_path

    def _build_matrix_data(self) -> pd.DataFrame:
        """Build matrix data from test results"""

        # Initialize matrix
        technique_coverage = {}

        tests_executed = self.test_results.get('tests_executed', [])

        for result in tests_executed:
            technique_id = result['technique']
            tactic = result.get('tactic', 'Unknown')
            detection = result.get('detection', {})

            # Determine maturity level
            maturity = self._calculate_maturity_level(detection, result)

            if tactic not in technique_coverage:
                technique_coverage[tactic] = {}

            technique_coverage[tactic][technique_id] = maturity

        # Convert to DataFrame
        # For simplicity, aggregate by tactic
        tactic_maturity = {}
        for tactic, techniques in technique_coverage.items():
            if techniques:
                avg_maturity = sum(techniques.values()) / len(techniques)
                tactic_maturity[tactic] = round(avg_maturity)
            else:
                tactic_maturity[tactic] = 0

        # Create simple visualization - one column per tactic
        data = [[tactic_maturity.get(tactic, 0)] for tactic in self.TACTICS]

        df = pd.DataFrame(data, index=self.TACTICS, columns=['Maturity'])

        return df

    def _calculate_maturity_level(self, detection: Dict, result: Dict) -> int:
        """
        Calculate maturity level:
        0 = Not tested or failed
        1 = Detected (basic)
        2 = Detected (validated, good coverage)
        3 = Detected (tuned, high confidence)
        4 = Detected + automated response (future state)
        """

        if result.get('test_status') != 'success':
            return 0

        detected = detection.get('detected', False)
        confidence = detection.get('confidence_score', 0)
        event_count = detection.get('event_count', 0)

        if not detected:
            return 0
        elif confidence >= 90 and event_count >= 5:
            return 3  # Tuned
        elif confidence >= 70 and event_count >= 3:
            return 2  # Validated
        elif detected:
            return 1  # Basic detection
        else:
            return 0

    def generate_coverage_chart(self) -> Path:
        """Generate coverage breakdown pie chart"""

        print("📊 Generating Coverage Breakdown Chart...")

        tests_executed = self.test_results.get('tests_executed', [])

        # Count by detection status
        detected = sum(1 for t in tests_executed if t.get('detection', {}).get('detected', False))
        partial = sum(1 for t in tests_executed
                     if t.get('detection', {}).get('event_count', 0) > 0
                     and not t.get('detection', {}).get('detected', False))
        undetected = len(tests_executed) - detected - partial

        # Create pie chart
        fig, ax = plt.subplots(figsize=(10, 8))

        sizes = [detected, partial, undetected]
        labels = [f'Detected ({detected})', f'Partial ({partial})', f'Not Detected ({undetected})']
        colors = ['#00CC00', '#FFD700', '#FF6B6B']
        explode = (0.1, 0, 0)

        ax.pie(sizes, explode=explode, labels=labels, colors=colors,
               autopct='%1.1f%%', shadow=True, startangle=90,
               textprops={'fontsize': 12, 'fontweight': 'bold'})

        ax.axis('equal')

        plt.title('Detection Coverage Breakdown\n' +
                 f'Total Techniques: {len(tests_executed)}',
                 fontsize=14, fontweight='bold', pad=20)

        # Save
        output_path = self.output_dir / 'coverage_breakdown.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"✓ Coverage chart generated: {output_path}")

        return output_path

    def generate_severity_chart(self) -> Path:
        """Generate gap severity breakdown chart"""

        print("📊 Generating Severity Breakdown Chart...")

        # Load gap analysis if available
        gap_analysis_path = Path('gap_analysis/gap_analysis_report.json')

        if not gap_analysis_path.exists():
            print("⚠️  Gap analysis not found, skipping severity chart")
            return None

        with open(gap_analysis_path, 'r') as f:
            gap_analysis = json.load(f)

        severity_counts = gap_analysis.get('statistics', {}).get('by_severity', {})

        if not severity_counts:
            print("⚠️  No severity data available")
            return None

        # Create bar chart
        fig, ax = plt.subplots(figsize=(10, 6))

        severities = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
        counts = [severity_counts.get(s, 0) for s in severities]
        colors_map = {'CRITICAL': '#FF0000', 'HIGH': '#FF6B6B', 'MEDIUM': '#FFD700', 'LOW': '#90EE90'}
        colors = [colors_map[s] for s in severities]

        bars = ax.bar(severities, counts, color=colors, edgecolor='black', linewidth=1.5)

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontweight='bold', fontsize=12)

        ax.set_ylabel('Number of Gaps', fontsize=12, fontweight='bold')
        ax.set_xlabel('Severity', fontsize=12, fontweight='bold')
        ax.set_title('Detection Gaps by Severity\n' +
                    'Purple Team Validation Results',
                    fontsize=14, fontweight='bold', pad=20)

        plt.tight_layout()

        # Save
        output_path = self.output_dir / 'gap_severity_breakdown.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"✓ Severity chart generated: {output_path}")

        return output_path

    def generate_all_visualizations(self) -> Dict[str, Path]:
        """Generate all visualization types"""

        print("\n🎨 Generating All Visualizations...")
        print("=" * 70)

        outputs = {}

        # Generate heatmap
        outputs['heatmap'] = self.generate_heatmap()

        # Generate coverage chart
        outputs['coverage'] = self.generate_coverage_chart()

        # Generate severity chart
        severity_chart = self.generate_severity_chart()
        if severity_chart:
            outputs['severity'] = severity_chart

        print(f"\n✅ {len(outputs)} visualizations generated")

        return outputs

    def generate_summary_report(self) -> str:
        """Generate text summary of visualizations"""

        tests = self.test_results.get('tests_executed', [])
        stats = self.test_results.get('statistics', {})

        summary = []
        summary.append("=" * 70)
        summary.append("DETECTION MATURITY VISUALIZATION SUMMARY")
        summary.append("=" * 70)
        summary.append(f"\nGenerated: {datetime.now().isoformat()}")
        summary.append(f"Total Techniques Tested: {len(tests)}")

        summary.append("\n\nVISUALIZATIONS GENERATED:")
        summary.append(f"  📊 Detection Maturity Heatmap")
        summary.append(f"  📊 Coverage Breakdown Chart")
        summary.append(f"  📊 Gap Severity Breakdown")

        summary.append("\n\nKEY METRICS:")
        summary.append(f"  Detected: {stats.get('detected', 0)}")
        summary.append(f"  Partial: {stats.get('partial_detection', 0)}")
        summary.append(f"  Not Detected: {stats.get('not_detected', 0)}")

        if len(tests) > 0:
            coverage_pct = (stats.get('detected', 0) / len(tests)) * 100
            summary.append(f"\n  Overall Coverage: {coverage_pct:.1f}%")

        summary.append("\n\nOUTPUT FILES:")
        summary.append(f"  {self.output_dir}/detection_maturity_heatmap.png")
        summary.append(f"  {self.output_dir}/coverage_breakdown.png")
        summary.append(f"  {self.output_dir}/gap_severity_breakdown.png")

        summary.append("\n" + "=" * 70)

        return "\n".join(summary)


def main():
    """Main execution function"""

    print("🎨 Detection Maturity Heatmap Generator")
    print("=" * 70)

    # Check for test results
    test_results_path = "test_matrix/test_execution_results.json"
    if not Path(test_results_path).exists():
        print("❌ Test execution results not found!")
        print("   Run: python automation_scripts/atomic_test_executor.py")
        return

    # Create matrix generator
    matrix = DetectionMaturityMatrix(test_results_path)

    # Generate all visualizations
    outputs = matrix.generate_all_visualizations()

    # Generate summary
    summary = matrix.generate_summary_report()
    print("\n" + summary)

    # Save summary
    summary_path = matrix.output_dir / "visualization_summary.txt"
    with open(summary_path, 'w') as f:
        f.write(summary)

    print(f"\n✅ Visualization generation complete!")
    print(f"   📁 Output directory: {matrix.output_dir}")
    print(f"   📄 Summary: visualization_summary.txt")


if __name__ == "__main__":
    main()
