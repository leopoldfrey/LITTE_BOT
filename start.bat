cd C:\Users\littl\Documents\LITTE_BOT\LitteBotEditor
start python3 ./LitteBotEditor.py

cd C:\Users\littl\Documents\LITTE_BOT\LitteBotServer
start python3 ./LitteBotBrain.py

timeout /t 40 /nobreak

python3 ./LitteBotServer.py


:: ps -name python3.9 | select -expand id
