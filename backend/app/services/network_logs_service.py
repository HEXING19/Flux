import time
import json
import requests
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from ..utils.sdk.aksk_py3 import Signature


class NetworkLogsService:
    """Service for querying network security logs via Flux XDR API"""

    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False  # Ignore SSL certificate warnings

    async def get_log_count(
        self,
        auth_code: str,
        base_url: str,
        start_timestamp: int = None,
        end_timestamp: int = None,
        product_types: List[str] = None,
        access_directions: List[int] = None,
        threat_classes: List[str] = None,
        src_ips: List[str] = None,
        dst_ips: List[str] = None,
        attack_states: List[int] = None,
        severities: List[int] = None,
        include_comparison: bool = False,
        include_distribution: bool = False,
        include_trend: bool = False
    ) -> dict:
        """
        Query network security log count from Flux API

        Args:
            auth_code: Flux authentication code
            base_url: Flux API base URL
            start_timestamp: Start timestamp (default: 7 days ago)
            end_timestamp: End timestamp (default: now)
            product_types: Product type filter ["STA", "EDR", "AC", etc.]
            access_directions: Access direction filter [1:外对内, 2:内对外, 3:内对内]
            threat_classes: Threat class filter (一级分类, e.g., ["94", "214"])
            src_ips: Source IP filter
            dst_ips: Destination IP filter
            attack_states: Attack state filter [0:尝试, 1:失败, 2:成功, 3:失陷]
            severities: Severity filter [0:信息, 1:低危, 2:中危, 3:高危, 4:严重]
            include_comparison: Include comparison data (上周、上月)
            include_distribution: Include distribution data (严重程度、访问方向、产品类型)
            include_trend: Include trend data (按天统计)

        Returns:
            Dictionary with query results:
            {
                "success": True/False,
                "message": str,
                "data": {
                    "total": int,
                    "start_time": int,
                    "end_time": int,
                    "filters": dict,
                    "comparisons": dict (optional),
                    "distributions": dict (optional),
                    "trend": list (optional),
                    "anomalies": list (optional)
                },
                "error_type": str (optional)
            }
        """
        try:
            # Default time range: last 7 days
            if not start_timestamp:
                start_timestamp = int((datetime.now() - timedelta(days=7)).timestamp())
            if not end_timestamp:
                end_timestamp = int(datetime.now().timestamp())

            # Build request parameters
            params = {}
            if start_timestamp:
                params['startTimestamp'] = start_timestamp
            if end_timestamp:
                params['endTimestamp'] = end_timestamp
            if product_types:
                params['productTypes'] = product_types
            if access_directions:
                params['accessDirections'] = access_directions
            if threat_classes:
                params['threatClasses'] = threat_classes
            if src_ips:
                params['srcIps'] = src_ips
            if dst_ips:
                params['dstIps'] = dst_ips
            if attack_states:
                params['attackStates'] = attack_states
            if severities:
                params['severities'] = severities

            # Call Flux API
            api_endpoint = f"{base_url.rstrip('/')}/api/xdr/v1/analysislog/networksecurity/count"

            # Create signature
            signature = Signature(auth_code=auth_code)
            headers = {"content-type": "application/json"}
            req = requests.Request(
                "POST",
                api_endpoint,
                headers=headers,
                data=json.dumps(params)
            )
            signature.signature(req)

            # Send request
            start_time = time.time()
            response = self.session.send(req.prepare())
            end_time = time.time()
            latency_ms = round((end_time - start_time) * 1000, 2)

            # Check response
            if response.status_code != 200:
                return {
                    "success": False,
                    "message": f"API请求失败: HTTP {response.status_code}",
                    "error_type": "api_error"
                }

            data = response.json()

            if data.get("code") != "Success":
                return {
                    "success": False,
                    "message": data.get("message", "未知错误"),
                    "error_type": "api_error"
                }

            # Extract total count
            total = data.get("data", {}).get("total", 0)

            # Build result
            result = {
                "success": True,
                "message": "查询成功",
                "data": {
                    "total": total,
                    "start_time": start_timestamp,
                    "end_time": end_timestamp,
                    "filters": params,
                    "latency_ms": latency_ms
                }
            }

            # Optional: Get comparison data
            if include_comparison:
                result["data"]["comparisons"] = await self._get_comparison(
                    auth_code, base_url, start_timestamp, end_timestamp, params
                )

            # Optional: Get distribution data
            if include_distribution:
                result["data"]["distributions"] = await self._get_distribution(
                    auth_code, base_url, params
                )

            # Optional: Get trend data
            if include_trend:
                result["data"]["trend"] = await self._get_trend(
                    auth_code, base_url, start_timestamp, end_timestamp, params
                )

            # Optional: Detect anomalies
            if include_comparison or include_trend:
                anomalies = self._detect_anomalies(
                    total,
                    result["data"].get("comparisons", {}),
                    result["data"].get("trend", [])
                )
                if anomalies:
                    result["data"]["anomalies"] = anomalies

            return result

        except Exception as e:
            error_msg = str(e)
            # Check for specific error types
            if "auth code" in error_msg.lower() or "联动码" in error_msg:
                return {
                    "success": False,
                    "message": "认证码错误，请检查联动码是否正确",
                    "error_type": "auth_error"
                }
            elif "connection" in error_msg.lower():
                return {
                    "success": False,
                    "message": f"连接失败: {error_msg}",
                    "error_type": "connection_error"
                }
            elif "timeout" in error_msg.lower():
                return {
                    "success": False,
                    "message": "请求超时，请稍后重试",
                    "error_type": "timeout_error"
                }
            else:
                return {
                    "success": False,
                    "message": f"查询失败: {error_msg}",
                    "error_type": "unknown_error"
                }

    async def _get_comparison(
        self,
        auth_code: str,
        base_url: str,
        start_ts: int,
        end_ts: int,
        params: dict
    ) -> dict:
        """
        Get comparison data (上周、上月)

        Args:
            auth_code: Authentication code
            base_url: API base URL
            start_ts: Current start timestamp
            end_ts: Current end timestamp
            params: Original query parameters

        Returns:
            Dictionary with comparison data
        """
        comparisons = {}
        current_count = 0  # Will be populated by caller

        # Calculate time differences
        week_diff = 7 * 24 * 60 * 60
        month_diff = 30 * 24 * 60 * 60

        # Get last week data
        last_week_params = params.copy()
        last_week_params['startTimestamp'] = start_ts - week_diff
        last_week_params['endTimestamp'] = end_ts - week_diff

        last_week_count = await self._fetch_count(
            auth_code, base_url, last_week_params
        )

        if last_week_count is not None:
            week_change = 0
            if last_week_count > 0 and current_count > 0:
                week_change = ((current_count - last_week_count) / last_week_count) * 100

            comparisons['last_week'] = {
                'count': last_week_count,
                'change_percent': week_change
            }

        # Get last month data
        last_month_params = params.copy()
        last_month_params['startTimestamp'] = start_ts - month_diff
        last_month_params['endTimestamp'] = end_ts - month_diff

        last_month_count = await self._fetch_count(
            auth_code, base_url, last_month_params
        )

        if last_month_count is not None:
            month_change = 0
            if last_month_count > 0 and current_count > 0:
                month_change = ((current_count - last_month_count) / last_month_count) * 100

            comparisons['last_month'] = {
                'count': last_month_count,
                'change_percent': month_change
            }

        return comparisons

    async def _get_distribution(
        self,
        auth_code: str,
        base_url: str,
        params: dict
    ) -> dict:
        """
        Get distribution data (按严重程度、访问方向、产品类型)

        Args:
            auth_code: Authentication code
            base_url: API base URL
            params: Original query parameters

        Returns:
            Dictionary with distribution data
        """
        distributions = {}

        # Distribution by severity
        severity_dist = {}
        severity_names = {0: '信息', 1: '低危', 2: '中危', 3: '高危', 4: '严重'}

        for severity in [0, 1, 2, 3, 4]:
            severity_params = params.copy()
            severity_params['severities'] = [severity]
            count = await self._fetch_count(auth_code, base_url, severity_params)
            if count is not None:
                severity_dist[severity_names[severity]] = count

        if severity_dist:
            distributions['severity'] = severity_dist

        # Distribution by access direction
        direction_dist = {}
        direction_names = {1: '外对内', 2: '内对外', 3: '内对内'}

        for direction in [1, 2, 3]:
            direction_params = params.copy()
            direction_params['accessDirections'] = [direction]
            count = await self._fetch_count(auth_code, base_url, direction_params)
            if count is not None:
                direction_dist[direction_names[direction]] = count

        if direction_dist:
            distributions['access_direction'] = direction_dist

        # Distribution by product type
        product_dist = {}
        product_names = {
            "STA": "WAF",
            "EDR": "EDR",
            "AC": "防火墙",
            "CWPP": "云安全",
            "NTA": "流量分析"
        }

        for product in ["STA", "EDR", "AC", "CWPP", "NTA"]:
            product_params = params.copy()
            product_params['productTypes'] = [product]
            count = await self._fetch_count(auth_code, base_url, product_params)
            if count is not None:
                product_dist[product_names[product]] = count

        if product_dist:
            distributions['product_type'] = product_dist

        return distributions

    async def _get_trend(
        self,
        auth_code: str,
        base_url: str,
        start_ts: int,
        end_ts: int,
        params: dict
    ) -> list:
        """
        Get trend data (按天统计)

        Args:
            auth_code: Authentication code
            base_url: API base URL
            start_ts: Start timestamp
            end_ts: End timestamp
            params: Original query parameters

        Returns:
            List of daily data points
        """
        trend = []
        current = start_ts
        day_seconds = 24 * 60 * 60

        while current < end_ts:
            day_end = min(current + day_seconds, end_ts)
            day_params = params.copy()
            day_params['startTimestamp'] = current
            day_params['endTimestamp'] = day_end

            count = await self._fetch_count(auth_code, base_url, day_params)
            if count is not None:
                trend.append({
                    'date': datetime.fromtimestamp(current).strftime('%Y-%m-%d'),
                    'count': count
                })

            current = day_end

        return trend

    def _detect_anomalies(
        self,
        current_count: int,
        comparisons: dict,
        trend: list
    ) -> list:
        """
        Detect anomalies in log data

        Args:
            current_count: Current log count
            comparisons: Comparison data
            trend: Trend data

        Returns:
            List of anomaly alerts
        """
        anomalies = []

        # Check for significant week-over-week change
        if 'last_week' in comparisons:
            week_change = comparisons['last_week'].get('change_percent', 0)
            if abs(week_change) > 20:
                anomaly_type = 'warning' if week_change > 0 else 'info'
                direction = "增长" if week_change > 0 else "下降"
                anomalies.append({
                    'type': anomaly_type,
                    'message': f'日志量环比{direction} {abs(week_change):.1f}%'
                })

        # Check for daily spikes
        if len(trend) > 1:
            avg_count = sum(day['count'] for day in trend) / len(trend)
            for day in trend:
                if day['count'] > avg_count * 1.5:
                    increase_percent = ((day['count'] - avg_count) / avg_count) * 100
                    anomalies.append({
                        'type': 'warning',
                        'message': f'{day["date"]} 日志量突增 (+{increase_percent:.1f}%)'
                    })

        return anomalies

    async def _fetch_count(
        self,
        auth_code: str,
        base_url: str,
        params: dict
    ) -> Optional[int]:
        """
        Helper method to fetch a single count

        Args:
            auth_code: Authentication code
            base_url: API base URL
            params: Query parameters

        Returns:
            Count value or None if failed
        """
        try:
            api_endpoint = f"{base_url.rstrip('/')}/api/xdr/v1/analysislog/networksecurity/count"

            signature = Signature(auth_code=auth_code)
            headers = {"content-type": "application/json"}
            req = requests.Request(
                "POST",
                api_endpoint,
                headers=headers,
                data=json.dumps(params)
            )
            signature.signature(req)

            response = self.session.send(req.prepare())

            if response.status_code == 200:
                data = response.json()
                if data.get("code") == "Success":
                    return data.get("data", {}).get("total", 0)

            return None

        except Exception:
            return None
