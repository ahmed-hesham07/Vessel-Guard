"""
Comprehensive test runner for the Vessel Guard backend.

Provides test execution with coverage reporting, performance
benchmarking, and detailed test analysis.
"""

import os
import sys
import argparse
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Any

import pytest
import coverage


class TestRunner:
    """Enhanced test runner with comprehensive reporting."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_dir = self.project_root / "tests"
        self.coverage_dir = self.project_root / "htmlcov"
        self.reports_dir = self.project_root / "test_reports"
        
        # Ensure reports directory exists
        self.reports_dir.mkdir(exist_ok=True)
    
    def run_unit_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """Run unit tests with coverage."""
        print("🧪 Running unit tests...")
        
        # Coverage configuration
        cov = coverage.Coverage(
            source=['app'],
            omit=[
                '*/tests/*',
                '*/venv/*',
                '*/migrations/*',
                '*/alembic/*',
                '*/__pycache__/*'
            ]
        )
        
        cov.start()
        
        # Run unit tests
        args = [
            'python', '-m', 'pytest',
            str(self.test_dir / 'test_models.py'),
            str(self.test_dir / 'test_services.py'),
            str(self.test_dir / 'test_calculations.py'),
            '--tb=short',
            '--disable-warnings',
            f'--junitxml={self.reports_dir}/unit_tests.xml'
        ]
        
        if verbose:
            args.append('-v')
        
        start_time = time.time()
        result = subprocess.run(args, capture_output=True, text=True)
        end_time = time.time()
        
        cov.stop()
        cov.save()
        
        # Generate coverage report
        coverage_percent = cov.report()
        cov.html_report(directory=str(self.coverage_dir))
        
        return {
            'success': result.returncode == 0,
            'duration': end_time - start_time,
            'coverage': coverage_percent,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
    
    def run_integration_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """Run integration tests."""
        print("🔗 Running integration tests...")
        
        args = [
            'python', '-m', 'pytest',
            str(self.test_dir / 'test_integration.py'),
            '--tb=short',
            '--disable-warnings',
            f'--junitxml={self.reports_dir}/integration_tests.xml'
        ]
        
        if verbose:
            args.append('-v')
        
        start_time = time.time()
        result = subprocess.run(args, capture_output=True, text=True)
        end_time = time.time()
        
        return {
            'success': result.returncode == 0,
            'duration': end_time - start_time,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
    
    def run_api_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """Run API endpoint tests."""
        print("🌐 Running API tests...")
        
        args = [
            'python', '-m', 'pytest',
            str(self.test_dir / 'test_api.py'),
            str(self.test_dir / 'test_auth.py'),
            '--tb=short',
            '--disable-warnings',
            f'--junitxml={self.reports_dir}/api_tests.xml'
        ]
        
        if verbose:
            args.append('-v')
        
        start_time = time.time()
        result = subprocess.run(args, capture_output=True, text=True)
        end_time = time.time()
        
        return {
            'success': result.returncode == 0,
            'duration': end_time - start_time,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
    
    def run_performance_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """Run performance tests."""
        print("⚡ Running performance tests...")
        
        args = [
            'python', '-m', 'pytest',
            str(self.test_dir / 'test_performance.py'),
            '-m', 'performance',
            '--tb=short',
            '--disable-warnings',
            f'--junitxml={self.reports_dir}/performance_tests.xml'
        ]
        
        if verbose:
            args.append('-v')
        
        start_time = time.time()
        result = subprocess.run(args, capture_output=True, text=True)
        end_time = time.time()
        
        return {
            'success': result.returncode == 0,
            'duration': end_time - start_time,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
    
    def run_security_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """Run security-focused tests."""
        print("🔒 Running security tests...")
        
        # Security tests using bandit
        bandit_args = [
            'bandit', '-r', 'app/',
            '-f', 'json',
            '-o', str(self.reports_dir / 'security_report.json'),
            '--exclude', 'tests/*'
        ]
        
        start_time = time.time()
        bandit_result = subprocess.run(bandit_args, capture_output=True, text=True)
        
        # Run auth-specific tests
        auth_args = [
            'python', '-m', 'pytest',
            str(self.test_dir / 'test_auth.py'),
            '-k', 'security',
            '--tb=short',
            '--disable-warnings'
        ]
        
        if verbose:
            auth_args.append('-v')
        
        auth_result = subprocess.run(auth_args, capture_output=True, text=True)
        end_time = time.time()
        
        return {
            'success': bandit_result.returncode == 0 and auth_result.returncode == 0,
            'duration': end_time - start_time,
            'bandit_output': bandit_result.stdout,
            'auth_output': auth_result.stdout,
            'bandit_errors': bandit_result.stderr,
            'auth_errors': auth_result.stderr
        }
    
    def run_all_tests(self, verbose: bool = False, include_performance: bool = False) -> Dict[str, Any]:
        """Run all test suites."""
        print("🚀 Running comprehensive test suite...")
        
        overall_start = time.time()
        results = {}
        
        # Run test suites
        results['unit'] = self.run_unit_tests(verbose)
        results['integration'] = self.run_integration_tests(verbose)
        results['api'] = self.run_api_tests(verbose)
        results['security'] = self.run_security_tests(verbose)
        
        if include_performance:
            results['performance'] = self.run_performance_tests(verbose)
        
        overall_end = time.time()
        
        # Summary
        total_duration = overall_end - overall_start
        success_count = sum(1 for r in results.values() if r['success'])
        total_count = len(results)
        
        summary = {
            'total_duration': total_duration,
            'success_count': success_count,
            'total_count': total_count,
            'success_rate': success_count / total_count * 100,
            'results': results
        }
        
        self.generate_summary_report(summary)
        
        return summary
    
    def generate_summary_report(self, summary: Dict[str, Any]):
        """Generate a comprehensive test summary report."""
        report_file = self.reports_dir / 'test_summary.txt'
        
        with open(report_file, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("VESSEL GUARD TEST SUMMARY REPORT\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Test Execution Time: {summary['total_duration']:.2f} seconds\n")
            f.write(f"Success Rate: {summary['success_rate']:.1f}% ({summary['success_count']}/{summary['total_count']})\n\n")
            
            f.write("TEST SUITE RESULTS:\n")
            f.write("-" * 40 + "\n")
            
            for suite_name, result in summary['results'].items():
                status = "✅ PASS" if result['success'] else "❌ FAIL"
                duration = result.get('duration', 0)
                
                f.write(f"{suite_name.upper()}: {status} ({duration:.2f}s)\n")
                
                if suite_name == 'unit' and 'coverage' in result:
                    f.write(f"  Coverage: {result['coverage']:.1f}%\n")
                
                if not result['success']:
                    f.write(f"  Errors: {result.get('stderr', 'Unknown error')}\n")
                
                f.write("\n")
            
            f.write("RECOMMENDATIONS:\n")
            f.write("-" * 40 + "\n")
            
            # Generate recommendations based on results
            if summary['results']['unit']['success']:
                coverage = summary['results']['unit'].get('coverage', 0)
                if coverage < 85:
                    f.write(f"• Increase test coverage from {coverage:.1f}% to target 85%+\n")
                else:
                    f.write(f"• Excellent test coverage at {coverage:.1f}%\n")
            
            if not all(r['success'] for r in summary['results'].values()):
                f.write("• Fix failing tests before deployment\n")
            
            if summary['total_duration'] > 300:  # 5 minutes
                f.write("• Consider optimizing slow tests for faster feedback\n")
            
            f.write("\nReport generated at: " + time.strftime("%Y-%m-%d %H:%M:%S"))
        
        print(f"📊 Summary report generated: {report_file}")
    
    def quick_test(self, pattern: str = None, verbose: bool = False) -> bool:
        """Run a quick subset of tests for fast feedback."""
        print("⚡ Running quick tests...")
        
        args = ['python', '-m', 'pytest', '--tb=short', '--disable-warnings']
        
        if pattern:
            args.extend(['-k', pattern])
        else:
            # Run a subset of critical tests
            args.extend([
                str(self.test_dir / 'test_models.py'),
                str(self.test_dir / 'test_auth.py::TestAuthentication::test_login'),
                str(self.test_dir / 'test_api.py::TestProjectAPI::test_create_project')
            ])
        
        if verbose:
            args.append('-v')
        
        result = subprocess.run(args)
        return result.returncode == 0
    
    def test_with_database_reset(self, verbose: bool = False) -> Dict[str, Any]:
        """Run tests with fresh database."""
        print("🗄️  Running tests with database reset...")
        
        # Reset test database
        try:
            from app.db.init_db import reset_database
            reset_database()
            print("Database reset successful")
        except Exception as e:
            print(f"Database reset failed: {e}")
        
        return self.run_all_tests(verbose)


def main():
    """Main test runner entry point."""
    parser = argparse.ArgumentParser(description="Vessel Guard Test Runner")
    
    parser.add_argument('--quick', action='store_true', help='Run quick tests only')
    parser.add_argument('--unit', action='store_true', help='Run unit tests only')
    parser.add_argument('--integration', action='store_true', help='Run integration tests only')
    parser.add_argument('--api', action='store_true', help='Run API tests only')
    parser.add_argument('--performance', action='store_true', help='Run performance tests only')
    parser.add_argument('--security', action='store_true', help='Run security tests only')
    parser.add_argument('--all', action='store_true', help='Run all tests')
    parser.add_argument('--with-performance', action='store_true', help='Include performance tests in full run')
    parser.add_argument('--reset-db', action='store_true', help='Reset database before testing')
    parser.add_argument('--pattern', '-k', help='Test pattern to match')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    try:
        if args.quick:
            success = runner.quick_test(args.pattern, args.verbose)
            sys.exit(0 if success else 1)
        
        elif args.unit:
            result = runner.run_unit_tests(args.verbose)
        
        elif args.integration:
            result = runner.run_integration_tests(args.verbose)
        
        elif args.api:
            result = runner.run_api_tests(args.verbose)
        
        elif args.performance:
            result = runner.run_performance_tests(args.verbose)
        
        elif args.security:
            result = runner.run_security_tests(args.verbose)
        
        elif args.all or args.reset_db or args.with_performance:
            if args.reset_db:
                result = runner.test_with_database_reset(args.verbose)
            else:
                result = runner.run_all_tests(args.verbose, args.with_performance)
        
        else:
            # Default: run core tests
            result = runner.run_all_tests(args.verbose)
        
        # Exit with appropriate code
        if isinstance(result, dict):
            if 'success_rate' in result:
                success = result['success_rate'] == 100
            else:
                success = result.get('success', False)
        else:
            success = result
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n❌ Test execution interrupted by user")
        sys.exit(1)
    
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()