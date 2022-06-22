import sys, os, time, json, random, datetime
#from gtts_synth import TextToSpeechNoThread
from gtts_synth import TextToSpeech

TextToSpeech("Dom Juan").start()

time.sleep(3)

txt = "je vous en prie, ré-interpretez-moi s'il vous plaît, ne me laissez pas me pétrifier dans ma caricature"
print(txt)
TextToSpeech(txt, pitch=-10, speed=0.5, voice=0).start()
TextToSpeech(txt, pitch=-10, speed=0.5, voice=4).start()

'''
dialog_path = "../data/"
def_questions_common = "dom_juan_common"
def_questions_seduction = "dom_juan_seduction"
def_questions_provocation = "dom_juan_provocation"
def_questions_fuite = "dom_juan_fuite"
def_questions_epilogue = "dom_juan_epilogue"

sentences = []

print("Loading ", dialog_path+def_questions_common+".json")
with open(dialog_path+def_questions_common+".json") as dj_common:
    tmp = json.load(dj_common)
    for i in tmp:
        for qq in tmp[i]['q']:
            qql = qq.lower()
            # print(qq)
            if qq.__contains__("__") or qq.__contains__('#') or tmp[i]['a'].__contains__("__REPEAT__") or tmp[i]['a'].__contains__("__TO_EPILOGUE__"):
                pass
            else:
                for s in tmp[i]['a']:
                    if s.__contains__("FUITE"):
                        pass
                    else:
                        sentences.append(s.replace("__START__", "").replace("__NAME__", "").replace("?", "").replace("!", "").replace(".", ""))

print("Loading ", dialog_path+def_questions_seduction+".json")
with open(dialog_path+def_questions_seduction+".json") as dj:
    tmp = json.load(dj)
    for i in tmp:
        for qq in tmp[i]['q']:
            if qq.__contains__("__") or qq.__contains__('#') or tmp[i]['a'].__contains__("__REPEAT__") or tmp[i]['a'].__contains__("__TO_EPILOGUE__"):
                pass
            else:
                for s in tmp[i]['a']:
                    if s.__contains__("FUITE"):
                        pass
                    else:
                        sentences.append(s.replace("__START__", "").replace("__NAME__", "").replace("?", "").replace("!", "").replace(".", ""))

print("Loading ", dialog_path+def_questions_provocation+".json")
with open(dialog_path+def_questions_provocation+".json") as dj:
    tmp = json.load(dj)
    dom_juan_provocation = {}
    for i in tmp:
        for qq in tmp[i]['q']:
            if qq.__contains__("__") or qq.__contains__('#') or tmp[i]['a'].__contains__("__REPEAT__") or tmp[i]['a'].__contains__("__TO_EPILOGUE__"):
                pass
            else:
                for s in tmp[i]['a']:
                    if s.__contains__("FUITE"):
                        pass
                    else:
                        sentences.append(s.replace("__START__", "").replace("__NAME__", "").replace("?", "").replace("!", "").replace(".", ""))

print("Loading ", dialog_path+def_questions_fuite+".json")
with open(dialog_path+def_questions_fuite+".json") as dj:
    tmp = json.load(dj)
    dom_juan_fuite = {}
    for i in tmp:
        for qq in tmp[i]['q']:
            if qq.__contains__("__") or qq.__contains__('#') or tmp[i]['a'].__contains__("__REPEAT__") or tmp[i]['a'].__contains__("__TO_EPILOGUE__"):
                pass
            else:
                for s in tmp[i]['a']:
                    if s.__contains__("FUITE"):
                        pass
                    else:
                        sentences.append(s.replace("__START__", "").replace("__NAME__", "").replace("?", "").replace("!", "").replace(".", ""))

while("" in sentences) :
    sentences.remove("")

# print(sentences)

tts = TextToSpeechNoThread()

cc = 0

while cc < 1:
    f = "voices/"+datetime.datetime.now().strftime("%d%m%y_%H%M%S")
    count = 0
    str = ''
    while count < 50 :
        ii = random.randrange(len(sentences))
        # print(ii, sentences[ii])
        # w = sentences[ii].split()
        # wr = random.sample(w, len(w))
        #
        # idx = random.randrange(len(wr))
        # idx2 = random.randrange(idx, len(wr))

        # wrl = ' '.join(wr[idx:idx2])
        # p = random.randrange(10) - 5
        # s = (random.randrange(100) - 50) / 100. + 1
        # if(wrl != "" and wrl != " "):
            # print("_"+wrl+"_")#, p, s)
        str += sentences[ii] + ", "#wrl + " "
        count += 1
        # tts.synthesize(wrl, pitch=float(p), speed=s)

    p = float(random.randrange(70) - 130) / 10.
    s = (random.randrange(20) - 10) / 100. + 0.7
    print(str, p, s)
    tts.synthesize(str, pitch=p, speed=s, fname=f, play=False)

    cc += 1
'''
