import os
from dotenv import load_dotenv
from gemini_assistant.assistant_proxy_gemini import AssistantProxyGemini
from gpt_assistant.assistant_proxy_gpt import AssistantProxyGpt
from mediators.mediator_state_machine import MediatorStateMachine
from mediators.mediator_basic import MediatorBasic
from user_proxy.user_proxy import UserProxy

load_dotenv()

def start_conversation(type="gpt", **cfg):
    mediator = get_default_mediator()
    user_proxy = UserProxy(mediator)
    asst_proxy = get_assistant_proxy(type, mediator, **cfg)
    mediator.set_proxies(asst_proxy, user_proxy)
    return user_proxy

def get_default_mediator():
    type = os.environ["MEDIATOR_TYPE"]
    if type:
        return get_mediator(type)
    return MediatorBasic()

def get_mediator(type):
    match type:
        case "basic" : mediator = MediatorBasic()
        case "stateMachine": mediator = MediatorStateMachine()
        case _: return None

    return mediator

def get_assistant_proxy(type, mediator, **cfg):
    match type:
        case "gpt" :
            proxy = AssistantProxyGpt(mediator, cfg["assistant_id"])
        case "gemini": proxy = AssistantProxyGemini(mediator)
        case _: return None

    return proxy


