from typing_extensions import TypedDict
from langchain_core.messages import AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from agent.prompt import coordinator_prompt, planner_prompt
from dotenv import load_dotenv

load_dotenv()

import os

# 初始化模型
llm = ChatOpenAI(
    model = os.environ.get("MODEL", ""),
    api_key=os.environ.get("OPENAI_API_KEY", ""),
    base_url=os.environ.get("OPENAI_BASE_URL", ""),
    streaming=True  # 修改为True以支持流式输出
)

class State(TypedDict):
    messages: list

REWRITE_PROMPT = (
    "Look at the input and try to reason about the underlying semantic intent / meaning.\n"
    "Here is the initial question:"
    "\n ------- \n"
    "{question}"
    "\n ------- \n"
    "Formulate an improved question:"
)


async def rewrite_question(state: State):
    """Rewrite the original user question."""
    messages = state["messages"]
    question = messages[0]
    prompt = REWRITE_PROMPT.format(question=question)
    print("rewrite_question is: ", prompt)
    response = await llm.ainvoke([{"role": "user", "content": prompt}])
    print("rewrite_question response is: ", response)
    return {"messages": [{"role": "user", "content": response.content}]}

async def coordinator(state: State):
    last_message = state["messages"][-1]
    print("coordinator is: ", last_message)
    response = await llm.ainvoke([SystemMessage(content=coordinator_prompt), last_message])
    state['current_plan'] = response.content
    print("coordinator response is: ", response)
    return {"messages": [AIMessage(content=response.content)]}

async def planner(state: State):
    last_message = state["messages"][-1]
    print("planner is: ", last_message)
    response = await llm.ainvoke([SystemMessage(content=planner_prompt), last_message])
    print("planner response is: ", response)
    return {"messages": [AIMessage(content=response.content)]}

async def chat(state: State):
    last_message = state["messages"][-1]
    response = await llm.ainvoke([SystemMessage(content=planner_prompt), last_message])
    return {"messages": [AIMessage(content=response.content)]}

# 定义路由函数，根据状态返回不同的节点
def route_to_node(state: State):
    current_plan = state.get("current_plan")
    if "handoff_to_planner" in current_plan:
        return "planner"
    return "end"


# The first argument is the unique node name
# The second argument is the function or object that will be called whenever
# the node is used.
def build_graph():
    graph_builder = StateGraph(State)
    graph_builder.add_node("rewrite_question", rewrite_question)
    graph_builder.add_node("coordinator", coordinator)
    graph_builder.add_node("planner", planner)
    graph_builder.add_edge(START, "rewrite_question")
    graph_builder.add_edge("rewrite_question", "coordinator")
    graph_builder.add_conditional_edges("coordinator", route_to_node, {"planner": "planner","end": END})
    graph_builder.add_edge("planner", END)
    
    graph = graph_builder.compile()
    return graph