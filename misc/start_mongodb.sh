#!/bin/bash

# After I start ther server, check if working using `mongosh` command

# to run: sh start_mongodb.sh

# Custom MongoDB Data Directory
MONGO_DATA_DIR="$HOME/Library/CloudStorage/OneDrive-DukeUniversity/Code/cerebra_v2/data/db"

# Check if the MongoDB data directory exists, create it if it doesn't
if [ ! -d "$MONGO_DATA_DIR" ]; then
    mkdir -p "$MONGO_DATA_DIR"
fi

# Start MongoDB with the custom data directory
mongod --dbpath "$MONGO_DATA_DIR"

