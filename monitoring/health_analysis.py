from statistics import mean

from monitoring.health_history import load_history


def summarize_history(history):
    """Return a high-level summary of recorded health checks."""
    if not history:
        return {
            "total_checks": 0,
            "healthy": 0,
            "warning": 0,
            "critical": 0,
        }

    return {
        "total_checks": len(history),
        "healthy": sum(
            record.get("status") == "HEALTHY"
            for record in history
        ),
        "warning": sum(
            record.get("status") == "WARNING"
            for record in history
        ),
        "critical": sum(
            record.get("status") == "CRITICAL"
            for record in history
        ),
    }


def calculate_averages(history):
    """Calculate average resource utilization."""
    if not history:
        return {
            "cpu_percent": 0.0,
            "memory_percent": 0.0,
            "swap_percent": 0.0,
            "disk_percent": 0.0,
        }

    return {
        "cpu_percent": round(
            mean(record["cpu_percent"] for record in history), 2
        ),
        "memory_percent": round(
            mean(record["memory_percent"] for record in history), 2
        ),
        "swap_percent": round(
            mean(record["swap_percent"] for record in history), 2
        ),
        "disk_percent": round(
            mean(record["disk_percent"] for record in history), 2
        ),
    }


def find_maximums(history):
    """Find the highest recorded resource utilization."""
    if not history:
        return {
            "cpu_percent": 0.0,
            "memory_percent": 0.0,
            "swap_percent": 0.0,
            "disk_percent": 0.0,
        }

    return {
        "cpu_percent": max(
            record["cpu_percent"] for record in history
        ),
        "memory_percent": max(
            record["memory_percent"] for record in history
        ),
        "swap_percent": max(
            record["swap_percent"] for record in history
        ),
        "disk_percent": max(
            record["disk_percent"] for record in history
        ),
    }


def analyze_trends(history):
    """Determine whether resource usage is increasing or decreasing."""
    if len(history) < 2:
        return {
            "cpu": "INSUFFICIENT_DATA",
            "memory": "INSUFFICIENT_DATA",
            "disk": "INSUFFICIENT_DATA",
        }

    first = history[0]
    latest = history[-1]

    def trend(first_value, latest_value):
        if latest_value > first_value:
            return "INCREASING"
        if latest_value < first_value:
            return "DECREASING"
        return "STABLE"

    return {
        "cpu": trend(first["cpu_percent"], latest["cpu_percent"]),
        "memory": trend(
            first["memory_percent"],
            latest["memory_percent"],
        ),
        "disk": trend(
            first["disk_percent"],
            latest["disk_percent"],
        ),
    }


def get_latest_record(history):
    """Return the most recent health record."""
    if not history:
        return None

    return history[-1]


def get_history_analysis():
    """Load and analyze the persisted health history."""
    history = load_history()

    return {
        "summary": summarize_history(history),
        "averages": calculate_averages(history),
        "maximums": find_maximums(history),
        "trends": analyze_trends(history),
        "latest": get_latest_record(history),
    }
