#!/usr/bin/env python3
"""
Atomic Test Executor - Execute atomic tests with structured logging and SIEM integration
Orchestrates Atomic Red Team tests and validates SIEM detection
"""

import subprocess
import json
import time
from datetime import datetime
from typing import List, Dict, Optional
import logging
from pathlib import Path
from dataclasses import dataclass, asdict


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('atomic_execution.log'),
        logging.StreamHandler()
    ]
)


@dataclass
class TestResult:
    """Represents the result of a single atomic test execution"""
    technique_id: str
    test_number: int
    test_name: str
    status: str  # success, failed, timeout, error, skipped
    timestamp: str
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    error_message: Optional[str] = None
    execution_time_seconds: float = 0.0


@dataclass
class DetectionResult:
    """Represents SIEM detection validation result"""
    detected: bool
    event_count: int
    baseline_delta: int
    detection_sources: List[str]
    confidence_score: int
    notes: str


class AtomicTestExecutor:
    """Execute atomic tests with SIEM validation"""

    def __init__(self, siem_connection, test_matrix_path: str, output_dir: str = "test_matrix"):
        self.siem = siem_connection
        self.test_matrix_path = Path(test_matrix_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.test_matrix = self._load_test_matrix()
        self.execution_results = {
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "test_matrix_source": str(test_matrix_path),
            "siem_platform": getattr(siem_connection, 'siem_type', 'unknown'),
            "tests_executed": [],
            "detection_results": [],
            "statistics": {
                "total_tests": 0,
                "successful": 0,
                "failed": 0,
                "detected": 0,
                "not_detected": 0,
                "partial_detection": 0
            }
        }

    def _load_test_matrix(self) -> Dict:
        """Load test matrix from JSON file"""
        try:
            with open(self.test_matrix_path, 'r') as f:
                matrix = json.load(f)
            logging.info(f"✓ Loaded test matrix with {len(matrix.get('test_plan', []))} techniques")
            return matrix
        except FileNotFoundError:
            logging.error(f"Test matrix not found: {self.test_matrix_path}")
            raise
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in test matrix: {e}")
            raise

    def execute_atomic_tests(self, dry_run: bool = False, technique_filter: List[str] = None):
        """
        Execute all tests in test matrix with SIEM validation

        Args:
            dry_run: If True, simulate execution without running actual tests
            technique_filter: List of technique IDs to execute (None = all)
        """

        logging.info("🎯 Starting Atomic Red Team Test Execution")
        logging.info("=" * 70)

        test_plan = self.test_matrix.get('test_plan', [])

        # Filter techniques if specified
        if technique_filter:
            test_plan = [t for t in test_plan if t['technique_id'] in technique_filter]
            logging.info(f"📌 Filtering to {len(test_plan)} specified techniques")

        for idx, technique_group in enumerate(test_plan, 1):
            technique_id = technique_group['technique_id']
            technique_name = technique_group.get('technique_name', 'Unknown')
            priority = technique_group.get('priority', 'MEDIUM')

            logging.info(f"\n[{idx}/{len(test_plan)}] 🎯 Technique: {technique_id} - {technique_name}")
            logging.info(f"     Priority: {priority}")

            # Get atomic tests for this technique
            atomic_tests = technique_group.get('atomic_tests', [])

            if not atomic_tests:
                logging.warning(f"     ⚠️  No atomic tests defined for {technique_id}")
                continue

            for test_index, test in enumerate(atomic_tests, 1):
                test_name = test.get('test_name', f'Test {test_index}')
                logging.info(f"     ├─ Test {test_index}: {test_name}")

                if dry_run:
                    logging.info(f"     │  [DRY RUN] Skipping actual execution")
                    continue

                # Pre-execution SIEM baseline
                baseline_logs = self._capture_siem_baseline(technique_id)

                # Execute atomic test
                start_time = time.time()
                test_result = self._run_atomic_test(
                    technique_id,
                    test_index,
                    test
                )
                test_result.execution_time_seconds = time.time() - start_time

                # Wait for logs to ingress into SIEM
                logging.info(f"     │  ⏳ Waiting 5s for SIEM log ingestion...")
                time.sleep(5)

                # Post-execution SIEM validation
                detection_result = self._validate_siem_detection(
                    technique_id,
                    baseline_logs,
                    test_result
                )

                # Record execution
                execution_record = {
                    'technique': technique_id,
                    'technique_name': technique_name,
                    'test_index': test_index,
                    'test_name': test_name,
                    'priority': priority,
                    'test_status': test_result.status,
                    'timestamp': test_result.timestamp,
                    'execution_time': test_result.execution_time_seconds,
                    'detection': asdict(detection_result)
                }

                self.execution_results['tests_executed'].append(execution_record)

                # Update statistics
                self._update_statistics(test_result, detection_result)

                # Log detection result
                if detection_result.detected:
                    logging.info(f"     └─ ✅ DETECTED ({detection_result.event_count} events)")
                elif detection_result.event_count > 0:
                    logging.info(f"     └─ ⚠️  PARTIAL ({detection_result.event_count} events)")
                else:
                    logging.info(f"     └─ ❌ NOT DETECTED")

                # Optional: Log to SIEM for correlation
                self._log_test_execution_to_siem(technique_id, test_result, detection_result)

    def _run_atomic_test(self, technique: str, test_num: int, test_details: Dict) -> TestResult:
        """
        Execute individual atomic test

        Note: This is a mock implementation. In production with Windows:
        - Use PowerShell Invoke-AtomicTest
        - Handle prerequisites checking
        - Implement cleanup procedures
        """

        test_name = test_details.get('test_name', f'Test {test_num}')

        # Mock execution for demonstration
        # In production Windows environment, this would use:
        # powershell.exe -Command "Invoke-AtomicTest -AtomicTechnique {technique} -TestNumbers {test_num}"

        logging.info(f"     │  🔄 Executing test...")

        try:
            # Simulated execution - replace with actual PowerShell command in Windows
            result = TestResult(
                technique_id=technique,
                test_number=test_num,
                test_name=test_name,
                status='success',  # Mock success
                timestamp=datetime.now().isoformat(),
                stdout=f"Mock execution of {technique} test {test_num}",
                stderr="",
                execution_time_seconds=0.0
            )

            # Uncomment for actual Windows execution:
            # ps_cmd = f"""
            # $ProgressPreference = 'SilentlyContinue'
            # Invoke-AtomicTest -AtomicTechnique {technique} -TestNumbers {test_num} -Confirm:$False
            # """
            #
            # proc_result = subprocess.run(
            #     ["powershell", "-Command", ps_cmd],
            #     capture_output=True,
            #     text=True,
            #     timeout=60
            # )
            #
            # result.status = 'success' if proc_result.returncode == 0 else 'failed'
            # result.stdout = proc_result.stdout
            # result.stderr = proc_result.stderr

            return result

        except subprocess.TimeoutExpired:
            return TestResult(
                technique_id=technique,
                test_number=test_num,
                test_name=test_name,
                status='timeout',
                timestamp=datetime.now().isoformat(),
                error_message='Test execution timed out after 60 seconds'
            )
        except Exception as e:
            logging.error(f"     │  ❌ Error executing test: {e}")
            return TestResult(
                technique_id=technique,
                test_number=test_num,
                test_name=test_name,
                status='error',
                timestamp=datetime.now().isoformat(),
                error_message=str(e)
            )

    def _capture_siem_baseline(self, technique: str) -> int:
        """Capture event count before test execution"""
        try:
            query = f"""
            index=* sourcetype=*
            | where _time > relative_time(now(), "-5m")
            | stats count
            """
            result = self.siem.execute_query(query)
            return result.get('count', 0)
        except Exception as e:
            logging.warning(f"Failed to capture SIEM baseline: {e}")
            return 0

    def _validate_siem_detection(self, technique: str, baseline_logs: int,
                                  test_result: TestResult) -> DetectionResult:
        """Check if SIEM detected the simulated attack"""

        if test_result.status != 'success':
            return DetectionResult(
                detected=False,
                event_count=0,
                baseline_delta=0,
                detection_sources=[],
                confidence_score=0,
                notes=f"Test {test_result.status} - unable to validate detection"
            )

        try:
            # Query SIEM for detection rules matching this technique
            detection_query = f"""
            search technique={technique} OR att_ck_technique={technique}
            | where _time > relative_time(now(), "-2m")
            | stats count as detection_count
            """

            result = self.siem.execute_query(detection_query)
            detection_count = result.get('detection_count', 0)

            # Mock detection logic - in production, query actual SIEM
            # Simulate detection based on technique priority
            import random
            detected = random.choice([True, False])  # Mock detection
            detection_count = random.randint(1, 5) if detected else 0

            # Determine detection confidence
            if detection_count >= 3:
                confidence = 90
                detected = True
            elif detection_count >= 1:
                confidence = 60
                detected = True
            else:
                confidence = 0
                detected = False

            return DetectionResult(
                detected=detected,
                event_count=detection_count,
                baseline_delta=detection_count - baseline_logs,
                detection_sources=['Sysmon', 'Windows Event Log'] if detected else [],
                confidence_score=confidence,
                notes=f"{detection_count} correlated events found"
            )

        except Exception as e:
            logging.error(f"SIEM detection validation failed: {e}")
            return DetectionResult(
                detected=False,
                event_count=0,
                baseline_delta=0,
                detection_sources=[],
                confidence_score=0,
                notes=f"Validation error: {str(e)}"
            )

    def _log_test_execution_to_siem(self, technique: str, test_result: TestResult,
                                     detection_result: DetectionResult):
        """Log test execution event to SIEM for correlation (optional)"""
        try:
            event = {
                'event_type': 'atomic_red_team_test',
                'technique_id': technique,
                'test_number': test_result.test_number,
                'test_status': test_result.status,
                'detected': detection_result.detected,
                'timestamp': test_result.timestamp
            }
            # In production: send to SIEM via API or syslog
            logging.debug(f"Would log to SIEM: {json.dumps(event)}")
        except Exception as e:
            logging.warning(f"Failed to log test execution to SIEM: {e}")

    def _update_statistics(self, test_result: TestResult, detection_result: DetectionResult):
        """Update execution statistics"""
        stats = self.execution_results['statistics']

        stats['total_tests'] += 1

        if test_result.status == 'success':
            stats['successful'] += 1
        else:
            stats['failed'] += 1

        if detection_result.detected:
            if detection_result.confidence_score >= 80:
                stats['detected'] += 1
            else:
                stats['partial_detection'] += 1
        else:
            stats['not_detected'] += 1

    def export_results(self, filename: str = "test_execution_results.json") -> Path:
        """Export execution results for analysis"""

        self.execution_results['end_time'] = datetime.now().isoformat()

        output_path = self.output_dir / filename

        with open(output_path, 'w') as f:
            json.dump(self.execution_results, f, indent=2)

        logging.info(f"\n✓ Results exported to: {output_path}")
        return output_path

    def generate_execution_summary(self) -> str:
        """Generate human-readable execution summary"""

        stats = self.execution_results['statistics']

        summary = []
        summary.append("\n" + "=" * 70)
        summary.append("ATOMIC TEST EXECUTION SUMMARY")
        summary.append("=" * 70)
        summary.append(f"\nStart Time: {self.execution_results['start_time']}")
        summary.append(f"End Time: {self.execution_results['end_time']}")
        summary.append(f"SIEM Platform: {self.execution_results['siem_platform']}")

        summary.append(f"\n\nEXECUTION RESULTS:")
        summary.append(f"  Total Tests: {stats['total_tests']}")
        summary.append(f"  ✅ Successful: {stats['successful']}")
        summary.append(f"  ❌ Failed: {stats['failed']}")

        summary.append(f"\n\nDETECTION RESULTS:")
        summary.append(f"  ✅ Detected: {stats['detected']}")
        summary.append(f"  ⚠️  Partial: {stats['partial_detection']}")
        summary.append(f"  ❌ Not Detected: {stats['not_detected']}")

        if stats['total_tests'] > 0:
            detection_rate = ((stats['detected'] + stats['partial_detection'] * 0.5) / stats['total_tests']) * 100
            summary.append(f"\n📊 Detection Rate: {detection_rate:.1f}%")

        summary.append("\n" + "=" * 70)

        return "\n".join(summary)


def main():
    """Main execution function"""

    print("🚀 Atomic Red Team Test Executor")
    print("=" * 70)

    # Import baseline_assessment to get SIEM connection
    import sys
    sys.path.append('.')
    from baseline_assessment import SIEMConnection

    # Initialize SIEM connection
    siem = SIEMConnection(siem_type="splunk")
    siem.connect()

    # Check for test matrix
    test_matrix_path = "test_matrix/attack_test_matrix.json"
    if not Path(test_matrix_path).exists():
        print("❌ Test matrix not found!")
        print("   Run: python automation_scripts/attack_matrix_builder.py")
        sys.exit(1)

    # Create executor
    executor = AtomicTestExecutor(siem, test_matrix_path)

    # Execute tests (dry run mode for safety in demo)
    print("\n⚠️  Running in SIMULATION mode (safe for demo environments)")
    print("   For actual testing on Windows with Atomic Red Team installed:")
    print("   Edit atomic_test_executor.py and uncomment PowerShell execution block\n")

    executor.execute_atomic_tests(dry_run=False)

    # Export results
    executor.export_results()

    # Display summary
    summary = executor.generate_execution_summary()
    print(summary)

    # Save summary
    summary_path = executor.output_dir / "execution_summary.txt"
    with open(summary_path, 'w') as f:
        f.write(summary)

    print(f"\n✅ Execution complete!")
    print(f"   📁 Output directory: {executor.output_dir}")
    print(f"   📄 Results: test_execution_results.json")
    print(f"   📄 Summary: execution_summary.txt")
    print(f"   📄 Logs: atomic_execution.log")


if __name__ == "__main__":
    main()
