#!/usr/bin/env python3
import json, pickle, random, logging, os, signal
from typing import Union
from pyosc import Client, Server
from botLog import BotLog
from sys import platform as _platform

import gradio as gr
import numpy as np

# os.environ["CUDA_VISIBLE_DEVICES"]="1"
if _platform == "win32" or _platform == "win64":
    os.add_dll_directory("C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v11.6/bin")
    os.add_dll_directory("C:/tools/cuda/bin")

import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text
import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer

dialog_path = "../data/"
def_questions_common = "dom_juan_common"
def_questions_seduction = "dom_juan_seduction"
def_questions_provocation = "dom_juan_provocation"
def_questions_fuite = "dom_juan_fuite"
def_questions_epilogue = "dom_juan_epilogue"

def_tokenizer = "../model/emil2000/dialogpt-for-french-language"
def_model = "../model/Chatbot-Moliere-V4"
def_module = "../model/universal-sentence-encoder-multilingual-large_3"

OFF = 0
INTRO = 1
SEDUCTION = 2
PROVOCATION = 3
FUITE = 4

COLOR_INTRO = 32
COLOR_SEDUCTION = 33
COLOR_PROVOCATION = 35
COLOR_FUITE = 36
COLOR_OFF = 37

color = [COLOR_OFF, COLOR_INTRO, COLOR_SEDUCTION, COLOR_PROVOCATION, COLOR_FUITE, COLOR_OFF ]

# section = ["Off", "Introduction", "Séduction", "Provocation", "Fuite", "Epilogue"]

MAX_HISTORY_SIZE = 5

def print_formatColor_table():
    """
    prints table of formatColorted text formatColor options
    """
    for style in range(8):
        for fg in range(30,38):
            s1 = ''
            for bg in range(40,48):
                formatColor = ';'.join([str(style), str(fg), str(bg)])
                s1 += '\x1b[%sm %s \x1b[0m' % (formatColor, formatColor.replace(";",","))
            print(s1)
        print('\n')

def formatColor(style, fg, bg, s):
    f = ';'.join([str(style), str(fg), str(bg)])
    return '\x1b[%sm%s\x1b[0m' % (f, s)

