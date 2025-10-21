#!/bin/sh
set -e

# Create data directory if it doesn't exist
mkdir -p /app/data/epg_files

# Set proper permissions
chmod 755 /app/data
chmod 755 /app/data/epg_files

# Wait for any initialization
echo "Starting EPG Merger..."

# Execute the main command
exec "$@"
