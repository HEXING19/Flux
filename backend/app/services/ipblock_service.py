"""
IP Block Service for Flux XDR API
Handles IP blocking status checking, device management, and blocking operations
"""

import re
import ipaddress
import requests
from typing import Dict, Any, Optional, List
from ..utils.sdk.aksk_py3 import Signature
from ..utils.error_handler import parse_api_error, format_error_message


class IpBlockService:
    """IP blocking service for Flux XDR API"""

    # Active block status values that indicate an IP is currently blocked
    ACTIVE_BLOCK_STATUSES = ["block success", "block ip in deal"]

    def __init__(self, base_url: str, auth_code: Optional[str] = None,
                 ak: Optional[str] = None, sk: Optional[str] = None):
        """
        Initialize IP block service

        Args:
            base_url: API base URL (e.g., "https://10.5.41.194")
            auth_code: Flux authentication code
            ak: Access Key (alternative to auth_code)
            sk: Secret Key (alternative to auth_code)
        """
        self.base_url = base_url.rstrip('/')
        self.auth_code = auth_code
        self.ak = ak
        self.sk = sk
        self.signature = None

        # Initialize signature if credentials are provided
        if auth_code or (ak and sk):
            self.signature = Signature(auth_code=auth_code, ak=ak, sk=sk)

    def validate_ip(self, ip: str) -> bool:
        """Validate IP address format"""
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

    def _normalize_device_name(self, name: str) -> str:
        """Normalize device names for tolerant matching."""
        if not name:
            return ""
        normalized = str(name).strip().strip('“”"\'`')
        normalized = re.sub(r'^\s*(?:设备|防火墙|网关)\s*', '', normalized, flags=re.IGNORECASE)
        normalized = re.sub(r'\s+', '', normalized)
        return normalized.lower()

    def check_ip_blocked(self, ip_address: str) -> Dict[str, Any]:
        """
        Check if an IP address is already blocked

        Args:
            ip_address: IP address to check

        Returns:
            Dict with keys:
                - success: bool
                - blocked: bool
                - rules: list of blocking rules (if blocked)
                - devices: list of devices where IP is blocked
                - error_info: dict (if error occurred)
        """
        # Validate IP address
        if not self.validate_ip(ip_address):
            return {
                "success": False,
                "blocked": False,
                "error_info": {
                    "error_type": "validation_error",
                    "friendly_message": f"IP地址格式不正确: {ip_address}",
                    "raw_message": f"Invalid IP address format: {ip_address}",
                    "suggestion": "请检查IP地址格式，应如192.168.1.1",
                    "actions": ["检查IP地址格式", "重新输入"]
                }
            }

        try:
            # Prepare API request
            api_endpoint = f"{self.base_url}/api/xdr/v1/responses/blockiprule/list"

            # Build request body - search for IP in view field
            request_body = {
                "pageSize": 100,
                "page": 1,
                "searchInfos": [
                    {
                        "fieldName": "view",
                        "fieldValue": ip_address
                    }
                ]
            }

            # Create and sign request
            req = requests.Request(
                "POST",
                api_endpoint,
                headers={"content-type": "application/json"},
                json=request_body
            )

            if not self.signature:
                return {
                    "success": False,
                    "blocked": False,
                    "error_info": {
                        "error_type": "auth_error",
                        "friendly_message": "认证信息未配置",
                        "raw_message": "Signature not initialized",
                        "suggestion": "请提供Flux认证信息（auth_code或ak/sk）",
                        "actions": ["检查认证配置", "联系管理员"]
                    }
                }

            # Sign the request
            self.signature.signature(req)

            # Send request
            session = requests.Session()
            session.verify = False  # Disable SSL verification for development
            response = session.send(req.prepare())

            # Parse response
            if response.status_code == 200:
                result = response.json()

                if result.get("code") == "Success":
                    data = result.get("data", {})
                    items = data.get("item", [])

                    # Check if IP is found in any rule
                    blocked_rules = []
                    all_devices = []

                    for item in items:
                        block_ip_rule = item.get("blockIpRule", {})
                        view_list = block_ip_rule.get("view", [])

                        # Check if IP matches (exact match or in list) AND rule is active
                        if ip_address in view_list and item.get("status") in self.ACTIVE_BLOCK_STATUSES:
                            blocked_rules.append({
                                "id": item.get("id"),
                                "name": item.get("name"),
                                "status": item.get("status"),
                                "createTime": item.get("createTime"),
                                "updateTime": item.get("updateTime"),
                                "blockIpMethod": item.get("blockIpMethod"),
                                "blockIpTimeRange": item.get("blockIpTimeRange"),
                                "blockIpRule": block_ip_rule,
                                "reason": item.get("reason"),
                                "createUser": item.get("createUser")
                            })

                            # Collect devices
                            devices = item.get("devices", [])
                            all_devices.extend(devices)

                    return {
                        "success": True,
                        "blocked": len(blocked_rules) > 0,
                        "rules": blocked_rules,
                        "devices": all_devices,
                        "total_rules": len(blocked_rules)
                    }
                else:
                    # API returned error
                    return {
                        "success": False,
                        "blocked": False,
                        "error_info": parse_api_error(response.status_code, response.text)
                    }
            else:
                # HTTP error
                return {
                    "success": False,
                    "blocked": False,
                    "error_info": parse_api_error(response.status_code, response.text)
                }

        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "blocked": False,
                "error_info": {
                    "error_type": "network_error",
                    "friendly_message": "网络请求失败",
                    "raw_message": f"Request failed: {str(e)}",
                    "suggestion": "请检查网络连接和API地址配置",
                    "actions": ["检查网络连接", "检查API地址", "重试"]
                }
            }
        except Exception as e:
            return {
                "success": False,
                "blocked": False,
                "error_info": {
                    "error_type": "system_error",
                    "friendly_message": "系统错误",
                    "raw_message": f"Unexpected error: {str(e)}",
                    "suggestion": "请联系系统管理员",
                    "actions": ["查看日志", "联系管理员"]
                }
            }

    def get_available_devices(self, device_type: str = "AF") -> Dict[str, Any]:
        """
        Get available blocking devices

        Args:
            device_type: Device type filter - "AF" for network, "EDR" for endpoint

        Returns:
            Dict with keys:
                - success: bool
                - devices: list of available devices
                - error_info: dict (if error occurred)
        """
        try:
            # Prepare API request
            api_endpoint = f"{self.base_url}/api/xdr/v1/device/blockdevice/list"

            # Build request body
            request_body = {
                "type": [device_type]
            }

            # Create and sign request
            req = requests.Request(
                "POST",
                api_endpoint,
                headers={"content-type": "application/json"},
                json=request_body
            )

            if not self.signature:
                return {
                    "success": False,
                    "devices": [],
                    "error_info": {
                        "error_type": "auth_error",
                        "friendly_message": "认证信息未配置",
                        "raw_message": "Signature not initialized",
                        "suggestion": "请提供Flux认证信息（auth_code或ak/sk）",
                        "actions": ["检查认证配置", "联系管理员"]
                    }
                }

            # Sign the request
            self.signature.signature(req)

            # Send request
            session = requests.Session()
            session.verify = False
            response = session.send(req.prepare())

            # Parse response
            if response.status_code == 200:
                result = response.json()

                if result.get("code") == "Success":
                    data = result.get("data", {})
                    items = data.get("item", [])

                    # Format devices
                    devices = []
                    for item in items:
                        devices.append({
                            "device_id": item.get("deviceId"),
                            "device_name": item.get("deviceName"),
                            "device_type": item.get("deviceType"),
                            "device_status": item.get("deviceStatus"),
                            "device_version": item.get("deviceVersion"),
                            "device_ip": item.get("deviceIp"),
                            "remark": item.get("remark"),
                            "gateway_id": item.get("gatewayId"),
                            "company_id": item.get("companyId")
                        })

                    return {
                        "success": True,
                        "devices": devices,
                        "total": len(devices)
                    }
                else:
                    # API returned error
                    return {
                        "success": False,
                        "devices": [],
                        "error_info": parse_api_error(response.status_code, response.text)
                    }
            else:
                # HTTP error
                return {
                    "success": False,
                    "devices": [],
                    "error_info": parse_api_error(response.status_code, response.text)
                }

        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "devices": [],
                "error_info": {
                    "error_type": "network_error",
                    "friendly_message": "网络请求失败",
                    "raw_message": f"Request failed: {str(e)}",
                    "suggestion": "请检查网络连接和API地址配置",
                    "actions": ["检查网络连接", "检查API地址", "重试"]
                }
            }
        except Exception as e:
            return {
                "success": False,
                "devices": [],
                "error_info": {
                    "error_type": "system_error",
                    "friendly_message": "系统错误",
                    "raw_message": f"Unexpected error: {str(e)}",
                    "suggestion": "请联系系统管理员",
                    "actions": ["查看日志", "联系管理员"]
                }
            }

    async def search_rules(
        self,
        page_size: int = 100,
        page: int = 1,
        search_infos: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Search IP block rules.

        Args:
            page_size: Number of records per page
            page: Page number
            search_infos: Optional search filters

        Returns:
            Dict with keys:
                - success: bool
                - data: {"item": list, "total": int}
                - error_info: dict (if error occurred)
        """
        try:
            api_endpoint = f"{self.base_url}/api/xdr/v1/responses/blockiprule/list"

            request_body: Dict[str, Any] = {
                "pageSize": page_size,
                "page": page
            }

            if search_infos:
                request_body["searchInfos"] = search_infos

            req = requests.Request(
                "POST",
                api_endpoint,
                headers={"content-type": "application/json"},
                json=request_body
            )

            if not self.signature:
                return {
                    "success": False,
                    "data": {"item": [], "total": 0},
                    "error_info": {
                        "error_type": "auth_error",
                        "friendly_message": "认证信息未配置",
                        "raw_message": "Signature not initialized",
                        "suggestion": "请提供Flux认证信息（auth_code或ak/sk）",
                        "actions": ["检查认证配置", "联系管理员"]
                    }
                }

            self.signature.signature(req)

            session = requests.Session()
            session.verify = False
            response = session.send(req.prepare())

            if response.status_code == 200:
                result = response.json()
                if result.get("code") == "Success":
                    data = result.get("data", {}) or {}
                    items = data.get("item", []) or []
                    total = data.get("total", len(items))
                    return {
                        "success": True,
                        "data": {
                            "item": items,
                            "total": total
                        }
                    }

                return {
                    "success": False,
                    "data": {"item": [], "total": 0},
                    "error_info": parse_api_error(response.status_code, response.text)
                }

            return {
                "success": False,
                "data": {"item": [], "total": 0},
                "error_info": parse_api_error(response.status_code, response.text)
            }

        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "data": {"item": [], "total": 0},
                "error_info": {
                    "error_type": "network_error",
                    "friendly_message": "网络请求失败",
                    "raw_message": f"Request failed: {str(e)}",
                    "suggestion": "请检查网络连接和API地址配置",
                    "actions": ["检查网络连接", "检查API地址", "重试"]
                }
            }
        except Exception as e:
            return {
                "success": False,
                "data": {"item": [], "total": 0},
                "error_info": {
                    "error_type": "system_error",
                    "friendly_message": "系统错误",
                    "raw_message": f"Unexpected error: {str(e)}",
                    "suggestion": "请联系系统管理员",
                    "actions": ["查看日志", "联系管理员"]
                }
            }

    def block_ip(
        self,
        ip_address: str,
        device_id: int,
        device_name: str,
        device_type: str = "AF",
        device_version: str = "",
        block_type: str = "SRC_IP",
        time_type: str = "forever",
        time_value: Optional[int] = None,
        time_unit: str = "d",
        reason: str = ""
    ) -> Dict[str, Any]:
        """
        Execute IP blocking operation

        Args:
            ip_address: IP address to block
            device_id: Device ID for blocking
            device_name: Device name
            device_type: Device type (AF, EDR, etc.)
            device_version: Device version
            block_type: Block entity type (SRC_IP, DST_IP, URL, DNS)
            time_type: Duration type ("forever" or "temporary")
            time_value: Duration value when temporary
            time_unit: Duration unit ("d", "h", "m")
            reason: Block reason

        Returns:
            Dict with keys:
                - success: bool
                - rule_ids: list of created rule IDs
                - message: str
                - error_info: dict (if error occurred)
        """
        # Validate IP address
        if not self.validate_ip(ip_address):
            return {
                "success": False,
                "rule_ids": [],
                "message": "IP地址格式不正确",
                "error_info": {
                    "error_type": "validation_error",
                    "friendly_message": f"IP地址格式不正确: {ip_address}",
                    "raw_message": f"Invalid IP address format: {ip_address}",
                    "suggestion": "请检查IP地址格式，应如192.168.1.1",
                    "actions": ["检查IP地址格式", "重新输入"]
                }
            }

        # Validate temporary block parameters
        if time_type == "temporary":
            if time_value is None:
                return {
                    "success": False,
                    "rule_ids": [],
                    "message": "临时封禁需要指定时长",
                    "error_info": {
                        "error_type": "validation_error",
                        "friendly_message": "临时封禁需要指定封禁时长",
                        "raw_message": "time_value is required when time_type is 'temporary'",
                        "suggestion": "请指定封禁时长，如7天、2小时等",
                        "actions": ["指定封禁时长", "选择永久封禁"]
                    }
                }

        try:
            # Prepare API request
            api_endpoint = f"{self.base_url}/api/xdr/v1/responses/blockiprule/network"

            # Build request body
            request_body = {
                "name": f"Block {ip_address} on {device_name}",
                "timeType": time_type,
                "blockIpRule": {
                    "type": block_type,
                    "mode": "in",
                    "view": [ip_address]
                },
                "devices": [
                    {
                        "devId": device_id,
                        "devName": device_name,
                        "devType": device_type,
                        "devVersion": device_version
                    }
                ]
            }

            # Add time parameters
            # Note: API requires timeValue and timeUnit even for "forever" blocks
            # Based on API docs constraints, use max allowed duration (15 days)
            if time_type == "forever":
                # Permanent blocking - use maximum allowed duration as workaround
                request_body["timeValue"] = 15  # Maximum allowed value for days
                request_body["timeUnit"] = "d"
            elif time_type == "temporary" and time_value is not None:
                # Temporary blocking - send actual duration
                request_body["timeValue"] = time_value
                request_body["timeUnit"] = time_unit

            if reason:
                request_body["reason"] = reason

            # Create and sign request
            req = requests.Request(
                "POST",
                api_endpoint,
                headers={"content-type": "application/json"},
                json=request_body
            )

            if not self.signature:
                return {
                    "success": False,
                    "rule_ids": [],
                    "message": "认证信息未配置",
                    "error_info": {
                        "error_type": "auth_error",
                        "friendly_message": "认证信息未配置",
                        "raw_message": "Signature not initialized",
                        "suggestion": "请提供Flux认证信息（auth_code或ak/sk）",
                        "actions": ["检查认证配置", "联系管理员"]
                    }
                }

            # Sign the request
            self.signature.signature(req)

            # Log the request for debugging
            print(f"[DEBUG] IP Block Request:")
            print(f"  URL: {api_endpoint}")
            print(f"  Body: {request_body}")
            print(f"  Headers: {req.headers}")

            # Send request with retry logic for connection issues
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    session = requests.Session()
                    session.verify = False

                    # Configure session with better SSL/TLS handling
                    from requests.adapters import HTTPAdapter
                    from urllib3.util.retry import Retry

                    retry_strategy = Retry(
                        total=3,
                        backoff_factor=1,
                        status_forcelist=[429, 500, 502, 503, 504],
                        allowed_methods=["POST"]
                    )
                    adapter = HTTPAdapter(
                        max_retries=retry_strategy,
                        pool_connections=10,
                        pool_maxsize=10
                    )
                    session.mount('https://', adapter)
                    session.mount('http://', adapter)

                    # Increase timeout
                    response = session.send(req.prepare(), timeout=(10, 30))

                    # If we get here, request succeeded
                    break

                except (requests.exceptions.ConnectionError,
                        requests.exceptions.ConnectionResetError,
                        requests.exceptions.SSLError) as e:
                    if attempt < max_retries - 1:
                        print(f"[DEBUG] Connection error (attempt {attempt + 1}/{max_retries}): {e}, retrying...")
                        import time
                        time.sleep(1)  # Wait before retry
                        continue
                    else:
                        return {
                            "success": False,
                            "rule_ids": [],
                            "message": "网络连接失败，无法连接到API服务器",
                            "error_info": {
                                "error_type": "network_error",
                                "friendly_message": "网络连接失败（连接被重置）",
                                "raw_message": f"Connection error: {str(e)}",
                                "suggestion": "请检查：1) 网络连接是否稳定 2) API服务器是否可访问 3) 是否有防火墙阻止",
                                "actions": ["检查网络连接", "检查API服务器状态", "重试"]
                            }
                        }
                except requests.exceptions.Timeout:
                    return {
                        "success": False,
                        "rule_ids": [],
                        "message": "请求超时，服务器未响应",
                        "error_info": {
                            "error_type": "network_error",
                            "friendly_message": "请求超时",
                            "raw_message": "Request timeout",
                            "suggestion": "请检查网络连接或稍后重试",
                            "actions": ["检查网络", "重试", "联系管理员"]
                        }
                    }

            # Log the response
            print(f"[DEBUG] IP Block Response:")
            print(f"  Status: {response.status_code}")
            print(f"  Body: {response.text[:500]}")  # Log first 500 chars

            # Parse response
            if response.status_code == 200:
                result = response.json()

                if result.get("code") == "Success":
                    data = result.get("data", {})
                    rule_ids = data.get("ids", [])

                    return {
                        "success": True,
                        "rule_ids": rule_ids,
                        "message": f"IP {ip_address} 已成功在设备 {device_name} 上封禁",
                        "rule_count": len(rule_ids)
                    }
                else:
                    # API returned error
                    error_info = parse_api_error(response.status_code, response.text)
                    return {
                        "success": False,
                        "rule_ids": [],
                        "message": error_info.get("friendly_message", "封禁失败"),
                        "error_info": error_info
                    }
            else:
                # HTTP error
                error_info = parse_api_error(response.status_code, response.text)
                return {
                    "success": False,
                    "rule_ids": [],
                    "message": error_info.get("friendly_message", "封禁失败"),
                    "error_info": error_info
                }

        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "rule_ids": [],
                "message": "网络请求失败",
                "error_info": {
                    "error_type": "network_error",
                    "friendly_message": "网络请求失败",
                    "raw_message": f"Request failed: {str(e)}",
                    "suggestion": "请检查网络连接和API地址配置",
                    "actions": ["检查网络连接", "检查API地址", "重试"]
                }
            }
        except Exception as e:
            return {
                "success": False,
                "rule_ids": [],
                "message": "系统错误",
                "error_info": {
                    "error_type": "system_error",
                    "friendly_message": "系统错误",
                    "raw_message": f"Unexpected error: {str(e)}",
                    "suggestion": "请联系系统管理员",
                    "actions": ["查看日志", "联系管理员"]
                }
            }

    def check_and_block(
        self,
        ip_address: str,
        device_name: str,
        device_type: str = "AF"
    ) -> Dict[str, Any]:
        """
        Check IP status and prepare block parameters if not blocked

        Args:
            ip_address: IP address to check and potentially block
            device_name: Device name for blocking
            device_type: Device type (default: "AF")

        Returns:
            Dict with keys:
                - action: "already_blocked" | "need_block" | "error"
                - current_status: dict (if already blocked)
                - block_params: dict (if need block)
                - error_info: dict (if error)
        """
        # Step 1: Check if IP is already blocked
        check_result = self.check_ip_blocked(ip_address)

        if not check_result["success"]:
            return {
                "action": "error",
                "error_info": check_result.get("error_info")
            }

        if check_result["blocked"]:
            # Already blocked
            return {
                "action": "already_blocked",
                "current_status": {
                    "ip_address": ip_address,
                    "blocked": True,
                    "rules": check_result.get("rules", []),
                    "devices": check_result.get("devices", []),
                    "total_rules": check_result.get("total_rules", 0),
                    "message": f"IP {ip_address} 已被封禁"
                }
            }

        # Step 2: Get available devices
        devices_result = self.get_available_devices(device_type)

        if not devices_result["success"]:
            return {
                "action": "error",
                "error_info": devices_result.get("error_info")
            }

        # Find the specified device
        target_device = None
        normalized_requested = self._normalize_device_name(device_name)

        for device in devices_result["devices"]:
            if device["device_name"] == device_name:
                target_device = device
                break

        if not target_device and normalized_requested:
            # Tolerant match for quoted/space-variant user input
            for device in devices_result["devices"]:
                normalized_device = self._normalize_device_name(device.get("device_name", ""))
                if not normalized_device:
                    continue
                if normalized_device == normalized_requested:
                    target_device = device
                    break

        if not target_device and normalized_requested and len(normalized_requested) >= 3:
            # Last resort: partial match when user input contains extra words
            for device in devices_result["devices"]:
                normalized_device = self._normalize_device_name(device.get("device_name", ""))
                if not normalized_device:
                    continue
                if normalized_requested in normalized_device or normalized_device in normalized_requested:
                    target_device = device
                    break

        if not target_device:
            return {
                "action": "error",
                "error_info": {
                    "error_type": "device_not_found",
                    "friendly_message": f"未找到指定的设备: {device_name}",
                    "raw_message": f"Device {device_name} not found",
                    "suggestion": "请检查设备名称或查询可用设备列表",
                    "actions": ["查询设备列表", "检查设备名称", "选择其他设备"]
                }
            }

        # Check device status - 只有离线(offline)和未接入(not_active)不能联动
        # online（在线）和告警状态都可以联动
        if target_device["device_status"] in ["offline", "not_active"]:
            status_text = "离线" if target_device["device_status"] == "offline" else "未接入"
            return {
                "action": "error",
                "error_info": {
                    "error_type": "device_offline",
                    "friendly_message": f"设备 {device_name} 当前{status_text}，无法执行封禁操作",
                    "raw_message": f"Device {device_name} is {target_device['device_status']}",
                    "suggestion": "请检查设备网络连接或选择其他可用设备",
                    "actions": ["检查设备状态", "选择其他设备", "联系设备管理员"]
                }
            }

        # Step 3: Return block parameters for confirmation
        return {
            "action": "need_block",
            "block_params": {
                "ip": ip_address,
                "device_id": target_device["device_id"],
                "device_name": target_device["device_name"],
                "device_type": target_device["device_type"],
                "device_version": target_device.get("device_version", ""),
                "block_type": "SRC_IP",
                "time_type": "forever",
                "time_value": None,
                "time_unit": "d",
                "reason": "",
                "device_status": target_device["device_status"]
            },
            "message": f"IP {ip_address} 未被封禁，准备使用设备 {device_name} 进行封禁"
        }

    def extract_device_from_text(self, text: str) -> Dict[str, Any]:
        """
        Extract device information from text

        Args:
            text: Input text

        Returns:
            Dict with keys:
                - device_name: str or None
                - device_type: str (default "AF")
        """
        # Common patterns for device names
        # AF1, AF-01, AF_01, Firewall1, etc.
        device_patterns = [
            r'(?:设备|device|使用|调用|on|using)\s*([A-Za-z]+[\d-]+)',
            r'([A-Za-z]{2,}[\d-]+)',  # AF1, EDR-01, etc.
        ]

        for pattern in device_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                device_name = match.group(1)
                # Determine device type from name
                if "AF" in device_name.upper():
                    return {
                        "device_name": device_name,
                        "device_type": "AF"
                    }
                elif "EDR" in device_name.upper():
                    return {
                        "device_name": device_name,
                        "device_type": "EDR"
                    }
                else:
                    return {
                        "device_name": device_name,
                        "device_type": "AF"  # Default to AF
                    }

        return {
            "device_name": None,
            "device_type": "AF"
        }

    def extract_block_params_from_text(self, text: str) -> Dict[str, Any]:
        """
        Extract blocking parameters from text

        Args:
            text: Input text

        Returns:
            Dict with extracted parameters
        """
        params = {}

        # Extract IP address
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        ip_match = re.search(ip_pattern, text)
        if ip_match:
            params["ip_address"] = ip_match.group(0)

        # Extract device info
        device_info = self.extract_device_from_text(text)
        params.update(device_info)

        # Extract duration
        # Patterns: "7天", "7 days", "2小时", "2 hours", "永久", "forever"
        duration_patterns = [
            (r'(\d+)\s*[天days]', 'd', 'temporary'),
            (r'(\d+)\s*[小时hours]', 'h', 'temporary'),
            (r'(\d+)\s*[分钟minutes]', 'm', 'temporary'),
        ]

        for pattern, unit, time_type in duration_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                params["time_type"] = time_type
                params["time_value"] = int(match.group(1))
                params["time_unit"] = unit
                break

        # Check for permanent/forever
        if re.search(r'永久|forever|permanent', text, re.IGNORECASE):
            params["time_type"] = "forever"

        # Extract block type (default SRC_IP)
        if re.search(r'dst|目的|目标', text, re.IGNORECASE):
            params["block_type"] = "DST_IP"
        elif re.search(r'url|链接', text, re.IGNORECASE):
            params["block_type"] = "URL"
        elif re.search(r'dns|域名', text, re.IGNORECASE):
            params["block_type"] = "DNS"
        else:
            params["block_type"] = "SRC_IP"

        # Extract reason
        reason_patterns = [
            r'因为\s*(.+?)(?:\.|$)',
            r'原因\s*[:：]\s*(.+?)(?:\.|$)',
            r'备注\s*[:：]\s*(.+?)(?:\.|$)',
        ]

        for pattern in reason_patterns:
            match = re.search(pattern, text)
            if match:
                params["reason"] = match.group(1).strip()
                break

        return params
