#!/usr/bin/env python3
"""
CI/CD Pipeline Monitoring Script

Monitors the CI/CD pipeline status, collects metrics,
and provides reporting capabilities for deployment tracking.
"""

import os
import sys
import json
import time
import requests
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline-monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class PipelineRun:
    """Represents a CI/CD pipeline run."""
    id: str
    status: str
    conclusion: str
    head_sha: str
    head_branch: str
    created_at: datetime
    updated_at: datetime
    html_url: str
    jobs: List[Dict[str, Any]]


@dataclass
class DeploymentMetrics:
    """Deployment metrics and statistics."""
    total_deployments: int
    successful_deployments: int
    failed_deployments: int
    average_duration_minutes: float
    success_rate: float
    deployments_per_day: float
    last_deployment: Optional[datetime]
    mean_time_to_recovery_hours: float


class GitHubMonitor:
    """Monitor GitHub Actions pipeline."""
    
    def __init__(self, owner: str, repo: str, token: str):
        self.owner = owner
        self.repo = repo
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def get_workflow_runs(self, workflow_id: str = "ci-cd.yml", 
                         per_page: int = 50) -> List[PipelineRun]:
        """Get recent workflow runs."""
        try:
            url = f"{self.base_url}/repos/{self.owner}/{self.repo}/actions/workflows/{workflow_id}/runs"
            params = {"per_page": per_page, "status": "completed"}
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            runs = []
            
            for run in data.get("workflow_runs", []):
                # Get jobs for this run
                jobs = self.get_workflow_jobs(run["id"])
                
                pipeline_run = PipelineRun(
                    id=str(run["id"]),
                    status=run["status"],
                    conclusion=run["conclusion"],
                    head_sha=run["head_sha"],
                    head_branch=run["head_branch"],
                    created_at=datetime.fromisoformat(run["created_at"].replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(run["updated_at"].replace('Z', '+00:00')),
                    html_url=run["html_url"],
                    jobs=jobs
                )
                runs.append(pipeline_run)
            
            return runs
            
        except Exception as e:
            logger.error(f"Failed to get workflow runs: {e}")
            return []
    
    def get_workflow_jobs(self, run_id: str) -> List[Dict[str, Any]]:
        """Get jobs for a specific workflow run."""
        try:
            url = f"{self.base_url}/repos/{self.owner}/{self.repo}/actions/runs/{run_id}/jobs"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            return data.get("jobs", [])
            
        except Exception as e:
            logger.error(f"Failed to get jobs for run {run_id}: {e}")
            return []
    
    def get_deployment_metrics(self, days: int = 30) -> DeploymentMetrics:
        """Calculate deployment metrics over the specified period."""
        try:
            # Get deployments from the last N days
            since = datetime.now() - timedelta(days=days)
            
            url = f"{self.base_url}/repos/{self.owner}/{self.repo}/deployments"
            params = {"environment": "production", "per_page": 100}
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            deployments = response.json()
            
            # Filter deployments within the time period
            recent_deployments = [
                d for d in deployments 
                if datetime.fromisoformat(d["created_at"].replace('Z', '+00:00')) > since
            ]
            
            # Get deployment statuses
            successful = 0
            failed = 0
            durations = []
            
            for deployment in recent_deployments:
                status = self.get_deployment_status(deployment["id"])
                if status == "success":
                    successful += 1
                elif status == "failure":
                    failed += 1
                
                # Calculate duration if available
                if "updated_at" in deployment and "created_at" in deployment:
                    created = datetime.fromisoformat(deployment["created_at"].replace('Z', '+00:00'))
                    updated = datetime.fromisoformat(deployment["updated_at"].replace('Z', '+00:00'))
                    duration = (updated - created).total_seconds() / 60  # minutes
                    durations.append(duration)
            
            total = len(recent_deployments)
            success_rate = (successful / total * 100) if total > 0 else 0
            avg_duration = sum(durations) / len(durations) if durations else 0
            deployments_per_day = total / days if days > 0 else 0
            
            last_deployment = None
            if recent_deployments:
                last_deployment = datetime.fromisoformat(
                    recent_deployments[0]["created_at"].replace('Z', '+00:00')
                )
            
            # Calculate MTTR (simplified - time between failure and next success)
            mttr = self.calculate_mttr(recent_deployments)
            
            return DeploymentMetrics(
                total_deployments=total,
                successful_deployments=successful,
                failed_deployments=failed,
                average_duration_minutes=avg_duration,
                success_rate=success_rate,
                deployments_per_day=deployments_per_day,
                last_deployment=last_deployment,
                mean_time_to_recovery_hours=mttr
            )
            
        except Exception as e:
            logger.error(f"Failed to get deployment metrics: {e}")
            return DeploymentMetrics(0, 0, 0, 0, 0, 0, None, 0)
    
    def get_deployment_status(self, deployment_id: str) -> str:
        """Get status of a specific deployment."""
        try:
            url = f"{self.base_url}/repos/{self.owner}/{self.repo}/deployments/{deployment_id}/statuses"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            statuses = response.json()
            if statuses:
                return statuses[0]["state"]  # Most recent status
            return "unknown"
            
        except Exception as e:
            logger.error(f"Failed to get deployment status: {e}")
            return "unknown"
    
    def calculate_mttr(self, deployments: List[Dict[str, Any]]) -> float:
        """Calculate Mean Time to Recovery in hours."""
        try:
            # This is a simplified MTTR calculation
            # In practice, you'd want more sophisticated failure detection
            recovery_times = []
            
            for i in range(len(deployments) - 1):
                current = deployments[i]
                next_deployment = deployments[i + 1]
                
                current_status = self.get_deployment_status(current["id"])
                next_status = self.get_deployment_status(next_deployment["id"])
                
                if current_status == "failure" and next_status == "success":
                    current_time = datetime.fromisoformat(current["created_at"].replace('Z', '+00:00'))
                    next_time = datetime.fromisoformat(next_deployment["created_at"].replace('Z', '+00:00'))
                    recovery_time = (next_time - current_time).total_seconds() / 3600  # hours
                    recovery_times.append(recovery_time)
            
            return sum(recovery_times) / len(recovery_times) if recovery_times else 0
            
        except Exception as e:
            logger.error(f"Failed to calculate MTTR: {e}")
            return 0


class PipelineReporter:
    """Generate reports from pipeline monitoring data."""
    
    def __init__(self, monitor: GitHubMonitor):
        self.monitor = monitor
    
    def generate_status_report(self) -> Dict[str, Any]:
        """Generate current pipeline status report."""
        runs = self.monitor.get_workflow_runs(per_page=10)
        metrics = self.monitor.get_deployment_metrics(days=30)
        
        # Latest run status
        latest_run = runs[0] if runs else None
        
        # Job success rates
        job_stats = self.calculate_job_statistics(runs)
        
        # Trends
        trends = self.calculate_trends(runs)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "latest_run": {
                "status": latest_run.status if latest_run else "unknown",
                "conclusion": latest_run.conclusion if latest_run else "unknown",
                "branch": latest_run.head_branch if latest_run else "unknown",
                "url": latest_run.html_url if latest_run else None,
                "created_at": latest_run.created_at.isoformat() if latest_run else None
            },
            "metrics": asdict(metrics),
            "job_statistics": job_stats,
            "trends": trends,
            "recommendations": self.generate_recommendations(metrics, job_stats)
        }
        
        return report
    
    def calculate_job_statistics(self, runs: List[PipelineRun]) -> Dict[str, Any]:
        """Calculate statistics for individual jobs."""
        job_stats = {}
        
        for run in runs:
            for job in run.jobs:
                job_name = job.get("name", "unknown")
                
                if job_name not in job_stats:
                    job_stats[job_name] = {
                        "total_runs": 0,
                        "successful_runs": 0,
                        "failed_runs": 0,
                        "average_duration_seconds": 0,
                        "durations": []
                    }
                
                job_stats[job_name]["total_runs"] += 1
                
                if job.get("conclusion") == "success":
                    job_stats[job_name]["successful_runs"] += 1
                elif job.get("conclusion") == "failure":
                    job_stats[job_name]["failed_runs"] += 1
                
                # Calculate duration
                if job.get("started_at") and job.get("completed_at"):
                    started = datetime.fromisoformat(job["started_at"].replace('Z', '+00:00'))
                    completed = datetime.fromisoformat(job["completed_at"].replace('Z', '+00:00'))
                    duration = (completed - started).total_seconds()
                    job_stats[job_name]["durations"].append(duration)
        
        # Calculate averages and success rates
        for job_name, stats in job_stats.items():
            if stats["durations"]:
                stats["average_duration_seconds"] = sum(stats["durations"]) / len(stats["durations"])
            del stats["durations"]  # Remove raw durations from output
            
            if stats["total_runs"] > 0:
                stats["success_rate"] = (stats["successful_runs"] / stats["total_runs"]) * 100
            else:
                stats["success_rate"] = 0
        
        return job_stats
    
    def calculate_trends(self, runs: List[PipelineRun]) -> Dict[str, Any]:
        """Calculate pipeline trends."""
        if len(runs) < 2:
            return {"insufficient_data": True}
        
        # Success rate trend (last 10 vs previous 10)
        recent_runs = runs[:10]
        older_runs = runs[10:20] if len(runs) >= 20 else []
        
        recent_success_rate = len([r for r in recent_runs if r.conclusion == "success"]) / len(recent_runs) * 100
        older_success_rate = len([r for r in older_runs if r.conclusion == "success"]) / len(older_runs) * 100 if older_runs else recent_success_rate
        
        # Duration trend
        recent_durations = []
        older_durations = []
        
        for run in recent_runs:
            duration = (run.updated_at - run.created_at).total_seconds() / 60  # minutes
            recent_durations.append(duration)
        
        for run in older_runs:
            duration = (run.updated_at - run.created_at).total_seconds() / 60
            older_durations.append(duration)
        
        recent_avg_duration = sum(recent_durations) / len(recent_durations) if recent_durations else 0
        older_avg_duration = sum(older_durations) / len(older_durations) if older_durations else recent_avg_duration
        
        return {
            "success_rate_change": recent_success_rate - older_success_rate,
            "duration_change_minutes": recent_avg_duration - older_avg_duration,
            "recent_success_rate": recent_success_rate,
            "recent_average_duration_minutes": recent_avg_duration
        }
    
    def generate_recommendations(self, metrics: DeploymentMetrics, 
                               job_stats: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Success rate recommendations
        if metrics.success_rate < 95:
            recommendations.append(f"🔴 Deployment success rate ({metrics.success_rate:.1f}%) is below target (95%). Investigate failing deployments.")
        
        # Duration recommendations
        if metrics.average_duration_minutes > 30:
            recommendations.append(f"⏱️ Average deployment duration ({metrics.average_duration_minutes:.1f} min) is high. Consider optimizing pipeline.")
        
        # Job-specific recommendations
        for job_name, stats in job_stats.items():
            if stats["success_rate"] < 90:
                recommendations.append(f"🔧 Job '{job_name}' has low success rate ({stats['success_rate']:.1f}%). Review and stabilize.")
            
            if stats["average_duration_seconds"] > 1800:  # 30 minutes
                duration_minutes = stats["average_duration_seconds"] / 60
                recommendations.append(f"⚡ Job '{job_name}' takes {duration_minutes:.1f} minutes. Consider optimization.")
        
        # Recovery time recommendations
        if metrics.mean_time_to_recovery_hours > 4:
            recommendations.append(f"🚨 Mean time to recovery ({metrics.mean_time_to_recovery_hours:.1f} hours) is high. Improve monitoring and response.")
        
        # Deployment frequency
        if metrics.deployments_per_day < 1:
            recommendations.append("📈 Low deployment frequency. Consider implementing continuous deployment.")
        
        if not recommendations:
            recommendations.append("✅ All metrics are within acceptable ranges. Keep up the good work!")
        
        return recommendations
    
    def save_report(self, report: Dict[str, Any], filename: str = None):
        """Save report to file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pipeline_report_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            logger.info(f"Report saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
    
    def print_summary(self, report: Dict[str, Any]):
        """Print a human-readable summary."""
        print("\n" + "=" * 60)
        print("🚀 VESSEL GUARD CI/CD PIPELINE REPORT")
        print("=" * 60)
        
        latest = report["latest_run"]
        metrics = report["metrics"]
        
        # Latest run status
        status_emoji = "✅" if latest["conclusion"] == "success" else "❌"
        print(f"\n📊 Latest Run: {status_emoji} {latest['status']} ({latest['conclusion']})")
        print(f"   Branch: {latest['branch']}")
        print(f"   Time: {latest['created_at']}")
        
        # Key metrics
        print(f"\n📈 Deployment Metrics (Last 30 Days):")
        print(f"   Success Rate: {metrics['success_rate']:.1f}%")
        print(f"   Total Deployments: {metrics['total_deployments']}")
        print(f"   Average Duration: {metrics['average_duration_minutes']:.1f} minutes")
        print(f"   Deployments/Day: {metrics['deployments_per_day']:.1f}")
        print(f"   MTTR: {metrics['mean_time_to_recovery_hours']:.1f} hours")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        for rec in report["recommendations"]:
            print(f"   {rec}")
        
        print("\n" + "=" * 60)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Monitor CI/CD Pipeline")
    parser.add_argument("--owner", required=True, help="GitHub repository owner")
    parser.add_argument("--repo", required=True, help="GitHub repository name")
    parser.add_argument("--token", help="GitHub token (or use GITHUB_TOKEN env var)")
    parser.add_argument("--days", type=int, default=30, help="Days to analyze")
    parser.add_argument("--output", help="Output file for JSON report")
    parser.add_argument("--watch", action="store_true", help="Continuously monitor")
    parser.add_argument("--interval", type=int, default=300, help="Watch interval in seconds")
    
    args = parser.parse_args()
    
    # Get GitHub token
    token = args.token or os.environ.get("GITHUB_TOKEN")
    if not token:
        logger.error("GitHub token is required. Use --token or set GITHUB_TOKEN environment variable.")
        sys.exit(1)
    
    # Initialize monitor and reporter
    monitor = GitHubMonitor(args.owner, args.repo, token)
    reporter = PipelineReporter(monitor)
    
    def generate_and_display_report():
        """Generate and display a report."""
        try:
            logger.info("Generating pipeline report...")
            report = reporter.generate_status_report()
            
            reporter.print_summary(report)
            
            if args.output:
                reporter.save_report(report, args.output)
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            return None
    
    if args.watch:
        logger.info(f"Starting continuous monitoring (interval: {args.interval}s)")
        try:
            while True:
                generate_and_display_report()
                logger.info(f"Waiting {args.interval} seconds...")
                time.sleep(args.interval)
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
    else:
        generate_and_display_report()


if __name__ == "__main__":
    main()