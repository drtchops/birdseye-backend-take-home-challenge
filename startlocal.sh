#!/bin/sh

alembic upgrade head
python -Xfrozen_modules=off -m debugpy --listen 0.0.0.0:5678 -m fastapi dev --host 0.0.0.0 src/api.py
