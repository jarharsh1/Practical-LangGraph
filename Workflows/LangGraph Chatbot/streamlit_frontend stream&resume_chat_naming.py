import re
import uuid
import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage

def gen_thread_id() -> str:
    return str(uuid.uuid4())

def make_title(text: str, max_words: int = 4) -> str:
    text = re.sub(r"\s+", " ", (text or "").strip())
    if not text:
        return "New chat"
    return " ".join(text.split(" ")[:max_words])[:40]

def add_thread(thread_id: str) -> None:
    if thread_id not in st.session_state["chat_thread"]:
        st.session_state["chat_thread"].append(thread_id)

def load_conversation(thread_id: str):
    state = chatbot.get_state(config={"configurable": {"thread_id": str(thread_id)}})
    try:
        return state.values["messages"]
    except KeyError:
        return []

def reset_chat() -> None:
    st.session_state["thread_id"] = gen_thread_id()
    add_thread(st.session_state["thread_id"])
    st.session_state["message_history"] = []
    st.session_state["thread_titles"][st.session_state["thread_id"]] = "New chat"

# ---------------- Session setup ----------------
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = gen_thread_id()

if "chat_thread" not in st.session_state:
    st.session_state["chat_thread"] = []

if "thread_titles" not in st.session_state:
    st.session_state["thread_titles"] = {}

add_thread(st.session_state["thread_id"])

if st.session_state["thread_id"] not in st.session_state["thread_titles"]:
    st.session_state["thread_titles"][st.session_state["thread_id"]] = "New chat"

# ---------------- Sidebar ----------------
st.sidebar.title("LangGraph Chatbot")

if st.sidebar.button("New Chat"):
    reset_chat()

st.sidebar.header("My Conversations")

for thread_id in st.session_state["chat_thread"][::-1]:
    if thread_id in st.session_state["thread_titles"]:
        label = st.session_state["thread_titles"][thread_id]
    else:
        label = "New chat"

    if st.sidebar.button(label, key=f"thread_{thread_id}"):
        st.session_state["thread_id"] = thread_id
        st.session_state["message_history"] = [
            {
                "role": ("user" if isinstance(m, HumanMessage) else "assistant"),
                "content": m.content,
            }
            for m in load_conversation(thread_id)
        ]

# ---------------- Main UI ----------------
for m in st.session_state["message_history"]:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

user_input = st.chat_input("Type here")

if user_input:
    if (st.session_state["thread_id"] not in st.session_state["thread_titles"]) or (
        st.session_state["thread_titles"][st.session_state["thread_id"]] == "New chat"
    ):
        st.session_state["thread_titles"][st.session_state["thread_id"]] = make_title(user_input, 4)

    st.session_state["message_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        ai_message = st.write_stream(
            chunk.content
            for chunk, _meta in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config={"configurable": {"thread_id": st.session_state["thread_id"]}},
                stream_mode="messages",
            )
            if getattr(chunk, "content", "")
        )

    st.session_state["message_history"].append({"role": "assistant", "content": ai_message})
