"""
Dashboard API Endpoints
Provides statistics and monitoring data for the AI Security Operations Cockpit
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from ....services.dashboard_service import DashboardService


router = APIRouter()


class StatisticsResponse(BaseModel):
    """Response model for dashboard statistics"""
    success: bool
    data: dict
    message: Optional[str] = None


class MonitoringResponse(BaseModel):
    """Response model for monitoring data"""
    success: bool
    data: dict
    message: Optional[str] = None


@router.get("/statistics", response_model=StatisticsResponse)
async def get_dashboard_statistics(
    time_range: str = "week",
    x_auth_code: str = Header(None, alias="x-auth-code"),
    x_base_url: str = Header(None, alias="x-base-url")
):
    """
    Get dashboard statistics

    Args:
        time_range: Time range for statistics ('week' | 'month')
        x_auth_code: Flux authentication code
        x_base_url: Flux API base URL

    Returns:
        Statistics data including:
        - weeklyHandled: Number of incidents handled this week
        - monthlyHandled: Number of incidents handled this month
        - blockedIPs: Total number of blocked IPs
        - pendingIncidents: Number of pending incidents
        - successRate: Success rate percentage
        - trend: Trend data over time
        - distribution: Distribution by severity and type
    """
    try:
        if not x_auth_code or not x_base_url:
            raise HTTPException(
                status_code=400,
                detail="Missing authentication headers: x-auth-code and x-base-url are required"
            )

        # Validate time_range parameter
        if time_range not in ["week", "month"]:
            time_range = "week"

        # Create service instance and fetch statistics
        dashboard_service = DashboardService()
        statistics = await dashboard_service.get_statistics(
            auth_code=x_auth_code,
            base_url=x_base_url,
            time_range=time_range
        )

        return StatisticsResponse(
            success=True,
            data=statistics,
            message="Statistics retrieved successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve statistics: {str(e)}"
        )


@router.get("/monitoring", response_model=MonitoringResponse)
async def get_monitoring_status(
    x_auth_code: str = Header(None, alias="x-auth-code"),
    x_base_url: str = Header(None, alias="x-base-url")
):
    """
    Get real-time monitoring data

    Args:
        x_auth_code: Flux authentication code
        x_base_url: Flux API base URL

    Returns:
        Monitoring data including:
        - systemStatus: System status ('online' | 'warning' | 'offline')
        - activeAlerts: Number of active alerts
        - lastUpdate: Last update timestamp
        - recentIncidents: List of recent high-severity incidents
        - performanceMetrics: Performance metrics (latency, success rate, error rate)
    """
    try:
        if not x_auth_code or not x_base_url:
            raise HTTPException(
                status_code=400,
                detail="Missing authentication headers: x-auth-code and x-base-url are required"
            )

        # Create service instance and fetch monitoring data
        dashboard_service = DashboardService()
        monitoring = await dashboard_service.get_monitoring(
            auth_code=x_auth_code,
            base_url=x_base_url
        )

        return MonitoringResponse(
            success=True,
            data=monitoring,
            message="Monitoring data retrieved successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve monitoring data: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for the dashboard service"""
    return {
        "status": "healthy",
        "service": "dashboard",
        "version": "1.0.0"
    }
