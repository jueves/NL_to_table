#!/bin/bash
DATE="$(date +%Y-%m-%d)"
BACKUPS_PATH="./db-backups"
docker run --rm -v nl_to_table_db-data:/db-data -v "$BACKUPS_PATH":/backup ubuntu tar cvf /backup/backup"$DATE".tar /db-data