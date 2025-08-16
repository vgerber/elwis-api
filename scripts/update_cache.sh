#!/bin/bash

# Usage: ./update_cache.sh [port]
PORT=${1:-8000}

# Read credentials from secrets files
USER=$(cat ./secrets/admin_user)
PASS=$(cat ./secrets/admin_password)

# Call the cache update endpoint with HTTP Basic Auth
curl -u "$USER:$PASS" -X POST http://localhost:$PORT/cache/update
