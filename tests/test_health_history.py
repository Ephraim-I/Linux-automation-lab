from monitoring.health_history import (
    append_history,
    create_history_record,
    get_history_path,
    load_history,
    save_history,
)


def sample_report():
    return {
        "timestamp": "2026-09-08T14:30:00",
        "cpu_percent": 50.0,
        "memory": {
            "used_percent": 40.0,
        },
        "swap": {
            "used_percent": 0.0,
        },
        "disk_root": {
            "percent_used": 92.5,
        },
        "status": "WARNING",
        "reasons": [
            "Disk usage is high: 92.5%"
        ],
    }


def test_create_history_record():
    record = create_history_record(sample_report())

    assert record["timestamp"] == "2026-09-08T14:30:00"
    assert record["cpu_percent"] == 50.0
    assert record["memory_percent"] == 40.0
    assert record["swap_percent"] == 0.0
    assert record["disk_percent"] == 92.5
    assert record["status"] == "WARNING"


def test_load_history_when_file_missing(tmp_path, monkeypatch):
    history_path = tmp_path / "health_history.json"

    monkeypatch.setattr(
        "monitoring.health_history.get_history_path",
        lambda: history_path,
    )

    assert load_history() == []


def test_save_and_load_history(tmp_path, monkeypatch):
    history_path = tmp_path / "health_history.json"

    monkeypatch.setattr(
        "monitoring.health_history.get_history_path",
        lambda: history_path,
    )

    history = [
        {
            "timestamp": "2026-09-08T14:30:00",
            "cpu_percent": 50.0,
            "status": "HEALTHY",
        }
    ]

    save_history(history)

    assert history_path.exists()
    assert load_history() == history


def test_append_history(tmp_path, monkeypatch):
    history_path = tmp_path / "health_history.json"

    monkeypatch.setattr(
        "monitoring.health_history.get_history_path",
        lambda: history_path,
    )

    append_history(sample_report())
    append_history(sample_report())

    history = load_history()

    assert len(history) == 2
    assert history[0]["cpu_percent"] == 50.0
    assert history[1]["disk_percent"] == 92.5


def test_load_history_handles_invalid_json(tmp_path, monkeypatch):
    history_path = tmp_path / "health_history.json"

    history_path.write_text("this is not valid json")

    monkeypatch.setattr(
        "monitoring.health_history.get_history_path",
        lambda: history_path,
    )

    assert load_history() == []

    