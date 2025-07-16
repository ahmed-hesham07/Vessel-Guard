#!/usr/bin/env python3
"""
Log management utilities for Vessel Guard API.

Provides functions to rotate, archive, and analyze log files.
"""

import os
import gzip
import shutil
import datetime
from pathlib import Path
from typing import Dict, List, Any
import json
import re

from app.core.config import settings


class LogManager:
    """Manages log files for the Vessel Guard API."""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
    
    def rotate_logs(self, max_size_mb: int = 10, max_files: int = 5):
        """Rotate log files when they exceed size limit."""
        for log_file in self.log_dir.glob("*.log"):
            if log_file.stat().st_size > max_size_mb * 1024 * 1024:
                self._rotate_file(log_file, max_files)
    
    def _rotate_file(self, log_file: Path, max_files: int):
        """Rotate a specific log file."""
        # Move existing rotated files
        for i in range(max_files - 1, 0, -1):
            old_file = log_file.with_suffix(f".log.{i}")
            new_file = log_file.with_suffix(f".log.{i + 1}")
            if old_file.exists():
                if new_file.exists():
                    new_file.unlink()
                old_file.rename(new_file)
        
        # Rotate current file
        rotated_file = log_file.with_suffix(".log.1")
        if rotated_file.exists():
            rotated_file.unlink()
        log_file.rename(rotated_file)
        
        # Create new empty log file
        log_file.touch()
    
    def compress_old_logs(self, days_old: int = 7):
        """Compress log files older than specified days."""
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_old)
        
        for log_file in self.log_dir.glob("*.log.*"):
            if log_file.stat().st_mtime < cutoff_date.timestamp():
                compressed_file = log_file.with_suffix(log_file.suffix + ".gz")
                
                with open(log_file, 'rb') as f_in:
                    with gzip.open(compressed_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                log_file.unlink()
                print(f"Compressed {log_file} to {compressed_file}")
    
    def clean_old_logs(self, days_old: int = 30):
        """Remove compressed log files older than specified days."""
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_old)
        
        for log_file in self.log_dir.glob("*.gz"):
            if log_file.stat().st_mtime < cutoff_date.timestamp():
                log_file.unlink()
                print(f"Removed old log file: {log_file}")
    
    def get_log_files(self) -> List[Path]:
        """Get list of all log files."""
        return list(self.log_dir.glob("*.log*"))
    
    def get_log_stats(self) -> Dict[str, Any]:
        """Get statistics about log files."""
        stats = {
            'total_files': 0,
            'total_size_mb': 0,
            'files_by_type': {},
            'oldest_file': None,
            'newest_file': None
        }
        
        oldest_time = None
        newest_time = None
        
        for log_file in self.get_log_files():
            stats['total_files'] += 1
            size_mb = log_file.stat().st_size / (1024 * 1024)
            stats['total_size_mb'] += size_mb
            
            # Count by type
            file_type = log_file.stem.replace('.log', '')
            if file_type not in stats['files_by_type']:
                stats['files_by_type'][file_type] = {'count': 0, 'size_mb': 0}
            stats['files_by_type'][file_type]['count'] += 1
            stats['files_by_type'][file_type]['size_mb'] += size_mb
            
            # Track oldest and newest
            mtime = log_file.stat().st_mtime
            if oldest_time is None or mtime < oldest_time:
                oldest_time = mtime
                stats['oldest_file'] = str(log_file)
            if newest_time is None or mtime > newest_time:
                newest_time = mtime
                stats['newest_file'] = str(log_file)
        
        stats['total_size_mb'] = round(stats['total_size_mb'], 2)
        for file_type in stats['files_by_type']:
            stats['files_by_type'][file_type]['size_mb'] = round(
                stats['files_by_type'][file_type]['size_mb'], 2
            )
        
        return stats


