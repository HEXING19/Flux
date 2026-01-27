"""
Asset Service for Flux XDR API
Handles asset creation, validation, and parameter inference
"""

import re
import ipaddress
import requests
from typing import Dict, Any, Optional, List
from ..utils.sdk.aksk_py3 import Signature


class AssetService:
    """Asset management service for Flux XDR API"""

    def __init__(self, base_url: str, auth_code: Optional[str] = None,
                 ak: Optional[str] = None, sk: Optional[str] = None):
        """
        Initialize asset service

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
        self.api_endpoint = f"{self.base_url}/api/xdr/v1/assets"

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

    def validate_mac(self, mac: str) -> bool:
        """Validate MAC address format"""
        mac_pattern = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
        return bool(mac_pattern.match(mac))

    def get_os_type_mapping(self) -> Dict[str, str]:
        """Mapping of natural language terms to OS types"""
        return {
            # Linux variants
            "linux": "Linux", "ubuntu": "Linux", "centos": "Linux",
            "rhel": "Linux", "redhat": "Linux", "debian": "Linux",
            "fedora": "Linux", "suse": "Linux",
            # Windows
            "windows": "Windows", "win": "Windows", "server": "Windows",
            "server 2019": "Windows", "server 2022": "Windows",
            # Apple
            "mac": "OS X", "macos": "OS X", "os x": "OS X",
            # Mobile
            "ios": "iOS", "iphone": "iOS", "ipad": "iOS",
            "android": "Android",
            # Virtualization
            "vmware": "VMware", "esxi": "VMware", "vsphere": "VMware",
            # Network
            "cisco": "Cisco", "junos": "Cisco",
            # Other
            "unix": "Unix", "solaris": "Unix", "aix": "Unix",
            "freebsd": "FreeBSD",
        }

    def get_category_mapping(self) -> Dict[str, tuple]:
        """
        Mapping of natural language terms to (classify1Id, classifyId)
        Returns: Dict[str, tuple] where tuple is (primary_category, detailed_category)
        """
        return {
            # Servers (classify1Id: 1)
            "web server": (1, 100012),
            "website": (1, 100012),
            "nginx": (1, 100012),
            "apache": (1, 100012),
            "database": (1, 100010),
            "mysql": (1, 100010),
            "postgresql": (1, 100010),
            "postgres": (1, 100010),
            "oracle": (1, 100010),
            "sql server": (1, 100010),
            "mongodb": (1, 100010),
            "dns": (1, 100037),
            "dns server": (1, 100037),
            "mail": (1, 100033),
            "mail server": (1, 100033),
            "email": (1, 100033),
            "smtp": (1, 100004),
            "ftp": (1, 100002),
            "file server": (1, 100025),
            "domain controller": (1, 100009),
            "active directory": (1, 100008),
            "ad": (1, 100008),
            "application server": (1, 100014),
            "app server": (1, 100014),

            # Terminals (classify1Id: 2)
            "desktop": (2, 200002),
            "laptop": (2, 200003),
            "notebook": (2, 200003),
            "workstation": (2, 200002),
            "pc": (2, 200002),

            # Network Devices (classify1Id: 5)
            "router": (5, 500014),
            "switch": (5, 500015),
            "wap": (5, 500017),
            "access point": (5, 500017),
            "wireless ap": (5, 500017),
            "load balancer": (5, 500012),
            "lb": (5, 500012),
            "proxy": (5, 500004),

            # Security Devices (classify1Id: 8)
            "firewall": (8, 800004),
            "ids": (8, 800016),
            "ips": (8, 800016),
            "waf": (8, 800015),
            "web application firewall": (8, 800015),
            "siem": (8, 800009),
            "edr": (8, 800005),
            "xdr": (8, 800005),
            "antivirus": (8, 800001),

            # IoT (classify1Id: 6)
            "camera": (6, 600099),
            "ip camera": (6, 600099),
            "sensor": (6, 600079),
            "smart device": (6, 600079),
            "iot device": (6, 600001),
            "iot": (6, 600001),

            # Mobile (classify1Id: 7)
            "iphone": (7, 700002),
            "android phone": (7, 700002),
            "smartphone": (7, 700002),
            "tablet": (7, 700003),
            "ipad": (7, 700003),
        }

    def create_asset(self, asset_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new asset via the Flux XDR API

        Args:
            asset_data: Dictionary containing asset parameters

        Returns:
            API response dictionary
        """
        try:
            # Validate required fields
            if "ip" not in asset_data:
                return {
                    "success": False,
                    "message": "IP address is required"
                }

            if not self.validate_ip(asset_data["ip"]):
                return {
                    "success": False,
                    "message": f"Invalid IP address format: {asset_data['ip']}"
                }

            if "branchId" not in asset_data:
                return {
                    "success": False,
                    "message": "Asset group ID (branchId) is required"
                }

            # Validate MAC address if provided
            if "mac" in asset_data and asset_data.get("mac"):
                if not self.validate_mac(asset_data["mac"]):
                    return {
                        "success": False,
                        "message": f"Invalid MAC address format: {asset_data['mac']}"
                    }

            # Validate field lengths
            if "assetName" in asset_data and asset_data.get("assetName"):
                if len(asset_data["assetName"]) > 95:
                    return {
                        "success": False,
                        "message": "Asset name must be 95 characters or less"
                    }

            if "hostName" in asset_data and asset_data.get("hostName"):
                if len(asset_data["hostName"]) > 95:
                    return {
                        "success": False,
                        "message": "Hostname must be 95 characters or less"
                    }

            if "comment" in asset_data and asset_data.get("comment"):
                if len(asset_data["comment"]) > 95:
                    return {
                        "success": False,
                        "message": "Comment must be 95 characters or less"
                    }

            # Validate tags
            if "tags" in asset_data and asset_data.get("tags"):
                if len(asset_data["tags"]) > 10:
                    return {
                        "success": False,
                        "message": "Maximum 10 tags allowed"
                    }
                for tag in asset_data["tags"]:
                    if len(tag) > 20:
                        return {
                            "success": False,
                            "message": f"Tag '{tag}' exceeds 20 character limit"
                        }

            # Construct request
            headers = {
                "content-type": "application/json"
            }

            # Build request body with only provided fields
            request_body = {
                "ip": asset_data["ip"],
                "branchId": asset_data["branchId"]
            }

            # Add optional fields if present
            optional_fields = ["mac", "assetName", "hostName", "type",
                             "magnitude", "tags", "classify1Id",
                             "classifyId", "comment", "users"]

            for field in optional_fields:
                if field in asset_data and asset_data[field] is not None:
                    request_body[field] = asset_data[field]

            # Check if signature is initialized
            if not self.signature:
                return {
                    "success": False,
                    "message": "Authentication not configured. Please provide auth_code or ak/sk."
                }

            # Create and sign request
            req = requests.Request(
                "POST",
                self.api_endpoint,
                headers=headers,
                json=request_body
            )

            # Sign the request
            self.signature.signature(req)

            # Send request
            session = requests.Session()
            session.verify = False  # Disable SSL verification for development

            response = session.send(req.prepare())

            if response.status_code == 200:
                result = response.json()
                if result.get("code") == "Success":
                    return {
                        "success": True,
                        "message": "Asset created successfully",
                        "data": result
                    }
                else:
                    return {
                        "success": False,
                        "message": result.get("message", "Unknown error"),
                        "data": result
                    }
            else:
                return {
                    "success": False,
                    "message": f"API error: HTTP {response.status_code} - {response.text}"
                }

        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "message": f"Request failed: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Unexpected error: {str(e)}"
            }

    def infer_parameters(self, text: str, provided_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Infer asset parameters from natural language text

        Args:
            text: Natural language description
            provided_params: Already extracted parameters

        Returns:
            Enhanced parameter dictionary
        """
        result = provided_params.copy()
        text_lower = text.lower()

        # Extract IP address
        if "ip" not in result:
            ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
            ips = re.findall(ip_pattern, text)
            if ips:
                result["ip"] = ips[0]

        # Extract MAC address
        if "mac" not in result:
            mac_pattern = r'\b([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})\b'
            mac_match = re.search(mac_pattern, text)
            if mac_match:
                result["mac"] = mac_match.group(0)

        # Infer OS type
        if "type" not in result:
            os_mapping = self.get_os_type_mapping()
            for term, os_type in os_mapping.items():
                if term in text_lower:
                    result["type"] = os_type
                    break

        # Infer category
        if "classify1Id" not in result or "classifyId" not in result:
            category_mapping = self.get_category_mapping()
            for term, (cat1, cat2) in category_mapping.items():
                if term in text_lower:
                    result["classify1Id"] = cat1
                    result["classifyId"] = cat2
                    break

        # Infer importance/magnitude
        if "magnitude" not in result:
            if any(word in text_lower for word in ["production", "critical", "core", "important", "prod"]):
                result["magnitude"] = "core"
            else:
                result["magnitude"] = "normal"

        # Extract asset name
        if "assetName" not in result:
            # Look for patterns like "name it X", "called X", "named X"
            name_patterns = [
                r'(?:name|named|called)\s+["\']?([a-zA-Z0-9-_]+)["\']?',
                r'["\']([a-zA-Z0-9-_]{3,})["\']',
            ]
            for pattern in name_patterns:
                match = re.search(pattern, text)
                if match:
                    result["assetName"] = match.group(1)
                    break

        # Extract hostname
        if "hostName" not in result:
            # Look for hostname patterns
            hostname_pattern = r'\b[a-z0-9]+([-][a-z0-9]+)*(\.[a-z0-9]+([-][a-z0-9]+)*)*\b'
            matches = re.findall(hostname_pattern, text_lower)
            for match in matches:
                candidate = match[0]
                if "." in candidate and len(candidate) > 5:  # Likely a hostname
                    result["hostName"] = candidate
                    break

        # Extract tags
        if "tags" not in result:
            # Look for tag indicators
            if "tag" in text_lower:
                # Extract words after "tag" or "tags"
                tag_pattern = r'(?:tag|tags)[s]?(?:[:\s]+)([a-zA-Z0-9-_,\s]+)'
                match = re.search(tag_pattern, text_lower)
                if match:
                    tags_str = match.group(1)
                    result["tags"] = [tag.strip() for tag in tags_str.split(",") if tag.strip()]

        # Set defaults for missing optional fields
        if "type" not in result:
            result["type"] = "Unknown"
        if "classify1Id" not in result:
            result["classify1Id"] = 0
        if "classifyId" not in result:
            result["classifyId"] = 100000  # Server-Unknown
        if "magnitude" not in result:
            result["magnitude"] = "normal"
        if "tags" not in result:
            result["tags"] = []
        if "users" not in result:
            result["users"] = []

        return result
