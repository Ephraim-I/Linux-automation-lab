import pytest
import logging
import json

from logging.handlers import RotatingFileHandler

import subprocess
import sys
from pathlib import Path

from monitoring.health_monitor import (
    collect_system_health,
    collect_top_processes,
    evaluate_health,
    load_config,
    validate_config,
)

from monitoring.system_health_check import (
    get_report_path,
    setup_logging,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = PROJECT_ROOT / "monitoring" / "system_health_check.py"


TEST_CONFIG = {
    "cpu": {
        "warning": 75,
        "critical": 90,
    },
    "memory": {
        "warning": 75,
        "critical": 90,
    },
    "disk": {
        "warning": 85,
        "critical": 95,
    },
}


def run_cli(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        capture_output=True,
        text=True,
    )


def test_cli_help():
    result = run_cli("--help")

    assert result.returncode == 0
    assert "usage" in result.stdout.lower()


def test_cli_quiet():
    result = run_cli("--quiet")

    assert result.returncode in (0, 1, 2)
    assert "System Status:" in result.stdout


def test_cli_json():
    result = run_cli("--json")

    assert result.returncode in (0, 1, 2)
    assert "JSON report saved" in result.stdout

def test_cli_json_report():
    result = run_cli("--json")

    assert result.returncode in (0, 1, 2)

    report_path = PROJECT_ROOT / "reports" / "health_report.json"

    assert report_path.exists()

    with open(report_path, "r") as f:
        report = json.load(f)

    assert "timestamp" in report
    assert "cpu_percent" in report
    assert "memory" in report
    assert "disk_root" in report
    assert "status" in report
    assert "reasons" in report

def test_collect_system_health():
    report = collect_system_health()

    assert "timestamp" in report
    assert "cpu_percent" in report
    assert "memory" in report
    assert "swap" in report
    assert "load_average" in report
    assert "disk_root" in report


def test_health_evaluation_healthy():
    report = {
        "cpu_percent": 40,
        "memory": {
            "used_percent": 40,
        },
        "disk_root": {
            "percent_used": 60,
        },
    }

    status, exit_code, reasons = evaluate_health(report, TEST_CONFIG)

    assert status == "HEALTHY"
    assert exit_code == 0
    assert reasons == []


def test_health_evaluation_warning():
    report = {
        "cpu_percent": 80,
        "memory": {
            "used_percent": 40,
        },
        "disk_root": {
            "percent_used": 60,
        },
    }

    status, exit_code, reasons = evaluate_health(report, TEST_CONFIG)

    assert status == "WARNING"
    assert exit_code == 1
    assert "CPU usage is high: 80%" in reasons


def test_health_evaluation_critical():
    report = {
        "cpu_percent": 95,
        "memory": {
            "used_percent": 40,
        },
        "disk_root": {
            "percent_used": 60,
        },
    }

    status, exit_code, reasons = evaluate_health(report, TEST_CONFIG)

    assert status == "CRITICAL"
    assert exit_code == 2
    assert "CPU usage is critical: 95%" in reasons


def test_health_exit_codes():
    test_cases = [
        (
            {
                "cpu_percent": 40,
                "memory": {
                    "used_percent": 40,
                },
                "disk_root": {
                    "percent_used": 60,
                },
            },
            0,
        ),
        (
            {
                "cpu_percent": 80,
                "memory": {
                    "used_percent": 40,
                },
                "disk_root": {
                    "percent_used": 60,
                },
            },
            1,
        ),
        (
            {
                "cpu_percent": 95,
                "memory": {
                    "used_percent": 40,
                },
                "disk_root": {
                    "percent_used": 60,
                },
            },
            2,
        ),
    ]

    for report, expected_exit_code in test_cases:
        _, exit_code, _ = evaluate_health(report, TEST_CONFIG)
        assert exit_code == expected_exit_code


def test_custom_thresholds():
    config = {
        "cpu": {
            "warning": 50,
            "critical": 80,
        },
        "memory": {
            "warning": 75,
            "critical": 90,
        },
        "disk": {
            "warning": 85,
            "critical": 95,
        },
    }

    report = {
        "cpu_percent": 60,
        "memory": {
            "used_percent": 40,
        },
        "disk_root": {
            "percent_used": 60,
        },
    }

    status, exit_code, reasons = evaluate_health(report, config)

    assert status == "WARNING"
    assert exit_code == 1
    assert "CPU usage is high: 60%" in reasons


def test_load_config():
    config = load_config()

    assert config["cpu"]["warning"] == 75
    assert config["cpu"]["critical"] == 90

    assert config["memory"]["warning"] == 75
    assert config["memory"]["critical"] == 90

    assert config["disk"]["warning"] == 85
    assert config["disk"]["critical"] == 95


def test_valid_config():
    validate_config(TEST_CONFIG)


def test_config_missing_metric():
    config = {
        "cpu": {
            "warning": 75,
            "critical": 90,
        },
    }

    with pytest.raises(ValueError):
        validate_config(config)


def test_config_invalid_threshold():
    config = {
        "cpu": {
            "warning": 110,
            "critical": 120,
        },
        "memory": {
            "warning": 75,
            "critical": 90,
        },
        "disk": {
            "warning": 85,
            "critical": 95,
        },
    }

    with pytest.raises(ValueError):
        validate_config(config)


def test_config_invalid_threshold_order():
    config = {
        "cpu": {
            "warning": 95,
            "critical": 90,
        },
        "memory": {
            "warning": 75,
            "critical": 90,
        },
        "disk": {
            "warning": 85,
            "critical": 95,
        },
    }

    with pytest.raises(ValueError):
        validate_config(config)


def test_report_path():
    report_path = get_report_path()

    assert report_path.name == "health_report.json"
    assert report_path.parent.name == "reports"
    

def test_setup_logging():
    log_file = setup_logging()

    assert log_file.name == "system_health.log"
    assert log_file.parent.name == "logs"
    assert log_file.exists()

def test_log_rotation(tmp_path):
    log_file = tmp_path / "test.log"

    handler = RotatingFileHandler(
        log_file,
        maxBytes=100,
        backupCount=2
    )

    logger = logging.getLogger("rotation_test")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    for _ in range(20):
        logger.info("This is a test log message that should trigger rotation.")

    handler.close()
    logger.removeHandler(handler)

    assert log_file.exists()
    assert (tmp_path / "test.log.1").exists()



def test_collect_top_processes():
    processes = collect_top_processes(limit=3)

    assert "top_cpu" in processes
    assert "top_memory" in processes

    assert len(processes["top_cpu"]) <= 3
    assert len(processes["top_memory"]) <= 3

    for process in processes["top_cpu"]:
        assert "pid" in process
        assert "name" in process
        assert "cpu_percent" in process
        assert "memory_percent" in process


def test_processes_are_sorted_by_cpu():
    processes = collect_top_processes(limit=5)

    cpu_values = [
        process["cpu_percent"]
        for process in processes["top_cpu"]
    ]

    assert cpu_values == sorted(cpu_values, reverse=True)



def test_processes_are_sorted_by_memory():
    processes = collect_top_processes(limit=5)

    memory_values = [
        process["memory_percent"]
        for process in processes["top_memory"]
    ]

    assert memory_values == sorted(memory_values, reverse=True)