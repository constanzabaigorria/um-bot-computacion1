#!/usr/bin/env bash
set -e

# El token puede pasarse por argumento (./start.sh <TOKEN>) o quedar en
# un archivo .env con BOT_TOKEN=... (ver .env.example). Si no hay ninguno
# de los dos, run.py va a avisar y salir.

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
pip install -q -r requirements.txt

python run.py "$@"