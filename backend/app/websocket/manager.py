from fastapi import WebSocket
from typing import Dict


class ConnectionManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, task_id: str, websocket: WebSocket):
        """接受新的 WebSocket 连接"""
        await websocket.accept()
        self.active_connections[task_id] = websocket

    def disconnect(self, task_id: str):
        """断开连接"""
        if task_id in self.active_connections:
            del self.active_connections[task_id]

    async def send_to_task(self, task_id: str, message: dict):
        """向特定任务发送消息"""
        if task_id in self.active_connections:
            await self.active_connections[task_id].send_json(message)

    async def broadcast(self, message: dict):
        """广播消息到所有连接"""
        for connection in self.active_connections.values():
            await connection.send_json(message)


# 全局连接管理器实例
manager = ConnectionManager()
