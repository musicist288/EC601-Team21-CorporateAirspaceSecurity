#!/bin/bash
set -e

REMOTE="ubuntu@192.168.45.1"
PACKAGE=airsec-0.1.0.tar.gz

eval $(ssh-agent -s)
ssh-add
declare -a services=("airsec-web.service" "airsec-monitor.service")
ssh "$REMOTE" "sudo date -u -s \"$(date -u +'%Y-%m-%d %H:%M:%S')\""

# Build the package
poetry build
scp dist/$PACKAGE $REMOTE:/home/ubuntu/$PACKAGE

# Stop the services
for service in "${services[@]}"
do
    ssh "$REMOTE" "sudo /usr/bin/systemctl stop $service"
done

ssh "$REMOTE" "sudo /usr/bin/pip3 install --upgrade /home/ubuntu/$PACKAGE"

# Copy and move the services into place
for service in "${services[@]}"
do
    scp config/$service $REMOTE:/home/ubuntu/$service
    ssh "$REMOTE" "sudo /usr/bin/mv /home/ubuntu/$service /etc/systemd/system/$service"
done

# Reload the service files
ssh "$REMOTE" "sudo /usr/bin/systemctl daemon-reload"

# Start the servies
for service in "${services[@]}"
do
    ssh "$REMOTE" "sudo /usr/bin/systemctl start $service"
done

ssh-agent -k
