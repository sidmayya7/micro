#!/bin/bash

# Restore MySQL dump
echo "Restoring MySQL database..."
docker-compose exec -T mysql-hotel mysql -u root -proot hotel_db < database_dumps/mysql_dump.sql

# Restore MongoDB dump
echo "Restoring MongoDB database..."
docker-compose exec mongodb mongorestore /data/db/dump

echo "Database restoration complete!"
