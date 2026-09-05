import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import psutil


def collect_system_health():
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    disk = psutil.disk_usage("/")

    report = {
        "timestamp": datetime.now().isoformat(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory": {
            "total_gb": round(memory.total / (1024 ** 3), 2),
            "used_percent": memory.percent,
            "available_gb": round(memory.available / (1024 ** 3), 2),
        },
        "swap": {
            "total_gb": round(swap.total / (1024 ** 3), 2),
            "used_percent": swap.percent,
        },
        "load_average": ", ".join(
            f"{value:.2f}" for value in psutil.getloadavg()
        ),
        "disk_root": {
            "total_gb": round(disk.total / (1024 ** 3), 2),
            "used_gb": round(disk.used / (1024 ** 3), 2),
            "percent_used": disk.percent,
        },
    }

    return report


def evaluate_health(report):
    cpu = report["cpu_percent"]
    mem = report["memory"]["used_percent"]
    disk = report["disk_root"].get("percent_used", 0)

    status = "HEALTHY"
    severity = 0
    reasons = []

    if cpu > 90:
        reasons.append(f"CPU usage is critical: {cpu}%")
        severity = max(severity, 2)
    elif cpu > 75:
        reasons.append(f"CPU usage is high: {cpu}%")
        severity = max(severity, 1)

    if mem > 90:
        reasons.append(f"Memory usage is critical: {mem}%")
        severity = max(severity, 2)
    elif mem > 75:
        reasons.append(f"Memory usage is high: {mem}%")
        severity = max(severity, 1)

    if disk > 95:
        reasons.append(f"Disk usage is critical: {disk}%")
        severity = max(severity, 2)
    elif disk > 85:
        reasons.append(f"Disk usage is high: {disk}%")
        severity = max(severity, 1)

    if severity == 2:
        status = "CRITICAL"
    elif severity == 1:
        status = "WARNING"

    return status, severity, reasons


def get_report_path():
    project_root = Path(__file__).resolve().parent.parent
    report_dir = project_root / "reports"
    report_dir.mkdir(exist_ok=True)

    return report_dir / "health_report.json"


def save_report(report):
    report_path = get_report_path()

    with open(report_path, "w") as f:
        json.dump(report, f, indent=4)

    return report_path


def display_report(report, status, reasons):
    print("\n## System Health Report\n")

    print(f"Timestamp: {report['timestamp']}")
    print(f"CPU Usage: {report['cpu_percent']}%")
    print(f"Load Average: {report['load_average']}")
    print(f"Memory Used: {report['memory']['used_percent']}%")
    print(f"Memory Available: {report['memory']['available_gb']}GB")
    print(f"Swap Used: {report['swap']['used_percent']}%")
    print(f"Disk Usage (/): {report['disk_root']['percent_used']}%")

    print("---------------------")
    print(f"\nSystem Status: {status}")

    if reasons:
        print("\nReasons:")
        for reason in reasons:
            print(f"- {reason}")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Linux system health monitoring tool"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Save the health report as JSON"
    )

    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only display the final health status"
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    report = collect_system_health()

    status, exit_code, reasons = evaluate_health(report)

    report["status"] = status
    report["reasons"] = reasons

    if args.quiet:
        print(f"System Status: {status}")
    else:
        display_report(report, status, reasons)

    if args.json:
        report_path = save_report(report)
        print(f"JSON report saved to {report_path}")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())

    