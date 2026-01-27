"""
IP Block API Endpoints
Provides REST API for IP blocking operations
"""

from fastapi import APIRouter, HTTPException
from typing import Optional, List
from pydantic import BaseModel

from ....services.ipblock_service import IpBlockService


router = APIRouter()


# Request/Response Models
class CheckIPRequest(BaseModel):
    ip: str
    auth_code: Optional[str] = None
    ak: Optional[str] = None
    sk: Optional[str] = None
    flux_base_url: str


class GetDevicesRequest(BaseModel):
    device_type: str = "AF"
    auth_code: Optional[str] = None
    ak: Optional[str] = None
    sk: Optional[str] = None
    flux_base_url: str


class BlockIPRequest(BaseModel):
    ip: str
    device_id: int
    device_name: str
    device_type: str = "AF"
    device_version: str = ""
    block_type: str = "SRC_IP"
    time_type: str = "forever"
    time_value: Optional[int] = None
    time_unit: str = "d"
    reason: str = ""
    auth_code: Optional[str] = None
    ak: Optional[str] = None
    sk: Optional[str] = None
    flux_base_url: str


class CheckAndBlockRequest(BaseModel):
    ip: str
    device_name: str
    device_type: str = "AF"
    auth_code: Optional[str] = None
    ak: Optional[str] = None
    sk: Optional[str] = None
    flux_base_url: str


class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
    error_info: Optional[dict] = None


@router.post("/check", response_model=APIResponse)
async def check_ip_status(request: CheckIPRequest):
    """
    Check if an IP address is already blocked

    Args:
        request: CheckIPRequest with IP and authentication info

    Returns:
        APIResponse with blocking status
    """
    try:
        # Initialize service
        service = IpBlockService(
            base_url=request.flux_base_url,
            auth_code=request.auth_code,
            ak=request.ak,
            sk=request.sk
        )

        # Check IP status
        result = service.check_ip_blocked(request.ip)

        if result["success"]:
            if result["blocked"]:
                return APIResponse(
                    success=True,
                    message=f"IP {request.ip} 已被封禁，共找到 {result['total_rules']} 条封禁规则",
                    data={
                        "blocked": True,
                        "rules": result.get("rules", []),
                        "devices": result.get("devices", []),
                        "total_rules": result.get("total_rules", 0)
                    }
                )
            else:
                return APIResponse(
                    success=True,
                    message=f"IP {request.ip} 未被封禁",
                    data={
                        "blocked": False,
                        "rules": [],
                        "devices": []
                    }
                )
        else:
            return APIResponse(
                success=False,
                message=result.get("error_info", {}).get("friendly_message", "查询失败"),
                error_info=result.get("error_info")
            )

    except Exception as e:
        return APIResponse(
            success=False,
            message=f"查询IP封禁状态时发生错误: {str(e)}",
            error_info={
                "error_type": "system_error",
                "friendly_message": "系统错误",
                "raw_message": str(e),
                "suggestion": "请联系系统管理员",
                "actions": ["查看日志", "联系管理员"]
            }
        )


@router.post("/devices", response_model=APIResponse)
async def get_devices(request: GetDevicesRequest):
    """
    Get available blocking devices

    Args:
        request: GetDevicesRequest with device type and authentication info

    Returns:
        APIResponse with device list
    """
    try:
        # Initialize service
        service = IpBlockService(
            base_url=request.flux_base_url,
            auth_code=request.auth_code,
            ak=request.ak,
            sk=request.sk
        )

        # Get devices
        result = service.get_available_devices(request.device_type)

        if result["success"]:
            return APIResponse(
                success=True,
                message=f"查询到 {result['total']} 个可用设备",
                data={
                    "devices": result.get("devices", []),
                    "total": result.get("total", 0),
                    "device_type": request.device_type
                }
            )
        else:
            return APIResponse(
                success=False,
                message=result.get("error_info", {}).get("friendly_message", "查询设备失败"),
                error_info=result.get("error_info")
            )

    except Exception as e:
        return APIResponse(
            success=False,
            message=f"查询设备列表时发生错误: {str(e)}",
            error_info={
                "error_type": "system_error",
                "friendly_message": "系统错误",
                "raw_message": str(e),
                "suggestion": "请联系系统管理员",
                "actions": ["查看日志", "联系管理员"]
            }
        )


