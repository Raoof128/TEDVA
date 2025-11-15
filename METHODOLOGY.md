# 📋 Purple Team Validation Methodology

## Overview

This document outlines the systematic approach for conducting purple team exercises using Atomic Red Team to validate security detection capabilities and identify gaps.

## Table of Contents

1. [Testing Philosophy](#testing-philosophy)
2. [Phase-by-Phase Breakdown](#phase-by-phase-breakdown)
3. [Test Selection Criteria](#test-selection-criteria)
4. [Execution Guidelines](#execution-guidelines)
5. [Detection Validation](#detection-validation)
6. [Gap Analysis Process](#gap-analysis-process)
7. [Remediation Workflow](#remediation-workflow)
8. [Continuous Improvement](#continuous-improvement)

---

## Testing Philosophy

### Core Principles

1. **Evidence-Based Assessment**
   - All findings backed by empirical test data
   - Quantified metrics (detection rates, coverage percentages)
   - Reproducible test methodology

2. **Risk-Driven Prioritization**
   - Focus on high-impact, high-likelihood threats
   - Align with organization's threat model
   - Prioritize techniques observed in recent threat intelligence

3. **Collaborative Approach**
   - Red Team (offensive) + Blue Team (defensive) collaboration
   - Shared learning and knowledge transfer
   - Continuous feedback loop

4. **Safe Testing Environment**
   - Isolated lab environment
   - No production system impact
   - Rollback capability for all changes

---

## Phase-by-Phase Breakdown

### Phase 1: Baseline Assessment (Week 1)

**Objective:** Understand current detection capabilities before testing

**Activities:**
1. Inventory existing detection rules
   - SIEM correlation rules
   - EDR signatures
   - Network IDS/IPS rules
   - Custom detection scripts

2. Map rules to MITRE ATT&CK techniques
   - Identify technique coverage
   - Document detection methods
   - Assess rule quality and tuning

3. Establish baseline metrics
   - Current detection rate
   - False positive rates
   - Alert volume baselines

**Deliverables:**
- `baseline_assessment.json`
- Coverage matrix spreadsheet
- Pre-testing metrics dashboard

**Success Criteria:**
- Complete inventory of detection rules
- Mapping to 80%+ of targeted techniques
- Baseline metrics established

---

### Phase 2: Test Matrix Development (Week 1)

**Objective:** Create prioritized testing plan aligned to business risk

**Activities:**
1. Select techniques for testing
   - Review threat intelligence reports
   - Analyze industry threat trends
   - Consult MITRE ATT&CK Navigator

2. Prioritize by risk
   - Business impact assessment
   - Likelihood based on threat landscape
   - Existing control gaps

3. Define expected detection artifacts
   - Log sources that should capture activity
   - Specific event IDs
   - Detection rule mappings

**Deliverables:**
- `attack_test_matrix.json`
- Technique prioritization matrix
- Expected detection documentation

**Success Criteria:**
- 40+ techniques selected and prioritized
- Expected detections defined for each
- Stakeholder approval obtained

---

### Phase 3: Controlled Execution (Weeks 2-3)

**Objective:** Execute atomic tests and validate detection

**Safety Measures:**
1. **Pre-Execution Checklist**
   - Verify isolated lab environment
   - Confirm backups/snapshots
   - Notify SOC team of testing window
   - Enable verbose logging

2. **During Execution**
   - Execute one technique at a time
   - Wait 5-10 minutes between tests (log ingestion)
   - Monitor SIEM for alerts
   - Document observations

3. **Post-Execution**
   - Run cleanup scripts
   - Verify system state restored
   - Export test logs

**Execution Workflow:**

```
For each technique:
  1. Pre-execution snapshot
  2. Capture baseline SIEM event count
  3. Execute atomic test
  4. Wait for log ingestion (5 mins)
  5. Query SIEM for detection
  6. Document results
  7. Run cleanup
  8. Verify cleanup success
```

**Deliverables:**
- `test_execution_results.json`
- Per-technique execution logs
- SIEM query results

**Success Criteria:**
- 95%+ tests execute successfully
- All cleanups complete without errors
- Full audit trail maintained

---

### Phase 4: Detection Validation (Week 3)

**Objective:** Verify whether security controls detected the tests

**Validation Criteria:**

| Detection Level | Criteria | Classification |
|----------------|----------|----------------|
| **Detected** | ≥3 SIEM events, correlation rule triggered | ✅ Detected |
| **Partial** | 1-2 SIEM events, no rule triggered | ⚠️ Partial |
| **Not Detected** | 0 SIEM events | ❌ Undetected |

**Validation Process:**

1. **SIEM Query** (per technique)
   ```sql
   index=* sourcetype=*
   | where _time > <test_timestamp> AND _time < <test_timestamp + 10min>
   | search technique=<technique_id> OR <technique_keywords>
   | stats count
   ```

2. **EDR Verification**
   - Check endpoint console for alerts
   - Verify process tree captured
   - Confirm behavioral detection

3. **Network Detection**
   - Query IDS/IPS logs
   - Check firewall deny logs
   - Validate DNS/proxy logs

**Deliverables:**
- Detection validation matrix
- SIEM query screenshots
- EDR alert examples

**Success Criteria:**
- Every test has validated detection status
- Evidence documented for each classification
- Edge cases reviewed with SMEs

---

### Phase 5: Gap Analysis (Week 4)

**Objective:** Identify and prioritize detection gaps

**Analysis Framework:**

1. **Gap Identification**
   - Undetected techniques
   - Partially detected techniques
   - Weak/unreliable detections

2. **Severity Assessment**

| Severity | Criteria | Example Techniques |
|----------|----------|-------------------|
| **CRITICAL** | High business impact + commonly exploited | T1548, T1562, T1078 |
| **HIGH** | Moderate impact + observed in recent attacks | T1059.001, T1021, T1140 |
| **MEDIUM** | Low-moderate impact + less common | T1112, T1005 |
| **LOW** | Low impact + rare | T1529 |

3. **Risk Scoring**
   ```
   Risk Score = (Severity Weight) × (Coverage Gap %)

   Severity Weights:
   - CRITICAL: 10
   - HIGH: 7
   - MEDIUM: 4
   - LOW: 1
   ```

**Deliverables:**
- `gap_analysis_report.json`
- Risk-prioritized gap list
- Executive summary presentation

**Success Criteria:**
- All gaps categorized by severity
- Business impact documented
- Remediation timeline proposed

---

### Phase 6: Rule Development (Week 5)

**Objective:** Create detection rules to close gaps

**Rule Development Process:**

1. **Research**
   - Review Sigma rule repository
   - Study attack technique details
   - Identify detection artifacts

2. **Rule Creation**
   - Write Sigma rule (vendor-neutral)
   - Define detection logic
   - List expected false positives
   - Set appropriate severity level

3. **Testing**
   - Re-run atomic test
   - Validate rule triggers correctly
   - Measure false positive rate

4. **Tuning**
   - Adjust thresholds
   - Add exclusions for known FPs
   - Optimize performance

**Quality Criteria:**

- **Detection Rate:** ≥90% of test executions detected
- **False Positive Rate:** <5% in production baseline
- **Performance:** Query executes in <10 seconds
- **Documentation:** Complete metadata (MITRE tags, references)

**Deliverables:**
- Production-ready Sigma rules
- Validation test results
- Deployment guide

**Success Criteria:**
- Rules for all CRITICAL gaps developed
- All rules tested against historical data
- FP rate <5% achieved

---

### Phase 7: Deployment & Monitoring (Week 6)

**Objective:** Deploy new rules and monitor effectiveness

**Deployment Process:**

1. **Convert Sigma to SIEM Format**
   ```bash
   # For Splunk
   sigmac -t splunk -c splunk-windows rule.yml

   # For Elasticsearch
   sigmac -t es-qs -c winlogbeat rule.yml
   ```

2. **Staging Environment Testing**
   - Deploy to test SIEM instance
   - Run against 30-day baseline
   - Measure FP rate
   - Tune as needed

3. **Production Deployment**
   - Schedule change window
   - Deploy rules in alert mode
   - Monitor for 1 week
   - Enable response actions

4. **Post-Deployment Validation**
   - Re-run atomic tests
   - Confirm detection working
   - Document final metrics

**Deliverables:**
- Deployed detection rules
- Post-deployment validation report
- Updated coverage metrics

**Success Criteria:**
- 85%+ detection coverage achieved
- <2% FP rate in production
- SOC team trained on new alerts

---

## Test Selection Criteria

### Primary Criteria

1. **Threat Relevance**
   - Techniques used by threat actors targeting your industry
   - Recent CVE exploitations
   - Ransomware TTPs

2. **Business Impact**
   - Data breach potential
   - Operational disruption risk
   - Regulatory compliance requirements

3. **Feasibility**
   - Safe to test in lab environment
   - Cleanup scripts available
   - Prerequisite tools accessible

### Australian Context Priorities

Focus on techniques commonly seen in Australian threat landscape:

- **Initial Access:** Phishing (T1566), Valid Accounts (T1078)
- **Execution:** PowerShell (T1059.001)
- **Privilege Escalation:** UAC Bypass (T1548)
- **Defense Evasion:** Impair Defenses (T1562)
- **Lateral Movement:** Remote Services (T1021)
- **Exfiltration:** Cloud Services (T1567)

---

## Execution Guidelines

### Safety Protocols

1. **Environment Isolation**
   - Dedicated VLAN for testing
   - No connection to production networks
   - Host-only networking in VMs

2. **Change Control**
   - Documented test plan
   - Rollback procedures defined
   - SOC notification 24 hours prior

3. **Data Protection**
   - No production data in test environment
   - Synthetic test data only
   - Encrypted storage for test results

### Best Practices

1. **Timing**
   - Execute during business hours (for SOC response validation)
   - Allow 5-10 min between tests
   - Complete full technique before moving to next

2. **Documentation**
   - Screenshot each test execution
   - Capture SIEM queries
   - Note any unexpected behavior

3. **Communication**
   - Daily standup with SOC team
   - Slack channel for real-time updates
   - End-of-day summary email

---

## Detection Validation

### Multi-Layer Validation

Validate detection across all security layers:

1. **Endpoint (EDR)**
   - Process creation events
   - File modifications
   - Registry changes
   - Network connections

2. **Network (IDS/IPS)**
   - Suspicious network traffic
   - C2 beaconing patterns
   - Data exfiltration attempts

3. **SIEM**
   - Correlation rule triggers
   - Threat intelligence matches
   - Anomaly detection

4. **Cloud (CASB/CWPP)**
   - Cloud API activity
   - Data movement
   - Identity anomalies

### Quality Metrics

- **True Positive Rate:** % of tests correctly detected
- **False Positive Rate:** % of alerts with no malicious activity
- **Time to Detect (TTD):** Time from execution to alert
- **Time to Respond (TTR):** Time from alert to analyst action

---

## Gap Analysis Process

### Categorization

**Undetected Gaps:**
- Zero detection events
- No visibility into technique
- Highest priority for remediation

**Partial Detection:**
- Some events logged but no alert
- Detection logic exists but disabled/broken
- Medium priority

**Weak Detection:**
- Alert triggers but high FP rate
- Detection unreliable
- Tuning required

### Root Cause Analysis

For each gap, determine:

1. **Visibility Gap:** No logs collected
2. **Detection Gap:** Logs exist but no rule
3. **Tuning Gap:** Rule exists but needs optimization
4. **Coverage Gap:** Rule covers some variants but not all

---

## Remediation Workflow

```
Identify Gap
    │
    ├─ Visibility Gap?
    │   └─ Enable logging (Sysmon, audit policy, etc.)
    │
    ├─ Detection Gap?
    │   └─ Develop new Sigma rule
    │
    ├─ Tuning Gap?
    │   └─ Optimize existing rule
    │
    └─ Coverage Gap?
        └─ Expand rule coverage
```

### Remediation Timeline

| Priority | Timeline | Stakeholder |
|----------|----------|-------------|
| CRITICAL | 24-48 hours | CISO approval |
| HIGH | 1 week | Security manager |
| MEDIUM | 2-4 weeks | Detection engineer |
| LOW | Backlog | Sprint planning |

---

## Continuous Improvement

### Weekly Validation Cycle

```
Monday:     Execute automated atomic tests
Tuesday:    Review detection results
Wednesday:  Analyze new gaps
Thursday:   Update/tune detection rules
Friday:     Deploy rule updates
```

### Monthly Review

- Detection coverage trend analysis
- FP rate tracking
- New technique additions to test matrix
- Threat intelligence integration

### Quarterly Assessment

- Full gap analysis refresh
- SOC maturity scoring
- Executive reporting
- Budget planning for tool improvements

---

## Metrics & KPIs

### Detection Effectiveness

- **Detection Coverage:** % of ATT&CK techniques detected
- **True Positive Rate:** % of attacks correctly detected
- **False Positive Rate:** % of benign activity flagged
- **Mean Time to Detect (MTTD):** Avg time to detect attack

### Program Health

- **Test Automation Rate:** % of tests automated
- **Gap Closure Rate:** # gaps closed per month
- **Rule Quality:** Avg confidence score of detection rules
- **SOC Response Time:** Time from alert to containment

### Business Impact

- **Risk Reduction:** Decrease in undetected attack paths
- **Cost Avoidance:** Estimated breach cost prevented
- **Compliance Score:** % of controls validated
- **Stakeholder Satisfaction:** Survey score from SOC team

---

## References

- **MITRE ATT&CK:** https://attack.mitre.org/
- **Atomic Red Team:** https://github.com/redcanaryco/atomic-red-team
- **Sigma Rules:** https://github.com/SigmaHQ/sigma
- **NIST Cybersecurity Framework:** https://www.nist.gov/cyberframework

---

**Document Version:** 1.0
**Last Updated:** January 2025
**Author:** Purple Team Framework Project
