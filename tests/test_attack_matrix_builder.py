#!/usr/bin/env python3
"""
Unit tests for attack_matrix_builder.py
"""

import pytest
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'automation_scripts'))

from attack_matrix_builder import AtomicTestMatrix


class TestAtomicTestMatrix:
    """Test cases for AtomicTestMatrix class"""

    def test_initialization(self, tmp_path):
        """Test matrix initialization"""
        matrix = AtomicTestMatrix(output_dir=str(tmp_path))
        assert matrix.output_dir == tmp_path
        assert 'metadata' in matrix.matrix
        assert 'test_plan' in matrix.matrix

    def test_build_test_matrix(self, tmp_path):
        """Test test matrix building"""
        matrix = AtomicTestMatrix(output_dir=str(tmp_path))
        result = matrix.build_test_matrix()

        assert 'test_plan' in result
        assert len(result['test_plan']) > 0
        assert 'statistics' in result

    def test_technique_coverage(self, tmp_path):
        """Test that priority techniques are included"""
        matrix = AtomicTestMatrix(output_dir=str(tmp_path))
        result = matrix.build_test_matrix()

        technique_ids = [t['technique_id'] for t in result['test_plan']]

        # Check some key techniques
        assert 'T1059.001' in technique_ids  # PowerShell
        assert 'T1548' in technique_ids  # UAC Bypass
        assert 'T1562' in technique_ids  # Impair Defenses

    def test_export_matrix(self, tmp_path):
        """Test matrix export functionality"""
        matrix = AtomicTestMatrix(output_dir=str(tmp_path))
        matrix.build_test_matrix()

        output_file = matrix.export_matrix('test_matrix.json')

        assert output_file.exists()

        # Validate JSON structure
        with open(output_file, 'r') as f:
            data = json.load(f)

        assert 'metadata' in data
        assert 'test_plan' in data
        assert 'statistics' in data

    def test_expected_detections(self, tmp_path):
        """Test expected detection definitions"""
        matrix = AtomicTestMatrix(output_dir=str(tmp_path))
        result = matrix.build_test_matrix()

        # Check first technique has detection definitions
        first_technique = result['test_plan'][0]
        assert 'expected_detections' in first_technique
        assert len(first_technique['expected_detections']) > 0

    def test_statistics_generation(self, tmp_path):
        """Test statistics are generated correctly"""
        matrix = AtomicTestMatrix(output_dir=str(tmp_path))
        result = matrix.build_test_matrix()

        stats = result['statistics']
        assert 'by_priority' in stats
        assert 'by_tactic' in stats
        assert stats['total_techniques'] > 0

    def test_summary_report_generation(self, tmp_path):
        """Test summary report generation"""
        matrix = AtomicTestMatrix(output_dir=str(tmp_path))
        matrix.build_test_matrix()

        summary = matrix.generate_summary_report()

        assert isinstance(summary, str)
        assert len(summary) > 0
        assert 'ATOMIC RED TEAM TEST MATRIX SUMMARY' in summary


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
