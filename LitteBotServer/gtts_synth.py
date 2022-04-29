#!/usr/bin/env python3
import os, sys
import google.cloud.texttospeech as tts
from threading import Thread
from playsound import playsound
from pedalboard import Pedalboard, PitchShift, Reverb
from pedalboard.io import AudioFile

VOICE = "fr-FR-Wavenet-D"

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
'''

API_KEY_PATH = "../model/gtts_api_key.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = API_KEY_PATH

# Make a Pedalboard object, containing multiple plugins:
board = Pedalboard([PitchShift(semitones=+3), Reverb(room_size=0.02,damping=0.1,wet_level=0.3,dry_level=0.8,width=0.9,freeze_mode=0)])


def list_voices():
    client = tts.TextToSpeechClient()
    voices = client.list_voices()

    for voice in voices.voices:
        if"fr-FR" in voice.language_codes:
            print(f"{voice.name}")

class TextToSpeech(Thread):
    def __init__(self, text):
        Thread.__init__(self)
        #print("TTS", text)
        self.language_code = "-".join(VOICE.split("-")[:2])
        self.text_input = tts.SynthesisInput(text=text)
        self.voice_params = tts.VoiceSelectionParams(
            language_code=self.language_code, name=VOICE
        )
        self.audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.LINEAR16)
        self.client = tts.TextToSpeechClient()

    def run(self):
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

        playsound('processed-output.wav')

        # playsound(filename)

class TextToSpeechNoThread():
    def __init__(self):
        self.language_code = "-".join(VOICE.split("-")[:2])
        self.voice_params = tts.VoiceSelectionParams(
            language_code=self.language_code, name=VOICE
        )
        self.audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.LINEAR16)
        self.client = tts.TextToSpeechClient()

    def synthesize(self, text):
        self.text_input = tts.SynthesisInput(text=text)
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

        playsound('processed-output.wav')

        # playsound(filename)

if __name__ == '__main__':
    # list_voices()
    if len(sys.argv) == 2:
        thd = TextToSpeech(sys.argv[1]);
        thd.start();
    else:
        print('usage: %s <text-to-synthesize>')
