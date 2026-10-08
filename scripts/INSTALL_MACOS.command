#!/bin/bash
set -e
cd "$(dirname "$0")/.."
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
echo
echo "Vacuum Voice Hub installed. Opening local UI..."
python -m vacuum_voice_hub web
