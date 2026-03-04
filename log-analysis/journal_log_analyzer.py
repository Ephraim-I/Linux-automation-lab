import subprocess
import json
import sys
import argparse
from datetime import datetime

def parse_arguments():
    parser = argparse.ArgumentParser(description= "Journal Log Analyzer Tool")

    parser.add_argument("--lines", type=int, default=200, help="Number of journal lines to analyze (default: 200)")

    parser.add_argument("--json-only", action="store_true", help="Output JSON only")

    parser.add_argument("--since", type=str, help="Start time for log analysis (e.g. '2025-01-01 10:00:00')")

    parser.add_argument("--until", type=str, help="End time for log analysis (e.g. '2025-01-01 12:00:00')")

    parser.add_argument("--auth-log", action="store_true", help="Analyze /var/log/auth.log instead of journalctl")

    return parser.parse_args()

def get_journal_logs(line_count, since=None, until=None):
    try:
        command = ["journalctl", "-n", str(line_count), "--no-pager"]

        if since:
            command.extend(["--since", since])

        if until:
            command.extend(["--until", until])

        if not since and not until:
            command.extend(["-n", str(line_count)])

        result = subprocess.run(command, capture_output=True, text=True, check=True)
        
        return result.stdout.splitlines()
    
    except subprocess.CalledProcessError as e: 
        return {"error": e.stderr.strip()}
    
def get_auth_logs_lines():
    try:
        with open("/var/log/auth.log", "r") as f:
            return f.readlines() [-200:]
        
    except Exception as e:
        return {"error": str(e)}
    
def analyze_logs(log_lines):
    if isinstance(log_lines, dict):
        return log_lines
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "lines_analyzed": len(log_lines),
        "failed_services": 0,
        "authentication_failures": 0,
        "invalid_users": 0,
        "ssh_failed_attempts": 0,
        "critical_errors": 0,
        "warnings": 0
    }
    for line in log_lines:
        lower_line = line.lower()

        # Service failures
        if "failed to start" in lower_line or "failed to" in lower_line:
            report["failed_services"] +=1

        # SSH invalid users
        if "invalid user" in lower_line:
            report["invalid_users"] += 1

        # SSH failed login attempts
        if "failed password" in lower_line:
            report["ssh_failed_attempts"] += 1

        # Authentication failures (PAM)
        if "authentication failure" in lower_line:
            report["authentication_failures"] += 1

        # Critical kernel/system errors
        if "kernel panic" in lower_line or "segfault" in lower_line:
            report["critical_errors"] += 1

        # Warning level messages
        if "warning" in lower_line:
            report["warnings"] += 1

    return report
    
def evaluate_severity(report):
    if "error" in report: 
        return "ERROR", 3
    
    if report["critical_errors"] > 0:
        return "CRITICAL", 2
    
    total_security_events = (report["invalid_users"] + report["ssh_failed_attempts"] + report["authentication_failures"])

    if total_security_events > 20:
        return "CRITICAL", 2
    
    elif total_security_events > 5:
        return "WARNING", 1
    
    elif report["failed_services"] > 5:
        return "WARNING", 1
    else:
        return "HEALTHY", 0
    
def print_console_report(report, status):
    print("\nJournal Log Analysis")
    print("-" * 40)

    if "error" in report:
        print("Error retrieving logs:", report["error"])
        return
    
    print(f"Timestamp: {report['timestamp']}")
    print(f"Lines Analyzed: {report['lines_analyzed']}")
    print(f"Failed Services: {report['failed_services']}")
    print(f"Authentication Failures: {report['authentication_failures']}")
    print(f"Invalid Users: {report['invalid_users']}")
    print(f"SSH Failed Attempts: {report['ssh_failed_attempts']}")
    print(f"Critical Errors: {report['critical_errors']}")
    print(f"Warnings: {report['warnings']}")

    print("-" * 40)

if __name__== "__main__":
    args = parse_arguments()

    if args.auth_log:
        logs = get_auth_logs_lines()
    else:
        logs = get_journal_logs(args.lines, args.since, args.until)

    report = analyze_logs(logs)

    status, exit_code = evaluate_severity(report)

    if not args.json_only:
        print_console_report(report, status)

    if args.json_only:
        print(json.dumps(report, indent=4))

    sys.exit(exit_code)