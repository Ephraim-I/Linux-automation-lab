# Linux Automation Lab

A collection of Python and Bash tools for Linux system monitoring, diagnostics, log analysis, and infrastructure automation.

This repository is part of my hands-on engineering journey into **Linux systems, Python automation, system administration, monitoring, defensive infrastructure, and reliable software tooling**.

The project is intentionally built incrementally, with automated tests, configuration-driven behavior, logging, historical analysis, and system-level automation.

---

## 🚀 Current Projects

### 1. Linux System Health Monitoring Toolkit

A command-line system monitoring utility that collects Linux resource metrics, evaluates system health against configurable thresholds, records results, and supports automated execution.

### Monitored Resources

- CPU utilization
- Memory utilization
- Swap usage
- Root filesystem disk usage
- System load average
- Top CPU-consuming processes
- Top memory-consuming processes

### Health States

The system classifies the machine into:

```text
HEALTHY
WARNING
CRITICAL
```

The severity is determined using configurable CPU, memory, and disk thresholds.

---

## ✨ Features

### System Monitoring

Collects system metrics using `psutil` and produces structured health reports.

### Configurable Thresholds

Health thresholds are stored separately from the application logic:

```text
config/health_config.json
```

Example:

```json
{
    "cpu": {
        "warning": 75,
        "critical": 90
    },
    "memory": {
        "warning": 75,
        "critical": 90
    },
    "disk": {
        "warning": 85,
        "critical": 95
    }
}
```

This allows monitoring behavior to be changed without modifying the Python source code.

### JSON Reports

Health reports can be exported to:

```text
reports/health_report.json
```

### Health History

The `--history` option records each health check in:

```text
reports/health_history.json
```

Each historical record contains:

- Timestamp
- CPU utilization
- Memory utilization
- Swap utilization
- Disk utilization
- Health status
- Health evaluation reasons

### Historical Analysis

The monitoring toolkit can analyze recorded health history to determine:

- Total number of health checks
- Number of healthy, warning, and critical checks
- Average resource utilization
- Maximum recorded utilization
- Resource usage trends
- Latest health status

### Logging

Health checks are recorded in:

```text
logs/system_health.log
```

The logging system records health-check execution, evaluation results, warnings, critical conditions, and report generation.

### Automation

A Bash wrapper is provided:

```text
automation/run_health_check.sh
```

The script uses the project's virtual environment and provides a stable entry point for automated execution.

### systemd Integration

The project includes user-level systemd units:

```text
automation/systemd/linux-health-check.service
automation/systemd/linux-health-check.timer
```

The timer can periodically execute the health monitoring service without requiring the monitoring program to remain continuously running.

---

## 🏗️ Architecture

```text
                         Linux System
                              │
                              ▼
                  ┌─────────────────────┐
                  │  health_monitor.py  │
                  │                     │
                  │ CPU / Memory / Disk │
                  │ Swap / Load / Tasks │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ system_health_check │
                  │       .py           │
                  │                     │
                  │ CLI + Evaluation    │
                  └──────────┬──────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
        Console Output    JSON Report    Logger
                                             │
                                             ▼
                                      system_health.log
              │
              ▼
       Health History
              │
              ▼
       Historical Analysis
              │
              ▼
       Trends / Averages /
       Maximums / Status
              │
              ▼
       Automation / systemd
```

---

## 📁 Repository Structure

```text
linux-automation-lab/
│
├── automation/
│   ├── run_health_check.sh
│   └── systemd/
│       ├── linux-health-check.service
│       └── linux-health-check.timer
│
├── config/
│   └── health_config.json
│
├── log-analysis/
│   └── journal_log_analyzer.py
│
├── monitoring/
│   ├── health_analysis.py
│   ├── health_history.py
│   ├── health_logger.py
│   ├── health_monitor.py
│   └── system_health_check.py
│
├── reports/
│   └── health_report.json
│
├── tests/
│   ├── test_health_analysis.py
│   ├── test_health_history.py
│   ├── test_health_logger.py
│   └── test_system_health.py
│
├── .gitignore
├── README.md
└── requirements.txt
```

Generated logs and historical runtime data are intentionally excluded from version control.

---

## 🛠️ Technologies

- Python 3
- Bash
- Linux
- `psutil`
- `pytest`
- JSON
- systemd
- Git
- GitHub

