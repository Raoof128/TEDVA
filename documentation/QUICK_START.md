# 🚀 Quick Start Guide - Purple Team Validation Lab

This guide will help you set up a complete purple team validation environment from scratch.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Lab Architecture](#lab-architecture)
3. [Step-by-Step Setup](#step-by-step-setup)
4. [Installation & Configuration](#installation--configuration)
5. [Running Your First Test](#running-your-first-test)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 4 cores | 8+ cores |
| RAM | 16 GB | 32+ GB |
| Storage | 100 GB | 250+ GB SSD |
| Network | Isolated subnet | Dedicated VLAN |

### Software Requirements

**Host Machine:**
- Hypervisor: VMware Workstation, VirtualBox, or Hyper-V
- Operating System: Windows 10/11 or Linux

**Virtual Machines:**
- Windows Server 2019/2022 (test target)
- Windows 10/11 Enterprise (optional - workstation testing)
- Ubuntu 20.04/22.04 (SIEM - Wazuh or ELK)

---

## Lab Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Isolated Lab Network                       │
│                     10.0.0.0/24                              │
└──────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┴───────────────────┐
          │                                       │
    ┌─────▼──────┐                         ┌─────▼──────┐
    │  Windows   │                         │   SIEM     │
    │  Server    │◀───────logs─────────────│  Server    │
    │  2019      │                         │  (Ubuntu)  │
    │            │                         │            │
    │ 10.0.0.10  │                         │ 10.0.0.20  │
    └────────────┘                         └────────────┘
    - Sysmon                                - Wazuh/ELK
    - Atomic Red Team                       - Dashboards
    - Test target                           - Detection rules
```

---

## Step-by-Step Setup

### Phase 1: Virtual Machine Creation

#### 1.1 Windows Server 2019 (Test Target)

**VM Specifications:**
- CPU: 2 cores
- RAM: 4 GB
- Disk: 60 GB
- Network: Host-only adapter (10.0.0.10/24)

**Installation Steps:**

1. Download Windows Server 2019 evaluation ISO
   - Microsoft Evaluation Center: https://www.microsoft.com/en-us/evalcenter/

2. Create new VM in your hypervisor
   ```
   Name: WIN-ATOMIC-TEST
   OS: Windows Server 2019
   Network: Host-only (10.0.0.0/24)
   ```

3. Complete Windows installation
   - Server with Desktop Experience
   - Set Administrator password
   - Configure static IP: 10.0.0.10

#### 1.2 Ubuntu Server (SIEM)

**VM Specifications:**
- CPU: 2 cores
- RAM: 8 GB
- Disk: 80 GB
- Network: Host-only adapter (10.0.0.20/24)

**Installation Steps:**

1. Download Ubuntu Server 22.04 LTS ISO
   - https://ubuntu.com/download/server

2. Create new VM
   ```
   Name: SIEM-SERVER
   OS: Ubuntu 22.04
   Network: Host-only (10.0.0.0/24)
   ```

3. Configure static IP
   ```bash
   sudo nano /etc/netplan/00-installer-config.yaml
   ```

   ```yaml
   network:
     version: 2
     ethernets:
       ens33:
         addresses: [10.0.0.20/24]
         gateway4: 10.0.0.1
         nameservers:
           addresses: [8.8.8.8, 8.8.4.4]
   ```

   ```bash
   sudo netplan apply
   ```

---

### Phase 2: Windows Test Target Configuration

#### 2.1 Install Sysmon

**On Windows Server (10.0.0.10):**

1. Download Sysmon
   ```powershell
   # Run PowerShell as Administrator
   Invoke-WebRequest -Uri https://download.sysinternals.com/files/Sysmon.zip -OutFile C:\Temp\Sysmon.zip
   Expand-Archive C:\Temp\Sysmon.zip -DestinationPath C:\Temp\Sysmon
   ```

2. Download SwiftOnSecurity Sysmon config
   ```powershell
   Invoke-WebRequest -Uri https://raw.githubusercontent.com/SwiftOnSecurity/sysmon-config/master/sysmonconfig-export.xml -OutFile C:\Temp\Sysmon\config.xml
   ```

3. Install Sysmon
   ```powershell
   cd C:\Temp\Sysmon
   .\Sysmon64.exe -accepteula -i config.xml
   ```

4. Verify installation
   ```powershell
   Get-Service Sysmon64
   Get-WinEvent -LogName "Microsoft-Windows-Sysmon/Operational" -MaxEvents 5
   ```

#### 2.2 Enable PowerShell Logging

```powershell
# Enable Script Block Logging
$regPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging"
New-Item -Path $regPath -Force
Set-ItemProperty -Path $regPath -Name "EnableScriptBlockLogging" -Value 1

# Enable Module Logging
$regPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ModuleLogging"
New-Item -Path $regPath -Force
Set-ItemProperty -Path $regPath -Name "EnableModuleLogging" -Value 1

# Enable Transcription
$regPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\Transcription"
New-Item -Path $regPath -Force
Set-ItemProperty -Path $regPath -Name "EnableTranscripting" -Value 1
Set-ItemProperty -Path $regPath -Name "OutputDirectory" -Value "C:\PSTranscripts"
```

#### 2.3 Install Atomic Red Team

```powershell
# Set execution policy
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope CurrentUser -Force

# Install Atomic Red Team
IEX (IWR 'https://raw.githubusercontent.com/redcanaryco/invoke-atomicredteam/master/install-atomicredteam.ps1' -UseBasicParsing)
Install-AtomicRedTeam -getAtoms -Force

# Verify installation
Import-Module "C:\AtomicRedTeam\invoke-atomicredteam\Invoke-AtomicRedTeam.psd1"
Get-AtomicTechnique -Technique T1059.001
```

---

### Phase 3: SIEM Setup (Wazuh)

#### 3.1 Install Wazuh Server

**On Ubuntu Server (10.0.0.20):**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install curl apt-transport-https lsb-release gnupg -y

# Add Wazuh repository
curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | sudo gpg --no-default-keyring --keyring gnupg-ring:/usr/share/keyrings/wazuh.gpg --import
echo "deb [signed-by=/usr/share/keyrings/wazuh.gpg] https://packages.wazuh.com/4.x/apt/ stable main" | sudo tee /etc/apt/sources.list.d/wazuh.list

# Install Wazuh manager
sudo apt update
sudo apt install wazuh-manager -y

# Start Wazuh
sudo systemctl start wazuh-manager
sudo systemctl enable wazuh-manager
```

#### 3.2 Install Wazuh Dashboard (Kibana)

```bash
# Install Elasticsearch and Wazuh indexer
curl -s https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo gpg --no-default-keyring --keyring gnupg-ring:/usr/share/keyrings/elasticsearch.gpg --import

echo "deb [signed-by=/usr/share/keyrings/elasticsearch.gpg] https://artifacts.elastic.co/packages/7.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-7.x.list

sudo apt update
sudo apt install elasticsearch -y

# Configure Elasticsearch
sudo sed -i 's/#network.host: 192.168.0.1/network.host: 10.0.0.20/' /etc/elasticsearch/elasticsearch.yml

sudo systemctl start elasticsearch
sudo systemctl enable elasticsearch

# Install Kibana
sudo apt install kibana -y
sudo /usr/share/kibana/bin/kibana-plugin install https://packages.wazuh.com/4.x/ui/kibana/wazuh_kibana-4.5.0_7.17.9-1.zip

# Configure Kibana
sudo sed -i 's/#server.host: "localhost"/server.host: "10.0.0.20"/' /etc/kibana/kibana.yml

sudo systemctl start kibana
sudo systemctl enable kibana
```

#### 3.3 Configure Wazuh Agent on Windows

**On Windows Server:**

```powershell
# Download Wazuh agent
Invoke-WebRequest -Uri https://packages.wazuh.com/4.x/windows/wazuh-agent-4.5.0-1.msi -OutFile C:\Temp\wazuh-agent.msi

# Install agent
Start-Process msiexec.exe -ArgumentList '/i','C:\Temp\wazuh-agent.msi','/q','WAZUH_MANAGER="10.0.0.20"' -Wait

# Start agent
NET START WazuhSvc
```

**On Ubuntu SIEM Server:**

```bash
# Register agent
sudo /var/ossec/bin/agent_auth -m 10.0.0.20 -A WIN-ATOMIC-TEST

# Restart Wazuh manager
sudo systemctl restart wazuh-manager
```

---

### Phase 4: Python Framework Setup

#### 4.1 Clone Repository

**On your host machine (or Ubuntu SIEM):**

```bash
# Install Git
sudo apt install git -y

# Clone repository
git clone https://github.com/your-org/atomic-red-team-validation.git
cd atomic-red-team-validation
```

#### 4.2 Install Python Dependencies

```bash
# Install Python 3.8+
sudo apt install python3 python3-pip -y

# Install required packages
pip3 install -r automation_scripts/requirements.txt
```

#### 4.3 Configure SIEM Connection

Edit `automation_scripts/baseline_assessment.py`:

```python
# Update SIEM connection details
siem = SIEMConnection(
    siem_type="wazuh",  # or "splunk", "elk"
    config={
        'host': '10.0.0.20',
        'port': 55000,
        'username': 'wazuh',
        'password': 'your_password'
    }
)
```

---

## Running Your First Test

### Step 1: Build Test Matrix

```bash
cd automation_scripts
python3 attack_matrix_builder.py
```

**Expected Output:**
```
🎯 Atomic Red Team Test Matrix Builder
======================================================================
🔨 Building MITRE ATT&CK test matrix...
  ├─ Processing T1059.001: PowerShell
  ├─ Processing T1548: Abuse Elevation Control
  ...
✓ Test matrix generated: 15 techniques
✓ Test matrix exported to: test_matrix/attack_test_matrix.json
```

### Step 2: Assess Baseline Coverage

```bash
python3 baseline_assessment.py
```

**Expected Output:**
```
🛡️  Baseline Detection Assessment Tool
======================================================================
📡 Connecting to wazuh SIEM...
🔍 Assessing Baseline Detection Coverage...
✅ T1059.001   | detected   | 85% | 2 active rules with high confidence
⚠️  T1548      | partial    | 60% | 1 active rule with moderate coverage
❌ T1562       | missing    |  0% | No detection rules found
...
✓ Baseline assessment exported to: gap_analysis/baseline_assessment.json
```

### Step 3: Execute Atomic Test (Single Technique)

**On Windows Server:**

```powershell
# Import module
Import-Module "C:\AtomicRedTeam\invoke-atomicredteam\Invoke-AtomicRedTeam.psd1"

# Execute PowerShell test (T1059.001)
Invoke-AtomicTest -AtomicTechnique T1059.001 -TestNumbers 1 -Confirm:$False
```

**Verify Detection in Wazuh:**

1. Open browser: http://10.0.0.20:5601
2. Navigate to Wazuh app
3. Go to "Security Events"
4. Search for recent alerts

### Step 4: Run Full Automated Test Suite

**On host machine:**

```bash
python3 atomic_test_executor.py
```

This will:
- Execute all techniques in test matrix
- Validate SIEM detection
- Generate results report

### Step 5: Analyze Gaps

```bash
python3 gap_analysis_generator.py
```

**Expected Output:**
```
📊 Detection Gap Analysis Generator
======================================================================
🔍 Analyzing Detection Gaps...
❌ T1548        | UNDETECTED   | CRITICAL |   0%
⚠️  T1112       | PARTIAL      | MEDIUM   |  45%
✅ T1059.001    | DETECTED     | HIGH     |  95%
...
✓ Gap analysis exported to: gap_analysis/gap_analysis_report.json
```

### Step 6: Generate Sigma Rules

```bash
python3 sigma_rule_builder.py
```

**Output:**
- Sigma rules in `detection_rules/sigma_rules/`
- Validation results
- Deployment guide

### Step 7: Visualize Results

```bash
python3 maturity_heatmap.py
```

**Output:**
- `visualizations/detection_maturity_heatmap.png`
- `visualizations/coverage_breakdown.png`

---

## Troubleshooting

### Common Issues

#### Issue: Atomic Red Team tests fail with "Access Denied"

**Solution:**
```powershell
# Run PowerShell as Administrator
# Disable Windows Defender (test environment only!)
Set-MpPreference -DisableRealtimeMonitoring $true
```

#### Issue: No SIEM events detected

**Checklist:**
1. Verify Wazuh agent running:
   ```powershell
   Get-Service WazuhSvc
   ```

2. Check agent connection:
   ```bash
   # On Ubuntu
   sudo /var/ossec/bin/agent_control -l
   ```

3. Verify Sysmon logging:
   ```powershell
   Get-WinEvent -LogName "Microsoft-Windows-Sysmon/Operational" -MaxEvents 10
   ```

#### Issue: Python scripts fail with import errors

**Solution:**
```bash
# Reinstall dependencies
pip3 install --upgrade -r automation_scripts/requirements.txt
```

#### Issue: Network connectivity between VMs

**Solution:**
```bash
# Test connectivity
ping 10.0.0.20  # From Windows
ping 10.0.0.10  # From Ubuntu

# Check firewall
# On Windows:
netsh advfirewall set allprofiles state off  # Test only!

# On Ubuntu:
sudo ufw status
sudo ufw allow from 10.0.0.0/24
```

---

## Next Steps

1. **Customize Test Matrix**
   - Add techniques relevant to your organization
   - Prioritize based on threat intelligence

2. **Integrate with SOAR**
   - Set up automated response playbooks
   - Configure Slack/Teams notifications

3. **Schedule Automated Tests**
   - Deploy Kubernetes CronJob (if applicable)
   - Set up weekly validation cycles

4. **Expand Coverage**
   - Add Linux test targets
   - Include cloud environments

5. **Share Results**
   - Present findings to SOC team
   - Update detection engineering backlog

---

## Additional Resources

- **Atomic Red Team Docs:** https://github.com/redcanaryco/atomic-red-team/wiki
- **Wazuh Documentation:** https://documentation.wazuh.com/
- **Sigma Rules:** https://github.com/SigmaHQ/sigma
- **MITRE ATT&CK Navigator:** https://mitre-attack.github.io/attack-navigator/

---

## Support

If you encounter issues:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review logs in `automation_scripts/atomic_execution.log`
3. Open an issue on GitHub

---

**Happy Testing! 🎯**
