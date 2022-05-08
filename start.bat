pwd

cd LitteBotEditor
start python3 ./LitteBotEditor.py

 cd ../LitteBotServer
 start python3 ./LitteBotBrain.py

 timeout /t 40 /nobreak

 python3 ./LitteBotServer.py
