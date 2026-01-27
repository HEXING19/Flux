"""
Asset Management API Endpoints
Provides REST API for creating and managing assets in Flux XDR
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field, validator
from ....services.asset_service import AssetService


router = APIRouter()


class AssetCreateRequest(BaseModel):
    """Request model for creating an asset"""
    ip: str = Field(..., description="IP address of the asset")
    branchId: int = Field(..., description="Asset group ID")
    mac: Optional[str] = Field(None, description="MAC address")
    assetName: Optional[str] = Field(None, max_length=95, description="Asset name")
    hostName: Optional[str] = Field(None, max_length=95, description="Hostname")
    type: Optional[str] = Field("Unknown", description="OS type")
    magnitude: Optional[str] = Field("normal", description="Importance level")
    tags: Optional[List[str]] = Field([], description="Asset tags")
    classify1Id: Optional[int] = Field(0, description="Primary category ID")
    classifyId: Optional[int] = Field(100000, description="Detailed category ID")
    comment: Optional[str] = Field(None, max_length=95, description="Remarks")
    users: Optional[List[dict]] = Field([], description="Responsible persons")

    @validator('ip')
    def validate_ip(cls, v):
        import ipaddress
        try:
            ipaddress.ip_address(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid IP address format: {v}")

    @validator('mac')
    def validate_mac(cls, v):
        if v is None:
            return v
        import re
        mac_pattern = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
        if not mac_pattern.match(v):
            raise ValueError(f"Invalid MAC address format: {v}")
        return v

    @validator('tags')
    def validate_tags(cls, v):
        if len(v) > 10:
            raise ValueError("Maximum 10 tags allowed")
        for tag in v:
            if len(tag) > 20:
                raise ValueError(f"Tag '{tag}' exceeds 20 character limit")
        return v

    @validator('type')
    def validate_type(cls, v):
        valid_types = [
            "Unknown", "Windows", "Linux", "OS X", "iOS", "airOS",
            "Android", "FreeBSD", "VMware", "Cisco", "MikroTik",
            "VxWorks", "F5 Networks", "Unix", "Mac", "Other"
        ]
        if v not in valid_types:
            raise ValueError(f"Invalid OS type. Must be one of: {', '.join(valid_types)}")
        return v

    @validator('magnitude')
    def validate_magnitude(cls, v):
        if v not in ["normal", "core"]:
            raise ValueError("Magnitude must be either 'normal' or 'core'")
        return v


class AssetCreateResponse(BaseModel):
    """Response model for asset creation"""
    success: bool
    message: str
    data: Optional[dict] = None


class AssetInferRequest(BaseModel):
    """Request model for inferring asset parameters from natural language"""
    text: str = Field(..., description="Natural language description")
    provided_params: Optional[dict] = Field({}, description="Already extracted parameters")


class AssetInferResponse(BaseModel):
    """Response model for parameter inference"""
    success: bool
    message: str
    parameters: dict


@router.post("/create", response_model=AssetCreateResponse)
async def create_asset(
    request: AssetCreateRequest,
    x_auth_code: Optional[str] = Header(None, alias="X-Auth-Code"),
    x_base_url: Optional[str] = Header(None, alias="X-Base-Url")
):
    """
    Create a new asset in the Flux XDR system

    Args:
        request: Asset creation request
        x_auth_code: Flux authentication code (from header)
        x_base_url: Flux API base URL (from header)

    Returns:
        Asset creation result
    """
    if not x_auth_code:
        raise HTTPException(status_code=400, detail="X-Auth-Code header is required")

    if not x_base_url:
        raise HTTPException(status_code=400, detail="X-Base-Url header is required")

    # Create asset service instance
    asset_service = AssetService(
        base_url=x_base_url,
        auth_code=x_auth_code
    )

    # Convert request to dict
    asset_data = request.dict(exclude_unset=True)

    # Create asset
    result = asset_service.create_asset(asset_data)

    return AssetCreateResponse(**result)


@router.post("/infer", response_model=AssetInferResponse)
async def infer_asset_parameters(request: AssetInferRequest):
    """
    Infer asset parameters from natural language text

    Args:
        request: Inference request with text and optional parameters

    Returns:
        Inferred parameters
    """
    # Create asset service instance (no auth needed for inference)
    asset_service = AssetService(base_url="https://placeholder")

    # Infer parameters
    inferred_params = asset_service.infer_parameters(
        text=request.text,
        provided_params=request.provided_params
    )

    return AssetInferResponse(
        success=True,
        message="Parameters inferred successfully",
        parameters=inferred_params
    )


@router.get("/categories")
async def get_asset_categories():
    """
    Get available asset categories and their mappings

    Returns:
        Category mappings for classify1Id and classifyId
    """
    asset_service = AssetService(base_url="https://placeholder")

    return {
        "os_types": asset_service.get_os_type_mapping(),
        "categories": asset_service.get_category_mapping(),
        "primary_categories": {
            0: "Unknown",
            1: "Server",
            2: "Terminal",
            5: "Network Device",
            6: "IoT Device",
            7: "Mobile Device",
            8: "Security Product",
            9: "Cloud Platform",
            10: "Enterprise Application"
        }
    }
