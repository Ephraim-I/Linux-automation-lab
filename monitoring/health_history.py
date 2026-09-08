import json
from pathlib import Path


def get_history_path():
    project_root = Path(__file__).resolve().parent.parent
    history_dir = project_root / "reports"
    history_dir.mkdir(exist_ok=True)

    return history_dir / "health_history.json"


def load_history():
    history_path = get_history_path()

    if not history_path.exists():
        return []

    try:
        with open(history_path, "r") as f:
            history = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []

    if not isinstance(history, list):
        return []

    return history


def create_history_record(report):
    return {
        "timestamp": report["timestamp"],
        "cpu_percent": report["cpu_percent"],
        "memory_percent": report["memory"]["used_percent"],
        "swap_percent": report["swap"]["used_percent"],
        "disk_percent": report["disk_root"]["percent_used"],
        "status": report.get("status", "UNKNOWN"),
        "reasons": report.get("reasons", []),
    }


def save_history(history):
    history_path = get_history_path()

    with open(history_path, "w") as f:
        json.dump(history, f, indent=4)

    return history_path


def append_history(report):
    history = load_history()
    record = create_history_record(report)

    history.append(record)

    return save_history(history)
