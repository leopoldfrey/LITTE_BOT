#!/bin/sh
SCRIPT_DIR=$(dirname $0)
cd $SCRIPT_DIR
source venv/bin/activate
cd $SCRIPT_DIR/LitteBotServer
export PYTHONPATH=$SCRIPT_DIR
python3 ./LitteBotBrain.py &
sleep 30
python3 ./LitteBotServer.py