class LitteBot:
    def __init__(self):
        tf.compat.v1.logging.set_verbosity(40) # ERROR

        self.botmode = 1
        self.botresponses = []
        self.filter = []
        self.currentStart = []
        self.start = []
        self.currentFirst = []
        self.first = []
        self.currentSecond = []
        self.second = []
        self.currentThird = []
        self.third = []
        self.currentQuit = []
        self.quit = []
        self.epilogue = []
        self.curEpilogue = 0
        self.history = [[], []]
        self.lastresponse = ""
        self.username = ""

        self.log = BotLog()

        print()
        print(formatColor(6,37,40,"Starting Chatbot"))

        """Initializes the bot."""
        print("Loading module "+def_module)
        self.module_url = ( def_module )
        self.model_embeddings = hub.load(self.module_url)
        self.model_url = def_model
        self.tokenizer_url = def_tokenizer

        self.loadQuestionsAndEmbeddings()
        self.model, self.tokenizer = self.load_model()

        self.css = """ .footer {display:none !important} """

        self.osc_server = Server('127.0.0.1', 14001, self.oscIn)
        self.osc_client = Client('127.0.0.1', 14000)

        print(formatColor(0,37,40,"Chatbot ready"))
        print()

    def kill(self):
        self.osc_server.stop()
        os._exit(0)

    def loadQuestionsAndEmbeddings(self):
        print("Loading questions")# "+def_questions)
        self.dom_juan = self.load_questions_from_json()
        self.dom_juan_questions = self.load_questions_keys()
        print("Building embeddings")
        self.dom_juan_questions_embeddings = self.build_embeddings()

    def oscIn(self, address, *args):
        # print("OSC IN ", address, args[0])
        if(address == '/getresponse'):
            self.getResponse(args[0])
        elif(address == '/setbotmode'):
            self.setBotMode(args[0])
        elif(address == '/newConversation'):
            self.newConversation()
        elif(address == '/relance'):
            self.relance()
        elif(address == '/first'):
            self.speakFirst()
        elif(address == '/second'):
            self.speakSecond(args[0])
        elif(address == '/third'):
            self.speakThird(args[0])
        elif(address == '/nextEpilogue'):
            self.nextEpilogue()
        elif(address == '/reload'):
            self.loadQuestionsAndEmbeddings()
        elif(address == '/logbot'):
            print(formatColor(0,color[self.botmode],40, "bot: "+args[0]))
            self.log.logBot(str(self.botmode), args[0])
        elif(address == '/logme'):
            print("user: "+args[0])
            self.log.logMe(args[0])
        else:
            print("OSC IN : "+str(address))
            for x in range(0,len(args)):
                print("     " + str(args[x]))

    def setBotMode(self, mode):
        self.botmode = mode
        if self.botmode != 1:
            self.currentStart = self.start[self.botmode].copy()
        if self.botmode == 0:
            print(" - "+formatColor(1,color[OFF],40,"Bot Mode Passe-partout"))
        elif self.botmode == 1:
            print(" - "+formatColor(1,color[INTRO],40,"Bot Mode Introduction"))
        elif self.botmode == 2:
            print(" - "+formatColor(1,color[SEDUCTION],40,"Bot Mode Seduction"))
        elif self.botmode == 3:
            print(" - "+formatColor(1,color[PROVOCATION],40,"Bot Mode Provocation"))
        elif self.botmode == 4:
            print(" - "+formatColor(1,color[FUITE],40,"Bot Mode Fuite"))

    def nextEpilogue(self):
        if(self.curEpilogue < len(self.epilogue)):
            # print("NEXT EPILOGUE", self.epilogue)
            self.lastresponse = self.postProcess(self.epilogue[self.curEpilogue].strip())
            print(formatColor(0,color[self.botmode],40, "bot: "+self.lastresponse))
            self.botresponses.append(self.lastresponse)
            self.log.logBot(str(self.botmode), self.lastresponse)
            self.osc_client.send('/curEpilogue',self.lastresponse)
            self.curEpilogue += 1
        else:
            self.osc_client.send('/endEpilogue',1)

    def getResponse(self, q):
        self.log.logMe(q)
        print("user: "+q)
        response = self.predict(q, self.history)
        # i = 0
        # while self.lastresponse in self.botresponses and i < 10:
        #     self.predict(q, self.history)
        #     # print("\t"+formatColor(0,color[self.botmode],40,"(repetitive response, new : "+ response+")"))
        #     i = i + 1
        print(formatColor(0,color[self.botmode],40, "bot: "+self.lastresponse))
        self.botresponses.append(self.lastresponse)
        self.log.logBot(str(self.botmode), self.lastresponse)
        self.osc_client.send('/lastresponse',self.lastresponse)
        return self.lastresponse

    def getAllResponses(self):
        return self.botresponses

    def newConversation(self):
        self.username = ""
        self.setBotMode(1)
        self.currentStart = self.start[self.botmode].copy()
        self.curEpilogue = 0
        self.history = [[], []]
        self.log.start()
        self.botresponses.clear()

    def relance(self):
        # print("BRAIN RELANCE")
        if(len(self.currentStart) == 0):
            self.currentStart = self.start[self.botmode].copy()
        idx = random.randrange(len(self.currentStart))
        self.lastresponse = self.currentStart.pop(idx).strip()
        print(formatColor(0,color[self.botmode],40, "bot: "+self.lastresponse))
        self.botresponses.append(self.lastresponse)
        self.log.logBot(str(self.botmode), self.lastresponse)
        self.osc_client.send('/lastresponse',self.lastresponse)

    def speakFirst(self):
        # print("BRAIN FIRST")
        if(len(self.currentFirst) == 0):
            self.currentFirst = self.first.copy()
        idx = random.randrange(len(self.currentFirst))
        self.lastresponse = self.currentFirst.pop(idx).strip()
        print(formatColor(0,color[self.botmode],40, "bot: "+self.lastresponse))
        self.botresponses.append(self.lastresponse)
        self.log.logBot(str(self.botmode), self.lastresponse)
        self.osc_client.send('/lastresponse',self.lastresponse)

    def speakSecond(self, mess):
        if(mess.__contains__("moi c'est ")):
            self.username = mess.split("moi c'est ")[-1]
        elif(mess.__contains__("suis là")):
            pass
        elif(mess.__contains__("c'est moi ")):
            self.username = mess.split("c'est moi ")[-1]
        elif(mess.__contains__("moi")):
            pass
        elif(mess.__contains__("appelle")):
            self.username = mess.split("appelle ")[-1]
        elif(mess.__contains__("suis")):
            self.username = mess.split("suis ")[-1]
        elif(mess.__contains__("nomme")):
            self.username = mess.split("nomme ")[-1]
        elif(mess.__contains__("est")):
            self.username = mess.split("est ")[-1]

        # print("BRAIN SECOND", ">"+self.username+"<")

        if(self.username == ""):
            # print("NO USERNAME")
            if(len(self.currentSecond) == 0):
                self.currentSecond = self.second.copy()
            idx = random.randrange(len(self.currentSecond))
            self.lastresponse = self.currentSecond.pop(idx).strip()
            print(formatColor(0,color[self.botmode],40, "bot: "+self.lastresponse))
            self.botresponses.append(self.lastresponse)
            self.log.logBot(str(self.botmode), self.lastresponse)
            self.osc_client.send('/lastresponse',self.lastresponse)
        else:
            self.osc_client.send('/username',self.username)
            if(len(self.currentThird) == 0):
                self.currentThird = self.third.copy()
            idx = random.randrange(len(self.currentThird))
            self.lastresponse = self.currentThird.pop(idx).strip()
            self.lastresponse = self.postProcess(self.lastresponse)
            print(formatColor(0,color[self.botmode],40, "bot: "+self.lastresponse))
            self.botresponses.append(self.lastresponse)
            self.log.logBot(str(self.botmode), self.lastresponse)
            self.osc_client.send('/lastresponse',self.lastresponse)

    def speakThird(self, mess):
        if(mess.__contains__("moi c'est ")):
            self.username = mess.split("moi c'est ")[-1]
        if(mess.__contains__("c'est moi ")):
            self.username = mess.split("c'est moi ")[-1]
        elif(mess.__contains__("appelle")):
            self.username = mess.split("appelle ")[-1]
        elif(mess.__contains__("suis")):
            self.username = mess.split("suis ")[-1]
        elif(mess.__contains__("nomme")):
            self.username = mess.split("nomme ")[-1]
        elif(mess.__contains__("est")):
            self.username = mess.split("est ")[-1]
        else:
            self.username = mess.split(" ")[-1]

        # print("BRAIN THIRD", self.username)

        self.osc_client.send('/username',self.username)

        if(len(self.currentThird) == 0):
            self.currentThird = self.third.copy()
        idx = random.randrange(len(self.currentThird))
        self.lastresponse = self.currentThird.pop(idx).strip()
        self.lastresponse = self.postProcess(self.lastresponse)
        print(formatColor(0,color[self.botmode],40, "bot: "+self.lastresponse))
        self.botresponses.append(self.lastresponse)
        self.log.logBot(str(self.botmode), self.lastresponse)
        self.osc_client.send('/lastresponse',self.lastresponse)

    def postProcess(self, msg):
        if(msg == " « " or msg == " » " or msg == " Ah " or msg == "Oh!  " or msg == " Eh " or msg == " Eh bien " or msg == " Oh! " or msg == "Ah! " or msg == "Ah, ah, ah!"):
            msg = "__START__"
        if(msg.__contains__("__NAME__")):
            if(self.username != ""):
                msg = msg.replace("__NAME__", self.username)
            else:
                msg = msg.replace("__NAME__", "")
        if(msg.__contains__("__START__")):
            if(len(self.currentStart) == 0):
                self.currentStart = self.start[self.botmode].copy()
            idx = random.randrange(len(self.currentStart))
            start = self.currentStart.pop(idx).strip()
            msg = msg.replace("__START__", start)
        if(msg.__contains__("%u0153")):
            msg = msg.replace("%u0153", "oe")
        if(msg.__contains__("_") and not msg.__contains__("__TO_EPILOGUE__")):
            msg = msg.replace("_", " ")
        if(self.username != ""):
            if(msg.__contains__("Monsignor")):
                msg = msg.replace("Monsignor", self.username)
            elif(msg.__contains__("mon cher Monsieur")):
                msg = msg.replace("mon cher Monsieur", "cher "+self.username)
            elif(msg.__contains__("mon cher monsieur")):
                msg = msg.replace("mon cher monsieur", "cher "+self.username)
            elif(msg.__contains__("Monsieur le chevalier")):
                msg = msg.replace("Monsieur le chevalier", self.username)
            elif(msg.__contains__("Monsieur")):
                msg = msg.replace("Monsieur", self.username)
            elif(msg.__contains__("monsieur")):
                msg = msg.replace("monsieur", self.username)
            elif(msg.__contains__("Monsieu")):
                msg = msg.replace("Monsieu", self.username)
            elif(msg.__contains__("monsieu")):
                msg = msg.replace("monsieu", self.username)
            elif(msg.__contains__("Monsir")):
                msg = msg.replace("Monsir", self.username)
            elif(msg.__contains__("Madame")):
                msg = msg.replace("Madame", self.username)
            elif(msg.__contains__("madame")):
                msg = msg.replace("madame", self.username)

        return msg

    def embed(self, input: Union[str, list, dict]) -> tf.Tensor:
        """Embed a string or list or dictionary of strings.

        Args:
            input (Union[str, list, dict]): input string

        Returns:
            tf.python.framework.ops.EagerTensor: Embedding of the input string
        """
        return self.model_embeddings(input)

    def load_model(
        self,
    ) -> Union[
        transformers.models.gpt2.modeling_gpt2.GPT2LMHeadModel,
        transformers.models.gpt2.tokenization_gpt2_fast.GPT2TokenizerFast,
    ]:
        """Loads the model and tokenizer.

        Returns:
            Union[transformers.models.gpt2.modeling_gpt2.GPT2LMHeadModel,transformers.models.gpt2.tokenization_gpt2_fast.GPT2TokenizerFast]: Model and tokenizer
        """
        print("Loading model "+self.model_url)
        model = AutoModelForCausalLM.from_pretrained(self.model_url)
        print("Loading tokenizer "+self.tokenizer_url)
        tokenizer = AutoTokenizer.from_pretrained(self.tokenizer_url)
        return model, tokenizer

    def load_questions_from_json(self) -> dict:
        """Loads the questions from a json file.

        Returns:
            dict: Dictionary of questions
        """
        self.filter = []
        self.start = []
        self.quit = []
        self.first = []
        self.second = []
        self.third = []
        self.epilogue = []
        dom_juan = []
        print("Loading ", dialog_path+def_questions_common+".json")
        with open(dialog_path+def_questions_common+".json") as dj_common:
            tmp = json.load(dj_common)
            dom_juan_common = {}
            start_common = []
            filter_common = {}
            for i in tmp:
                for qq in tmp[i]['q']:
                    # print(qq, tmp[i]['a'])
                    qql = qq.lower()
                    if qq.__contains__("__START__"):
                        start_common = tmp[i]['a']
                    elif qq.__contains__("__QUIT__"):
                        self.quit = tmp[i]['a']
                    elif qq.__contains__("__FIRST__"):
                        self.first = tmp[i]['a']
                    elif qq.__contains__("__SECOND__"):
                        self.second = tmp[i]['a']
                    elif qq.__contains__("__THIRD__"):
                        self.third = tmp[i]['a']
                    elif qql.__contains__('#'):
                        #print("WILDCARD", qq, tmp[i]['a'])
                        filter_common[qql] = tmp[i]['a']
                    else:
                        dom_juan_common[qql] = tmp[i]['a']
            print("Loading ", dialog_path+def_questions_seduction+".json")
            with open(dialog_path+def_questions_seduction+".json") as dj:
                tmp = json.load(dj)
                tmp_seduction = {}
                start_seduction = []
                tmp_filter = {}
                for i in tmp:
                    for qq in tmp[i]['q']:
                        # print(qq, tmp[i]['a'])
                        qql = qq.lower()
                        if qq.__contains__("__START__"):
                            start_seduction = tmp[i]['a']
                        elif qql.__contains__('#'):
                            #print("WILDCARD", qq, tmp[i]['a'])
                            tmp_filter[qql] = tmp[i]['a']
                        else:
                            tmp_seduction[qql] = tmp[i]['a']
                dom_juan_seduction = {**dom_juan_common, **tmp_seduction}
                filter_seduction = {**filter_common, **tmp_filter}
            print("Loading ", dialog_path+def_questions_provocation+".json")
            with open(dialog_path+def_questions_provocation+".json") as dj:
                tmp = json.load(dj)
                tmp_provocation = {}
                tmp_filter = {}
                start_provocation = []
                for i in tmp:
                    for qq in tmp[i]['q']:
                        # print(qq, tmp[i]['a'])
                        qql = qq.lower()
                        if qq.__contains__("__START__"):
                            start_provocation = tmp[i]['a']
                        elif qql.__contains__('#'):
                            #print("WILDCARD", qq, tmp[i]['a'])
                            tmp_filter[qql] = tmp[i]['a']
                        else:
                            tmp_provocation[qql] = tmp[i]['a']
                dom_juan_provocation = {**tmp_provocation, **dom_juan_common}
                filter_provocation = {**tmp_filter, **filter_common}
            print("Loading ", dialog_path+def_questions_fuite+".json")
            with open(dialog_path+def_questions_fuite+".json") as dj:
                tmp = json.load(dj)
                tmp_fuite = {}
                tmp_filter = {}
                start_fuite = []
                for i in tmp:
                    for qq in tmp[i]['q']:
                        # print(qq, tmp[i]['a'])
                        qql = qq.lower()
                        if qq.__contains__("__START__"):
                            start_fuite = tmp[i]['a']
                        elif qql.__contains__('#'):
                            #print("WILDCARD", qq, tmp[i]['a'])
                            tmp_filter[qql] = tmp[i]['a']
                        else:
                            tmp_fuite[qql] = tmp[i]['a']
                dom_juan_fuite = {**tmp_fuite, **dom_juan_common}
                filter_fuite = {**tmp_filter, **filter_common}
        dom_juan.append(dom_juan_common)
        dom_juan.append(dom_juan_common)
        dom_juan.append(dom_juan_seduction)
        dom_juan.append(dom_juan_provocation)
        dom_juan.append(dom_juan_fuite)
        dom_juan.append(dom_juan_common)

        self.filter.append(filter_common)
        self.filter.append(filter_common)
        self.filter.append(filter_seduction)
        self.filter.append(filter_provocation)
        self.filter.append(filter_fuite)
        self.filter.append(filter_common)

        self.start.append(start_common)
        self.start.append(start_common)
        self.start.append(start_seduction)
        self.start.append(start_provocation)
        self.start.append(start_fuite)
        self.start.append(start_common)

        self.currentStart = self.start[self.botmode].copy()
        self.currentQuit = self.quit.copy()
        self.currentFirst = self.first.copy()
        self.currentSecond = self.second.copy()
        self.currentThird = self.third.copy()

        print("Loading ", dialog_path+def_questions_epilogue+".json")
        with open(dialog_path+def_questions_epilogue+".json") as dj:
            tmp = json.load(dj)
            for i in tmp:
                for qq in tmp[i]['q']:
                    if qq.__contains__("__EPILOGUE__"):
                        #print("__EPILOGUE__", qq, tmp[i]['a'])
                        self.epilogue = tmp[i]['a']

        # print("EPILOGUE", len(self.epilogue), self.epilogue)
        # print("START", len(self.start), self.start)
        # print("FIRST", len(self.first), self.first)
        # print("SECOND", len(self.second), self.second)
        # print("THIRD", len(self.third), self.third)

        return dom_juan

    def load_questions_keys(self):
        dom_juan_questions = []
        dom_juan_questions.append(list(self.dom_juan[0].keys()))
        dom_juan_questions.append(list(self.dom_juan[1].keys()))
        dom_juan_questions.append(list(self.dom_juan[2].keys()))
        dom_juan_questions.append(list(self.dom_juan[3].keys()))
        dom_juan_questions.append(list(self.dom_juan[4].keys()))
        dom_juan_questions.append(list(self.dom_juan[5].keys()))
        return dom_juan_questions

    def build_embeddings(self):
        embeddings = []
        embeddings.append(self.embed(self.dom_juan_questions[0]))
        embeddings.append(self.embed(self.dom_juan_questions[1]))
        embeddings.append(self.embed(self.dom_juan_questions[2]))
        embeddings.append(self.embed(self.dom_juan_questions[3]))
        embeddings.append(self.embed(self.dom_juan_questions[4]))
        embeddings.append(self.embed(self.dom_juan_questions[5]))
        return embeddings

    def predict(self, user_input: str, history: list) -> list:
        """Predict the next message.

        Args:
            user_input (str): User input
            history (list): History of the conversation

        Returns:
            list: Answer and history of the conversation
        """
        history = history or [[], []]

        mode_filter = self.filter[self.botmode]
        mode_response = self.dom_juan[self.botmode]
        mode_questions = self.dom_juan_questions[self.botmode]
        mode_embeddings = self.dom_juan_questions_embeddings[self.botmode]
        # mode_start = self.start[self.botmode]

        new_question = user_input.lower()
        new_question_embedding = self.embed(new_question)

        self.prevResponse = self.lastresponse

        found = False
        for filt in mode_filter.keys():
            f = filt.replace("#","")
            if new_question.__contains__(f):
                #print("FILTER OK", filt, mode_filter[filt])
                res = mode_filter[filt]
                tmp = ""
                if type(res) == list:
                    tmp_response = random.choice(res)
                else:
                    tmp_response = res
                found = True

        if not found:
            all_questions_embedding = np.concatenate(
                (new_question_embedding, mode_embeddings), axis=0
            )
            corr = np.inner(all_questions_embedding, all_questions_embedding)[0][1:]
            max_score = max(corr)

            if max_score >= 0.6:
                index = np.where(corr == max_score)[0][0]
                res = mode_response[mode_questions[index]]
                if type(res) == list:
                    tmp_response = random.choice(res)
                else:
                    tmp_response = res
            else:
                response, history[1] = self.predict_nlp(new_question, history[1])
                tmp_response = list(response[-1])[-1]

        tmp_response = self.postProcess(tmp_response)
        if tmp_response.__contains__("__TO_EPILOGUE__"):
            self.lastresponse = tmp_response
        elif tmp_response.__contains__("__REPEAT__"):
            self.lastresponse = self.prevResponse
        else:
            self.lastresponse = tmp_response

        history[0].append(tuple([user_input,self.lastresponse]))

        # print ("history[0]", len(history[0]), history[0])
        if(len(history[0]) > MAX_HISTORY_SIZE):
            history[0].pop(0)
            # print (">> pop", len(history[0]), history[0])

        self.history = history
        # print("RESPONSE", self.lastresponse)


        return history[0], history

    def predict_nlp(self, user_input: str, history: list = None) -> list:
        """Predict the next message using NLP.

        Args:
            user_input (str): User input
            history (list, optional): History of the conversation. Defaults to None.

        Returns:
            list: Answer and history of the conversation
        """
        print(formatColor(0,color[self.botmode],40, "...(bot think)..."))
        if history is None:
            history = []
        new_user_input_ids = self.tokenizer.encode(
            user_input + self.tokenizer.eos_token, return_tensors="pt"
        )

        bot_input_ids = torch.cat(
            [torch.LongTensor(history), new_user_input_ids], dim=-1
        )

        history = self.model.generate(
            bot_input_ids,
            max_length=4096,
            pad_token_id=self.tokenizer.eos_token_id,
            no_repeat_ngram_size=3,
            do_sample=False,
            top_k=10,
            top_p=1,
            temperature=0,
        )

        response = self.tokenizer.decode(history[0]).split("<|endoftext|>")
        if "" in response:
            response.remove("")
        res=[]
        for i, msg in enumerate(response):
            if i%2==0:
                res.append((response[i],response[i+1]))
            else:
                continue

        return res, history

    def gradio_interface(self) -> gr.interface.Interface:
        """Returns the gradio interface.

        Returns:
            gr.interface.Interface: Interface
        """
        return gr.Interface(
            fn=self.predict,
            theme="default",
            inputs=[
                gr.inputs.Textbox(
                    placeholder="Bonjour !", label="Parlez avec Dom Juan:"
                ),
                "state",
            ],
            outputs=["chatbot", "state"],
            title="LITTE_BOT",
            allow_flagging="never",
            css=self.css,
        )

def handler(signum, frame):
    litte_bot.kill()

signal.signal(signal.SIGINT, handler)

if __name__ == "__main__":
    litte_bot = LitteBot()
    # gr.close_all()
    # interface = litte_bot.gradio_interface()
    # interface.launch(server_name="0.0.0.0", server_port=7892)
