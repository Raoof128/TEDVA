#!/usr/bin/env python3
"""
Baseline Detection Assessment Module
Assess current detection coverage BEFORE executing atomic tests
"""

import json
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from pathlib import Path
from enum import Enum


class DetectionStatus(Enum):
    """Detection coverage status levels"""
    DETECTED = "detected"
    PARTIAL = "partial"
    MISSING = "missing"
    UNKNOWN = "unknown"


@dataclass
class DetectionCapability:
    """Represents detection capability for a specific technique"""
    technique_id: str
    technique_name: str
    detection_method: str  # SIEM rule, EDR signature, network-based
    status: str  # detected, partial, missing
    confidence: int  # 0-100%
    notes: str
    rule_id: Optional[str] = None
    last_validated: Optional[str] = None


class SIEMConnection:
    """
    Mock SIEM connection interface
    In production, this would connect to Splunk/ELK/Wazuh APIs
    """

    def __init__(self, siem_type: str = "splunk", config: Dict = None):
        self.siem_type = siem_type
        self.config = config or {}
        self.connected = False

    def connect(self) -> bool:
        """Establish connection to SIEM"""
        print(f"📡 Connecting to {self.siem_type} SIEM...")
        # In production: implement actual connection logic
        self.connected = True
        return True

    def query_detection_rules(self) -> List[Dict]:
        """
        Query SIEM for existing detection rules
        Returns list of detection rules with metadata
        """
        # Mock data - in production this would query actual SIEM
        mock_rules = [
            {
                'rule_id': 'sigma_001',
                'name': 'PowerShell Execution Detection',
                'technique_id': 'T1059.001',
                'technique_name': 'PowerShell',
                'type': 'SIEM Rule',
                'enabled': True,
                'keywords': ['powershell.exe', 'encoded', 'bypass'],
                'accuracy_score': 85,
                'description': 'Detects suspicious PowerShell execution patterns'
            },
            {
                'rule_id': 'sigma_002',
                'name': 'Service Creation',
                'technique_id': 'T1543',
                'technique_name': 'Create or Modify System Process',
                'type': 'SIEM Rule',
                'enabled': True,
                'keywords': ['sc.exe', 'new', 'service'],
                'accuracy_score': 92,
                'description': 'Detects new service creation'
            },
            {
                'rule_id': 'edr_001',
                'name': 'UAC Bypass Detection',
                'technique_id': 'T1548',
                'technique_name': 'Abuse Elevation Control',
                'type': 'EDR Signature',
                'enabled': False,  # Disabled rule
                'keywords': ['eventvwr.exe', 'fodhelper.exe'],
                'accuracy_score': 70,
                'description': 'Detects common UAC bypass techniques'
            },
            {
                'rule_id': 'sigma_003',
                'name': 'Lateral Movement - SMB',
                'technique_id': 'T1021',
                'technique_name': 'Remote Services',
                'type': 'SIEM Rule',
                'enabled': True,
                'keywords': ['psexec', 'admin$'],
                'accuracy_score': 78,
                'description': 'Detects lateral movement via SMB'
            },
            {
                'rule_id': 'network_001',
                'name': 'C2 HTTP Beaconing',
                'technique_id': 'T1071',
                'technique_name': 'Application Layer Protocol',
                'type': 'Network Detection',
                'enabled': True,
                'keywords': ['beaconing', 'periodic', 'http'],
                'accuracy_score': 65,
                'description': 'Detects periodic C2 beaconing patterns'
            }
        ]

        return mock_rules

    def execute_query(self, query: str) -> Dict:
        """Execute custom SIEM query"""
        # Mock implementation
        return {'count': 0, 'results': []}