@router.post("/block", response_model=APIResponse)
async def block_ip(request: BlockIPRequest):
    """
    Execute IP blocking operation

    Args:
        request: BlockIPRequest with blocking parameters

    Returns:
        APIResponse with blocking result
    """
    try:
        # Initialize service
        service = IpBlockService(
            base_url=request.flux_base_url,
            auth_code=request.auth_code,
            ak=request.ak,
            sk=request.sk
        )

        # Block IP
        result = service.block_ip(
            ip_address=request.ip,
            device_id=request.device_id,
            device_name=request.device_name,
            device_type=request.device_type,
            device_version=request.device_version,
            block_type=request.block_type,
            time_type=request.time_type,
            time_value=request.time_value,
            time_unit=request.time_unit,
            reason=request.reason
        )

        if result["success"]:
            return APIResponse(
                success=True,
                message=result["message"],
                data={
                    "rule_ids": result.get("rule_ids", []),
                    "rule_count": result.get("rule_count", 0),
                    "ip": request.ip,
                    "device": request.device_name
                }
            )
        else:
            return APIResponse(
                success=False,
                message=result["message"],
                error_info=result.get("error_info")
            )

    except Exception as e:
        return APIResponse(
            success=False,
            message=f"执行IP封禁时发生错误: {str(e)}",
            error_info={
                "error_type": "system_error",
                "friendly_message": "系统错误",
                "raw_message": str(e),
                "suggestion": "请联系系统管理员",
                "actions": ["查看日志", "联系管理员"]
            }
        )


@router.post("/check-and-block", response_model=APIResponse)
async def check_and_block(request: CheckAndBlockRequest):
    """
    Check IP status and prepare block parameters if not blocked

    Args:
        request: CheckAndBlockRequest with IP and device info

    Returns:
        APIResponse with action needed (already_blocked, need_block, or error)
    """
    try:
        # Initialize service
        service = IpBlockService(
            base_url=request.flux_base_url,
            auth_code=request.auth_code,
            ak=request.ak,
            sk=request.sk
        )

        # Check and prepare block
        result = service.check_and_block(
            ip_address=request.ip,
            device_name=request.device_name,
            device_type=request.device_type
        )

        if result["action"] == "already_blocked":
            return APIResponse(
                success=True,
                message=result["current_status"]["message"],
                data={
                    "action": "already_blocked",
                    "ip_address": request.ip,
                    "blocked": True,
                    "rules": result["current_status"].get("rules", []),
                    "devices": result["current_status"].get("devices", []),
                    "total_rules": result["current_status"].get("total_rules", 0)
                }
            )
        elif result["action"] == "need_block":
            return APIResponse(
                success=True,
                message=result["message"],
                data={
                    "action": "need_block",
                    "block_params": result["block_params"]
                }
            )
        else:
            return APIResponse(
                success=False,
                message=result.get("error_info", {}).get("friendly_message", "操作失败"),
                error_info=result.get("error_info")
            )

    except Exception as e:
        return APIResponse(
            success=False,
            message=f"检查IP状态时发生错误: {str(e)}",
            error_info={
                "error_type": "system_error",
                "friendly_message": "系统错误",
                "raw_message": str(e),
                "suggestion": "请联系系统管理员",
                "actions": ["查看日志", "联系管理员"]
            }
        )


@router.post("/confirm-block", response_model=APIResponse)
async def confirm_block(request: BlockIPRequest):
    """
    Confirm and execute IP blocking (for frontend confirmation dialog)

    Args:
        request: BlockIPRequest with blocking parameters

    Returns:
        APIResponse with blocking result
    """
    # This endpoint is the same as /block but with clearer semantics
    # It's called after user confirms the blocking operation
    return await block_ip(request)
