#!/usr/bin/env bash
echo Migrations...
alembic upgrade head;
echo Start app...
gunicorn main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
