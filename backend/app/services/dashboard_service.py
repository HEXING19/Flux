"""
Dashboard Service
Aggregates data from multiple services for the AI Security Operations Cockpit
"""

import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from .security_incidents_service import SecurityIncidentsService
from .ipblock_service import IpBlockService


class DashboardService:
    """Dashboard data aggregation service for cockpit statistics and monitoring"""

    def __init__(self):
        # Services will be initialized per-request with auth_code and base_url
        pass

    async def get_statistics(
        self,
        auth_code: str,
        base_url: str,
        time_range: str = "week"
    ) -> Dict[str, Any]:
        """
        Get dashboard statistics including handled incidents, blocked IPs, etc.

        Args:
            auth_code: Flux authentication code
            base_url: Flux API base URL
            time_range: Time range for statistics ('week' | 'month')

        Returns:
            Dictionary with statistics data
        """
        try:
            # Determine date range based on time_range
            if time_range == "week":
                days = 7
            elif time_range == "month":
                days = 30
            else:
                days = 7  # Default to week

            # Calculate timestamps
            end_timestamp = int(datetime.now().timestamp())
            week_start_timestamp = int((datetime.now() - timedelta(days=7)).timestamp())
            month_start_timestamp = int((datetime.now() - timedelta(days=30)).timestamp())

            # Fetch incidents data in parallel
            weekly_incidents_task = self._fetch_incidents_count(
                auth_code=auth_code,
                base_url=base_url,
                start_timestamp=week_start_timestamp,
                end_timestamp=end_timestamp
            )

            monthly_incidents_task = self._fetch_incidents_count(
                auth_code=auth_code,
                base_url=base_url,
                start_timestamp=month_start_timestamp,
                end_timestamp=end_timestamp
            )

            pending_incidents_task = self._fetch_pending_incidents_count(
                auth_code=auth_code,
                base_url=base_url
            )

            # Fetch IP block statistics
            blocked_ips_task = self._fetch_blocked_ips_count(
                auth_code=auth_code,
                base_url=base_url,
                start_timestamp=month_start_timestamp
            )

            # Execute all tasks in parallel
            weekly_incidents, monthly_incidents, pending_incidents, blocked_ips = await asyncio.gather(
                weekly_incidents_task,
                monthly_incidents_task,
                pending_incidents_task,
                blocked_ips_task,
                return_exceptions=True
            )

            # Handle exceptions and set default values
            weekly_handled = weekly_incidents if not isinstance(weekly_incidents, Exception) else 0
            monthly_handled = monthly_incidents if not isinstance(monthly_incidents, Exception) else 0
            pending_count = pending_incidents if not isinstance(pending_incidents, Exception) else 0
            blocked_count = blocked_ips if not isinstance(blocked_ips, Exception) else 0

            # Calculate success rate (handled / total)
            total_incidents = weekly_handled + pending_count
            success_rate = round((weekly_handled / total_incidents * 100), 1) if total_incidents > 0 else 100.0

            # Generate trend data (mock data for now, can be enhanced with real historical data)
            trend = self._generate_trend_data(days=days)

            return {
                "weeklyHandled": weekly_handled,
                "monthlyHandled": monthly_handled,
                "blockedIPs": blocked_count,
                "pendingIncidents": pending_count,
                "successRate": success_rate,
                "trend": trend,
                "distribution": self._get_distribution_data(auth_code, base_url)
            }

        except Exception as e:
            print(f"Error in get_statistics: {str(e)}")
            # Return default values on error
            return {
                "weeklyHandled": 0,
                "monthlyHandled": 0,
                "blockedIPs": 0,
                "pendingIncidents": 0,
                "successRate": 100.0,
                "trend": [],
                "distribution": {}
            }

    async def get_monitoring(
        self,
        auth_code: str,
        base_url: str
    ) -> Dict[str, Any]:
        """
        Get real-time monitoring data including system status and alerts

        Args:
            auth_code: Flux authentication code
            base_url: Flux API base URL

        Returns:
            Dictionary with monitoring data
        """
        try:
            # Get pending high-severity incidents for alerts
            recent_incidents = await self._fetch_recent_high_severity_incidents(
                auth_code=auth_code,
                base_url=base_url,
                limit=10
            )

            # Count active alerts (high and critical severity incidents)
            active_alerts = len([inc for inc in recent_incidents if inc.get("severity", 0) >= 3])

            # Determine system status based on alerts
            if active_alerts == 0:
                system_status = "online"
            elif active_alerts < 5:
                system_status = "warning"
            else:
                system_status = "offline"  # High alert state

            # Measure API latency
            start_time = time.time()
            await self._test_api_latency(auth_code, base_url)
            api_latency = round((time.time() - start_time) * 1000, 2)

            # Calculate performance metrics
            success_rate = max(95.0, 100.0 - (active_alerts * 0.5))  # Mock calculation
            error_rate = 100.0 - success_rate

            return {
                "systemStatus": system_status,
                "activeAlerts": active_alerts,
                "lastUpdate": int(datetime.now().timestamp()),
                "recentIncidents": recent_incidents[:5],  # Last 5 incidents
                "performanceMetrics": {
                    "apiLatency": api_latency,
                    "successRate": round(success_rate, 1),
                    "errorRate": round(error_rate, 1)
                }
            }

        except Exception as e:
            print(f"Error in get_monitoring: {str(e)}")
            # Return default values on error
            return {
                "systemStatus": "offline",
                "activeAlerts": 0,
                "lastUpdate": int(datetime.now().timestamp()),
                "recentIncidents": [],
                "performanceMetrics": {
                    "apiLatency": 0,
                    "successRate": 0.0,
                    "errorRate": 0.0
                }
            }

    async def _fetch_incidents_count(
        self,
        auth_code: str,
        base_url: str,
        start_timestamp: int,
        end_timestamp: int
    ) -> int:
        """Fetch count of incidents in the given time range"""
        try:
            incidents_service = SecurityIncidentsService()
            result = await incidents_service.get_incidents(
                auth_code=auth_code,
                base_url=base_url,
                start_timestamp=start_timestamp,
                end_timestamp=end_timestamp,
                page_size=1,  # We only need the count
                page=1
            )
            return result.get("total", 0)
        except Exception as e:
            print(f"Error fetching incidents count: {str(e)}")
            return 0

    async def _fetch_pending_incidents_count(
        self,
        auth_code: str,
        base_url: str
    ) -> int:
        """Fetch count of pending (not handled) incidents"""
        try:
            incidents_service = SecurityIncidentsService()
            # Get today's incidents with severity >= 3 and dealStatus = 0
            end_timestamp = int(datetime.now().timestamp())
            start_timestamp = int((datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)).timestamp())

            result = await incidents_service.get_incidents(
                auth_code=auth_code,
                base_url=base_url,
                start_timestamp=start_timestamp,
                end_timestamp=end_timestamp,
                min_severity=3,
                deal_status=0,  # Not handled
                page_size=100,
                page=1
            )
            return result.get("total", 0)
        except Exception as e:
            print(f"Error fetching pending incidents: {str(e)}")
            return 0

    async def _fetch_blocked_ips_count(
        self,
        auth_code: str,
        base_url: str,
        start_timestamp: int
    ) -> int:
        """Fetch count of blocked IPs in the given time range"""
        try:
            ipblock_service = IpBlockService(base_url=base_url, auth_code=auth_code)
            # Query IP block rules created after start_timestamp
            result = await ipblock_service.search_rules(
                page_size=100,
                page=1
            )
            # Filter by creation time (if available in the response)
            rules = result.get("data", {}).get("item", [])
            # For now, return total count (can be enhanced with date filtering)
            return len(rules)
        except Exception as e:
            print(f"Error fetching blocked IPs: {str(e)}")
            return 0

    async def _fetch_recent_high_severity_incidents(
        self,
        auth_code: str,
        base_url: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Fetch recent high-severity incidents"""
        try:
            incidents_service = SecurityIncidentsService()
            end_timestamp = int(datetime.now().timestamp())
            start_timestamp = int((datetime.now() - timedelta(hours=24)).timestamp())

            result = await incidents_service.get_incidents(
                auth_code=auth_code,
                base_url=base_url,
                start_timestamp=start_timestamp,
                end_timestamp=end_timestamp,
                min_severity=2,  # Medium and above
                page_size=limit,
                page=1
            )

            incidents = result.get("incidents", [])
            return [
                {
                    "id": inc.get("uuId", ""),
                    "severity": inc.get("severity", 0),
                    "message": inc.get("name", "Unknown"),
                    "timestamp": inc.get("endTime", 0)
                }
                for inc in incidents
            ]
        except Exception as e:
            print(f"Error fetching recent incidents: {str(e)}")
            return []

    async def _test_api_latency(
        self,
        auth_code: str,
        base_url: str
    ) -> bool:
        """Test API latency by making a quick call"""
        try:
            incidents_service = SecurityIncidentsService()
            await incidents_service.test_connectivity(
                auth_code=auth_code,
                base_url=base_url
            )
            return True
        except Exception:
            return False

    def _generate_trend_data(self, days: int = 7) -> List[Dict[str, Any]]:
        """Generate mock trend data (can be replaced with real historical data)"""
        trend = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=days - i - 1)).strftime("%Y-%m-%d")
            # Mock data with some variation
            count = max(5, 20 - abs(i - days // 2) * 2 + (i % 3))
            trend.append({
                "date": date,
                "count": count
            })
        return trend

    def _get_distribution_data(
        self,
        auth_code: str,
        base_url: str
    ) -> Dict[str, Any]:
        """Get distribution data for incidents (severity and type)"""
        # This is a simplified version - can be enhanced with real data
        return {
            "severity": {
                "严重": 2,
                "高危": 8,
                "中危": 15,
                "低危": 25
            },
            "type": {
                "恶意文件": 5,
                "网络攻击": 12,
                "异常行为": 8,
                "其他": 25
            }
        }
