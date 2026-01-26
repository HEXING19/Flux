from typing import Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ....services.llm_service import LLMService


router = APIRouter()
llm_service = LLMService()


class LLMTestRequest(BaseModel):
    provider: str
    api_key: str
    base_url: Optional[str] = None


class LLMTestResponse(BaseModel):
    success: bool
    message: str
    provider: Optional[str] = None
    model: Optional[str] = None


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    provider: str
    api_key: str
    base_url: Optional[str] = None


class ChatResponse(BaseModel):
    success: bool
    message: str


@router.post("/test", response_model=LLMTestResponse)
async def test_llm_connection(request: LLMTestRequest):
    """
    测试与大模型API的连通性

    Args:
        request: 包含提供商、API Key和可选的Base URL

    Returns:
        测试结果
    """
    if not request.api_key:
        raise HTTPException(status_code=400, detail="API Key不能为空")

    result = await llm_service.test_connection(
        provider=request.provider,
        api_key=request.api_key,
        base_url=request.base_url
    )

    return LLMTestResponse(**result)


@router.post("/chat", response_model=ChatResponse)
async def chat_with_llm(request: ChatRequest):
    """
    与大模型进行对话

    Args:
        request: 包含对话历史、提供商、API Key和可选的Base URL

    Returns:
        对话响应
    """
    if not request.api_key:
        raise HTTPException(status_code=400, detail="API Key不能为空")

    if not request.messages:
        raise HTTPException(status_code=400, detail="消息列表不能为空")

    # 转换消息格式
    messages = [
        {"role": msg.role, "content": msg.content}
        for msg in request.messages
    ]

    result = await llm_service.chat(
        messages=messages,
        provider=request.provider,
        api_key=request.api_key,
        base_url=request.base_url
    )

    return ChatResponse(**result)


@router.get("/providers")
async def get_supported_providers():
    """
    获取支持的模型提供商列表

    Returns:
        提供商列表
    """
    providers = llm_service.get_supported_providers()
    return {
        "providers": providers
    }