class BaselineAssessment:
    """Assess current detection coverage before atomic testing"""

    def __init__(self, siem_connection: SIEMConnection, output_dir: str = "gap_analysis"):
        self.siem = siem_connection
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.baseline_timestamp = datetime.now().isoformat()
        self.assessment_data = {
            "timestamp": self.baseline_timestamp,
            "siem_type": self.siem.siem_type,
            "total_techniques": 0,
            "detected": 0,
            "partial": 0,
            "missing": 0,
            "techniques": []
        }

    def assess_detection_rules(self, test_matrix_path: str = None) -> Dict:
        """Inventory current detection rules and their coverage"""

        print("\n🔍 Assessing Baseline Detection Coverage...")
        print("=" * 70)

        # Load test matrix to understand which techniques to assess
        if test_matrix_path:
            with open(test_matrix_path, 'r') as f:
                test_matrix = json.load(f)
            techniques_to_assess = {t['technique_id']: t['technique_name']
                                     for t in test_matrix['test_plan']}
        else:
            techniques_to_assess = {}

        # Query SIEM for existing rules
        rules = self.siem.query_detection_rules()

        print(f"📊 Found {len(rules)} detection rules in SIEM")

        # Map rules to techniques
        rule_coverage = {}
        for rule in rules:
            technique_id = rule.get('technique_id')
            if technique_id:
                if technique_id not in rule_coverage:
                    rule_coverage[technique_id] = []
                rule_coverage[technique_id].append(rule)

        # Assess coverage for each technique
        for technique_id, technique_name in techniques_to_assess.items():
            rules_for_technique = rule_coverage.get(technique_id, [])

            if not rules_for_technique:
                status = DetectionStatus.MISSING.value
                detection_method = "None"
                confidence = 0
                notes = "No detection rules found"
            else:
                # Determine coverage status
                enabled_rules = [r for r in rules_for_technique if r.get('enabled', False)]

                if not enabled_rules:
                    status = DetectionStatus.MISSING.value
                    detection_method = "Disabled Rules"
                    confidence = 0
                    notes = f"{len(rules_for_technique)} rules exist but disabled"
                else:
                    avg_accuracy = sum(r.get('accuracy_score', 0) for r in enabled_rules) / len(enabled_rules)

                    if avg_accuracy >= 80 and len(enabled_rules) >= 2:
                        status = DetectionStatus.DETECTED.value
                        confidence = int(avg_accuracy)
                        notes = f"{len(enabled_rules)} active rules with high confidence"
                    elif avg_accuracy >= 60 or len(enabled_rules) >= 1:
                        status = DetectionStatus.PARTIAL.value
                        confidence = int(avg_accuracy)
                        notes = f"{len(enabled_rules)} active rules with moderate coverage"
                    else:
                        status = DetectionStatus.MISSING.value
                        confidence = int(avg_accuracy)
                        notes = "Low confidence detection"

                    detection_method = ", ".join(set(r['type'] for r in enabled_rules))

            # Create capability entry
            capability = DetectionCapability(
                technique_id=technique_id,
                technique_name=technique_name,
                detection_method=detection_method,
                status=status,
                confidence=confidence,
                notes=notes,
                rule_id=", ".join(r['rule_id'] for r in rules_for_technique[:3]) if rules_for_technique else None,
                last_validated=self.baseline_timestamp
            )

            self.assessment_data['techniques'].append(asdict(capability))
            self.assessment_data['total_techniques'] += 1

            # Update statistics
            if status == DetectionStatus.DETECTED.value:
                self.assessment_data['detected'] += 1
                status_icon = "✅"
            elif status == DetectionStatus.PARTIAL.value:
                self.assessment_data['partial'] += 1
                status_icon = "⚠️"
            else:
                self.assessment_data['missing'] += 1
                status_icon = "❌"

            print(f"{status_icon} {technique_id:12} | {status:10} | {confidence:3}% | {notes}")

        return self.assessment_data

    def export_baseline(self, filename: str = "baseline_assessment.json") -> Path:
        """Export baseline assessment to JSON"""

        output_path = self.output_dir / filename

        with open(output_path, 'w') as f:
            json.dump(self.assessment_data, f, indent=2)

        print(f"\n✓ Baseline assessment exported to: {output_path}")
        return output_path

    def generate_coverage_summary(self) -> str:
        """Generate human-readable coverage summary"""

        total = self.assessment_data['total_techniques']
        detected = self.assessment_data['detected']
        partial = self.assessment_data['partial']
        missing = self.assessment_data['missing']

        if total == 0:
            return "No techniques assessed"

        coverage_pct = ((detected + (partial * 0.5)) / total) * 100

        summary = []
        summary.append("\n" + "=" * 70)
        summary.append("BASELINE DETECTION COVERAGE SUMMARY")
        summary.append("=" * 70)
        summary.append(f"\nAssessment Date: {self.baseline_timestamp}")
        summary.append(f"SIEM Platform: {self.siem.siem_type}")
        summary.append(f"\nTotal Techniques Assessed: {total}")
        summary.append(f"\n  ✅ Fully Detected:    {detected:3} ({(detected/total)*100:.1f}%)")
        summary.append(f"  ⚠️  Partial Detection: {partial:3} ({(partial/total)*100:.1f}%)")
        summary.append(f"  ❌ Not Detected:      {missing:3} ({(missing/total)*100:.1f}%)")
        summary.append(f"\n📊 Overall Coverage Score: {coverage_pct:.1f}%")

        if coverage_pct >= 85:
            summary.append("   Rating: EXCELLENT - Strong detection coverage")
        elif coverage_pct >= 70:
            summary.append("   Rating: GOOD - Adequate coverage with room for improvement")
        elif coverage_pct >= 50:
            summary.append("   Rating: FAIR - Significant gaps present")
        else:
            summary.append("   Rating: POOR - Critical gaps require immediate attention")

        summary.append("\n" + "=" * 70)

        return "\n".join(summary)


def main():
    """Main execution function"""

    print("🛡️  Baseline Detection Assessment Tool")
    print("=" * 70)

    # Initialize SIEM connection
    siem = SIEMConnection(siem_type="splunk")
    siem.connect()

    # Create baseline assessment
    assessor = BaselineAssessment(siem)

    # Perform assessment (load test matrix if available)
    test_matrix_path = Path("test_matrix/attack_test_matrix.json")
    if test_matrix_path.exists():
        assessment = assessor.assess_detection_rules(str(test_matrix_path))
    else:
        print("⚠️  Test matrix not found. Run attack_matrix_builder.py first.")
        print("   Proceeding with rule inventory only...")
        assessment = assessor.assess_detection_rules()

    # Export results
    assessor.export_baseline()

    # Display summary
    summary = assessor.generate_coverage_summary()
    print(summary)

    # Save summary to file
    summary_path = assessor.output_dir / "baseline_summary.txt"
    with open(summary_path, 'w') as f:
        f.write(summary)

    print(f"\n✅ Baseline assessment complete!")
    print(f"   📁 Output directory: {assessor.output_dir}")
    print(f"   📄 Assessment data: baseline_assessment.json")
    print(f"   📄 Summary report: baseline_summary.txt")


if __name__ == "__main__":
    main()
