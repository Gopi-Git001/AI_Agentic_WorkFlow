import os
from typing import Any, Optional, Literal, Union

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse, Response, StreamingResponse
from starlette.background import BackgroundTask
from pydantic import BaseModel


load_dotenv()

app = FastAPI(title="My Ollama API Gateway")

MY_API_KEY = os.getenv("MY_API_KEY", "my-secret-key")
OLLAMA_OPENAI_BASE_URL = os.getenv(
    "OLLAMA_OPENAI_BASE_URL",
    "http://localhost:11434/v1"
).rstrip("/")

DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-oss:120b-cloud")


class Message(BaseModel):
    role: Literal["system", "user", "assistant", "tool"] = "user"
    content: Union[str, list, dict, None] = None


class ChatCompletionRequest(BaseModel):
    model: Optional[str] = None
    messages: list[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False
    tools: Optional[list[dict[str, Any]]] = None


class SimpleChatRequest(BaseModel):
    message: str
    model: Optional[str] = None
    system: Optional[str] = "You are a helpful AI assistant."


def check_api_key(
    x_api_key: Optional[str],
    authorization: Optional[str]
):
    valid_bearer = f"Bearer {MY_API_KEY}"

    if x_api_key == MY_API_KEY:
        return

    if authorization == valid_bearer:
        return

    raise HTTPException(status_code=401, detail="Invalid API key")


async def proxy_to_ollama(payload: dict):
    url = f"{OLLAMA_OPENAI_BASE_URL}/chat/completions"

    if payload.get("stream") is True:
        client = httpx.AsyncClient(timeout=None)
        request = client.build_request("POST", url, json=payload)
        response = await client.send(request, stream=True)

        async def close_connection():
            await response.aclose()
            await client.aclose()

        return StreamingResponse(
            response.aiter_raw(),
            status_code=response.status_code,
            media_type=response.headers.get("content-type", "text/event-stream"),
            background=BackgroundTask(close_connection),
        )

    async with httpx.AsyncClient(timeout=180) as client:
        response = await client.post(url, json=payload)

    try:
        return JSONResponse(
            status_code=response.status_code,
            content=response.json()
        )
    except Exception:
        return Response(
            status_code=response.status_code,
            content=response.text,
            media_type="text/plain"
        )


@app.get("/")
def home():
    return {
        "status": "running",
        "ollama_openai_base_url": OLLAMA_OPENAI_BASE_URL,
        "default_model": DEFAULT_MODEL
    }


@app.get("/health")
async def health():
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{OLLAMA_OPENAI_BASE_URL}/models")

        return {
            "fastapi": "ok",
            "ollama": response.status_code,
            "ollama_base_url": OLLAMA_OPENAI_BASE_URL
        }
    except Exception as error:
        return {
            "fastapi": "ok",
            "ollama": "not reachable",
            "error": str(error)
        }


@app.post("/chat")
async def simple_chat(
    body: SimpleChatRequest,
    x_api_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None),
):
    check_api_key(x_api_key, authorization)

    messages = []

    if body.system:
        messages.append({
            "role": "system",
            "content": body.system
        })

    messages.append({
        "role": "user",
        "content": body.message
    })

    payload = {
        "model": body.model or DEFAULT_MODEL,
        "messages": messages,
        "stream": False
    }

    return await proxy_to_ollama(payload)


@app.post("/v1/chat/completions")
async def openai_compatible_chat(
    body: ChatCompletionRequest,
    x_api_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None),
):
    check_api_key(x_api_key, authorization)

    payload = body.model_dump(exclude_none=True)
    payload["model"] = payload.get("model") or DEFAULT_MODEL

    return await proxy_to_ollama(payload)


@app.get("/v1/models")
async def list_models(
    x_api_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None),
):
    check_api_key(x_api_key, authorization)

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(f"{OLLAMA_OPENAI_BASE_URL}/models")

    try:
        return JSONResponse(
            status_code=response.status_code,
            content=response.json()
        )
    except Exception:
        return Response(
            status_code=response.status_code,
            content=response.text,
            media_type="text/plain"
        )