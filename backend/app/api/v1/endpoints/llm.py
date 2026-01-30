from typing import Optional, List, AsyncGenerator
from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
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
    auth_code: Optional[str] = None  # Flux auth code for asset operations
    flux_base_url: Optional[str] = None  # Flux API base URL


class ChatResponse(BaseModel):
    success: bool
    message: str
    type: Optional[str] = "text"  # "text" | "asset_confirmation" | "ipblock_confirmation" | "ipblock_status" | "incidents_list" | "incident_proof" | "incident_entities" | "incident_status_updated" | "scenario_start" | "scenario_completed"
    asset_params: Optional[dict] = None  # 资产参数（用于确认对话框）
    block_params: Optional[dict] = None  # IP封禁参数（用于确认对话框）
    status: Optional[dict] = None  # IP封禁状态
    incidents_data: Optional[dict] = None  # 事件列表数据
    proof_data: Optional[dict] = None  # 事件举证数据
    entities_data: Optional[dict] = None  # IP实体数据
    update_result: Optional[dict] = None  # 更新结果数据
    scenario_data: Optional[dict] = None  # 场景启动数据（步骤1-3的结果）
    scenario_result: Optional[dict] = None  # 场景执行结果（步骤4的结果）


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
    与大模型进行对话（支持资产添加）

    Args:
        request: 包含对话历史、提供商、API Key、可选的Base URL和认证信息

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

    # 调用支持资产添加的聊天方法
    result = await llm_service.chat_with_asset_support(
        messages=messages,
        provider=request.provider,
        api_key=request.api_key,
        base_url=request.base_url,
        auth_code=request.auth_code,
        flux_base_url=request.flux_base_url
    )

    return ChatResponse(**result)


class AssetConfirmRequest(BaseModel):
    """Request model for confirming asset creation"""
    params: dict
    auth_code: str
    flux_base_url: str


@router.post("/confirm-asset")
async def confirm_asset_creation(request: AssetConfirmRequest):
    """
    Confirm and create asset after user approval

    Args:
        request: Contains asset parameters and authentication info

    Returns:
        Asset creation result
    """
    from ....services.asset_service import AssetService

    try:
        # Create asset service
        asset_service = AssetService(
            base_url=request.flux_base_url,
            auth_code=request.auth_code
        )

        # Create asset
        result = asset_service.create_asset(request.params)

        # Format response
        if result.get("success"):
            return {
                "success": True,
                "message": "✅ 资产添加成功！",
                "type": "asset_summary",
                "asset_data": {
                    "ip": request.params.get("ip"),
                    "assetName": request.params.get("assetName"),
                    "type": request.params.get("type"),
                    "classify1Id": request.params.get("classify1Id"),
                    "classifyId": request.params.get("classifyId"),
                    "magnitude": request.params.get("magnitude"),
                    "branchId": request.params.get("branchId"),
                }
            }
        else:
            error_msg = result.get('message', '未知错误')

            # Handle common errors
            if "已存在资产" in error_msg or "already exists" in error_msg.lower():
                ip = request.params.get("ip", "未知")
                return {
                    "success": False,
                    "message": f"⚠️ 资产已存在\n\nIP 地址 {ip} 的资产已经在系统中存在。",
                    "type": "text"
                }
            else:
                return {
                    "success": False,
                    "message": f"❌ 添加失败：{error_msg}",
                    "type": "text"
                }

    except Exception as e:
        return {
            "success": False,
            "message": f"❌ 添加失败：{str(e)}",
            "type": "text"
        }


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


@router.get("/scenario/stream")
async def execute_scenario_stream(
    provider: Optional[str] = None,
    api_key: Optional[str] = None,
    llm_base_url: Optional[str] = None,
    auth_code: Optional[str] = None,
    flux_base_url: Optional[str] = None
):
    """
    SSE流式返回场景执行进度（GET请求）

    每个步骤完成后立即推送数据给前端

    Args:
        provider: LLM provider (query parameter)
        api_key: LLM API key (query parameter)
        llm_base_url: LLM base URL (query parameter)
        auth_code: Flux authentication code (query parameter)
        flux_base_url: Flux API base URL (query parameter)

    Returns:
        Server-Sent Events stream
    """
    async def event_generator() -> AsyncGenerator[str, None]:
        from ....services.scenario_orchestration_service import ScenarioOrchestrationService
        service = ScenarioOrchestrationService()

        try:
            # Step 1: 查询今日高危事件
            step1_result = await service._step1_query_incidents(
                auth_code=auth_code,
                base_url=flux_base_url
            )
            yield f"event: step_complete\ndata: {json.dumps({'step': 1, 'data': step1_result})}\n\n"

            # Step 2: 分析Top 10事件
            incidents = step1_result.get("incidents", [])
            step2_result = await service._step2_analyze_top_incidents(
                auth_code=auth_code,
                base_url=flux_base_url,
                incidents=incidents[:10],
                provider=provider,
                api_key=api_key,
                llm_base_url=llm_base_url
            )
            yield f"event: step_complete\ndata: {json.dumps({'step': 2, 'data': step2_result})}\n\n"

            # Step 3: 准备确认信息
            step3_result = service._step3_prepare_confirmation_for_top_incidents(
                step2_result=step2_result,
                incidents=incidents
            )
            yield f"event: step_complete\ndata: {json.dumps({'step': 3, 'data': step3_result})}\n\n"

            # 完成
            yield f"event: complete\ndata: {json.dumps({'success': True})}\n\n"

        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # 禁用nginx缓冲
        }
    )
