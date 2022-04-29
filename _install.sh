#!/bin/bash
SCRIPT_DIR=$(dirname $0)
cd $SCRIPT_DIR
COLOR="3[4;34;37m"
NONE="3[0m"

NO_FORMAT="\033[0m"
F_BOLD="\033[1m"
C_CHARTREUSE2="\033[38;5;82m"

mkdir -p logs

echo -e "${C_CHARTREUSE2}Installing Virtual Environment${NO_FORMAT}"
pip3 install virtualenv

echo -e "${C_CHARTREUSE2}Creating Virtual Environment${NO_FORMAT}"
virtualenv venv

echo -e "${C_CHARTREUSE2}Activating Virtual Environment${NO_FORMAT}"
source venv/bin/activate

echo -e "${C_CHARTREUSE2}Installing requirements ${NO_FORMAT}"
pip3 install -r ./LitteBotServer/requirements.txt

echo -e "${C_CHARTREUSE2}Installation complete${NO_FORMAT}"
