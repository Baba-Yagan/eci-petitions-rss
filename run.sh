#!/bin/bash

# Capture both time and wget output, with error redirection
{ time wget https://register.eci.ec.europa.eu/core/api/register/search/ALL/EN/0/1000 -O 1000.json > >(tee output.log) 2> >(tee error.log >&2); } 2>&1

# Check exit status
if [ $? -ne 0 ]; then
    echo "Getting file for updates failed - wget error occurred"
    exit 1
fi

# Generate RSS feed
python3 fin.py

echo "RSS generation completed"

# Remove the sleep when running in GitHub Actions (cron handles scheduling)
if [ -z "$GITHUB_ACTIONS" ]; then
    sleep 24h
fi
