 Linux Automation Lab

A collection of Python-based tools for Linux system monitoring, diagnostics, log analysis, and infrastructure automation.

This project is part of my hands-on learning journey in Linux systems, Python automation, server administration, monitoring, and defensive infrastructure engineering.

🚀 Projects

1. Linux System Health Check

A lightweight command-line utility for evaluating the health of a Linux system.

Monitors:

- CPU utilization
- Memory utilization
- Swap usage
- Disk usage
- Load average

Features:

- Human-readable system reports
- JSON output
- Health classification
- Automation-friendly exit codes
- File output support

Example health states:

HEALTHY
WARNING
CRITICAL

2. Log Analysis

Tools for examining Linux logs and extracting useful information from system activity.

The goal is to make repetitive log investigation easier and identify patterns that may require further investigation.

3. System Monitoring

Experiments and utilities for monitoring Linux system resources and understanding how system health can be measured programmatically.

---

🏗️ Architecture

                Linux System
                     │
          ┌──────────┴──────────┐
          │                        │
       System                Log Files
       Metrics                     │
          │                        │
          ▼                       ▼
   Health Monitor           Log Analyzer
          │                        │
          └──────────┬──────────┘
                     ▼
              Analysis / Report
                     │
             ┌───────┴───────┐
             │                  │
          Console             JSON
             │                  │
             └───────┬───────┘
                     ▼
              Automation /
              Administration

🛠️ Technologies

- Python 3
- Linux
- Bash
- psutil
- JSON
- Git
- GitHub

⚙️ Installation

Clone the repository:

git clone https://github.com/Ephraim-I/Linux-automation-lab.git
cd Linux-automation-lab

Install dependencies:

pip install -r requirements.txt

▶️ Usage

Run the system health checker:

python3 system_health_check.py

Generate JSON output:

python3 system_health_check.py --json-only

Disable file output:

python3 system_health_check.py --no-file

📊 Exit Codes

Code| Meaning
0| HEALTHY
1| WARNING
2| CRITICAL
3| Script execution error

These exit codes make the tool suitable for use in shell scripts and automated monitoring workflows.

🎯 What I Learned

Through this project I have worked with:

- Linux system resources
- Python system administration
- Process and resource monitoring
- Log analysis
- Command-line interfaces
- JSON data processing
- Automation-friendly program design
- Git and GitHub workflows

🔮 Future Improvements

Planned improvements include:

- Configurable health thresholds
- More detailed process analysis
- Network monitoring
- Automated alerting
- Suspicious login detection
- Scheduled reporting
- Historical metrics
- Docker-based deployment
- Integration with a centralized monitoring dashboard

👨‍💻 Author

Ephraim Iannah

Electrical/Electronics Engineering Student
Veritas University

Interested in:

Embedded Systems · IoT · Automation · Linux · Networking · Intelligent Engineering Systems
