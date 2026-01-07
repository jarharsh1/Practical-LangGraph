from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_ollama import ChatOllama
from langgraph.graph.message import add_messages
llm = ChatOllama(model="llama3.2")
from langgraph.checkpoint.memory import MemorySaver

## defining state
class ChatBot(TypedDict):
    messages: Annotated[list[BaseMessage],add_messages]
    
## defining node function
def chatnode(state:ChatBot)->ChatBot:
    
    ## take user query
    messages = state['messages']
    
    ## send to llm
    response = llm.invoke(messages)
    
    ## response back to state
    return {'messages':[response]}


## define checkpoint
checkpointer = MemorySaver()

## Define graph
graph = StateGraph(ChatBot)

## add nodes
graph.add_node('chatnode',chatnode)

## add edges
graph.add_edge(START,'chatnode')
graph.add_edge('chatnode',END)

chatbot = graph.compile(checkpointer=checkpointer)

# for message_chunk, metadata in chatbot.stream(
#     {'messages':HumanMessage(content='What is the recipe to make pasta ?')},
#     config={'configurable':{'thread_id':'thread-1'}},
#     stream_mode='messages'
# ):
#     if message_chunk.content:
#         print(message_chunk.content, end = " ", flush=True)


