from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse  # 重新添加StreamingResponse导入
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
import os
import uvicorn
import asyncio  # 添加asyncio导入
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
    
    if not messages:
        return {"error": "No messages provided"}
    
    user_message = messages[-1]["content"]
    
    async def stream_response():
        try:
            graph = build_graph()
            
            # 使用异步流式处理
            stream_chunks = graph.astream({
                "messages": [{
                    "role": "user",
                    "content": user_message
                }]
            })
            
            async for chunk in stream_chunks:
                for node, update in chunk.items():
                    if isinstance(update.get("messages"), list) and update["messages"]:
                        last_message = update["messages"][-1]
                        message_content = last_message.content if hasattr(last_message, 'content') else last_message.get("content", "")
                        # 按照SSE格式输出
                        yield f"data: {message_content}\n\n"
                await asyncio.sleep(0.005)  # 避免太快发送
        except Exception as e:
            yield f"data: Error: {str(e)}\n\n"
    
    return StreamingResponse(stream_response(), media_type="text/event-stream")

# 前端页面
@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run("fastapi_app:app", host="0.0.0.0", port=8001, reload=True)  # 启用自动重载