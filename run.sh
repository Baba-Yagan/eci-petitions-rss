#!/bin/bash
rm *.txt

# Capture both time and wget output, with error redirection
{ time wget https://register.eci.ec.europa.eu/core/api/register/search/ALL/EN/0/1000 -O 1000.json > >(tee output.log) 2> >(tee error.log >&2); } 2>&1

move () {
    mv *.txt /home/user/projects/xmpp-shared-folder/actual-mount/sender/notifications-uo8eivae7u/
}

# Check exit status
if [ $? -ne 0 ]; then
    echo "/home/user/projects/ec-petitions-rss/ getting file for updates failed so something is really wrong" > message.txt
    move
    exit 1
fi

python3 fin.py
move

sleep 24h
