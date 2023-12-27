import asyncio
import os
import traceback
from typing import MutableMapping
from dotenv import load_dotenv
import streamlit as st
import conversation
from pubsub import pub
from conversation import UserProxy

load_dotenv()

asst_id = os.environ["ASSISTANT_ID"]

def listener1(evt):
    st.chat_message("system").write(evt)
    store_message("system", evt)

def listener2(evt):
    run_details.append(evt)

@st.cache_resource
def initialize():
    store : MutableMapping[str, str] = []
    cache_dict = {
        "chat" : None,
        "choice" : "Start your conersation by clicking a button"
    }
    run_details_ = []
    pub.subscribe(listener=listener1, topicName="executedTool")

    pub.subscribe(listener=listener2, topicName="sentMessage")
    pub.subscribe(listener=listener2, topicName="executedTool")
    pub.subscribe(listener=listener2, topicName="retrievedMessage")
    return [store, cache_dict, run_details_, listener1, listener2]

def store_message(role, content):
    store.append({"role": f"{role}", "content": f"{content}"})

def clear_message_store():
    store.clear()

def clean_up():
    clear_message_store()
    st.session_state.conversation = None
    st.session_state.chat_history = None
    cache["chat"] = None
    run_details.clear()

async def run():
    sidebar = st.sidebar
    with sidebar:
        if st.button("Start GPT Conversation", type="secondary", key="start_gpt"):
            clean_up()
            user_proxy = conversation.start_conversation("gpt", assistant_id=asst_id)
            cache["chat"] = user_proxy
            cache["choice"] = "GPT Conversation"
            st.success('Conversation started!', icon="✅")
        elif st.button("Start Gemini Pro Conversation", type="secondary", key="start_gemini"):
            clean_up()
            user_proxy = conversation.start_conversation("gemini")
            cache["chat"] = user_proxy
            cache["choice"] = "Gemini Pro Conversation"
            st.success('Conversation started!', icon="✅")

        stream = st.checkbox('Stream')

    st.header("💬 " + str(cache["choice"]))

    for msg in store:
        st.chat_message(msg["role"]).write(msg["content"])

    prompt = st.chat_input()

    if prompt:
        run_details.clear()
        store_message("user", prompt)
        st.chat_message("user").write(prompt)

        try:
            user_proxy : UserProxy = cache["chat"]
            user_proxy.send_user_message(prompt, use_streamming=stream)
            response = await user_proxy.get_assistant_message()
            if isinstance(response, str):
                store_message("assistant", response)
                st.chat_message("assistant").write(response)
            else:
                asst_msg = st.chat_message("assistant")
                for msg in response:
                    store_message("assistant", msg)
                    asst_msg.write(msg, end="")
        except Exception:
            st.chat_message("system").write("Error")
            raise

    with sidebar:
        if (len(run_details) > 0):
            st.header("Last exchange details ")
            for e in run_details:
                st.info(e)

if __name__ == "__main__":
    [store, cache, run_details, listener1, listener2] = initialize()
    try:
        asyncio.run(run())
    except Exception as e:
        print(traceback.format_exc())
