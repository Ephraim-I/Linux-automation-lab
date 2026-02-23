# Linux System Health Check Tool

A lightweight Python-based monitoring utility for diagnosing Linux server health.

## Features

- CPU usage monitoring
- Memory and swap utilization tracking
- Disk usage inspection (/ root)
- Load average retrieval
- Health status classification (HEALTHY / WARNING / CRITICAL)
- JSON output support
- Automation-friendly exit codes

## Requirements

- Python 3.x
- psutil library

Install dependencies:

pip install psutil

## Usage

Standard console report:

python3 system_health_check.py

JSON output only:

python3 system_health_check.py --json-only

Disable file output:

python3 system_health_check.py --no-file

## Exit Codes

0 → HEALTHY  
1 → WARNING  
2 → CRITICAL  
3 → Script execution error  

## Example Output

System Health Report
----------------------------------------
CPU Usage: 12%
Load Average: 0.30, 0.25, 0.18
Memory Used: 42%
Swap Used: 0%
Disk Usage (/): 63%
System Status: HEALTHY

## Use Cases

- VPS diagnostics
- Server troubleshooting
- Cron-based health monitoring
- Infrastructure automation workflows