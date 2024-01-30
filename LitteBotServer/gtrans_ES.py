#!/usr/bin/env python3
import sys
from googletrans import Translator
from gtts_synthES import TextToSpeech

import functools
print = functools.partial(print, end='\n',flush=True)

translator = Translator()

def translateES(txt):
    try:
        return translator.translate(txt, src='fr', dest='es').text
    except:
        try:
            return translator.translate(txt, src='fr', dest='es').text
        except:
            print("[translate] An exception occurred")
            return txt
    
    

def translateFR(txt):
    try:
        return translator.translate(txt, src='es', dest='fr').text
    except:
        try:
            return translator.translate(txt, src='es', dest='fr').text
        except:
            print("[translate] An exception occurred")
            return txt
    
def translate(txt, src, dst):
    try:
        return translator.translate(txt, src=src, dest=dst).text
    except:
        try:
            return translator.translate(txt, src=src, dest=dst).text
        except:
            print("[translate] An exception occurred")
            return txt

if __name__ == '__main__':
    if len(sys.argv) == 3:
        res = translateES(sys.argv[1])
        print(res)
        thd = TextToSpeech(res, voice=int(sys.argv[2]))
        thd.start()
    elif len(sys.argv) == 4:
        print(translate(sys.argv[1], sys.argv[2], sys.argv[3]))
    else:
        print('usage: %s <txt_to_translate_to_spanish> <voice_number>')
        print('usage: %s <txt_to_translate> <source_language> <destination_language>')

    
