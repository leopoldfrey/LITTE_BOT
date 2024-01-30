#!/usr/bin/env python3
import os, sys, time
import google.cloud.texttospeech as tts
from sys import platform as _platform
from threading import Thread
from pedalboard import *
from pedalboard.io import AudioFile
import subprocess
import re
# if _platform == "darwin":
#     from playsound import playsound
import functools
print = functools.partial(print, end='\n',flush=True)

VOICE = ["es-ES-Wavenet-C", "es-ES-Wavenet-D", "es-ES-Wavenet-B", "es-ES-Neural2-A", "es-ES-Neural2-B", "es-ES-Neural2-C", "es-ES-Neural2-D", "es-ES-Neural2-E", "es-ES-Neural2-F", "es-ES-Polyglot-1" ]

'''
fr-FR-Wavenet-E
fr-FR-Wavenet-A
fr-FR-Wavenet-B
fr-FR-Wavenet-C
fr-FR-Wavenet-D
fr-FR-Standard-A
fr-FR-Standard-B
fr-FR-Standard-C
fr-FR-Standard-D
fr-FR-Standard-E

fr-FR-Neural2-A
fr-FR-Neural2-B
fr-FR-Neural2-C
fr-FR-Neural2-D
fr-FR-Neural2-E

es-ES-Wavenet-C
es-ES-Wavenet-D
es-ES-Wavenet-B
es-ES-Neural2-A
es-ES-Neural2-B
es-ES-Neural2-C
es-ES-Neural2-D
es-ES-Neural2-E
es-ES-Neural2-F
es-ES-Polyglot-1
'''

API_KEY_PATH = "../model/gtts_api_key.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = API_KEY_PATH

# Make a Pedalboard object, containing multiple plugins:
board = Pedalboard([Gain(4),PitchShift(semitones=-3),Chorus(),Reverb(room_size=0.02,damping=0.1,wet_level=0.7,dry_level=1.,width=0.9,freeze_mode=0)])

#PitchShift(semitones=+3),
def list_voices():
    client = tts.TextToSpeechClient()
    voices = client.list_voices()

    for voice in voices.voices:
        if"fr-FR" in voice.language_codes:
            print(f"{voice.name}")
        if"es-ES" in voice.language_codes:
            print(f"{voice.name}")

class TextToSpeech(Thread):
    def __init__(self, text, pitch=0.0, speed=1.08, voice=2, silent=False):
        Thread.__init__(self)
        print("[Server] [TextToSpeech]", pitch, speed, VOICE[voice])#, text)
        self.language_code = "-".join(VOICE[0].split("-")[:2])
        if(len(text) > 500):
            self.textA = re.split("[.!?;:]", text)
        else:
            self.textA = []
            self.textA.append(text)
        # print(len(self.textA), self.textA)
        self.voice = voice
        self.voice_params = tts.VoiceSelectionParams(
            language_code=self.language_code, name=VOICE[self.voice]
        )
        self.audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.LINEAR16, speaking_rate=speed, pitch=pitch)
        self.client = tts.TextToSpeechClient()
        self._running = True
        self.silent = silent
        self.pid = 0

    def stop(self):
        # print("TODO STOP VOICE", self.pid)
        self.textA = []
        if(self.pid != 0):
            if _platform == "darwin":
                subprocess.Popen(["kill", str(self.pid)])
            else:
                subprocess.Popen(["taskkill", "/PID", str(self.pid)])
        # pass

    def run(self):
        t = self.textA.pop(0)
        while t != "":
        # for t in self.textA :
            self.text_input = tts.SynthesisInput(text=t)
            if t != "":
                # print("speak", t)
                response = self.client.synthesize_speech(
                    input=self.text_input, voice=self.voice_params, audio_config=self.audio_config
                )
                filename = "output.wav"
                with open(filename, "wb") as out:
                    out.write(response.audio_content)

                # Read in a whole audio file:
                with AudioFile(filename, 'r') as f:
                  audio = f.read(f.frames)
                  samplerate = f.samplerate

                # Run the audio through this pedalboard!
                effected = board(audio, samplerate)

                # Write the audio back as a wav file:
                with AudioFile('processed-output.wav', 'w', samplerate, effected.shape[0]) as f:
                  f.write(effected)

                if self.silent:
                    return

                if _platform == "darwin":
                    self.proc = subprocess.Popen(["ffplay","-nodisp","-autoexit","-loglevel","quiet","processed-output.wav"])
                    self.pid = self.proc.pid
                    # print("process pid", self.pid)
                    self.proc.wait()
                    # while (self.proc.poll() is None):
                    #     print("wait")
                    #     time.sleep(1)
                    #playsound('processed-output.wav')
                elif _platform == "win32" or _platform == "win64":
                    self.proc = subprocess.Popen(["ffplay.exe","-nodisp","-autoexit","-loglevel","quiet","processed-output.wav"])
                    self.pid = self.proc.pid
                    # print("process pid", self.pid)
                    self.proc.wait()
                    #os.system("ffplay.exe -nodisp -autoexit -loglevel quiet .\processed-output.wav")
            if len(self.textA) > 0:
                t = self.textA.pop(0)
            else:
                return

class TextToSpeechNoThread():
    def __init__(self):
        self.language_code = "-".join(VOICE[0].split("-")[:2])
        #self.audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.LINEAR16)
        self.client = tts.TextToSpeechClient()

    def synthesize(self, text, pitch=0.0, speed=1.08, voice=0, fname="output", play=True):
        self.voice = voice
        self.voice_params = tts.VoiceSelectionParams(
            language_code=self.language_code, name=VOICE[self.voice]
        )
        self.audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.LINEAR16, speaking_rate=speed, pitch=pitch)
        self.text_input = tts.SynthesisInput(text=text)
        response = self.client.synthesize_speech(
            input=self.text_input, voice=self.voice_params, audio_config=self.audio_config
        )
        filename = "tmp.wav"
        with open(filename, "wb") as out:
            out.write(response.audio_content)

        # Read in a whole audio file:
        with AudioFile(filename, 'r') as f:
          audio = f.read(f.frames)
          samplerate = f.samplerate

        # Run the audio through this pedalboard!
        effected = board(audio, samplerate)

        # Write the audio back as a wav file:
        proc_filename = fname+".wav"
        with AudioFile(proc_filename, 'w', samplerate, effected.shape[0]) as f:
          f.write(effected)

        if play:
            self.proc = subprocess.Popen(["ffplay","-nodisp","-autoexit","-loglevel","quiet",proc_filename])
            self.pid = self.proc.pid
            # print("process pid", self.pid)
            self.proc.wait()
            # os.system("ffplay.exe -nodisp -autoexit -loglevel quiet .\processed-output.wav")


if __name__ == '__main__':
    #list_voices()
    if len(sys.argv) == 2:
        thd = TextToSpeech(sys.argv[1])
        thd.start()
    elif len(sys.argv) == 3:
        thd = TextToSpeech(sys.argv[1], voice=int(sys.argv[2]))
        thd.start()
    elif len(sys.argv) == 4:
        thd = TextToSpeech(sys.argv[1], float(sys.argv[2]), float(sys.argv[3]))
        thd.start()
    elif len(sys.argv) == 5:
        thd = TextToSpeech(sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4]))
        thd.start()
        # print(thd.is_alive())
        # tts = TextToSpeechNoThread()
        # tts.synthesize(sys.argv[1])
    else:
        print('usage: %s <text-to-synthesize>')
