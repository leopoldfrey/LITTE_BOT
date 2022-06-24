#!/usr/bin/env python3
import bottle, sys, os, time, json, webbrowser, random, signal
from subprocess import Popen
from sys import platform as _platform
from bottle import static_file
from gtts_synth import TextToSpeech
from threading import Thread
from websocket_server import WebsocketServer
from pyosc import Client, Server
# from ringCtrl import PhoneCtrl

import functools
print = functools.partial(print, flush=True)

class ThreadGroup(Thread):
    def __init__(self, parent):
        Thread.__init__(self)
        self.thread_group = []
        self.parent = parent;

    def addThread(self, t):
        self.thread_group.append(t)

    def stop(self):
        for t in self.thread_group[:]:
            t.stop()

    def run(self):
        while True:
            for t in self.thread_group[:]:
                if not t.is_alive(): #isAlive
                    # self.parent.video_client.send("/botspeak", 0)
                    self.parent.video_client.send("/phase", 0)
                    self.parent.sound_client.send("/phase", 0)
                    self.parent.lastInteractionTime = time.time()
                    # print("END OF SYNTH THREAD")
                    self.thread_group.remove(t)
                    if(self.parent.on == False):
                        # print("OFF!!!")
                        pass
                    elif(self.parent.flagUserLost == True):
                        print("[Server] USER LOST")
                        self.flagWaitUser = False
                        self.parent.areYouThere()
                    elif(self.parent.flagWaitUser == True):
                        print("[Server] WAIT USER")
                        self.parent.silent = False
                        self.parent.wsServer.broadcast({'command':'silent','value':False})
                    elif(self.parent.step == 3):
                        self.parent.nextInter()
                    elif(self.parent.step == 6):
                        self.parent.nextEpilogue()
                    else:
                        # print("DO RELANCE ?", self.parent.interactions % self.parent.config["max_inter_relance"])
                        if(self.parent.interactions % self.parent.config["max_inter_relance"] == self.parent.config["max_inter_relance"] - 1):
                            # print("DO RELANCE !!!")
                            time.sleep(1)
                            self.parent.relance()
                        else:
                            # print("REDONNE LA PAROLE !!!")
                            self.parent.silent = False
                            self.parent.wsServer.broadcast({'command':'silent','value':False})

