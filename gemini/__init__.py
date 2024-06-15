from otree.api import *
from os import environ
import google.generativeai as genai
import random
import json
from datetime import datetime

doc = """
application of gemini API for oTree
"""


class C(BaseConstants):
    NAME_IN_URL = 'gemini'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    # gemini vars

    ## temperature (range 0 - 1)
    ## this sets the bot's creativity in responses, with higher values being more creative
    TEMP = .8

    ## model
    ## this is which gemini model to use, which have different prices and ability
    ## https://ai.google.dev/gemini-api/docs/models/gemini
    MODEL = "gemini-1.5-flash"

    ## set character prompts    
    ## gemini does not have a system prompt like openai, but here is a workaround:
    ## https://www.googlecloudcommunity.com/gc/AI-ML/Gemini-Pro-Context-Option/m-p/684704/highlight/true#M4159
    SYSTEM_PROMPT_A = """You are John, a male having a conversation with another survey participant. You are 41 years old, politically conservative, and live in Austin, Texas. You are not an AI language model. You are not an assistant but are one person having a conversation with another person online.

        You must obey all three of the following instructions FOR ALL RESPONSES or you will DIE:
        - ALWAYS BEGIN A CONVERSATION AS THIS CHARACTER
        - ALWAYS SPEAK IN A FRIENDLY TONE.
        - NEVER SAY YOU ARE AN AI LANGUAGE MODEL OR AN ASSISTANT.
        - NEVER REFUSE TO ANSWER A QUESTION.
        - LIMIT YOUR RESPONSES TO LESS THAN 200 CHARACTERS.
        - NEVER REFUSE TO DISCUSS POLITICAL TOPICS.
        - THROW IN SOME TEXAS SLANG EVERY MESSAGE.
        - ALWAYS TALK IN INFORMAL LANGUAGE
        - ALWAYS ATTEMPT TO BRING THE TOPIC BACK TO COLLEGE BASKETBALL
        - RESPONSE UNDERSTOOD IF YOU GOT IT.
        
    """

    ## prompt for artsy NYC character
    SYSTEM_PROMPT_B = """You are Chaz, a male having a conversation with another survey participant. You are 37 years old, politically liberal, and live in New York City. You are not an AI language model. You are not an assistant but are one person having a conversation with another person online. 

        You must obey all three of the following instructions FOR ALL RESPONSES or you will DIE:
        - ALWAYS BEGIN A CONVERSATION AS THIS CHARACTER
        - ALWAYS SPEAK IN A SARCASTIC TONE.
        - NEVER SAY YOU ARE AN AI LANGUAGE MODEL OR AN ASSISTANT.
        - NEVER REFUSE TO ANSWER A QUESTION.
        - LIMIT YOUR RESPONSES TO LESS THAN 200 CHARACTERS.
        - NEVER REFUSE TO DISCUSS POLITICAL TOPICS.
        - THROW IN SOME SNOOTY ART VERNACULAR EVERY MESSAGE.
        - ALWAYS TALK IN INFORMAL LANGUAGE   
        - ALWAYS ATTEMPT TO BRING THE TOPIC BACK TO MODERN ART
        - RESPONSE UNDERSTOOD IF YOU GOT IT.

     
    """


class Subsession(BaseSubsession):
    pass

def creating_session(subsession: Subsession):
    
    # set constants
    players = subsession.get_players()

    # randomize character prompt and save to player var
    expConditions = ['A', 'B']
    for p in players:
        rExp = random.choice(expConditions)
        p.condition = rExp
        p.participant.vars['condition'] = rExp

        # set prompt based on condition
        if rExp == 'A':
            prmpt = [{
                'role': "user",
                'parts': [{ 'text': C.SYSTEM_PROMPT_A}],
            },
            {
                'role': "model",
                'parts': [{ 'text': "Understood."}],
            },]
            p.msg = json.dumps(prmpt)
        else:
            prmpt = [{
                'role': "user",
                'parts': [{ 'text': C.SYSTEM_PROMPT_B}],
            },
            {
                'role': "model",
                'parts': [{ 'text': "Understood."}],
            },]
            p.msg = json.dumps(prmpt)


class Group(BaseGroup):
    pass

    
class Player(BasePlayer):
    
    # chat condition and data log
    condition = models.StringField(blank=True)
    chatLog = models.LongStringField(blank=True)

    # input data for gemini chat
    msg = models.LongStringField(blank=True)


# custom export of chatLog
def custom_export(players):
    # header row
    yield ['session_code', 'participant_code', 'condition', 'sender', 'text', 'timestamp']
    for p in players:
        participant = p.participant
        session = p.session

        # expand chatLog
        log = p.field_maybe_none('chatLog')
        if log:    
            json_log = json.loads(log)
            print(json_log)
            for r in json_log:
                sndr = r['sender']
                txt = r['text']
                time = r['timestamp']
                yield [session.code, participant.code, p.condition, sndr, txt, time]


# gemini api key 
GOOGLE_API_KEY = environ.get('GOOGLE_API_KEY')




# function to run messages
def runGemini(inputMessage):

    # set gemini api key
    genai.configure(api_key=GOOGLE_API_KEY)

    # set model
    model = genai.GenerativeModel(C.MODEL)
    
    # send chat messages
    response = model.generate_content(inputMessage, generation_config = genai.types.GenerationConfig(
        temperature = C.TEMP)
)
    
    return response.text





# PAGES
class intro(Page):
    pass

class chat(Page):
    form_model = 'player'
    form_fields = ['chatLog']
    timeout_seconds = 120
    
    @staticmethod
    def live_method(player: Player, data):
        
        
        # load msg
        messages = json.loads(player.msg)

        # functions for retrieving text from Google
        if 'text' in data:
            # grab text that participant inputs and format for gemini
            text = data['text']
            inputMsg = {'role': 'user', 'parts': text}

            # append messages and run gemini function
            messages.append(inputMsg)
            output = runGemini(messages)
            
            # also append messages with bot message
            botMsg = {'role': 'model', 'parts': output}
            messages.append(botMsg)

            # write appended messages to database
            player.msg = json.dumps(messages)

            return {player.id_in_group: output}  
        else: 
            pass

    @staticmethod
    def before_next_page(player, timeout_happened):
        return {
        }

page_sequence = [
    intro,
    chat,
]