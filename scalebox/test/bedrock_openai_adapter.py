#!/usr/bin/env python3
"""
OpenAI-compatible adapter for Amazon Bedrock Claude 3.7 Sonnet
POST /v1/chat/completions  ->  Bedrock invoke-model
"""
import json, boto3, os
from fastapi import FastAPI, Response, status
from pydantic import BaseModel
from typing import List, Dict   # <- 修正语法

app = FastAPI()
BEDROCK = boto3.client("bedrock-runtime", region_name="us-east-1")
MODEL_ID = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str
    messages: List[Message]
    max_tokens: int = 4096
    temperature: float = 0.1

@app.post("/v1/chat/completions")
def chat_completions(req: ChatRequest):
    # 1. OpenAI -> Claude 格式
    claude_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": req.max_tokens,
        "temperature": req.temperature,
        "messages": [{"role": m.role, "content": m.content} for m in req.messages],
    }
    # 2. 调 Bedrock
    response = BEDROCK.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps(claude_body),
        contentType="application/json",
    )
    # 3. 解析 Claude 响应
    result = json.loads(response["body"].read())
    text = result["content"][0]["text"]

    # 4. 伪装成 OpenAI 格式返回
    openai_reply = {
        "id": "chatcmpl-bedrock",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "gpt-4",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": text},
                "finish_reason": "stop",
            }
        ],
    }
    return Response(content=json.dumps(openai_reply), media_type="application/json")

# 健康检查
@app.get("/v1/models")
def models():
    return {"data": [{"id": "gpt-4", "object": "model"}]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)