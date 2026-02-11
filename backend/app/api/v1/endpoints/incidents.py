"""
Security Incidents API Endpoints
Provides REST API for querying and managing security incidents in Flux XDR
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field, validator
from ....services.security_incidents_service import SecurityIncidentsService


router = APIRouter()


class IncidentListRequest(BaseModel):
    """Request model for querying incidents"""
    startTimestamp: Optional[int] = Field(None, description="Start timestamp")
    endTimestamp: Optional[int] = Field(None, description="End timestamp")
    timeField: Optional[str] = Field("endTime", description="Time field to filter on")
    severities: Optional[List[int]] = Field(None, description="Severity levels [1-4]")
    dealStatus: Optional[List[int]] = Field(None, description="Disposition status list")
    pageSize: Optional[int] = Field(20, ge=5, le=200, description="Results per page")
    page: Optional[int] = Field(1, ge=1, description="Page number")
    sort: Optional[str] = Field("endTime:desc,severity:desc", description="Sort order")

    # Additional filters
    uuIds: Optional[List[str]] = Field(None, description="Specific incident IDs")
    hostBranchId: Optional[List[int]] = Field(None, description="Asset group IDs")
    whiteStatus: Optional[List[str]] = Field(None, description="Whitelist status")
    threatDefines: Optional[List[int]] = Field(None, description="Threat classification")
    incidentSources: Optional[List[str]] = Field(None, description="Incident sources")
    gptResults: Optional[List[int]] = Field(None, description="AI conclusions")
    dataSources: Optional[List[str]] = Field(None, description="Data sources")

    @validator('timeField')
    def validate_time_field(cls, v):
        # Allow None - will use default value "endTime"
        if v is None:
            return v

        valid_fields = ["endTime", "startTime", "auditTime", "updateTime", "uploadTime",
                       "occurTime", "insertTime"]
        if v not in valid_fields:
            raise ValueError(f"Invalid timeField. Must be one of: {', '.join(valid_fields)}")
        return v

    @validator('severities')
    def validate_severities(cls, v):
        if v is not None:
            for severity in v:
                if severity not in [0, 1, 2, 3, 4]:
                    raise ValueError(f"Invalid severity: {severity}. Must be 0-4")
        return v

    @validator('dealStatus')
    def validate_deal_status(cls, v):
        if v is not None:
            for status in v:
                if status not in [0, 10, 30, 40, 50, 60, 70]:
                    raise ValueError(f"Invalid dealStatus: {status}. Must be one of: 0, 10, 30, 40, 50, 60, 70")
        return v


class IncidentListResponse(BaseModel):
    """Response model for incident list"""
    success: bool
    message: str
    data: Optional[dict] = None


class IncidentProofResponse(BaseModel):
    """Response model for incident proof"""
    success: bool
    message: str
    data: Optional[dict] = None


class IncidentUpdateRequest(BaseModel):
    """Request model for updating incident status"""
    uuIds: List[str] = Field(..., min_items=1, max_items=200, description="Incident ID list")
    dealStatus: int = Field(..., description="Disposition status [0, 10, 30, 40, 50, 60, 70]")
    dealComment: Optional[str] = Field(None, max_length=2048, description="Operation remarks")

    @validator('uuIds', each_item=True)
    def validate_uuids(cls, v):
        import re
        # Basic UUID format validation
        pattern = r'^incident-[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$'
        if not re.match(pattern, v, re.IGNORECASE):
            raise ValueError(f"Invalid incident ID format: {v}")
        return v

    @validator('dealStatus')
    def validate_deal_status(cls, v):
        valid_statuses = [0, 10, 30, 40, 50, 60, 70]
        if v not in valid_statuses:
            raise ValueError(f"Invalid dealStatus. Must be one of: {valid_statuses}")
        return v


class IncidentUpdateResponse(BaseModel):
    """Response model for incident update"""
    success: bool
    message: str
    data: Optional[dict] = None


class IncidentEntitiesResponse(BaseModel):
    """Response model for incident IP entities"""
    success: bool
    message: str
    data: Optional[dict] = None


@router.post("/list", response_model=IncidentListResponse)
async def list_incidents(
    request: IncidentListRequest,
    x_auth_code: Optional[str] = Header(None, alias="X-Auth-Code"),
    x_base_url: Optional[str] = Header(None, alias="X-Base-Url")
):
    """
    Query security incidents with filters

    Args:
        request: Incident list request with filters
        x_auth_code: Flux authentication code (from header)
        x_base_url: Flux API base URL (from header)

    Returns:
        Incident list data
    """
    if not x_auth_code:
        raise HTTPException(status_code=400, detail="X-Auth-Code header is required")

    if not x_base_url:
        raise HTTPException(status_code=400, detail="X-Base-Url header is required")

    # Create service instance
    service = SecurityIncidentsService()

    # Convert request to dict and extract additional filters
    request_dict = request.dict(exclude_unset=True, exclude={
        'startTimestamp', 'endTimestamp', 'timeField',
        'severities', 'dealStatus', 'pageSize', 'page', 'sort'
    })

    # Extract main parameters
    start_timestamp = request.startTimestamp
    end_timestamp = request.endTimestamp
    time_field = request.timeField
    severities = request.severities
    deal_status = request.dealStatus
    page_size = request.pageSize
    page = request.page
    sort = request.sort

    # Query incidents
    result = await service.get_incidents(
        auth_code=x_auth_code,
        base_url=x_base_url,
        start_timestamp=start_timestamp,
        end_timestamp=end_timestamp,
        time_field=time_field,
        severities=severities,
        deal_status=deal_status,
        page_size=page_size,
        page=page,
        sort=sort,
        **request_dict
    )

    return IncidentListResponse(**result)


@router.get("/{uuid}/proof", response_model=IncidentProofResponse)
async def get_incident_proof(
    uuid: str,
    x_auth_code: Optional[str] = Header(None, alias="X-Auth-Code"),
    x_base_url: Optional[str] = Header(None, alias="X-Base-Url")
):
    """
    Get incident evidence by uuId

    Args:
        uuid: Incident uuId
        x_auth_code: Flux authentication code (from header)
        x_base_url: Flux API base URL (from header)

    Returns:
        Incident proof data with timeline and evidence
    """
    if not x_auth_code:
        raise HTTPException(status_code=400, detail="X-Auth-Code header is required")

    if not x_base_url:
        raise HTTPException(status_code=400, detail="X-Base-Url header is required")

    # Create service instance
    service = SecurityIncidentsService()

    # Get incident proof
    result = await service.get_incident_proof(
        auth_code=x_auth_code,
        base_url=x_base_url,
        uuid=uuid
    )

    return IncidentProofResponse(**result)


@router.post("/update-status", response_model=IncidentUpdateResponse)
async def update_incident_status(
    request: IncidentUpdateRequest,
    x_auth_code: Optional[str] = Header(None, alias="X-Auth-Code"),
    x_base_url: Optional[str] = Header(None, alias="X-Base-Url")
):
    """
    Batch update incident disposition status

    Args:
        request: Incident update request
        x_auth_code: Flux authentication code (from header)
        x_base_url: Flux API base URL (from header)

    Returns:
        Update result with success/failure statistics
    """
    if not x_auth_code:
        raise HTTPException(status_code=400, detail="X-Auth-Code header is required")

    if not x_base_url:
        raise HTTPException(status_code=400, detail="X-Base-Url header is required")

    # Create service instance
    service = SecurityIncidentsService()

    # Convert request to dict
    update_data = request.dict(exclude_unset=True)

    # Extract parameters
    uuids = update_data.get('uuIds', [])
    deal_status = update_data.get('dealStatus')
    deal_comment = update_data.get('dealComment')

    # Update incident status
    result = await service.update_incident_status(
        auth_code=x_auth_code,
        base_url=x_base_url,
        uuids=uuids,
        deal_status=deal_status,
        deal_comment=deal_comment
    )

    return IncidentUpdateResponse(**result)


@router.get("/{uuid}/entities/ip", response_model=IncidentEntitiesResponse)
async def get_incident_entities_ip(
    uuid: str,
    x_auth_code: Optional[str] = Header(None, alias="X-Auth-Code"),
    x_base_url: Optional[str] = Header(None, alias="X-Base-Url")
):
    """
    Get incident IP entities by uuId

    Args:
        uuid: Incident uuId
        x_auth_code: Flux authentication code (from header)
        x_base_url: Flux API base URL (from header)

    Returns:
        IP entities data with threat intelligence and disposition status
    """
    if not x_auth_code:
        raise HTTPException(status_code=400, detail="X-Auth-Code header is required")

    if not x_base_url:
        raise HTTPException(status_code=400, detail="X-Base-Url header is required")

    # Create service instance
    service = SecurityIncidentsService()

    # Get incident IP entities
    result = await service.get_incident_entities_ip(
        auth_code=x_auth_code,
        base_url=x_base_url,
        uuid=uuid
    )

    return IncidentEntitiesResponse(**result)
