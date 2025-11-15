#!/usr/bin/env python3
"""
MITRE ATT&CK Test Matrix Builder for Atomic Red Team
Generates comprehensive testing matrix mapped to MITRE ATT&CK framework
"""

import json
import subprocess
import sys
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path


class AtomicTestMatrix:
    """Build comprehensive testing matrix mapped to MITRE ATT&CK framework"""

    # Priority tactics for SOC operations aligned to Australian threat landscape
    PRIORITY_TACTICS = {
        'T1566': {
            'name': 'Phishing',
            'tactic': 'Initial Access',
            'priority': 'CRITICAL',
            'description': 'Email-based initial access techniques'
        },
        'T1059.001': {
            'name': 'PowerShell',
            'tactic': 'Execution',
            'priority': 'CRITICAL',
            'description': 'PowerShell command and script execution'
        },
        'T1547': {
            'name': 'Boot or Logon Autostart Execution',
            'tactic': 'Persistence',
            'priority': 'HIGH',
            'description': 'Persistence via registry run keys'
        },
        'T1078': {
            'name': 'Valid Accounts',
            'tactic': 'Privilege Escalation',
            'priority': 'CRITICAL',
            'description': 'Abuse of legitimate credentials'
        },
        'T1021': {
            'name': 'Remote Services',
            'tactic': 'Lateral Movement',
            'priority': 'HIGH',
            'description': 'RDP, SMB, WinRM lateral movement'
        },
        'T1005': {
            'name': 'Data from Local System',
            'tactic': 'Collection',
            'priority': 'MEDIUM',
            'description': 'Local data collection and staging'
        },
        'T1567': {
            'name': 'Exfiltration Over Web Service',
            'tactic': 'Exfiltration',
            'priority': 'HIGH',
            'description': 'Data exfil via cloud services'
        },
        'T1529': {
            'name': 'System Shutdown/Reboot',
            'tactic': 'Impact',
            'priority': 'MEDIUM',
            'description': 'Service disruption techniques'
        },
        'T1548': {
            'name': 'Abuse Elevation Control Mechanism',
            'tactic': 'Privilege Escalation',
            'priority': 'CRITICAL',
            'description': 'UAC bypass and privilege escalation'
        },
        'T1562': {
            'name': 'Impair Defenses',
            'tactic': 'Defense Evasion',
            'priority': 'CRITICAL',
            'description': 'Disabling security controls'
        },
        'T1140': {
            'name': 'Deobfuscate/Decode Files or Information',
            'tactic': 'Defense Evasion',
            'priority': 'HIGH',
            'description': 'Decoding obfuscated payloads'
        },
        'T1112': {
            'name': 'Modify Registry',
            'tactic': 'Defense Evasion',
            'priority': 'MEDIUM',
            'description': 'Registry modification techniques'
        },
        'T1070': {
            'name': 'Indicator Removal',
            'tactic': 'Defense Evasion',
            'priority': 'HIGH',
            'description': 'Log deletion and evidence removal'
        },
        'T1543': {
            'name': 'Create or Modify System Process',
            'tactic': 'Persistence',
            'priority': 'HIGH',
            'description': 'Service creation and modification'
        },
        'T1071': {
            'name': 'Application Layer Protocol',
            'tactic': 'Command and Control',
            'priority': 'MEDIUM',
            'description': 'HTTP/HTTPS C2 communications'
        }
    }

    def __init__(self, output_dir: str = "test_matrix"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.matrix = {
            "metadata": {
                "created": datetime.now().isoformat(),
                "version": "1.0",
                "framework": "MITRE ATT&CK",
                "tool": "Atomic Red Team"
            },
            "test_plan": [],
            "statistics": {
                "total_techniques": len(self.PRIORITY_TACTICS),
                "by_priority": {},
                "by_tactic": {}
            }
        }

    def build_test_matrix(self) -> Dict:
        """Generate structured test execution plan"""

        print("🔨 Building MITRE ATT&CK test matrix...")

        for technique_id, technique_info in self.PRIORITY_TACTICS.items():
            print(f"  ├─ Processing {technique_id}: {technique_info['name']}")

            test_entry = {
                "technique_id": technique_id,
                "technique_name": technique_info['name'],
                "tactic": technique_info['tactic'],
                "priority": technique_info['priority'],
                "description": technique_info['description'],
                "atomic_tests": self._get_atomic_tests_metadata(technique_id),
                "expected_detections": self._define_expected_detections(technique_id),
                "baseline_status": "not_tested",
                "test_status": "pending"
            }

            self.matrix['test_plan'].append(test_entry)

            # Update statistics
            priority = technique_info['priority']
            tactic = technique_info['tactic']

            self.matrix['statistics']['by_priority'][priority] = \
                self.matrix['statistics']['by_priority'].get(priority, 0) + 1

            self.matrix['statistics']['by_tactic'][tactic] = \
                self.matrix['statistics']['by_tactic'].get(tactic, 0) + 1

        print(f"\n✓ Test matrix generated: {len(self.matrix['test_plan'])} techniques")
        return self.matrix

    def _get_atomic_tests_metadata(self, technique: str) -> List[Dict]:
        """
        Get metadata about available atomic tests for a technique.
        In production, this would query Invoke-AtomicRedTeam.
        For now, returns placeholder structure.
        """
        # Placeholder - in real environment this would query PowerShell
        return [
            {
                "test_number": 1,
                "test_name": f"Test {technique} - Variant 1",
                "executor": "powershell",
                "platforms": ["windows"],
                "description": f"Primary test for {technique}"
            }
        ]

    def _define_expected_detections(self, technique: str) -> List[Dict]:
        """Define expected detection artifacts for each technique"""

        detection_map = {
            'T1059.001': [
                {
                    'source': 'Windows Event Log',
                    'event_id': 4688,
                    'description': 'Process creation for powershell.exe'
                },
                {
                    'source': 'Sysmon',
                    'event_id': 1,
                    'description': 'Process Create - CommandLine contains encoded commands'
                },
                {
                    'source': 'PowerShell Operational',
                    'event_id': 4104,
                    'description': 'Script block logging'
                }
            ],
            'T1548': [
                {
                    'source': 'Sysmon',
                    'event_id': 1,
                    'description': 'Process creation with UAC bypass indicators'
                },
                {
                    'source': 'Windows Event Log',
                    'event_id': 4688,
                    'description': 'Elevated process creation'
                }
            ],
            'T1562': [
                {
                    'source': 'Sysmon',
                    'event_id': 13,
                    'description': 'Registry modification to disable security tools'
                },
                {
                    'source': 'Windows Event Log',
                    'event_id': 7040,
                    'description': 'Service state change (security services)'
                }
            ]
        }

        return detection_map.get(technique, [
            {
                'source': 'SIEM',
                'event_id': 'N/A',
                'description': f'Generic detection for {technique}'
            }
        ])

    def export_matrix(self, filename: str = "attack_test_matrix.json") -> Path:
        """Export test matrix to JSON file"""

        output_path = self.output_dir / filename

        with open(output_path, 'w') as f:
            json.dump(self.matrix, f, indent=2)

        print(f"\n✓ Test matrix exported to: {output_path}")
        return output_path

    def generate_summary_report(self) -> str:
        """Generate human-readable summary of test matrix"""

        report = []
        report.append("=" * 70)
        report.append("ATOMIC RED TEAM TEST MATRIX SUMMARY")
        report.append("=" * 70)
        report.append(f"\nGenerated: {self.matrix['metadata']['created']}")
        report.append(f"Total Techniques: {self.matrix['statistics']['total_techniques']}")

        report.append("\n\nBY PRIORITY:")
        for priority, count in sorted(self.matrix['statistics']['by_priority'].items()):
            report.append(f"  {priority:12} : {count} techniques")

        report.append("\n\nBY TACTIC:")
        for tactic, count in sorted(self.matrix['statistics']['by_tactic'].items()):
            report.append(f"  {tactic:30} : {count} techniques")

        report.append("\n\nTECHNIQUE DETAILS:")
        report.append("-" * 70)

        for test in self.matrix['test_plan']:
            report.append(f"\n{test['technique_id']} - {test['technique_name']}")
            report.append(f"  Tactic: {test['tactic']}")
            report.append(f"  Priority: {test['priority']}")
            report.append(f"  Description: {test['description']}")
            report.append(f"  Expected Detections: {len(test['expected_detections'])}")

        report.append("\n" + "=" * 70)

        summary = "\n".join(report)

        # Save summary to file
        summary_path = self.output_dir / "test_matrix_summary.txt"
        with open(summary_path, 'w') as f:
            f.write(summary)

        return summary


def main():
    """Main execution function"""

    print("🎯 Atomic Red Team Test Matrix Builder")
    print("=" * 70)

    # Build test matrix
    builder = AtomicTestMatrix()
    matrix = builder.build_test_matrix()

    # Export to JSON
    matrix_path = builder.export_matrix()

    # Generate summary report
    summary = builder.generate_summary_report()
    print("\n" + summary)

    print("\n✅ Matrix building complete!")
    print(f"   📁 Output directory: {builder.output_dir}")
    print(f"   📄 Matrix file: {matrix_path.name}")
    print(f"   📄 Summary file: test_matrix_summary.txt")


if __name__ == "__main__":
    main()
