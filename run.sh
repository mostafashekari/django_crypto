#!/bin/bash

until python3 manage.py runserver 46.249.102.39:8000; do
    echo "Server crashed with exit code $?. Respawning.." >&2
    sleep 1
done
