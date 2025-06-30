from typing import Annotated

from langchain.chat_models import init_chat_model
from typing_extensions import TypedDict
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from utils.call_llm import call_llm
import os

# 初始化模型
llm = ChatOpenAI(
    model = os.environ.get("MODEL", ""),
    api_key=os.environ.get("OPENAI_API_KEY", ""),
    base_url=os.environ.get("OPENAI_BASE_URL", ""),
    streaming=False
)

class State(TypedDict):
    messages: list


def chatbot(state: State):
    last_message = state["messages"][-1]
    response = llm.invoke([AIMessage(content="你是一个友好的助手"), last_message])
    return {"messages": [AIMessage(content=response.content)]}


# The first argument is the unique node name
# The second argument is the function or object that will be called whenever
# the node is used.
def build_graph():
    graph_builder = StateGraph(State)
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_edge(START, "chatbot")
    graph = graph_builder.compile()
    return graph