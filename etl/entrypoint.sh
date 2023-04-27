#!/bin/sh

sleep 20
python postgres_to_es.py

exec "$@"
