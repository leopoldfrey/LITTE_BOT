
cd ./LitteBotEditor
start py ./LitteBotEditor.py

cd ../LitteBotLed
start node ./ledCtrl.js

cd ../LitteBotServer
start py ./LitteBotSound.py

start py ./LitteBotBrain.py

timeout /t 40 /nobreak

py ./LitteBotServer.py