class LitteBotWebSocket(Thread):
    def __init__(self, parent):
        Thread.__init__(self)
        self.port=9001
        self.parent = parent
        self.server = WebsocketServer(port=self.port)
        self.server.set_fn_new_client(self.new_client)
        self.server.set_fn_client_left(self.client_left)
        self.server.set_fn_message_received(self.message_received)

    def broadcast(self, message):
        self.server.send_message_to_all(json.dumps(message))

    # Called for every client connecting (after handshake)
    def new_client(self, client, server):
        # print("[ws] Client(%d) connected" % client['id'])
        self.broadcast({"command":"message","value":"Connection established"})
        self.broadcast({"command":"on","value":self.parent.on})
        self.broadcast({"command":"phone","value":self.parent.phone})

    # Called for every client disconnecting
    def client_left(self, client, server):
    	#print("[ws] Client(%d) disconnected" % client['id'])
        pass

    # Called when a client sends a message
    def message_received(self, client, server, message):
        # if len(message) > 200:
        # 	message = message[:200]+'..'
        print("[Server] [ws] %s (%d)" % (message, client['id']))
        msg = json.loads(message)
        # print(msg["command"])
        if msg["command"] == "connect" :
            self.parent.wsServer.broadcast({'command':'step','value':self.parent.step})
            self.parent.wsServer.broadcast({'command':'silent','value':self.parent.silent})
        elif msg["command"] == "pause" :
            self.parent.pause()
        elif msg["command"] == "reset" :
            self.parent.reset()
        elif msg["command"] == "stop" :
            self.parent.reset()
        elif msg["command"] == "stepUp" :
            self.parent.resume()
            self.parent.stepUp()
        elif msg["command"] == "getConfig" :
            self.parent.getConfig()
        elif msg["command"] == "saveConfig" :
            # self.parent.config["max_interactions"] = int(msg["max_interactions"])
            # self.parent.config["max_section"] = int(msg["max_section"])
            self.parent.config["max_silence"] = int(msg["max_silence"])
            self.parent.config["max_inter_relance"] = int(msg["max_inter_relance"])
            self.parent.config["max_intro"] = int(msg["max_intro"])
            self.parent.config["max_seduction"] = int(msg["max_seduction"])
            self.parent.config["max_provocation"] = int(msg["max_provocation"])
            self.parent.config["max_fuite"] = int(msg["max_fuite"])
            self.parent.config["max_intro_s"] = int(msg["max_intro_s"])
            self.parent.config["max_seduction_s"] = int(msg["max_seduction_s"])
            self.parent.config["max_provocation_s"] = int(msg["max_provocation_s"])
            self.parent.config["max_fuite_s"] = int(msg["max_fuite_s"])
            self.parent.config["pitch_intro"] = float(msg["pitch_intro"])
            self.parent.config["pitch_seduction"] = float(msg["pitch_seduction"])
            self.parent.config["pitch_provocation"] = float(msg["pitch_provocation"])
            self.parent.config["pitch_fuite"] = float(msg["pitch_fuite"])
            self.parent.config["pitch_epilogue"] = float(msg["pitch_epilogue"])
            self.parent.config["speed_intro"] = float(msg["speed_intro"])
            self.parent.config["speed_seduction"] = float(msg["speed_seduction"])
            self.parent.config["speed_provocation"] = float(msg["speed_provocation"])
            self.parent.config["speed_fuite"] = float(msg["speed_fuite"])
            self.parent.config["speed_epilogue"] = float(msg["speed_epilogue"])
            self.parent.saveConfig()
        elif msg["command"] == "phone" :
            if(int(msg["phone"]) == 1):
                self.parent.phoneOn()
            else:
                self.parent.phoneOff()
        elif msg["command"] == "reload" :
            self.parent.osc_client.send("/reload", 1)

    def run(self):
        self.server.run_forever()

    def stop(self):
        self.server.stop()

