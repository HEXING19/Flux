"""
Network Security Logs API Endpoints
Provides REST API for querying network security log statistics in Flux XDR
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field, validator
from ....services.network_logs_service import NetworkLogsService


router = APIRouter()


class LogCountRequest(BaseModel):
    """Request model for querying log count"""
    startTimestamp: Optional[int] = Field(None, description="Start timestamp (Unix timestamp)")
    endTimestamp: Optional[int] = Field(None, description="End timestamp (Unix timestamp)")
    productTypes: Optional[List[str]] = Field(None, description="Product types: STA, EDR, AC, CWPP, SSL VPN, NTA, SIP SecLog, Logger")
    accessDirections: Optional[List[int]] = Field(None, description="Access directions: 1=外对内, 2=内对外, 3=内对内")
    threatClasses: Optional[List[str]] = Field(None, description="Threat class (一级分类)")
    srcIps: Optional[List[str]] = Field(None, description="Source IP addresses")
    dstIps: Optional[List[str]] = Field(None, description="Destination IP addresses")
    attackStates: Optional[List[int]] = Field(None, description="Attack states: 0=尝试, 1=失败, 2=成功, 3=失陷")
    severities: Optional[List[int]] = Field(None, description="Severity levels: 0=信息, 1=低危, 2=中危, 3=高危, 4=严重")
    includeComparison: Optional[bool] = Field(False, description="Include comparison data (上周、上月)")
    includeDistribution: Optional[bool] = Field(False, description="Include distribution data (严重程度、访问方向、产品类型)")
    includeTrend: Optional[bool] = Field(False, description="Include trend data (按天统计)")

    @validator('accessDirections')
    def validate_access_directions(cls, v):
        if v is not None:
            for direction in v:
                if direction not in [1, 2, 3]:
                    raise ValueError(f"Invalid access direction: {direction}. Must be 1, 2, or 3")
        return v

    @validator('attackStates')
    def validate_attack_states(cls, v):
        if v is not None:
            for state in v:
                if state not in [0, 1, 2, 3]:
                    raise ValueError(f"Invalid attack state: {state}. Must be 0, 1, 2, or 3")
        return v

    @validator('severities')
    def validate_severities(cls, v):
        if v is not None:
            for severity in v:
                if severity not in [0, 1, 2, 3, 4]:
                    raise ValueError(f"Invalid severity: {severity}. Must be 0-4")
        return v

    @validator('productTypes')
    def validate_product_types(cls, v):
        if v is not None:
            valid_types = ["STA", "EDR", "AC", "CWPP", "SSL VPN", "NTA", "SIP SecLog", "Logger"]
            for product_type in v:
                if product_type not in valid_types:
                    raise ValueError(f"Invalid product type: {product_type}. Must be one of: {', '.join(valid_types)}")
        return v


class LogCountResponse(BaseModel):
    """Response model for log count"""
    success: bool
    message: str
    data: Optional[dict] = None


@router.post("/networksecurity/count", response_model=LogCountResponse)
async def get_log_count(
    request: LogCountRequest,
    x_auth_code: Optional[str] = Header(None, alias="X-Auth-Code"),
    x_base_url: Optional[str] = Header(None, alias="X-Base-Url")
):
    """
    Query network security log count with filters

    Args:
        request: Log count request with filters
        x_auth_code: Flux authentication code (from header)
        x_base_url: Flux API base URL (from header)

    Returns:
        Log count statistics with optional comparison, distribution, and trend data
    """
    if not x_auth_code:
        raise HTTPException(status_code=400, detail="X-Auth-Code header is required")

    if not x_base_url:
        raise HTTPException(status_code=400, detail="X-Base-Url header is required")

    # Create service instance
    service = NetworkLogsService()

    # Extract parameters from request
    start_timestamp = request.startTimestamp
    end_timestamp = request.endTimestamp
    product_types = request.productTypes
    access_directions = request.accessDirections
    threat_classes = request.threatClasses
    src_ips = request.srcIps
    dst_ips = request.dstIps
    attack_states = request.attackStates
    severities = request.severities
    include_comparison = request.includeComparison
    include_distribution = request.includeDistribution
    include_trend = request.includeTrend

    # Call service
    result = await service.get_log_count(
        auth_code=x_auth_code,
        base_url=x_base_url,
        start_timestamp=start_timestamp,
        end_timestamp=end_timestamp,
        product_types=product_types,
        access_directions=access_directions,
        threat_classes=threat_classes,
        src_ips=src_ips,
        dst_ips=dst_ips,
        attack_states=attack_states,
        severities=severities,
        include_comparison=include_comparison,
        include_distribution=include_distribution,
        include_trend=include_trend
    )

    # Return response
    if result.get("success"):
        return LogCountResponse(
            success=True,
            message=result.get("message", "查询成功"),
            data=result.get("data")
        )
    else:
        # Return error response
        error_message = result.get("message", "查询失败")
        error_type = result.get("error_type", "unknown_error")

        # Map error types to appropriate HTTP status codes
        if error_type == "auth_error":
            raise HTTPException(status_code=401, detail=error_message)
        elif error_type == "connection_error":
            raise HTTPException(status_code=503, detail=error_message)
        elif error_type == "timeout_error":
            raise HTTPException(status_code=504, detail=error_message)
        else:
            raise HTTPException(status_code=500, detail=error_message)
