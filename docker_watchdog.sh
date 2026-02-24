#!/bin/bash

CONTAINER_NAME="friendly_diffie"
LOG_FILE="/var/log/docker-watchdog.log"
DATE=$(date "+%Y-%m-%d %H:%M:%S")

# Check if container exists
EXISTS=$(docker ps -a --filter "name=^/${CONTAINER_NAME}$" --format "{{.Names}}")

if [ -z "$EXISTS" ]; then
    echo "$DATE - Container $CONTAINER_NAME does not exist" >> $LOG_FILE
    exit 1
fi

# Check if container is running
RUNNING=$(docker ps --filter "name=^/${CONTAINER_NAME}$" --format "{{.Names}}")

if [ -z "$RUNNING" ]; then
    echo "$DATE - Container $CONTAINER_NAME is down. Starting..." >> $LOG_FILE
    docker start $CONTAINER_NAME >> $LOG_FILE 2>&1
else
    echo "$DATE - Container $CONTAINER_NAME is already running" >> $LOG_FILE
fi


*/2 * * * * cd /Users/pixyfart/Workspace/financial_intel && /usr/local/bin/docker compose run --rm app >> /Users/pixyfart/Workspace/financial_intel/docker_app.log 2>&1