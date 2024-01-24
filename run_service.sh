#!/bin/bash

# Stop on first error
set -o errexit
# Print each command ran
set -o xtrace

case "$SERVICE_NAME" in
producer)
    python -u src/producer_service_main.py --config_path config.json
    ;;
image_processor)
    python -u src/image_processing_service_main.py --config_path config.json
    ;;
stats_reporter)
    python -u src/stats_reporting_service_main.py --config_path config.json
    ;;
*)
    echo "Unknown service name!"
    exit 1
    ;;
esac
