set curdir = %CD%
cd %curdir%\LitteBotEditor
start python3 ./LitteBotEditor.py

cd %curdir%\LitteBotServer
start python3 ./LitteBotBrain.py

timeout /t 40 /nobreak

python3 ./LitteBotServer.py


:: ps -name python3.9 | select -expand id
