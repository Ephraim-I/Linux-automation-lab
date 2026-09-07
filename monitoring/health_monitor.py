import json
from datetime import datetime
from pathlib import Path

import psutil


def collect_top_processes(limit=5):
    processes = []

    for process in psutil.process_iter(
        ["pid", "name", "cpu_percent", "memory_percent"]
    ):
        try:
            info = process.info

            processes.append({
                "pid": info["pid"],
                "name": info["name"],
                "cpu_percent": round(info["cpu_percent"] or 0.0, 1),
                "memory_percent": round(info["memory_percent"] or 0.0, 1),
            })

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    top_cpu = sorted(
        processes,
        key=lambda process: process["cpu_percent"],
        reverse=True
    )[:limit]

    top_memory = sorted(
        processes,
        key=lambda process: process["memory_percent"],
        reverse=True
    )[:limit]

    return {
        "top_cpu": top_cpu,
        "top_memory": top_memory,
    }


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

        "processes": collect_top_processes(),
    }

    return report


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
            raise ValueError(
                f"Missing configuration for {metric}"
            )

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