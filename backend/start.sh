#!/bin/sh
set -e

echo "Running database schema migrations..."
python -m backend.scripts.migrate

echo "Seeding initial accounts, catalog, and customers if empty..."
python -m backend.scripts.seed

echo "Starting Uvicorn web server on port $PORT..."
exec uvicorn main:app --host 0.0.0.0 --port "$PORT"
