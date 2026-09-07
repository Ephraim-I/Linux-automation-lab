from monitoring.health_logger import (
    configure_logger,
    get_log_path,
    log_health_result,
)


def test_get_log_path():
    path = get_log_path()

    assert path.name == "system_health.log"
    assert path.parent.name == "logs"


def test_configure_logger():
    logger = configure_logger()

    assert logger.name == "system_health"
    assert logger.level == 20
    assert len(logger.handlers) >= 1


def test_log_health_result(tmp_path, monkeypatch):
    log_file = tmp_path / "system_health.log"

    monkeypatch.setattr(
        "monitoring.health_logger.get_log_path",
        lambda: log_file,
    )

    logger = configure_logger()

    report = {
        "cpu_percent": 50.0,
        "memory": {
            "used_percent": 40.0,
        },
        "disk_root": {
            "percent_used": 70.0,
        },
    }

    log_health_result(
        logger,
        "HEALTHY",
        report,
        [],
    )

    content = log_file.read_text()

    assert "status=HEALTHY" in content
    assert "cpu=50.0%" in content
    assert "memory=40.0%" in content
    assert "disk=70.0%" in content