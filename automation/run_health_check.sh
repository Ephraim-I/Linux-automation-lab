#!/bin/bash

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

cd "$PROJECT_ROOT" || exit 1

"$PROJECT_ROOT/.venv/bin/python" \
    "$PROJECT_ROOT/monitoring/system_health_check.py" \
    --json \
    --history

health_exit_code=$?

echo "Health check completed with status code: $health_exit_code"

exit 0
