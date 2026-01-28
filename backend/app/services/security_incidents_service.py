import time
import json
import requests
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from ..utils.sdk.aksk_py3 import Signature


class SecurityIncidentsService:
    """Service for managing security incidents via Flux XDR API"""

    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False  # Ignore SSL certificate warnings

    async def test_connectivity(
        self,
        auth_code: str,
        base_url: str = None
    ) -> dict:
        """
        Test connectivity by calling security incidents API

        Args:
            auth_code: The authentication code
            base_url: Base URL (default: https://10.5.41.194)

        Returns:
            Dictionary with test results
        """
        # Use default base URL if not provided
        if base_url is None:
            base_url = "https://10.5.41.194"

        base_url = base_url.rstrip('/')
        api_endpoint = f"{base_url}/api/xdr/v1/incidents/list"

        try:
            # Create signature object
            signature = Signature(auth_code=auth_code)

            # Prepare request parameters
            end_timestamp = int(datetime.now().timestamp())
            start_timestamp = int((datetime.now() - timedelta(days=7)).timestamp())

            params = {
                "startTimestamp": start_timestamp,
                "endTimestamp": end_timestamp,
                "timeField": "endTime",
                "pageSize": 5,  # Small page size for quick test
                "page": 1,
                "sort": "endTime:desc,severity:desc"
            }

            # Build request
            headers = {"content-type": "application/json"}
            req = requests.Request(
                "POST",
                api_endpoint,
                headers=headers,
                data=json.dumps(params)
            )

            # Sign the request
            signature.signature(req)

            # Send request and measure latency
            start_time = time.time()
            response = self.session.send(req.prepare())
            end_time = time.time()

            latency_ms = round((end_time - start_time) * 1000, 2)

            # Check response
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == "Success":
                    incident_count = data.get("data", {}).get("total", 0)
                    return {
                        "success": True,
                        "message": "连接成功",
                        "latency_ms": latency_ms,
                        "incident_count": incident_count
                    }
                else:
                    return {
                        "success": False,
                        "message": f"API返回错误: {data.get('message', '未知错误')}",
                        "error_type": "api_error"
                    }
            else:
                return {
                    "success": False,
                    "message": f"HTTP错误: 状态码 {response.status_code}",
                    "error_type": "api_error"
                }

        except Exception as e:
            error_msg = str(e)
            if "auth code" in error_msg.lower() or "联动码" in error_msg:
                return {
                    "success": False,
                    "message": "联动码格式错误或无效",
                    "error_type": "invalid_auth_code"
                }
            elif "connection" in error_msg.lower() or "network" in error_msg.lower():
                return {
                    "success": False,
                    "message": "网络连接失败，请检查目标地址",
                    "error_type": "network_error"
                }
            else:
                return {
                    "success": False,
                    "message": f"连接失败: {error_msg}",
                    "error_type": "unknown"
                }

    async def get_incidents(
        self,
        auth_code: str,
        base_url: str = None,
        start_timestamp: int = None,
        end_timestamp: int = None,
        time_field: str = "endTime",
        severities: List[int] = None,
        deal_status: List[int] = None,
        page_size: int = 20,
        page: int = 1,
        sort: str = "endTime:desc,severity:desc",
        **additional_filters
    ) -> dict:
        """
        Query security incidents with filters

        Args:
            auth_code: The authentication code
            base_url: Base URL (default: https://10.5.41.194)
            start_timestamp: Start timestamp (default: 7 days ago)
            end_timestamp: End timestamp (default: now)
            time_field: Time field to filter on (default: "endTime")
            severities: List of severity levels [1-4]
            deal_status: List of disposition status values
            page_size: Results per page (5-200)
            page: Page number
            sort: Sort order
            **additional_filters: Additional filter parameters

        Returns:
            Dictionary with incidents data
        """
        # Use default base URL if not provided
        if base_url is None:
            base_url = "https://10.5.41.194"

        base_url = base_url.rstrip('/')
        api_endpoint = f"{base_url}/api/xdr/v1/incidents/list"

        try:
            # Create signature object
            signature = Signature(auth_code=auth_code)

            # Calculate default timestamps if not provided
            if end_timestamp is None:
                end_timestamp = int(datetime.now().timestamp())
            if start_timestamp is None:
                start_timestamp = int((datetime.now() - timedelta(days=7)).timestamp())

            # Build request parameters
            params = {
                "startTimestamp": start_timestamp,
                "endTimestamp": end_timestamp,
                "timeField": time_field,
                "pageSize": page_size,
                "page": page,
                "sort": sort
            }

            # Add optional filters
            if severities:
                params["severities"] = severities
            if deal_status:
                params["dealStatus"] = deal_status

            # Add any additional filters
            params.update(additional_filters)

            # Build request
            headers = {"content-type": "application/json"}
            req = requests.Request(
                "POST",
                api_endpoint,
                headers=headers,
                data=json.dumps(params)
            )

            # Sign the request
            signature.signature(req)

            # Send request
            response = self.session.send(req.prepare())

            # Check response
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == "Success":
                    return {
                        "success": True,
                        "message": "查询成功",
                        "data": data.get("data", {})
                    }
                else:
                    return {
                        "success": False,
                        "message": f"API返回错误: {data.get('message', '未知错误')}",
                        "error_type": "api_error"
                    }
            else:
                return {
                    "success": False,
                    "message": f"HTTP错误: 状态码 {response.status_code}",
                    "error_type": "api_error"
                }

        except Exception as e:
            error_msg = str(e)
            if "auth code" in error_msg.lower() or "联动码" in error_msg:
                return {
                    "success": False,
                    "message": "联动码格式错误或无效",
                    "error_type": "invalid_auth_code"
                }
            elif "connection" in error_msg.lower() or "network" in error_msg.lower():
                return {
                    "success": False,
                    "message": "网络连接失败，请检查目标地址",
                    "error_type": "network_error"
                }
            else:
                return {
                    "success": False,
                    "message": f"查询失败: {error_msg}",
                    "error_type": "unknown"
                }

    async def get_incident_proof(
        self,
        auth_code: str,
        base_url: str = None,
        uuid: str = None
    ) -> dict:
        """
        Get incident evidence by uuId

        Args:
            auth_code: The authentication code
            base_url: Base URL (default: https://10.5.41.194)
            uuid: Incident uuId

        Returns:
            Dictionary with incident proof data
        """
        # Use default base URL if not provided
        if base_url is None:
            base_url = "https://10.5.41.194"

        base_url = base_url.rstrip('/')
        api_endpoint = f"{base_url}/api/xdr/v1/incidents/{uuid}/proof"

        try:
            # Create signature object
            signature = Signature(auth_code=auth_code)

            # Build GET request
            headers = {"content-type": "application/json"}
            req = requests.Request(
                "GET",
                api_endpoint,
                headers=headers
            )

            # Sign the request
            signature.signature(req)

            # Send request
            response = self.session.send(req.prepare())

            # Check response
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == "Success":
                    return {
                        "success": True,
                        "message": "获取举证信息成功",
                        "data": data.get("data", {})
                    }
                else:
                    return {
                        "success": False,
                        "message": f"API返回错误: {data.get('message', '未知错误')}",
                        "error_type": "api_error"
                    }
            else:
                return {
                    "success": False,
                    "message": f"HTTP错误: 状态码 {response.status_code}",
                    "error_type": "api_error"
                }

        except Exception as e:
            error_msg = str(e)
            if "auth code" in error_msg.lower() or "联动码" in error_msg:
                return {
                    "success": False,
                    "message": "联动码格式错误或无效",
                    "error_type": "invalid_auth_code"
                }
            elif "connection" in error_msg.lower() or "network" in error_msg.lower():
                return {
                    "success": False,
                    "message": "网络连接失败，请检查目标地址",
                    "error_type": "network_error"
                }
            else:
                return {
                    "success": False,
                    "message": f"获取举证失败: {error_msg}",
                    "error_type": "unknown"
                }

    async def update_incident_status(
        self,
        auth_code: str,
        base_url: str = None,
        uuids: List[str] = None,
        deal_status: int = None,
        deal_comment: str = None
    ) -> dict:
        """
        Batch update incident disposition status

        Args:
            auth_code: The authentication code
            base_url: Base URL (default: https://10.5.41.194)
            uuids: List of incident uuIds (1-200)
            deal_status: Disposition status [0, 10, 40, 50, 60, 70]
            deal_comment: Optional operation remarks

        Returns:
            Dictionary with update results
        """
        # Validate inputs
        if not uuids:
            return {
                "success": False,
                "message": "事件ID列表不能为空",
                "error_type": "validation_error"
            }

        if len(uuids) > 200:
            return {
                "success": False,
                "message": f"事件数量超过限制（最多200个），当前：{len(uuids)}",
                "error_type": "validation_error"
            }

        if deal_status is None:
            return {
                "success": False,
                "message": "处置状态不能为空",
                "error_type": "validation_error"
            }

        # Use default base URL if not provided
        if base_url is None:
            base_url = "https://10.5.41.194"

        base_url = base_url.rstrip('/')
        api_endpoint = f"{base_url}/api/xdr/v1/incidents/dealstatus"

        try:
            # Create signature object
            signature = Signature(auth_code=auth_code)

            # Build request body
            body = {
                "uuIds": uuids,
                "dealStatus": deal_status
            }

            if deal_comment:
                body["dealComment"] = deal_comment

            # Build POST request
            headers = {"content-type": "application/json"}
            req = requests.Request(
                "POST",
                api_endpoint,
                headers=headers,
                data=json.dumps(body)
            )

            # Sign the request
            signature.signature(req)

            # Send request
            response = self.session.send(req.prepare())

            # Check response
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == "Success":
                    result_data = data.get("data", {})
                    return {
                        "success": True,
                        "message": f"批量更新成功",
                        "data": result_data
                    }
                else:
                    return {
                        "success": False,
                        "message": f"API返回错误: {data.get('message', '未知错误')}",
                        "error_type": "api_error"
                    }
            else:
                return {
                    "success": False,
                    "message": f"HTTP错误: 状态码 {response.status_code}",
                    "error_type": "api_error"
                }

        except Exception as e:
            error_msg = str(e)
            if "auth code" in error_msg.lower() or "联动码" in error_msg:
                return {
                    "success": False,
                    "message": "联动码格式错误或无效",
                    "error_type": "invalid_auth_code"
                }
            elif "connection" in error_msg.lower() or "network" in error_msg.lower():
                return {
                    "success": False,
                    "message": "网络连接失败，请检查目标地址",
                    "error_type": "network_error"
                }
            else:
                return {
                    "success": False,
                    "message": f"批量更新失败: {error_msg}",
                    "error_type": "unknown"
                }

    async def get_incident_entities_ip(
        self,
        auth_code: str,
        base_url: str = None,
        uuid: str = None
    ) -> dict:
        """
        Get incident IP entities by uuId

        Args:
            auth_code: The authentication code
            base_url: Base URL (default: https://10.5.41.194)
            uuid: Incident uuId

        Returns:
            Dictionary with IP entities data
        """
        # Validate input
        if not uuid:
            return {
                "success": False,
                "message": "事件ID不能为空",
                "error_type": "validation_error"
            }

        # Use default base URL if not provided
        if base_url is None:
            base_url = "https://10.5.41.194"

        base_url = base_url.rstrip('/')
        api_endpoint = f"{base_url}/api/xdr/v1/incidents/{uuid}/entities/ip"

        try:
            # Create signature object
            signature = Signature(auth_code=auth_code)

            # Build GET request
            headers = {"content-type": "application/json"}
            req = requests.Request(
                "GET",
                api_endpoint,
                headers=headers
            )

            # Sign the request
            signature.signature(req)

            # Send request
            response = self.session.send(req.prepare())

            # Check response
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == "Success":
                    return {
                        "success": True,
                        "message": "获取IP实体成功",
                        "data": data.get("data", {})
                    }
                else:
                    return {
                        "success": False,
                        "message": f"API返回错误: {data.get('message', '未知错误')}",
                        "error_type": "api_error"
                    }
            else:
                return {
                    "success": False,
                    "message": f"HTTP错误: 状态码 {response.status_code}",
                    "error_type": "api_error"
                }

        except Exception as e:
            error_msg = str(e)
            if "auth code" in error_msg.lower() or "联动码" in error_msg:
                return {
                    "success": False,
                    "message": "联动码格式错误或无效",
                    "error_type": "invalid_auth_code"
                }
            elif "connection" in error_msg.lower() or "network" in error_msg.lower():
                return {
                    "success": False,
                    "message": "网络连接失败，请检查目标地址",
                    "error_type": "network_error"
                }
            else:
                return {
                    "success": False,
                    "message": f"获取IP实体失败: {error_msg}",
                    "error_type": "unknown"
                }
