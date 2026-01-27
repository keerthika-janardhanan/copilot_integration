"""Service for extracting test metrics from Playwright report files."""
from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime


class TestMetricsService:
    """Extract and aggregate test metrics from Playwright reports."""

    def __init__(self, framework_repos_path: str = "framework_repos"):
        """
        Initialize the test metrics service.
        
        Args:
            framework_repos_path: Base path to framework repositories containing reports
        """
        self.framework_repos_path = Path(framework_repos_path).absolute()
        print(f"[TestMetricsService] Initialized with path: {self.framework_repos_path}")
        print(f"[TestMetricsService] Path exists: {self.framework_repos_path.exists()}")

    def get_latest_report(self, repo_id: Optional[str] = None) -> Optional[Path]:
        """
        Get the latest report directory.
        
        Args:
            repo_id: Specific repository ID, or None to find the most recent across all repos
            
        Returns:
            Path to the latest report directory, or None if not found
        """
        if not self.framework_repos_path.exists():
            return None

        # If no repo_id specified, find the most recent across all repos
        if repo_id is None:
            all_reports = []
            for repo_dir in self.framework_repos_path.iterdir():
                if repo_dir.is_dir():
                    report_dir = repo_dir / "report"
                    if report_dir.exists():
                        for run_dir in report_dir.iterdir():
                            if run_dir.is_dir() and run_dir.name.startswith("run-"):
                                all_reports.append(run_dir)
            
            if not all_reports:
                return None
            
            # Sort by directory name (which contains timestamp)
            all_reports.sort(key=lambda p: p.name, reverse=True)
            return all_reports[0]
        
        # Find report for specific repo
        repo_dir = self.framework_repos_path / repo_id / "report"
        if not repo_dir.exists():
            return None
        
        run_dirs = [d for d in repo_dir.iterdir() if d.is_dir() and d.name.startswith("run-")]
        if not run_dirs:
            return None
        
        run_dirs.sort(key=lambda p: p.name, reverse=True)
        return run_dirs[0]

    def parse_report_json(self, report_dir: Path) -> Optional[Dict[str, Any]]:
        """
        Parse the report.json file.
        
        Args:
            report_dir: Path to the report directory
            
        Returns:
            Parsed JSON data or None if file not found
        """
        report_json = report_dir / "report.json"
        if not report_json.exists():
            return None
        
        try:
            with open(report_json, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error parsing report.json: {e}")
            return None

    def parse_junit_xml(self, report_dir: Path) -> Optional[ET.Element]:
        """
        Parse the junit.xml file.
        
        Args:
            report_dir: Path to the report directory
            
        Returns:
            Parsed XML root element or None if file not found
        """
        junit_xml = report_dir / "junit.xml"
        if not junit_xml.exists():
            return None
        
        try:
            tree = ET.parse(junit_xml)
            return tree.getroot()
        except Exception as e:
            print(f"Error parsing junit.xml: {e}")
            return None

    def extract_test_results(self, report_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract individual test results from report JSON.
        
        Args:
            report_data: Parsed report.json data
            
        Returns:
            List of test result dictionaries
        """
        tests = []
        
        def traverse_suites(suite: Dict[str, Any], file_name: str = ""):
            """Recursively traverse test suites."""
            current_file = suite.get('file', file_name)
            
            # Process specs (test cases)
            for spec in suite.get('specs', []):
                for test in spec.get('tests', []):
                    for result in test.get('results', []):
                        tests.append({
                            'title': spec.get('title', 'Unknown Test'),
                            'file': current_file,
                            'status': result.get('status', 'unknown'),
                            'duration': result.get('duration', 0),
                            'error': result.get('error', {}).get('message') if result.get('error') else None,
                            'retries': result.get('retry', 0),
                            'startTime': result.get('startTime'),
                        })
            
            # Recursively process nested suites
            for nested_suite in suite.get('suites', []):
                traverse_suites(nested_suite, current_file)
        
        # Start traversal from root suites
        for suite in report_data.get('suites', []):
            traverse_suites(suite)
        
        return tests

    def extract_junit_metrics(self, report_dir: Path) -> Dict[str, Any]:
        """
        Extract additional metrics from JUnit XML.
        
        Args:
            report_dir: Path to the report directory
            
        Returns:
            Dictionary containing JUnit-specific metrics
        """
        junit_root = self.parse_junit_xml(report_dir)
        if not junit_root:
            return {
                'browsers': {},
                'errorTypes': {'failures': 0, 'errors': 0, 'systemErrors': []},
                'testSuites': []
            }
        
        # Browser/Platform distribution
        browsers = {}
        error_types = {'failures': 0, 'errors': 0, 'systemErrors': []}
        test_suites = []
        
        for testsuite in junit_root.findall('.//testsuite'):
            suite_name = testsuite.get('name', 'Unknown')
            hostname = testsuite.get('hostname', 'unknown')
            suite_time = float(testsuite.get('time', 0))
            suite_tests = int(testsuite.get('tests', 0))
            suite_failures = int(testsuite.get('failures', 0))
            
            # Count browsers
            browsers[hostname] = browsers.get(hostname, 0) + suite_tests
            
            # Count error types
            error_types['failures'] += suite_failures
            error_types['errors'] += int(testsuite.get('errors', 0))
            
            # Test suite info
            test_suites.append({
                'name': suite_name,
                'browser': hostname,
                'duration': suite_time,
                'tests': suite_tests,
                'failures': suite_failures
            })
            
            # Extract system error messages
            for testcase in testsuite.findall('.//testcase'):
                # System errors from stderr
                stderr = testcase.find('system-err')
                if stderr is not None and stderr.text:
                    error_text = stderr.text.strip()
                    if error_text and error_text not in error_types['systemErrors']:
                        error_types['systemErrors'].append(error_text)
        
        return {
            'browsers': browsers,
            'errorTypes': error_types,
            'testSuites': test_suites
        }
        """
        Calculate comprehensive test metrics.
        
        Args:
            report_data: Parsed report.json data
            
        Returns:
            Dictionary containing aggregated metrics
        """
        stats = report_data.get('stats', {})
        tests = self.extract_test_results(report_data)
        
        total_tests = len(tests)
        passed = sum(1 for t in tests if t['status'] == 'passed')
        failed = sum(1 for t in tests if t['status'] == 'failed')
        skipped = sum(1 for t in tests if t['status'] == 'skipped')
        flaky = sum(1 for t in tests if t['status'] == 'flaky')
        
        # Calculate pass rate
        pass_rate = (passed / total_tests * 100) if total_tests > 0 else 0
        
        # Calculate average duration
        durations = [t['duration'] for t in tests if t['duration'] > 0]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        return {
            'totalTests': total_tests,
            'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'flaky': flaky,
            'duration': stats.get('duration', 0),
            'startTime': stats.get('startTime', ''),
            'tests': tests,
            'passRate': pass_rate,
            'avgDuration': avg_duration,
        }

    def get_test_metrics(self, repo_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get complete test metrics for the latest report.
        
        Args:
            repo_id: Optional repository ID to filter by
            
        Returns:
            Dictionary containing all test metrics
            
        Raises:
            FileNotFoundError: If no report data is found
        """
        print(f"[TestMetricsService] Getting metrics for repo_id: {repo_id}")
        report_dir = self.get_latest_report(repo_id)
        print(f"[TestMetricsService] Latest report dir: {report_dir}")
        
        if not report_dir:
            raise FileNotFoundError("No test reports found")
        
        report_data = self.parse_report_json(report_dir)
        if not report_data:
            raise FileNotFoundError(f"report.json not found in {report_dir}")
        
        # Extract JUnit metrics for additional insights
        junit_metrics = self.extract_junit_metrics(report_dir)
        
        print(f"[TestMetricsService] Successfully parsed report data")
        return self.calculate_metrics(report_data, junit_metrics)


# Singleton instance
_metrics_service: Optional[TestMetricsService] = None


def get_metrics_service() -> TestMetricsService:
    """Get or create the singleton test metrics service instance."""
    global _metrics_service
    if _metrics_service is None:
        _metrics_service = TestMetricsService()
    return _metrics_service
