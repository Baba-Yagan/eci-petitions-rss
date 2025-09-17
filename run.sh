#!/bin/bash
rm -f *.txt

# Capture both time and wget output, with error redirection
{ time wget https://register.eci.ec.europa.eu/core/api/register/search/ALL/EN/0/1000 -O 1000.json > >(tee output.log) 2> >(tee error.log >&2); } 2>&1

move () {
    # In GitHub Actions, we'll just keep the files in the repo
    # instead of moving to a specific local path
    if [ -n "$GITHUB_ACTIONS" ]; then
        echo "Running in GitHub Actions - keeping files in repository"
        return 0
    else
        # Original behavior for local runs
        mv *.txt /home/user/projects/xmpp-shared-folder/actual-mount/sender/notifications-uo8eivae7u/
    fi
}

# Check exit status
if [ $? -ne 0 ]; then
    echo "Getting file for updates failed - wget error occurred" > error_message.txt
    move
    exit 1
fi

python3 fin.py
move

# Remove the sleep when running in GitHub Actions (cron handles scheduling)
if [ -z "$GITHUB_ACTIONS" ]; then
    sleep 24h
fi
