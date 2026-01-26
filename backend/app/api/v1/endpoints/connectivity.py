import asyncio
import uuid
from typing import Optional
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from ....services import ConnectivityService, AuthService
from ....websocket.manager import manager


router = APIRouter()
connectivity_service = ConnectivityService()
auth_service = AuthService()


class TestRequest(BaseModel):
    target_url: str
    auth_code: str


class TestResponse(BaseModel):
    task_id: str
    status: str


class SecurityIncidentsTestRequest(BaseModel):
    auth_code: str
    base_url: Optional[str] = None


class SecurityIncidentsTestResponse(BaseModel):
    success: bool
    message: str
    latency_ms: Optional[float] = None
    incident_count: Optional[int] = None
    error_type: Optional[str] = None


@router.post("/test", response_model=TestResponse)
async def start_test(request: TestRequest):
    """
    启动连通性测试

    Args:
        request: 包含目标 URL 和联动码的请求

    Returns:
        任务 ID 和状态
    """
    # 先验证联动码
    success, message = auth_service.verify_auth_code(request.auth_code)
    if not success:
        raise HTTPException(status_code=401, detail=message)

    # 创建任务
    task_id = str(uuid.uuid4())

    # 异步执行测试
    asyncio.create_task(
        connectivity_service.test_with_sdk(
            target_url=request.target_url,
            auth_code=request.auth_code,
            task_id=task_id
        )
    )

    return TestResponse(task_id=task_id, status="running")


@router.websocket("/ws/test/{task_id}")
async def websocket_test(websocket: WebSocket, task_id: str):
    """
    WebSocket 端点 - 实时推送测试进度

    Args:
        websocket: WebSocket 连接
        task_id: 任务 ID
    """
    await manager.connect(task_id, websocket)
    try:
        while True:
            # 保持连接活跃
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(task_id)


@router.post("/test-security-incidents", response_model=SecurityIncidentsTestResponse)
async def test_security_incidents_connectivity(request: SecurityIncidentsTestRequest):
    """
    通过调用安全事件API测试连通性

    此端点直接返回测试结果（无需WebSocket，无需异步任务）

    Args:
        request: 包含联动码和可选的基础URL

    Returns:
        测试结果，包含成功状态、消息和可选的详细信息
    """
    # 验证联动码
    success, message = auth_service.verify_auth_code(request.auth_code)
    if not success:
        return SecurityIncidentsTestResponse(
            success=False,
            message=message,
            error_type="invalid_auth_code"
        )

    # 执行连通性测试
    result = await connectivity_service.test_with_security_incidents_api(
        auth_code=request.auth_code,
        base_url=request.base_url
    )

    return SecurityIncidentsTestResponse(**result)
