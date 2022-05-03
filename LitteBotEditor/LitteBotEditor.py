#!/usr/bin/env python3
import os, json, webbrowser, html
from bottle import post, static_file, template, Bottle, request
from sys import platform as _platform

import threading

dialog_path = "../data/"
def_questions_common = "dom_juan_common"
def_questions_seduction = "dom_juan_seduction"
def_questions_provocation = "dom_juan_provocation"
def_questions_fuite = "dom_juan_fuite"
def_questions_epilogue = "dom_juan_epilogue"


class LitteBotEditor():
    def __init__(self):

        print("Loading data...")
        self.filename = dialog_path + def_questions_common + ".json"
        self.load()

        print("___STARTING GOOGLE CHROME___")
        url = 'http://localhost:17995/'
        # MacOS
        if _platform == "darwin":
            chrome_path = 'open -a /Applications/Google\ Chrome.app %s'
        elif _platform == "win32" or _platform == "win64":
            chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
        # Linux
        # chrome_path = '/usr/bin/google-chrome %s'
        webbrowser.get(chrome_path).open(url)

        print("LitteBot Editor starting...")
        self.host = '0.0.0.0'
        self.port = int(os.environ.get("PORT", 17995))
        self.server = Bottle()
        self.route()
        self.start()

    def load(self):
        print("Loading data "+self.filename)
        with open(self.filename) as f:
            self.data = json.load(f)

    def start(self):
        # démarrage du serveur
        self.server.run(host=self.host, port=self.port)

    def route(self):
        self.server.route('/', method="GET", callback=self.index)
        self.server.route('/index', method="GET", callback=self.index)
        self.server.route('/index.html', method="GET", callback=self.index)
        self.server.route('/<dir>/<filename>', method="GET", callback=self.serveDir)
        self.server.route('/<filename>', method="GET", callback=self.serve)

        self.server.route('/getCommon', method="GET", callback=self.getCommon)
        self.server.route('/getSeduction', method="GET", callback=self.getSeduction)
        self.server.route('/getProvocation', method="GET", callback=self.getProvocation)
        self.server.route('/getFuite', method="GET", callback=self.getFuite)
        self.server.route('/getEpilogue', method="GET", callback=self.getEpilogue)

        self.server.route('/mod', method="POST", callback=self.mod)
        self.server.route('/save', method="POST", callback=self.save)
        self.server.route('/del', method="POST", callback=self.deleteId)

    def index(self):
        return static_file('index.html', root='./')

    def serveDir(self, dir, filename):
        return static_file(filename, root='./'+dir)

    def serve(self, filename):
        return static_file(filename, root='./')

    def getCommon(self):
        print("getCommon")
        self.filename = dialog_path + def_questions_common + ".json"
        self.load()
        return self.data

    def getSeduction(self):
        print("getSeduction")
        self.filename = dialog_path + def_questions_seduction + ".json"
        self.load()
        return self.data

    def getProvocation(self):
        print("getProvocation")
        self.filename = dialog_path + def_questions_provocation + ".json"
        self.load()
        return self.data

    def getFuite(self):
        print("getFuite")
        self.filename = dialog_path + def_questions_fuite + ".json"
        self.load()
        return self.data

    def getEpilogue(self):
        print("getEpilogue")
        self.filename = dialog_path + def_questions_epilogue + ".json"
        self.load()
        return self.data

    def save(self):
        with open(self.filename, "w") as f:
            json.dump(self.data, f, indent=4)
        return { "msg": "Sauvegarde en cours"}

    def mod(self):
        for k in request.forms:
            j = json.loads(k)
            idx = html.unescape(j['idx'])

            if j['q'].__contains__("_SEPARATOR_"):
                q = [html.unescape(l) for l in j['q'].split('_SEPARATOR_') if l.strip()]
            else:
                q = html.unescape(j['q'])

            if j['a'].__contains__("_SEPARATOR_"):
                a = [html.unescape(l) for l in j['a'].split('_SEPARATOR_') if l.strip()]
            else:
                a = html.unescape(j['a'])

            if idx in self.data:
                self.data[idx]['q'] = q
                self.data[idx]['a'] = a
            else:
                self.data[idx] = {'q':[], 'a':[]}
                self.data[idx]['q'] = q
                self.data[idx]['a'] = a

            self.save()

        return { "msg": "Modification effecuée"}

    def deleteId(self):
        for k in request.forms:
            idx = html.unescape(json.loads(k)['idx'])
            #print("TODO del", q)
            del self.data[idx]
            self.save()
        return { "msg": "Suppression effectuée"}

if __name__ == "__main__":
    try:
        server = LitteBotEditor()
    except KeyboardInterrupt:
        pass
    finally:
        os._exit(0)
