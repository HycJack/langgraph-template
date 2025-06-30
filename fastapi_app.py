from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
import os
import uvicorn
from agent import build_graph

# 初始化FastAPI应用
app = FastAPI(title="LangGraph Demo", version="1.0")

# 挂载静态文件和模板
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# API端点
@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    messages = data.get("messages", [])
    
    # 将用户消息转换为HumanMessage
    human_message = HumanMessage(content=messages[-1]["content"])
    graph = build_graph()
    # 执行工作流
    result = graph.invoke({"messages": [human_message]})
    
    return {"messages": [{"content": msg.content, "type": "ai"} for msg in result["messages"]]}

# 前端页面
@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)