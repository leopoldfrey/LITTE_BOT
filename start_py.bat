
cd ./LitteBotEditor
start py ./LitteBotEditor.py

cd ../LitteBotServer
start py ./LitteBotBrain.py

timeout /t 40 /nobreak

py ./LitteBotServer.py