class LitteBotServer:
    global is_restart_needed

    def __init__(self, http_server_port=8080, jsonFile="none"):
        #init
        self.http_server_port = http_server_port
        self.on = False
        self.phone = False
        self.silent = True
        self.step = 0
        self.username = ""
        self.startTime = time.time()
        self.startSectionTime = time.time()
        self.lastInteractionTime = time.time()
        self.globalTime = 0
        self.sectionTime = 0
        self.currentTime = 0
        self.interactions = 0
        self.interactions_section = 0
        self.is_restart_needed = True
        self.tmp_response = ""
        self.flagUserLost = False
        self.flagWaitUser = False
        self.flagWaitEnd = False
        self.waitHangPhone = False

        #read from settings.json
        print("[Server] ___READING CONFIG___")
        self.config = {
            "max_interactions": 12,
            "max_silence": 12,
            "max_section": 200,
            "max_inter_relance": 5,
            "max_intro": 5,
            "max_intro_s": 50,
            "pitch_intro": 0.0,
            "speed_intro": 1.08,
            "max_seduction": 30,
            "max_seduction_s": 200,
            "pitch_seduction": 0.0,
            "speed_seduction": 1.1,
            "max_provocation": 12,
            "max_provocation_s": 120,
            "pitch_provocation": 0.0,
            "speed_provocation": 1.12,
            "max_fuite": 12,
            "max_fuite_s": 120,
            "pitch_fuite": 0.0,
            "speed_fuite": 1.13,
            "pitch_epilogue": 0.0,
            "speed_epilogue": 1.14
        }
        self.readConfig()

        print("[Server] ___INIT TextToSpeech___")
        TextToSpeech("Dom Juan", silent=True).start()

        # print("[Server] ___INIT_RING___")
        # self.phoneCtrl = PhoneCtrl()

        #websocket
        print("[Server] ___STARTING WEBSOCKETSERVER___")
        self.wsServer = LitteBotWebSocket(self)
        self.wsServer.start()

        #threadgroup (pour surveiller la fin de la synthèse vocale)
        print("[Server] ___INIT THREADGROUP___")
        self.tg = ThreadGroup(self)
        self.tg.start()

        print("[Server] ___STARTING OSC___")
        self.osc_server = Server('0.0.0.0', 14000, self.oscIn)
        self.osc_client = Client('127.0.0.1', 14001)
        self.video_server = Server('127.0.0.1', 14002, self.video_oscIn)
        self.video_client = Client('127.0.0.1', 14003)
        self.sound_client = Client('127.0.0.1', 14004)
        self.led_client = Client('127.0.0.1', 14005)

        print("[Server] ___INIT BOT___")
        self.osc_client.send('/newConversation',1)

        print("[Server] ___CONFIGURING SERVER___")
        self.http_server = bottle.Bottle()
        self.http_server.get('/', callback=self.index)
        self.http_server.get('/viewer', callback=self.viewer)
        self.http_server.get('/style.css', callback=self.css)
        self.http_server.post('/reco', callback=self.reco)
        self.http_server.get('/poll', callback=self.poll)
        # print()
        # print('*** Please open chrome at http://127.0.0.1:%d' % self.http_server_port)
        # print()

        # ouverture de google chrome
        print("[Server] ___STARTING GOOGLE CHROME___")
        url = 'http://localhost:8080/'
        # MacOS
        if _platform == "darwin":
            chrome_path = 'open -a /Applications/Google\ Chrome.app %s'
            webbrowser.get(chrome_path).open(url)
        elif _platform == "win32" or _platform == "win64":
            Popen(['C:\Program Files\Google\Chrome\Application\chrome.exe','http://localhost:8080'])
        # Linux
        # chrome_path = '/usr/bin/google-chrome %s'

        #démarrage du serveur
        print("[Server] ___STARTING SERVER___")
        self.http_server.run(host='localhost', port=self.http_server_port, quiet=True)

    def video_oscIn(self, address, *args):
        print("[Server] VIDEO OSC IN ", address, args[0])
        if(address == '/facedetect'):
            if self.on :
                if self.flagWaitEnd :
                    return
                elif int(args[0]) == 1 :
                    print("[Server] FACEDETECT User found")
                    self.flagUserLost = False
                    self.flagWaitUser = False
                else:
                    if self.flagWaitUser :
                        return
                    else:
                        print("[Server] FACEDETECT User lost")
                        self.flagUserLost = True
                        self.flagWaitUser = False
                return
            else:
                if int(args[0]) == 1 :
                    print("[Server] FACEDETECT User detected")
                    if self.phone :
                        self.waitHangPhone = True
                        self.phoneHang()
                    else:
                        # self.phoneCtrl.ring()
                        self.sound_client.send("/phone", "ring")
                else:
                    if self.phone :
                        self.phoneHang()
                    else:
                        # self.phoneCtrl.stop()
                        self.sound_client.send("/phone", "stop")
        elif(address == '/end'):
            if int(args[0]) == 1 : #fin vidéo finale
                self.flagWaitEnd = False
                print("[Server] END > RESTART")
                # self.led_client.send("/on", 0)
                self.sound_client.send("/stop", 0)
                self.reset()
                time.sleep(3)
                if self.phone :
                    self.phoneHang()
        elif(address == '/led'):
            self.led_client.send("/on", int(args[0]))
        elif(address == '/brightness'):
            self.led_client.send("/brightness", int(args[0]))

        # else:
        #     print("VIDEO OSC IN : "+str(address))
        #     for x in range(0,len(args)):
        #         print("     " + str(args[x]))

    def oscIn(self, address, *args):
        print("[Server] OSC IN ", address, args[0])
        if(address == '/lastresponse'):
            self.receiveResponse(args[0])
        elif(address == '/curEpilogue'):
            self.curEpilogue(args[0])
        elif(address == '/endEpilogue'):
            self.endEpilogue()
        elif(address == '/curInter'):
            self.curInter(args[0])
        elif(address == '/endInter'):
            self.endInter()
        elif(address == '/username'):
            self.name(args[0])
        elif(address == '/phone'):
            if(args[0] == 1):
                self.phoneOn()
            else:
                self.phoneOff()
        else:
            print("[Server] OSC IN : "+str(address))
            for x in range(0,len(args)):
                print("     " + str(args[x]))

    def phoneOn(self):
        print("[Server] PHONE ON")
        if self.on or self.phone :
            return
        self.reset()
        # self.phoneCtrl.stop()
        self.sound_client.send("/phone", "stop")
        self.on = True
        self.phone = True
        self.video_client.send("/phone", 1)
        self.wsServer.broadcast({"command":"phone","value":self.phone})
        self.wsServer.broadcast({"command":"on","value":self.on})
        self.wsServer.broadcast({'command':'silent','value':self.silent})

        time.sleep(1)
        self.first()

    def phoneOff(self):
        print("[Server] PHONE OFF")
        if self.flagWaitEnd :
            self.phone = False
            self.video_client.send("/phone", 0)
        elif self.waitHangPhone :
            self.phone = False
            self.waitHangPhone = False
            self.video_client.send("/phone", 0)
            # self.phoneCtrl.ring()
            self.sound_client.send("/phone", "ring")
        elif self.on :
            # self.phoneCtrl.stop()
            self.sound_client.send("/phone", "stop")
            self.sound_client.send("/stop", 0)
            self.tg.stop()
            self.phone = False
            self.video_client.send("/phone", 0)
            self.silent = True
            self.reset()
        else:
            # self.phoneCtrl.stop()
            self.sound_client.send("/phone", "stop")
            self.sound_client.send("/stop", 0)
            self.tg.stop()
            self.phone = False
            self.video_client.send("/phone", 0)
            self.silent = True
        self.wsServer.broadcast({'command':'silent','value':self.silent})
        self.wsServer.broadcast({"command":"phone","value":self.phone})
        self.wsServer.broadcast({"command":"on","value":self.on})


    def phoneHang(self):
        print("[Server] RACCROCHEZ")
        # self.phoneCtrl.hang()
        self.sound_client.send("/phone", "hang")

    def reco(self):
        self.flagUserLost = False
        self.flagWaitUser = False
        result = {'transcript': str(bottle.request.forms.getunicode('transcript')),
                'confidence': float(bottle.request.forms.get('confidence', 0)),
                'sentence': int(bottle.request.forms.sentence)}
        mess = result['transcript']
        self.lastInteractionTime = time.time()
        # print(result['sentence'], mess);
        # if self.silent == True:
        #     if result['sentence'] == 1:
        #         print("(pause)phrase  _" + mess)
        #     else:
        #         print("(pause)mots    _" + mess)
        #     return ''
        if result['sentence'] == 1:
            # print("user:", mess)
            # self.lastInteractionTime = time.time()
            self.wsServer.broadcast({'command':'_user','value':mess})
            self.video_client.send("/user", mess)
            self.video_client.send("/phase", 1)
            self.sound_client.send("/phase", 1)
            self.silent = True
            self.wsServer.broadcast({'command':'silent','value':self.silent})
            # print("INTER", self.interactions)
            if self.interactions == 1:
                self.osc_client.send('/logme', mess)
                self.second(mess)
            elif self.interactions == 2:
                self.osc_client.send('/logme', mess)
                self.third(mess)
            elif self.step == 3:
                self.osc_client.send('/logme', mess)
                self.nextInter()
            elif self.step < 6 :
                self.osc_client.send('/getresponse', mess)
            else : #epilogue
                self.osc_client.send('/logme', mess)
                self.nextEpilogue()

        return ''

    def speak(self, txt):
        # print("SPEAK", txt, "pitch", self.pitch[self.step], "speed", self.speed[self.step])
        if self.step < 3 :
            v = random.randrange(5)
            p = (random.random() * 8.) - 4.
            s = self.speed[self.step] + (random.random() * 0.2 - 0.1)
        else:
            v = 0
            p = self.pitch[self.step]
            s = self.speed[self.step]
        tts = TextToSpeech(txt, pitch=p, speed=s, voice=v)
        tts.start()
        self.tg.addThread(tts)

    def receiveResponse(self, r):
        self.tmp_response = r
        if(self.tmp_response.__contains__("__TO_EPILOGUE__")):
            self.toEpilogue()
            return
        elif(self.flagUserLost):
            self.flagUserLost = False
            self.flagWaitUser = True
        # print("SERVER receiveResponse", self.tmp_response)
        self.video_client.send("/phase", 2)
        self.sound_client.send("/phase", 2)
        self.video_client.send("/bot", self.tmp_response)
        self.interactions += 1
        self.interactions_section += 1
        self.video_client.send("/interactions", self.interactions)
        self.lastInteractionTime = time.time()
        self.wsServer.broadcast({'command':'_bot','value':self.tmp_response})
        # print("INTERACTIONS", self.interactions % self.config["max_interactions"])
        if self.step == 0 :
            self.stepUp()
        elif self.step > 0 and self.interactions_section >= self.maxinter[self.step] :
            self.stepUp()
        self.speak(self.tmp_response)

    def stepUp(self):
        # print("STEP UP")
        # if self.step == 0 :
        #     self.osc_client.send("/newConversation", 1)
        self.step = self.step + 1
        self.interactions_section = 0
        if self.step == 1 :
            self.startTime = time.time()
            self.lastInteractionTime = time.time()
        self.startSectionTime = time.time()
        if self.step > 6 :
            self.step = 0
        self.osc_client.send("/setbotmode", self.step)
        self.video_client.send("/section", self.step)
        self.sound_client.send("/section", self.step)
        self.wsServer.broadcast({'command':'step','value':self.step})

    def toEpilogue(self):
        # print("TO EPILOGUE")
        self.step = 6
        self.startSectionTime = time.time()
        self.osc_client.send("/setbotmode", self.step)
        self.video_client.send("/section", self.step)
        self.sound_client.send("/section", self.step)
        self.wsServer.broadcast({'command':'step','value':self.step})
        self.nextEpilogue()

    def curEpilogue(self, s):
        self.interactions += 1
        self.interactions_section += 1
        self.video_client.send("/interactions", self.interactions)
        self.silent = True
        self.wsServer.broadcast({'command':'silent','value':self.silent})
        self.lastInteractionTime = time.time()
        self.video_client.send("/phase", 2)
        self.sound_client.send("/phase", 2)
        self.video_client.send("/bot", s)
        self.speak(s)
        self.wsServer.broadcast({"command":"bot","value":s})

    def endEpilogue(self):
        print("[Server] WAIT FOR END")
        self.flagWaitEnd = True
        self.silent = True
        self.wsServer.broadcast({'command':'silent','value':self.silent})
        self.video_client.send("/stop", 1) # déclenchement vidéo finale
        self.sound_client.send("/stop", 1)

    def nextEpilogue(self):
        self.osc_client.send("/nextEpilogue", 1)

    def curInter(self, s):
        self.interactions += 1
        self.interactions_section += 1
        self.video_client.send("/interactions", self.interactions)
        self.silent = True
        self.wsServer.broadcast({'command':'silent','value':self.silent})
        self.lastInteractionTime = time.time()
        self.video_client.send("/phase", 2)
        self.sound_client.send("/phase", 2)
        self.video_client.send("/bot", s)
        self.speak(s)
        self.wsServer.broadcast({"command":"bot","value":s})

    def endInter(self):
        self.silent = False
        self.wsServer.broadcast({'command':'silent','value':self.silent})
        self.stepUp()

    def nextInter(self):
        self.osc_client.send("/nextInter", 1)

    def areYouThere(self):
        self.osc_client.send("/areYouThere", 1)

    def relance(self):
        if(self.flagWaitUser):
            print("[Server] USER REALLY LOST > RESET")
            self.video_client.send("/stop", 0)
            self.sound_client.send("/stop", 0)
            self.phoneHang()
            self.reset()
        elif(self.flagUserLost):
            print("[Server] USER LOST")
            self.flagWaitUser = False
            self.areYouThere()
        else:
            self.silent = True
            self.wsServer.broadcast({'command':'silent','value':self.silent})
            self.lastInteractionTime = time.time()
            self.osc_client.send("/relance", 1)

    def first(self):
        print("[Server] FIRST")
        self.silent = True
        self.wsServer.broadcast({'command':'silent','value':self.silent})
        self.lastInteractionTime = time.time()
        self.osc_client.send("/first", 1)

    def second(self, mess):
        print("[Server] SECOND")
        self.silent = True
        self.wsServer.broadcast({'command':'silent','value':self.silent})
        self.lastInteractionTime = time.time()
        self.osc_client.send("/second", mess)

    def third(self, mess):
        print("[Server] THIRD")
        self.silent = True
        self.wsServer.broadcast({'command':'silent','value':self.silent})
        self.lastInteractionTime = time.time()
        self.osc_client.send("/third", mess)

    def reset(self):
        print("[Server] RESET")
        self.on = False
        self.step = 0
        self.name("")
        self.startTime = time.time()
        self.startSectionTime = time.time()
        self.lastInteractionTime = time.time()
        self.interactions = 0
        self.interactions_section = 0
        self.flagUserLost = False
        self.flagWaitUser = False
        self.flagWaitEnd = False
        self.video_client.send("/interactions", self.interactions)
        self.wsServer.broadcast({'command':'step','value':self.step})
        self.wsServer.broadcast({'command':'clear'})
        self.wsServer.broadcast({'command':'silent','value':self.silent})
        self.wsServer.broadcast({"command":"phone","value":self.phone})
        self.wsServer.broadcast({"command":"on","value":self.on})
        self.silent = True
        self.osc_client.send("/newConversation", 1)

    def name(self, name):
        self.username = name
        self.wsServer.broadcast({'command':'username','value':self.username})

    def updateTimers(self):
        if(self.step != 0):
            self.globalTime = time.time() - self.startTime
            self.sectionTime = time.time() - self.startSectionTime
            self.currentTime = time.time() - self.lastInteractionTime
            if self.currentTime > self.config["max_silence"]:
                if(self.step > 0 and self.step < 6 and not self.silent):
                    self.relance()
            if(self.step > 0 and self.step < 6 and self.sectionTime > self.maxsection[self.step]):
                self.stepUp()
        else:
            self.globalTime = 0
            self.sectionTime = 0
            self.currentTime = 0

        # self.video_client.send("/globalTime", int(self.globalTime))
        # self.video_client.send("/sectionTime", int(self.sectionTime))
        # self.video_client.send("/currentTime", int(self.currentTime))
        self.wsServer.broadcast({"command":"timers","global":self.globalTime, "section":self.sectionTime, "current":self.currentTime, 'interactions':self.interactions, 'interactions_section':self.interactions_section, 'maxinter_section':self.maxinter[self.step]})

    def poll(self):
        self.updateTimers()
        if self.is_restart_needed:
            self.is_restart_needed = False
            return {'restart':True};
        return {'restart':False};

    def index(self):
        return open("public/index.html", "rt").read()

    def viewer(self):
        return open("public/viewer.html", "rt").read()

    def css(self):
        return static_file("public/style.css", root="")

    def getConfig(self):
        self.wsServer.broadcast({
            'command':'params',
            # 'max_interactions':self.config["max_interactions"],
            # 'max_section':self.config["max_section"],
            'max_silence':self.config["max_silence"],
            'max_inter_relance':self.config["max_inter_relance"],
            'max_intro':self.config["max_intro"],
            'max_seduction':self.config["max_seduction"],
            'max_provocation':self.config["max_provocation"],
            'max_fuite':self.config["max_fuite"],
            'max_intro_s':self.config["max_intro_s"],
            'max_seduction_s':self.config["max_seduction_s"],
            'max_provocation_s':self.config["max_provocation_s"],
            'max_fuite_s':self.config["max_fuite_s"],
            'speed_intro':self.config["speed_intro"],
            'speed_seduction':self.config["speed_seduction"],
            'speed_provocation':self.config["speed_provocation"],
            'speed_fuite':self.config["speed_fuite"],
            'speed_epilogue':self.config["speed_epilogue"],
            'pitch_intro':self.config["pitch_intro"],
            'pitch_seduction':self.config["pitch_seduction"],
            'pitch_provocation':self.config["pitch_provocation"],
            'pitch_fuite':self.config["pitch_fuite"],
            'pitch_epilogue':self.config["pitch_epilogue"]
        })

    def saveConfig(self):
        # print("CONFIG", self.config)
        with open('settings.json', 'w') as f:
            json.dump(self.config, f, indent=4)
        self.updateParams()

    def readConfig(self):
        with open('settings.json', 'r') as f:
            self.config = json.load(f)
        self.updateParams()

    def updateParams(self):
        self.maxsection = []
        self.maxsection.append(200)
        self.maxsection.append(self.config["max_intro_s"])
        self.maxsection.append(self.config["max_seduction_s"])
        self.maxsection.append(self.config["max_seduction_s"])
        self.maxsection.append(self.config["max_provocation_s"])
        self.maxsection.append(self.config["max_fuite_s"])
        self.maxsection.append(200)

        self.maxinter = []
        self.maxinter.append(50)
        self.maxinter.append(self.config["max_intro"])
        self.maxinter.append(self.config["max_seduction"])
        self.maxinter.append(self.config["max_seduction"])
        self.maxinter.append(self.config["max_provocation"])
        self.maxinter.append(self.config["max_fuite"])
        self.maxinter.append(50)

        self.pitch = []
        self.pitch.append(self.config["pitch_intro"])
        self.pitch.append(self.config["pitch_intro"])
        self.pitch.append(self.config["pitch_seduction"])
        self.pitch.append(self.config["pitch_epilogue"])
        self.pitch.append(self.config["pitch_provocation"])
        self.pitch.append(self.config["pitch_fuite"])
        self.pitch.append(self.config["pitch_epilogue"])

        self.speed = []
        self.speed.append(self.config["speed_intro"])
        self.speed.append(self.config["speed_intro"])
        self.speed.append(self.config["speed_seduction"])
        self.speed.append(self.config["speed_epilogue"])
        self.speed.append(self.config["speed_provocation"])
        self.speed.append(self.config["speed_fuite"])
        self.speed.append(self.config["speed_epilogue"])

        # print("MAXSECTION", self.maxsection)
        # print("MAXINTER", self.maxinter)
        # print("PITCH", self.pitch)
        # print("SPEED", self.speed)

    def resume(self):
        self.silent = False
        self.wsServer.broadcast({'command':'silent','value':self.silent})

    def pause(self):
        self.silent = not self.silent
        self.wsServer.broadcast({'command':'silent','value':self.silent})

    def kill(self):
        # print("Stop Http Osc Server")
        # self.http_server.shutdown()
        # print("Stop Websocket")
        # self.wsServer.stop()
        print("[Server] Stop Video Osc Server")
        self.video_server.stop()
        print("[Server] Stop Brain Osc Server")
        self.osc_server.stop()
        os._exit(0)

if __name__ == '__main__':
    LitteBotServer()
    # try:
    #     bot_server = LitteBotServer()
    # except KeyboardInterrupt:
    #     pass
    # finally:
    #     bot_server.kill()
