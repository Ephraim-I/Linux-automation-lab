from monitoring.health_analysis import (
    summarize_history,
    calculate_averages,
    find_maximums,
    analyze_trends,
    get_latest_record,
    get_history_analysis,
)


def sample_history():
    return [
        {
            "timestamp": "2026-09-08T14:00:00",
            "cpu_percent": 40.0,
            "memory_percent": 30.0,
            "swap_percent": 0.0,
            "disk_percent": 80.0,
            "status": "HEALTHY",
            "reasons": [],
        },
        {
            "timestamp": "2026-09-08T14:05:00",
            "cpu_percent": 60.0,
            "memory_percent": 40.0,
            "swap_percent": 5.0,
            "disk_percent": 85.0,
            "status": "WARNING",
            "reasons": ["Disk usage is high"],
        },
        {
            "timestamp": "2026-09-08T14:10:00",
            "cpu_percent": 90.0,
            "memory_percent": 50.0,
            "swap_percent": 10.0,
            "disk_percent": 95.0,
            "status": "CRITICAL",
            "reasons": ["CPU usage is critical"],
        },
    ]


def test_summarize_history():
    history = sample_history()

    result = summarize_history(history)

    assert result == {
        "total_checks": 3,
        "healthy": 1,
        "warning": 1,
        "critical": 1,
    }


def test_summarize_empty_history():
    result = summarize_history([])

    assert result == {
        "total_checks": 0,
        "healthy": 0,
        "warning": 0,
        "critical": 0,
    }


def test_calculate_averages():
    history = sample_history()

    result = calculate_averages(history)

    assert result == {
        "cpu_percent": 63.33,
        "memory_percent": 40.0,
        "swap_percent": 5.0,
        "disk_percent": 86.67,
    }


def test_find_maximums():
    history = sample_history()

    result = find_maximums(history)

    assert result == {
        "cpu_percent": 90.0,
        "memory_percent": 50.0,
        "swap_percent": 10.0,
        "disk_percent": 95.0,
    }


def test_analyze_trends():
    history = sample_history()

    result = analyze_trends(history)

    assert result == {
        "cpu": "INCREASING",
        "memory": "INCREASING",
        "disk": "INCREASING",
    }


def test_analyze_trends_insufficient_data():
    result = analyze_trends([
        {
            "cpu_percent": 50.0,
            "memory_percent": 40.0,
            "disk_percent": 80.0,
        }
    ])

    assert result == {
        "cpu": "INSUFFICIENT_DATA",
        "memory": "INSUFFICIENT_DATA",
        "disk": "INSUFFICIENT_DATA",
    }


def test_get_latest_record():
    history = sample_history()

    result = get_latest_record(history)

    assert result == history[-1]


def test_get_latest_record_empty():
    assert get_latest_record([]) is None


def test_get_history_analysis(monkeypatch):
    history = sample_history()

    monkeypatch.setattr(
        "monitoring.health_analysis.load_history",
        lambda: history,
    )

    result = get_history_analysis()

    assert result["summary"]["total_checks"] == 3
    assert result["summary"]["healthy"] == 1
    assert result["summary"]["warning"] == 1
    assert result["summary"]["critical"] == 1

    assert result["averages"]["cpu_percent"] == 63.33
    assert result["maximums"]["disk_percent"] == 95.0

    assert result["trends"]["cpu"] == "INCREASING"

    assert result["latest"] == history[-1]

    