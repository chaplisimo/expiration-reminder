#!/bin/bash
# Wrapper script executed by cron.
# Runs the expiration-reminder using the virtualenv Python.

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$APP_DIR" || exit 1

"$APP_DIR/venv/bin/python" -m expiration_reminder
