import asyncio
import json

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessageChunk, ToolMessage
from pydantic import BaseModel

# 2. Ahora al importar src.agent y src.database ya leerán la URL de PostgreSQL del .env
from src.agent import agent_executor
from src.database import init_db

# Inicializamos la estructura de la base de datos
init_db()

app = FastAPI()

origins = ["http://localhost:5173","http://127.0.0.1:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    prompt: str

config = {
    "configurable": {
        "thread_id": "0001",
        "user_id": 1  # ID del usuario Juan Pérez
    }
}


async def run_python_agent(prompt: str):
    async for chunk, metadata in agent_executor.astream(
        input={"messages": [{"role": "user", "content": prompt}]},
        config=config,
        stream_mode="messages"
    ):
        if isinstance(chunk, AIMessageChunk) and chunk.content and isinstance(chunk.content, str):
            yield f"data: {chunk.content}\n\n"
            await asyncio.sleep(0)
        elif isinstance (chunk, ToolMessage):
            if chunk.name=="create_chart":
                chart_json = (
                    chunk.content
                    if isinstance(chunk.content, str)
                    else json.dumps(chunk.content)
                )
                yield f"event: chart\ndata: {chart_json}\n\n"

            elif chunk.name=="create_table":
                table_json = (
                    chunk.content
                    if isinstance(chunk.content, str)
                    else json.dumps(chunk.content)
                )
                yield f"event: table\ndata: {table_json}\n\n"

@app.post("/api/agent")
async def chat_endpoint(request: ChatRequest) -> StreamingResponse:
    return StreamingResponse(
        run_python_agent(request.prompt),
        media_type="text/event-stream"
    )
