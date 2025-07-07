from typing_extensions import TypedDict
from langchain_core.messages import AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from agent.prompt import coordinator_prompt, planner_prompt


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


def coordinator(state: State):
    last_message = state["messages"][-1]
    response = llm.invoke([SystemMessage(content=coordinator_prompt), last_message])
    state['current_plan'] = response.content
    return {"messages": [AIMessage(content=response.content)]}

def planner(state: State):
    last_message = state["messages"][-1]
    response = llm.invoke([SystemMessage(content=planner_prompt), last_message])
    return {"messages": [AIMessage(content=response.content)]}

def chat(state: State):
    last_message = state["messages"][-1]
    response = llm.invoke([SystemMessage(content=planner_prompt), last_message])
    return {"messages": [AIMessage(content=response.content)]}

# 定义路由函数，根据状态返回不同的节点
def route_to_node(state: State):
    current_plan = state.get("current_plan")
    if not current_plan or current_plan == "handoff_to_planner()":
        return "planner"
    return "end"


# The first argument is the unique node name
# The second argument is the function or object that will be called whenever
# the node is used.
def build_graph():
    graph_builder = StateGraph(State)
    graph_builder.add_node("coordinator", coordinator)
    graph_builder.add_node("planner", planner)
    graph_builder.add_edge(START, "coordinator")
    graph_builder.add_conditional_edges("coordinator", route_to_node, {"planner": "planner","end": END})
    graph_builder.add_edge("planner", END)
    
    graph = graph_builder.compile()
    return graph
