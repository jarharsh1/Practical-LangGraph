import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import BaseMessage, HumanMessage
import uuid
import re

################################ Utility  functions #######################################

def gen_thread_id():
    thread_id= uuid.uuid4()
    return thread_id

def make_title(text: str, max_words: int = 4) -> str:
    text = re.sub(r"\s+", " ", (text or "").strip())
    if not text:
        return "New chat"
    return " ".join(text.split(" ")[:max_words])[:40]

def reset_chat():
    st.session_state['thread_id'] = gen_thread_id()
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] =[]
    
def add_thread(thread_id):
    if thread_id not in st.session_state['chat_thread']:
        st.session_state['chat_thread'].append(thread_id)
        
def load_conversation(thread_id):
    return chatbot.get_state(config={'configurable':{'thread_id':str(thread_id)}}).values['messages']

################################ Session  setup #######################################

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []
    
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = gen_thread_id()
    
if 'chat_thread' not in st.session_state:
    st.session_state['chat_thread'] = []

if "thread_titles" not in st.session_state:
    st.session_state["thread_titles"] = {}

add_thread(st.session_state['thread_id'])
    
CONFIG = {'configurable':{'thread_id': st.session_state['thread_id']}}

if st.session_state["thread_id"] not in st.session_state["thread_titles"]:
    st.session_state["thread_titles"][st.session_state["thread_id"]] = "New chat"

#################################### Sidebar UI #############################################

st.sidebar.title('LangGraph Chatbot')

if st.sidebar.button('New Chat'):
    reset_chat()

st.sidebar.header('My Conversations')

for thread_id in st.session_state['chat_thread'][::-1]:
    if thread_id in st.session_state["thread_titles"]:
        label = st.session_state["thread_titles"][thread_id]
    else:
        label = "New chat"
    if st.sidebar.button(str(thread_id)):
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id)
        temp_message = []
        for message in messages:
            if isinstance(message,HumanMessage):
                role = 'user'
            else:
                role = 'assistant'
            temp_message.append({'role':role, 'content':message.content})
        st.session_state['message_history'] = temp_message


################################# Main UI ##################################################

## loading conversation history
for message in  st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input('Type here')

if user_input:
    
    
    
    st.session_state['message_history'].append({'role':'user','content':user_input})
    with st.chat_message('user'):
        st.text(user_input)
    
   
    with st.chat_message('assistant'):
        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in 
                chatbot.stream({'messages':HumanMessage(content=user_input)},
                config=CONFIG,
                stream_mode='messages'
                )
        )
        st.session_state['message_history'].append({'role':'assistant','content':ai_message})
    
    
