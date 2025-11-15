"""
Pytest configuration and shared fixtures
"""

import pytest
from pathlib import Path


@pytest.fixture
def test_data_dir():
    """Return path to test data directory"""
    return Path(__file__).parent / 'data'


@pytest.fixture
def sample_test_matrix():
    """Sample test matrix for testing"""
    return {
        "metadata": {
            "created": "2025-01-15T00:00:00",
            "version": "1.0",
            "framework": "MITRE ATT&CK"
        },
        "test_plan": [
            {
                "technique_id": "T1059.001",
                "technique_name": "PowerShell",
                "tactic": "Execution",
                "priority": "CRITICAL",
                "expected_detections": [
                    {
                        "source": "Sysmon",
                        "event_id": 1,
                        "description": "PowerShell process creation"
                    }
                ],
                "baseline_status": "not_tested"
            }
        ],
        "statistics": {
            "total_techniques": 1,
            "by_priority": {"CRITICAL": 1},
            "by_tactic": {"Execution": 1}
        }
    }


@pytest.fixture
def sample_detection_result():
    """Sample detection result for testing"""
    return {
        "detected": True,
        "event_count": 5,
        "baseline_delta": 5,
        "detection_sources": ["Sysmon", "Windows Event Log"],
        "confidence_score": 85,
        "notes": "Successfully detected"
    }
