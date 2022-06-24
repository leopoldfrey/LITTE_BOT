
cd ./LitteBotEditor
start python3 ./LitteBotEditor.py

cd ../LitteBotLed
start node ./ledCtrl.js

cd ../LitteBotServer
start python3 ./LitteBotSound.py

start python3 ./LitteBotBrain.py

timeout /t 40 /nobreak

python3 ./LitteBotServer.py