---

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/Ephraim-I/Linux-automation-lab.git
cd Linux-automation-lab
```

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ▶️ Usage

### Run the health checker

```bash
python monitoring/system_health_check.py
```

### Quiet mode

Display only the final health status:

```bash
python monitoring/system_health_check.py --quiet
```

Example:

```text
System Status: WARNING
```

### Generate a JSON report

```bash
python monitoring/system_health_check.py --json
```

### Record the result in health history

```bash
python monitoring/system_health_check.py --history
```

### Generate a JSON report and update history

```bash
python monitoring/system_health_check.py --json --history
```

### Run through the automation wrapper

```bash
./automation/run_health_check.sh
```

The wrapper automatically uses the project's virtual environment.

---

## 📊 Exit Codes

The health checker uses automation-friendly exit codes:

| Code | Meaning |
|---:|---|
| `0` | HEALTHY |
| `1` | WARNING |
| `2` | CRITICAL |
| `3` | Execution / configuration error |

This makes the utility suitable for shell scripts, scheduled jobs, and monitoring systems.

For example:

```bash
python monitoring/system_health_check.py --quiet

if [ $? -eq 0 ]; then
    echo "System is healthy"
elif [ $? -eq 1 ]; then
    echo "System requires attention"
elif [ $? -eq 2 ]; then
    echo "Critical system condition detected"
fi
```

---

## ⏱️ systemd Automation

The project includes a user-level systemd service and timer.

After installing the units into the appropriate user systemd directory, the timer can be enabled with:

```bash
systemctl --user daemon-reload
systemctl --user enable --now linux-health-check.timer
```

Check the timer:

```bash
systemctl --user status linux-health-check.timer
```

List scheduled executions:

```bash
systemctl --user list-timers --all
```

Run the service manually:

```bash
systemctl --user start linux-health-check.service
```

Inspect service logs:

```bash
journalctl --user -u linux-health-check.service
```

---

## 🧪 Testing

The project uses `pytest`.

Run the complete test suite:

```bash
python -m pytest
```

The current test suite covers:

- System metric collection
- Health evaluation
- Configuration validation
- CLI behavior
- Logging
- Health history
- Historical analysis
- Edge cases

Current status:

```text
38 passed
```

---

## 📈 Historical Analysis

The historical analysis module provides a programmatic interface for examining accumulated health checks.

Example:

```bash
python -c "from monitoring.health_analysis import get_history_analysis; print(get_history_analysis())"
```

The analysis includes:

```text
Summary
├── Total checks
├── Healthy
├── Warning
└── Critical

Averages
├── CPU
├── Memory
├── Swap
└── Disk

Maximums
├── CPU
├── Memory
├── Swap
└── Disk

Trends
├── CPU
├── Memory
└── Disk

Latest health record
```

---

## 🔍 Log Analysis

The repository also contains an experimental Linux journal log analyzer:

```text
log-analysis/journal_log_analyzer.py
```

The goal is to build tools that reduce repetitive system administration tasks and make Linux system activity easier to inspect.

---

## 🎯 Engineering Concepts Demonstrated

This project has provided practical experience with:

- Linux system administration
- Python system programming
- Resource monitoring
- Process inspection
- CLI application design
- Configuration-driven software
- Structured JSON data
- Logging
- Historical data collection
- Trend analysis
- Bash automation
- systemd services and timers
- Exit-code based automation
- Automated testing
- Defensive infrastructure concepts
- Git and GitHub workflows
- Incremental software development

---

## 🔮 Future Improvements

Possible future extensions include:

- Network monitoring
- Network interface statistics
- Temperature monitoring
- More detailed process analysis
- Suspicious login detection
- Automated alerting
- Email or local notification mechanisms
- Historical visualization
- CSV export
- Dashboard interface
- Service failure detection
- Container monitoring
- Remote monitoring
- Centralized monitoring
- Docker deployment

---

## 🤖 AI Assistance

ChatGPT was used as a development and learning assistant throughout this project.

Its assistance included:
- Discussing system architecture and implementation approaches
- Debugging and reasoning through implementation issues
- Designing and reviewing tests
- Improving documentation and project structure
- Explaining Linux, Python, automation, and software engineering concepts

All implementation decisions, testing, execution, and final integration were performed and verified by the author.

AI assistance is acknowledged as part of the development process, while the author retains responsibility for the project's code, design, and final result.


## 👨‍💻 Author

**Ephraim Iannah**

Electrical/Electronics Engineering Student  
Veritas University

Interested in:

**Embedded Systems · IoT · Automation · Linux · Networking · Intelligent Engineering Systems**

