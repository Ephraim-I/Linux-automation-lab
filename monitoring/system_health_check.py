import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import logging

from monitoring.health_monitor import (
    collect_system_health,
    evaluate_health,
    load_config,
    validate_config,
)

from monitoring.health_history import append_history
from monitoring.health_analysis import get_history_analysis


def setup_logging():
    project_root = Path(__file__).resolve().parent.parent
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / "system_health.log"

    handler = RotatingFileHandler(
        log_file,
        maxBytes=1024 * 1024,
        backupCount=3
    )

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        logger.addHandler(handler)

    return log_file



def get_config_path():
    project_root = Path(__file__).resolve().parent.parent
    return project_root / "config" / "health_config.json"


def load_config():
    config_path = get_config_path()

    with open(config_path, "r") as f:
        return json.load(f)

def validate_config(config):
    required_metrics = ["cpu", "memory", "disk"]
    required_levels = ["warning", "critical"]

    for metric in required_metrics:
        if metric not in config:
            raise ValueError(f"Missing configuration for {metric}")

        for level in required_levels:
            if level not in config[metric]:
                raise ValueError(
                    f"Missing {level} threshold for {metric}"
                )

            value = config[metric][level]

            if not isinstance(value, (int, float)):
                raise ValueError(
                    f"{metric} {level} threshold must be a number"
                )

            if not 0 <= value <= 100:
                raise ValueError(
                    f"{metric} {level} threshold must be between 0 and 100"
                )

        if config[metric]["warning"] >= config[metric]["critical"]:
            raise ValueError(
                f"{metric} warning threshold must be lower "
                f"than critical threshold"
            )


def evaluate_health(report, config):
    cpu = report["cpu_percent"]
    mem = report["memory"]["used_percent"]
    disk = report["disk_root"].get("percent_used", 0)

    cpu_warning = config["cpu"]["warning"]
    cpu_critical = config["cpu"]["critical"]

    mem_warning = config["memory"]["warning"]
    mem_critical = config["memory"]["critical"]

    disk_warning = config["disk"]["warning"]
    disk_critical = config["disk"]["critical"]

    severity = 0
    reasons = []

    if cpu > cpu_critical:
        reasons.append(f"CPU usage is critical: {cpu}%")
        severity = max(severity, 2)
    elif cpu > cpu_warning:
        reasons.append(f"CPU usage is high: {cpu}%")
        severity = max(severity, 1)

    if mem > mem_critical:
        reasons.append(f"Memory usage is critical: {mem}%")
        severity = max(severity, 2)
    elif mem > mem_warning:
        reasons.append(f"Memory usage is high: {mem}%")
        severity = max(severity, 1)

    if disk > disk_critical:
        reasons.append(f"Disk usage is critical: {disk}%")
        severity = max(severity, 2)
    elif disk > disk_warning:
        reasons.append(f"Disk usage is high: {disk}%")
        severity = max(severity, 1)

    if severity == 2:
        status = "CRITICAL"
    elif severity == 1:
        status = "WARNING"
    else:
        status = "HEALTHY"

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
    print("\nSystem Health Report\n")

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

    print("Top CPU Processes:")

    for process in report["processes"]["top_cpu"]:
        print(
            f"- {process['name']} "
            f"(PID {process['pid']}): "
            f"{process['cpu_percent']}% CPU"
        )

    print()

    print("Top Memory Processes:")

    for process in report["processes"]["top_memory"]:
        print(
            f"- {process['name']} "
            f"(PID {process['pid']}): "
            f"{process['memory_percent']}% memory"
        )

def display_history_analysis(analysis):
    print("\nHealth History Analysis\n")

    summary = analysis["summary"]
    averages = analysis["averages"]
    maximums = analysis["maximums"]
    trends = analysis["trends"]
    latest = analysis["latest"]

    print(f"Total Checks: {summary['total_checks']}")
    print(f"Healthy: {summary['healthy']}")
    print(f"Warning: {summary['warning']}")
    print(f"Critical: {summary['critical']}")

    print("\nAverage Usage:")
    print(f"- CPU: {averages['cpu_percent']}%")
    print(f"- Memory: {averages['memory_percent']}%")
    print(f"- Swap: {averages['swap_percent']}%")
    print(f"- Disk: {averages['disk_percent']}%")

    print("\nMaximum Usage:")
    print(f"- CPU: {maximums['cpu_percent']}%")
    print(f"- Memory: {maximums['memory_percent']}%")
    print(f"- Swap: {maximums['swap_percent']}%")
    print(f"- Disk: {maximums['disk_percent']}%")

    print("\nTrends:")
    print(f"- CPU: {trends['cpu']}")
    print(f"- Memory: {trends['memory']}")
    print(f"- Disk: {trends['disk']}")

    print("\nLatest Status:")
    if latest:
        print(f"- {latest['status']}")
        print(f"- Timestamp: {latest['timestamp']}")
    else:
        print("- No health history available")


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

    parser.add_argument(
        "--history",
        action="store_true",
        help="Save the current health result to health history",
    )

    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Analyze recorded health history",
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    log_file = setup_logging()

    logging.info("System health check started")

    try:
        report = collect_system_health()

        config = load_config()
        validate_config(config)

        status, exit_code, reasons = evaluate_health(report, config)

        logging.info(
            "Health evaluation completed: status=%s, exit_code=%s",
            status,
            exit_code
        )

        report["status"] = status
        report["reasons"] = reasons

        if args.analyze:
            analysis = get_history_analysis()
            display_history_analysis(analysis)
            return 0

        if args.history:
            history_path = append_history(report)
            logging.info("Health history updated: %s", history_path)
            print(f"Health history updated: {history_path}")   

        for reason in reasons:
            logging.warning(reason)

        if args.quiet:
            print(f"System Status: {status}")
        else:
            display_report(report, status, reasons)

        if args.json:
            report_path = save_report(report)
            logging.info("JSON report saved to %s", report_path)
            print(f"JSON report saved to {report_path}")

        return exit_code

    except FileNotFoundError:
        logging.error("Health configuration file was not found.")
        print("ERROR: Health configuration file was not found.")
        return 3

    except json.JSONDecodeError:
        logging.error("Health configuration file contains invalid JSON.")
        print("ERROR: Health configuration file contains invalid JSON.")
        return 3

    except ValueError as error:
        logging.error("Invalid configuration: %s", error)
        print(f"ERROR: Invalid configuration: {error}")
        return 3


if __name__ == "__main__":
    sys.exit(main())
