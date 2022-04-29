#!/bin/sh
source venv/bin/activate
SCRIPT_DIR=$(dirname $0)/LitteBotEditor
cd $SCRIPT_DIR
export PYTHONPATH=$SCRIPT_DIR
python3 ./LitteBotEditor.py
