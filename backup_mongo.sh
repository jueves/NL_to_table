#!/bin/bash
DATE="$(date +%Y-%m-%d)"
docker run --rm -v nl_to_table_db-data:/db-data -v ./db-backups:/backup ubuntu tar cvf /backup/backup"$DATE".tar /db-data