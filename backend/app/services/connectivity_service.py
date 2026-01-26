import asyncio
import time
import json
import requests
from ..utils.sdk.aksk_py3 import Signature
from ..websocket.manager import manager
from .security_incidents_service import SecurityIncidentsService


class ConnectivityService:
    """连通性测试服务 - 使用 SDK 发起签名请求测试连通性"""

    def __init__(self):
        self.security_incidents_service = SecurityIncidentsService()

    async def test_with_sdk(
        self,
        target_url: str,
        auth_code: str,
        task_id: str
    ) -> dict:
        """
        使用现有 SDK 发起签名请求，测试连通性

        Args:
            target_url: 目标 API 地址
            auth_code: 联动码
            task_id: 任务 ID

        Returns:
            测试结果
        """
        try:
            # 推送开始事件
            await manager.send_to_task(task_id, {
                "type": "test_start",
                "task_id": task_id,
                "message": "开始测试连通性..."
            })

            # 创建签名对象
            signature = Signature(auth_code=auth_code)

            # 构造请求（参考 test_aksk.py）
            headers = {
                "content-type": "application/json"
            }
            data = {}  # 根据实际 API 需求构造

            # 构造 POST 请求
            req = requests.Request("POST", target_url, headers=headers, json=data)

            # 对请求签名（关键步骤）
            signature.signature(req=req)

            # 发送请求并计时
            start_time = time.time()
            session = requests.Session()
            session.verify = False  # 忽略 SSL 证书验证
            response = session.send(req.prepare())
            end_time = time.time()

            latency = round((end_time - start_time) * 1000, 2)

            # 判断测试结果
            status = "success" if response.status_code == 200 else "failed"
            result = {
                "protocol": "HTTP/HTTPS",
                "status": status,
                "status_code": response.status_code,
                "latency": latency,
                "response_preview": response.text[:200] if response.text else ""
            }

            # 推送实时结果
            await manager.send_to_task(task_id, {
                "type": "test_progress",
                "task_id": task_id,
                "result": result
            })

            # 推送完成事件
            await manager.send_to_task(task_id, {
                "type": "test_complete",
                "task_id": task_id,
                "message": "测试完成"
            })

            return {
                "status": "success",
                "latency": latency,
                "status_code": response.status_code
            }

        except Exception as e:
            # 推送错误结果
            await manager.send_to_task(task_id, {
                "type": "test_progress",
                "task_id": task_id,
                "result": {
                    "protocol": "HTTP/HTTPS",
                    "status": "failed",
                    "error": str(e)
                }
            })

            # 推送完成事件
            await manager.send_to_task(task_id, {
                "type": "test_complete",
                "task_id": task_id,
                "message": f"测试失败: {str(e)}"
            })

            return {
                "status": "failed",
                "error": str(e)
            }

    async def test_with_security_incidents_api(
        self,
        auth_code: str,
        base_url: str = None
    ) -> dict:
        """
        Test connectivity using security incidents API

        This is a simpler, synchronous alternative to test_with_sdk

        Args:
            auth_code: The authentication code
            base_url: Base URL (optional)

        Returns:
            Test result with success status, message, and optional details
        """
        return await self.security_incidents_service.test_connectivity(
            auth_code=auth_code,
            base_url=base_url
        )
