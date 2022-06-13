#!/bin/sh
SCRIPT_DIR=$(dirname $0)
cd $SCRIPT_DIR
source venv/bin/activate
cd $SCRIPT_DIR/LitteBotServer
export PYTHONPATH=$SCRIPT_DIR
python3 ./LitteBotBrain.py &
python3 ./LitteBotSound.py &
sleep 20
python3 ./LitteBotServer.py
