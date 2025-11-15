#!/usr/bin/env python3
"""
Detection Gap Analysis Generator
Analyze test results and generate comprehensive gap analysis with remediation recommendations
"""

import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, asdict


class GapSeverity(Enum):
    """Severity levels for detection gaps"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


@dataclass
class DetectionGap:
    """Represents a detection gap"""
    technique_id: str
    technique_name: str
    tactic: str
    gap_type: str  # UNDETECTED, PARTIAL, WEAK
    severity: str
    business_impact: str
    attack_patterns: List[str]
    remediation_priority: str
    estimated_effort: str
    current_coverage: int  # 0-100%
    target_coverage: int  # 0-100%
    recommendation: str


class DetectionGapAnalyzer:
    """Analyze test results and identify detection gaps"""

    # Business impact mapping for Australian SOC context
    BUSINESS_IMPACT_MAP = {
        'T1486': 'CRITICAL - Ransomware execution (avg $2.2M AUD impact)',
        'T1490': 'CRITICAL - Data destruction/wiper malware',
        'T1078': 'HIGH - Unauthorized access, data breach risk',
        'T1021': 'HIGH - Lateral movement, domain compromise',
        'T1548': 'CRITICAL - Privilege escalation, full system control',
        'T1562': 'CRITICAL - Disabling security controls, blind SOC',
        'T1059.001': 'HIGH - Malicious PowerShell execution',
        'T1566': 'MEDIUM - Phishing, initial access vector',
        'T1140': 'HIGH - Payload execution, malware deployment',
        'T1112': 'MEDIUM - Configuration changes, persistence',
        'T1070': 'HIGH - Evidence destruction, forensics impediment',
        'T1543': 'MEDIUM - Persistence, unauthorized service',
        'T1071': 'MEDIUM - C2 communications, data exfiltration',
        'T1005': 'MEDIUM - Data theft, IP loss',
        'T1567': 'HIGH - Data exfiltration, compliance violation',
        'T1529': 'LOW - Service disruption (non-destructive)'
    }

    # Attack patterns and TTPs
    ATTACK_PATTERNS = {
        'T1548': ['UAC bypass via Fodhelper', 'UAC bypass via EventVwr', 'Token manipulation'],
        'T1562': ['Disable Windows Defender', 'Stop security services', 'Delete event logs'],
        'T1140': ['Base64 decode', 'XOR decryption', 'Deobfuscate PowerShell'],
        'T1059.001': ['Encoded PowerShell', 'Download cradle', 'Reflective loading'],
        'T1078': ['Credential dumping', 'Pass-the-hash', 'Golden ticket'],
        'T1021': ['PsExec lateral movement', 'WMI remote execution', 'RDP session hijacking']
    }

    def __init__(self, test_results_path: str, baseline_path: str = None, output_dir: str = "gap_analysis"):
        self.test_results_path = Path(test_results_path)
        self.baseline_path = Path(baseline_path) if baseline_path else None
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.test_results = self._load_json(test_results_path)
        self.baseline = self._load_json(baseline_path) if baseline_path else None

        self.gaps = []
        self.analysis = {
            "timestamp": datetime.now().isoformat(),
            "test_results_source": str(test_results_path),
            "baseline_source": str(baseline_path) if baseline_path else None,
            "total_techniques_tested": 0,
            "gaps": {
                "undetected": [],
                "partial": [],
                "detected": []
            },
            "risk_assessment": {},
            "recommendations": [],
            "statistics": {
                "by_severity": {},
                "by_tactic": {},
                "total_risk_score": 0
            }
        }

    def _load_json(self, path: str) -> Dict:
        """Load JSON file"""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  File not found: {path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON: {e}")
            return {}

    def analyze_gaps(self) -> Dict:
        """Identify undetected and partially detected techniques"""

        print("\n🔍 Analyzing Detection Gaps...")
        print("=" * 70)

        tests_executed = self.test_results.get('tests_executed', [])

        for result in tests_executed:
            technique = result['technique']
            technique_name = result.get('technique_name', 'Unknown')
            detection = result.get('detection', {})
            priority = result.get('priority', 'MEDIUM')

            self.analysis['total_techniques_tested'] += 1

            # Determine gap type
            detected = detection.get('detected', False)
            event_count = detection.get('event_count', 0)
            confidence = detection.get('confidence_score', 0)

            if not detected or event_count == 0:
                gap_type = 'UNDETECTED'
                current_coverage = 0
                category = 'undetected'
            elif confidence < 70 or event_count < 3:
                gap_type = 'PARTIAL'
                current_coverage = confidence
                category = 'partial'
            else:
                gap_type = 'DETECTED'
                current_coverage = confidence
                category = 'detected'

            # Assess severity
            severity = self._assess_severity(technique, priority)

            # Build gap entry
            gap = DetectionGap(
                technique_id=technique,
                technique_name=technique_name,
                tactic=result.get('tactic', 'Unknown'),
                gap_type=gap_type,
                severity=severity.name,
                business_impact=self._assess_business_impact(technique),
                attack_patterns=self._get_attack_patterns(technique),
                remediation_priority=self._determine_remediation_priority(severity, gap_type),
                estimated_effort=self._estimate_effort(gap_type, technique),
                current_coverage=current_coverage,
                target_coverage=85 if gap_type != 'DETECTED' else 95,
                recommendation=self._generate_recommendation(technique, gap_type)
            )

            self.analysis['gaps'][category].append(asdict(gap))
            self.gaps.append(gap)

            # Update statistics
            severity_name = severity.name
            self.analysis['statistics']['by_severity'][severity_name] = \
                self.analysis['statistics']['by_severity'].get(severity_name, 0) + 1

            # Display progress
            icon = "❌" if gap_type == "UNDETECTED" else "⚠️" if gap_type == "PARTIAL" else "✅"
            print(f"{icon} {technique:12} | {gap_type:12} | {severity.name:8} | {current_coverage:3}%")

        # Generate remediation recommendations
        self.analysis['recommendations'] = self._generate_recommendations()

        # Calculate risk assessment
        self.analysis['risk_assessment'] = self._calculate_risk_assessment()

        print(f"\n✓ Gap analysis complete: {len(self.gaps)} techniques analyzed")

        return self.analysis

    def _assess_severity(self, technique: str, priority: str = None) -> GapSeverity:
        """Determine gap severity based on ATT&CK framework and priority"""

        # Critical techniques (high impact, common in APT)
        critical_techniques = ['T1486', 'T1490', 'T1565', 'T1548', 'T1562']

        # High severity techniques
        high_techniques = ['T1078', 'T1021', 'T1087', 'T1140', 'T1070', 'T1567']

        if technique in critical_techniques:
            return GapSeverity.CRITICAL
        elif technique in high_techniques:
            return GapSeverity.HIGH
        elif priority == 'CRITICAL':
            return GapSeverity.CRITICAL
        elif priority == 'HIGH':
            return GapSeverity.HIGH
        elif priority == 'MEDIUM':
            return GapSeverity.MEDIUM
        else:
            return GapSeverity.LOW

    def _assess_business_impact(self, technique: str) -> str:
        """Get business impact description"""
        return self.BUSINESS_IMPACT_MAP.get(technique, 'MEDIUM - Standard security risk')

    def _get_attack_patterns(self, technique: str) -> List[str]:
        """Get known attack patterns for technique"""
        return self.ATTACK_PATTERNS.get(technique, ['General exploitation patterns'])

    def _determine_remediation_priority(self, severity: GapSeverity, gap_type: str) -> str:
        """Determine remediation priority"""
        if severity == GapSeverity.CRITICAL and gap_type == 'UNDETECTED':
            return 'IMMEDIATE (24-48 hours)'
        elif severity == GapSeverity.CRITICAL:
            return 'URGENT (1 week)'
        elif severity == GapSeverity.HIGH and gap_type == 'UNDETECTED':
            return 'HIGH (2 weeks)'
        elif severity == GapSeverity.HIGH:
            return 'MEDIUM (1 month)'
        else:
            return 'LOW (backlog)'

    def _estimate_effort(self, gap_type: str, technique: str) -> str:
        """Estimate remediation effort"""
        if gap_type == 'UNDETECTED':
            return '8-16 hours (rule dev + tuning)'
        elif gap_type == 'PARTIAL':
            return '4-8 hours (rule optimization)'
        else:
            return '2-4 hours (validation only)'

    def _generate_recommendation(self, technique: str, gap_type: str) -> str:
        """Generate specific recommendation"""

        recommendations = {
            'T1059.001': 'Enable PowerShell ScriptBlock logging (4104), module logging, transcription. Deploy Sigma rule for encoded commands.',
            'T1548': 'Monitor registry keys: HKCU\\Software\\Classes\\ms-settings, eventvwr.exe process creation. Deploy UAC bypass detection rules.',
            'T1562': 'Alert on security service state changes (Event ID 7040), Windows Defender modification, audit policy changes.',
            'T1140': 'Monitor for base64 decode, certutil -decode, decompression utilities. Correlate with network activity.',
            'T1078': 'Implement impossible travel detection, baseline normal logon times, alert on privilege escalation.',
            'T1021': 'Monitor admin$ shares, detect PsExec/RemCom, track lateral movement paths with Bloodhound.'
        }

        if gap_type == 'UNDETECTED':
            return recommendations.get(technique, 'Develop new detection rule. Consult Sigma rule repository.')
        elif gap_type == 'PARTIAL':
            return 'Tune existing rule: reduce false positives, expand coverage, add correlation.'
        else:
            return 'Validate rule effectiveness. Consider automated response playbook.'

    def _generate_recommendations(self) -> List[Dict]:
        """Generate actionable detection engineering tasks"""

        recommendations = []

        # Prioritize CRITICAL and UNDETECTED gaps
        critical_gaps = [g for g in self.gaps if g.severity == 'CRITICAL' and g.gap_type == 'UNDETECTED']

        for gap in critical_gaps[:10]:  # Top 10 critical gaps
            recommendation = {
                'gap_id': gap.technique_id,
                'technique_name': gap.technique_name,
                'priority': gap.remediation_priority,
                'detection_strategy': gap.recommendation,
                'rule_template': f"sigma_rules/{gap.technique_id.replace('.', '_')}.yml",
                'effort_estimate': gap.estimated_effort,
                'owner': 'Detection Engineering Team',
                'expected_outcome': f"Increase coverage from {gap.current_coverage}% to {gap.target_coverage}%"
            }
            recommendations.append(recommendation)

        return recommendations

    def _calculate_risk_assessment(self) -> Dict:
        """Calculate overall risk score and assessment"""

        risk_scores = {
            'CRITICAL': 10,
            'HIGH': 7,
            'MEDIUM': 4,
            'LOW': 1
        }

        total_risk = 0
        for gap in self.gaps:
            if gap.gap_type in ['UNDETECTED', 'PARTIAL']:
                risk_value = risk_scores.get(gap.severity, 1)
                # Weight by coverage gap
                coverage_gap = (gap.target_coverage - gap.current_coverage) / 100
                total_risk += risk_value * coverage_gap

        return {
            'total_risk_score': round(total_risk, 2),
            'risk_level': self._categorize_risk(total_risk),
            'undetected_critical': len([g for g in self.gaps if g.severity == 'CRITICAL' and g.gap_type == 'UNDETECTED']),
            'recommendation': self._risk_recommendation(total_risk)
        }

    def _categorize_risk(self, score: float) -> str:
        """Categorize risk level"""
        if score >= 50:
            return 'CRITICAL - Immediate action required'
        elif score >= 30:
            return 'HIGH - Significant gaps present'
        elif score >= 15:
            return 'MEDIUM - Moderate improvement needed'
        else:
            return 'LOW - Acceptable coverage'

    def _risk_recommendation(self, score: float) -> str:
        """Provide risk-based recommendation"""
        if score >= 50:
            return 'Deploy emergency detection rules for critical gaps within 48 hours. Escalate to CISO.'
        elif score >= 30:
            return 'Prioritize detection engineering sprint. Target 3-5 critical rules this week.'
        elif score >= 15:
            return 'Schedule detection improvement work. Address gaps over next month.'
        else:
            return 'Continue monitoring. Maintain current detection coverage.'

    def export_gap_analysis(self, filename: str = "gap_analysis_report.json") -> Path:
        """Export gap analysis to JSON"""

        output_path = self.output_dir / filename

        with open(output_path, 'w') as f:
            json.dump(self.analysis, f, indent=2)

        print(f"\n✓ Gap analysis exported to: {output_path}")
        return output_path

    def export_csv_summary(self, filename: str = "detected_techniques.csv") -> Path:
        """Export summary as CSV for easy analysis"""

        # Flatten gap data
        rows = []
        for gap in self.gaps:
            rows.append({
                'Technique ID': gap.technique_id,
                'Technique Name': gap.technique_name,
                'Tactic': gap.tactic,
                'Gap Type': gap.gap_type,
                'Severity': gap.severity,
                'Current Coverage %': gap.current_coverage,
                'Target Coverage %': gap.target_coverage,
                'Remediation Priority': gap.remediation_priority,
                'Estimated Effort': gap.estimated_effort,
                'Business Impact': gap.business_impact
            })

        df = pd.DataFrame(rows)
        output_path = self.output_dir / filename
        df.to_csv(output_path, index=False)

        print(f"✓ CSV summary exported to: {output_path}")
        return output_path

    def generate_summary_report(self) -> str:
        """Generate executive summary report"""

        stats = self.analysis['statistics']
        risk = self.analysis['risk_assessment']

        summary = []
        summary.append("=" * 70)
        summary.append("DETECTION GAP ANALYSIS - EXECUTIVE SUMMARY")
        summary.append("=" * 70)
        summary.append(f"\nAnalysis Date: {self.analysis['timestamp']}")
        summary.append(f"Techniques Tested: {self.analysis['total_techniques_tested']}")

        summary.append("\n\nGAP BREAKDOWN:")
        summary.append(f"  ❌ Undetected:    {len(self.analysis['gaps']['undetected'])}")
        summary.append(f"  ⚠️  Partial:       {len(self.analysis['gaps']['partial'])}")
        summary.append(f"  ✅ Detected:      {len(self.analysis['gaps']['detected'])}")

        summary.append("\n\nBY SEVERITY:")
        for severity, count in sorted(stats['by_severity'].items()):
            summary.append(f"  {severity:10} : {count}")

        summary.append(f"\n\nRISK ASSESSMENT:")
        summary.append(f"  Total Risk Score: {risk['total_risk_score']}")
        summary.append(f"  Risk Level: {risk['risk_level']}")
        summary.append(f"  Critical Undetected: {risk['undetected_critical']}")
        summary.append(f"\n  Recommendation: {risk['recommendation']}")

        summary.append("\n\nTOP PRIORITY GAPS:")
        critical_gaps = [g for g in self.gaps if g.severity == 'CRITICAL' and g.gap_type == 'UNDETECTED']
        for i, gap in enumerate(critical_gaps[:5], 1):
            summary.append(f"\n  {i}. {gap.technique_id} - {gap.technique_name}")
            summary.append(f"     Priority: {gap.remediation_priority}")
            summary.append(f"     Impact: {gap.business_impact}")

        summary.append("\n" + "=" * 70)

        return "\n".join(summary)


def main():
    """Main execution function"""

    print("📊 Detection Gap Analysis Generator")
    print("=" * 70)

    # Check for test results
    test_results_path = "test_matrix/test_execution_results.json"
    if not Path(test_results_path).exists():
        print("❌ Test execution results not found!")
        print("   Run: python automation_scripts/atomic_test_executor.py")
        return

    # Create analyzer
    analyzer = DetectionGapAnalyzer(test_results_path)

    # Perform analysis
    analysis = analyzer.analyze_gaps()

    # Export results
    analyzer.export_gap_analysis()
    analyzer.export_csv_summary()

    # Display summary
    summary = analyzer.generate_summary_report()
    print("\n" + summary)

    # Save summary
    summary_path = analyzer.output_dir / "gap_analysis_summary.txt"
    with open(summary_path, 'w') as f:
        f.write(summary)

    print(f"\n✅ Gap analysis complete!")
    print(f"   📁 Output directory: {analyzer.output_dir}")
    print(f"   📄 Full analysis: gap_analysis_report.json")
    print(f"   📄 CSV summary: detected_techniques.csv")
    print(f"   📄 Executive summary: gap_analysis_summary.txt")


if __name__ == "__main__":
    main()
