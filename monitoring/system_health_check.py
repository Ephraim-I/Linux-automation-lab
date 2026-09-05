import psutil
import subprocess
import json
import sys
import argparse
from pathlib import Path
from datetime import datetime

def get_load_average():
    try:
        result = subprocess.run(
            ["uptime"],
            capture_output=True,
            text=True,
            check=True
        )
        output = result.stdout.strip()
        load_part = output.split("load average:") [1].strip()
        return load_part
    except Exception as e:
        return f"Error retrieving load average: {e}"
    

def get_disk_usage():
    try:
        disk = psutil.disk_usage('/')
        return {
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "percent_used": disk.percent
        }
    except Exception as e:
        return {"error": str(e)}
    
def generate_report():
    try:
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        load = get_load_average()
        disk = get_disk_usage()

        report = {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": cpu,
            "memory": {
                "total_gb": round(memory.total / (1024**3), 2),
                "used_percent": round(memory.percent, 2),
                "available_gb": round(memory.available / (1024**3), 2)
            },
            "swap": {
                "total_gb": round(swap.total / (1024**3), 2),
                "used_percent": swap.percent
            },
            "load_average": load,
            "disk_root": disk
        }
        return report
    except Exception as e:
        return {"error" : str(e)}
    
def evaluate_health(report):
    cpu = report["cpu_percent"]
    mem = report["memory"]["used_percent"]
    swap = report["swap"]["used_percent"]
    disk = report["disk_root"].get("percent_used", 0)

    reasons = []
    severity = 0

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

    if swap > 90:
        reasons.append(f"Swap usage is critical: {swap}%")
        severity = max(severity, 2)
    elif swap > 75:
        reasons.append(f"Swap usage is high: {swap}%")
        severity = max(severity, 1)

    if disk > 95:
        reasons.append(f"Disk usage is critical: {disk}%")
        severity = max(severity, 2)
    elif disk > 85:
        reasons.append(f"Disk usage is high: {disk}%")
        severity = max(severity, 1)

    if severity == 2:
        return "CRITICAL", 2, reasons
    elif severity == 1:
        return "WARNING", 1, reasons
    else:
        return "HEALTHY", 0, reasons


def print_console_report(report):
    print("\nSystem Health Report")
    print("-" * 40)

    if "error" in report:
        print("Error generating report:", report["error"])
        return
    
    print(f"Timestamp: {report['timestamp']}")
    print(f"CPU Usage: {report['cpu_percent']}%")
    print(f"Load Average: {report['load_average']}")
    print(f"Memory Used: {report['memory']['used_percent']}%")
    print(f"Memory Available: {report['memory']['available_gb']}GB")
    print(f"Swap Used: {report['swap']['used_percent']}%")
    print(f"Disk Usage (/): {report['disk_root']['percent_used']}%")
    print("-" * 40)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Linux System Health Check Tool")
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Output JSON only (no console report)"
    )

    parser.add_argument(
        "--no-file",
        action="store_true",
        help="Do not write JSON report to file"
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    report = generate_report()

    status, exit_code, reasons = evaluate_health(report)
    report["status"] = status
    report["reasons"] = reasons

    # Console output
    if not args.json_only:
        print_console_report(report)
        print(f"System Status: {status}")

        if reasons:
            print("\nReasons:")
            for reason in reasons:
                print(f"  - {reason}")

    # JSON output (file)
    if not args.no_file:
        try:
            with open("health_report.json", "w") as f:
                json.dump(report, f, indent=4)
            print("JSON report saved to health_report.json")

        except Exception as e:
            print("Failed to write JSON file: ", e)
            sys.exit(3)

    if args.json_only:
        print(json.dumps(report, indent=4))

    sys.exit(exit_code)