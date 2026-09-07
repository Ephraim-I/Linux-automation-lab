import logging
from pathlib import Path


def get_log_path():
    project_root = Path(__file__).resolve().parent.parent
    return project_root / "logs" / "system_health.log"


def configure_logger():
    log_path = get_log_path()
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("system_health")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    # Remove existing handlers so the logger can be safely reconfigured.
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)

    handler = logging.FileHandler(log_path)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

def log_health_result(logger, status, report, reasons):
    cpu = report["cpu_percent"]
    memory = report["memory"]["used_percent"]
    disk = report["disk_root"]["percent_used"]

    message = (
        f"status={status} | "
        f"cpu={cpu}% | "
        f"memory={memory}% | "
        f"disk={disk}%"
    )

    if reasons:
        message += f" | reasons={'; '.join(reasons)}"

    if status == "CRITICAL":
        logger.critical(message)
    elif status == "WARNING":
        logger.warning(message)
    else:
        logger.info(message)