class LogAnalyzer:
    """Analyzes log files for errors and patterns."""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
    
    def analyze_errors(self, hours_back: int = 24) -> Dict[str, Any]:
        """Analyze errors from the last N hours."""
        cutoff_time = datetime.datetime.now() - datetime.timedelta(hours=hours_back)
        
        error_analysis = {
            'total_errors': 0,
            'error_types': {},
            'error_locations': {},
            'error_timeline': {},
            'critical_errors': [],
            'most_common_errors': []
        }
        
        # Analyze main error log
        error_log = self.log_dir / "errors.log"
        if error_log.exists():
            with open(error_log, 'r') as f:
                for line in f:
                    try:
                        # Try to parse JSON log entry
                        if line.strip().startswith('{'):
                            log_entry = json.loads(line.strip())
                            log_time = datetime.datetime.fromisoformat(
                                log_entry.get('timestamp', '').replace('Z', '+00:00')
                            )
                            
                            if log_time >= cutoff_time:
                                self._process_error_entry(log_entry, error_analysis)
                        else:
                            # Handle non-JSON log entries
                            self._process_text_error_entry(line, error_analysis)
                    except Exception as e:
                        # Skip malformed log entries
                        continue
        
        # Sort most common errors
        error_analysis['most_common_errors'] = sorted(
            error_analysis['error_types'].items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )[:10]
        
        return error_analysis
    
    def _process_error_entry(self, log_entry: Dict[str, Any], analysis: Dict[str, Any]):
        """Process a JSON error log entry."""
        analysis['total_errors'] += 1
        
        error_type = log_entry.get('error_type', 'unknown')
        location = log_entry.get('location', 'unknown')
        severity = log_entry.get('severity', 'ERROR')
        
        # Count error types
        if error_type not in analysis['error_types']:
            analysis['error_types'][error_type] = {'count': 0, 'severity': severity}
        analysis['error_types'][error_type]['count'] += 1
        
        # Count error locations
        if location not in analysis['error_locations']:
            analysis['error_locations'][location] = 0
        analysis['error_locations'][location] += 1
        
        # Track critical errors
        if severity == 'CRITICAL':
            analysis['critical_errors'].append({
                'timestamp': log_entry.get('timestamp'),
                'error_type': error_type,
                'location': location,
                'message': log_entry.get('message', '')
            })
    
    def _process_text_error_entry(self, line: str, analysis: Dict[str, Any]):
        """Process a text-based error log entry."""
        if 'ERROR' in line or 'CRITICAL' in line:
            analysis['total_errors'] += 1
            
            # Extract error type from line
            error_type = 'unknown'
            if 'ERROR' in line:
                error_type = 'text_error'
            elif 'CRITICAL' in line:
                error_type = 'text_critical'
            
            if error_type not in analysis['error_types']:
                analysis['error_types'][error_type] = {'count': 0, 'severity': 'ERROR'}
            analysis['error_types'][error_type]['count'] += 1
    
    def get_error_trends(self, days_back: int = 7) -> Dict[str, Any]:
        """Get error trends over the last N days."""
        trends = {
            'daily_error_counts': {},
            'error_type_trends': {},
            'improvement_areas': []
        }
        
        # This would require more sophisticated log parsing
        # For now, return basic structure
        return trends
    
    def check_log_health(self) -> Dict[str, Any]:
        """Check the health of the logging system."""
        health = {
            'status': 'healthy',
            'issues': [],
            'recommendations': []
        }
        
        # Check if log files exist
        required_logs = ['vessel_guard.log', 'errors.log', 'security.log']
        for log_name in required_logs:
            log_file = self.log_dir / log_name
            if not log_file.exists():
                health['issues'].append(f"Missing log file: {log_name}")
                health['status'] = 'warning'
        
        # Check log file sizes
        for log_file in self.log_dir.glob("*.log"):
            size_mb = log_file.stat().st_size / (1024 * 1024)
            if size_mb > 50:  # 50MB threshold
                health['issues'].append(f"Large log file: {log_file.name} ({size_mb:.1f}MB)")
                health['recommendations'].append(f"Consider rotating {log_file.name}")
        
        # Check for recent errors
        error_analysis = self.analyze_errors(hours_back=1)
        if error_analysis['total_errors'] > 10:
            health['issues'].append(f"High error rate: {error_analysis['total_errors']} errors in last hour")
            health['status'] = 'error'
        
        return health


def create_log_report(output_file: str = None) -> str:
    """Create a comprehensive log report."""
    log_manager = LogManager()
    log_analyzer = LogAnalyzer()
    
    report = {
        'generated_at': datetime.datetime.now().isoformat(),
        'log_stats': log_manager.get_log_stats(),
        'error_analysis': log_analyzer.analyze_errors(hours_back=24),
        'system_health': log_analyzer.check_log_health()
    }
    
    report_json = json.dumps(report, indent=2)
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(report_json)
        print(f"Log report written to {output_file}")
    
    return report_json


def maintenance_routine():
    """Perform regular log maintenance tasks."""
    print("Starting log maintenance routine...")
    
    log_manager = LogManager()
    
    # Rotate large log files
    log_manager.rotate_logs(max_size_mb=10, max_files=5)
    
    # Compress old logs
    log_manager.compress_old_logs(days_old=7)
    
    # Clean very old logs
    log_manager.clean_old_logs(days_old=30)
    
    # Generate health report
    log_analyzer = LogAnalyzer()
    health = log_analyzer.check_log_health()
    
    print("Log maintenance completed.")
    print(f"System health: {health['status']}")
    
    if health['issues']:
        print("Issues found:")
        for issue in health['issues']:
            print(f"  - {issue}")
    
    if health['recommendations']:
        print("Recommendations:")
        for rec in health['recommendations']:
            print(f"  - {rec}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "maintenance":
            maintenance_routine()
        elif command == "report":
            output_file = sys.argv[2] if len(sys.argv) > 2 else "log_report.json"
            create_log_report(output_file)
        elif command == "stats":
            log_manager = LogManager()
            stats = log_manager.get_log_stats()
            print(json.dumps(stats, indent=2))
        else:
            print(f"Unknown command: {command}")
            print("Available commands: maintenance, report, stats")
    else:
        print("Usage: python log_management.py [maintenance|report|stats]")
