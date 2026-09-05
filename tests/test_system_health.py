from monitoring.system_health_check import evaluate_health


def test_healthy_system():
    report = {
        "cpu_percent": 40,
        "memory": {
            "used_percent": 40
        },
        "swap": {
            "used_percent": 20
        },
        "disk_root": {
            "percent_used": 60
        }
    }

    status, exit_code, reasons = evaluate_health(report)

    assert status == "HEALTHY"
    assert exit_code == 0
    assert reasons == []

def test_warning_system():
    report = {
        "cpu_percent": 80,
        "memory": {
            "used_percent": 50
        },
        "swap": {
            "used_percent": 40
        },
        "disk_root": {
            "percent_used": 70
        }
    }

    status, exit_code, reasons = evaluate_health(report)

    assert status == "WARNING"
    assert exit_code == 1
    assert len(reasons) == 1
    assert "CPU usage is high" in reasons[0]


def test_critical_system():
    report = {
        "cpu_percent": 95,
        "memory": {
            "used_percent": 50
        },
        "swap": {
            "used_percent": 40
        },
        "disk_root": {
            "percent_used": 70
        }
    }

    status, exit_code, reasons = evaluate_health(report)

    assert status == "CRITICAL"
    assert exit_code == 2
    assert len(reasons) == 1
    assert "CPU usage is critical" in reasons[0]


def test_multiple_problems():
    report = {
        "cpu_percent": 80,
        "memory": {
            "used_percent": 80
        },
        "swap": {
            "used_percent": 20
        },
        "disk_root": {
            "percent_used": 96
        }
    }

    status, exit_code, reasons = evaluate_health(report)

    assert status == "CRITICAL"
    assert exit_code == 2
    assert len(reasons) == 3


def test_threshold_boundaries():
    report = {
        "cpu_percent": 75,
        "memory": {
            "used_percent": 75
        },
        "swap": {
            "used_percent": 75
        },
        "disk_root": {
            "percent_used": 85
        }
    }

    status, exit_code, reasons = evaluate_health(report)

    assert status == "HEALTHY"
    assert exit_code == 0
    assert reasons == []


def test_just_above_warning_threshold():
    report = {
        "cpu_percent": 75.1,
        "memory": {
            "used_percent": 75
        },
        "swap": {
            "used_percent": 75
        },
        "disk_root": {
            "percent_used": 85
        }
    }

    status, exit_code, reasons = evaluate_health(report)

    assert status == "WARNING"
    assert exit_code == 1
    assert len(reasons) == 1
    assert "CPU usage is high" in reasons[0]