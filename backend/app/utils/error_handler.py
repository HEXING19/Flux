"""
Error Handler Utility for Flux XDR API
Provides error parsing, message formatting, and user-friendly suggestions
"""

import json
import re
from typing import Dict, Any, Optional, List


# Error code to friendly message and suggestion mapping
ERROR_MAPPING = {
    "Unknown.SerComError": {
        "资产组与默认资产组不符": {
            "error_type": "permission_error",
            "friendly_message": "您没有权限添加资产到该资产组",
            "suggestion": "请检查：1) 使用正确的资产组ID（branchId=0通常是默认组）2) 联系管理员确认您的资产组权限",
            "actions": ["修改branchId参数", "联系管理员"]
        },
        "default": {
            "error_type": "service_error",
            "friendly_message": "服务处理请求时出错",
            "suggestion": "请检查请求参数是否正确，或联系系统管理员",
            "actions": ["检查参数", "重试"]
        }
    },
    "AuthError": {
        "default": {
            "error_type": "auth_error",
            "friendly_message": "认证失败",
            "suggestion": "请检查认证信息是否正确，或重新登录获取新的认证码",
            "actions": ["重新登录", "检查认证配置"]
        }
    },
    "ValidationError": {
        "default": {
            "error_type": "validation_error",
            "friendly_message": "请求参数验证失败",
            "suggestion": "请检查输入的参数格式是否正确",
            "actions": ["检查参数格式"]
        }
    },
    "IPBlockError": {
        "default": {
            "error_type": "ipblock_error",
            "friendly_message": "IP封禁操作失败",
            "suggestion": "请检查参数后重试",
            "actions": ["检查IP地址", "检查设备状态", "重试"]
        },
        "DEVICE_NOT_FOUND": {
            "error_type": "device_not_found",
            "friendly_message": "未找到指定的封禁设备",
            "suggestion": "请检查设备名称或查询可用设备列表",
            "actions": ["查询设备列表", "检查设备名称", "联系管理员"]
        },
        "DEVICE_OFFLINE": {
            "error_type": "device_offline",
            "friendly_message": "设备当前离线，无法执行封禁",
            "suggestion": "请检查设备网络连接或选择其他在线设备",
            "actions": ["检查设备状态", "选择其他设备", "联系设备管理员"]
        },
        "IP_ALREADY_BLOCKED": {
            "error_type": "ip_already_blocked",
            "friendly_message": "该IP地址已被封禁",
            "suggestion": "如需修改封禁规则，请先解封原规则",
            "actions": ["查看封禁详情", "解封IP", "修改封禁规则"]
        },
        "INVALID_IP_FORMAT": {
            "error_type": "invalid_ip_format",
            "friendly_message": "IP地址格式不正确",
            "suggestion": "请提供有效的IP地址格式（如192.168.1.1）",
            "actions": ["检查IP格式", "重新输入"]
        }
    },
    "NotFoundError": {
        "default": {
            "error_type": "not_found_error",
            "friendly_message": "请求的资源不存在",
            "suggestion": "请确认资源ID或路径是否正确",
            "actions": ["检查资源ID"]
        }
    },
    "RateLimitError": {
        "default": {
            "error_type": "rate_limit_error",
            "friendly_message": "请求过于频繁，请稍后重试",
            "suggestion": "您已达到请求频率限制，请等待几秒后重试",
            "actions": ["稍后重试"]
        }
    },
}


def decode_unicode(text: str) -> str:
    """
    Convert UNICODE escape sequences to Chinese characters
    Example: "\\u8d44\\u4ea7" -> "资产"

    Args:
        text: String containing UNICODE escape sequences

    Returns:
        Decoded string with Chinese characters
    """
    try:
        # Handle both \uXXXX and JSON unicode escapes
        decoded = text.encode('utf-8').decode('unicode-escape')
        # If the text contains literal backslash-u sequences, process them
        if '\\u' in decoded:
            decoded = re.sub(r'\\u([0-9a-fA-F]{4})',
                           lambda m: chr(int(m.group(1), 16)),
                           decoded)
        return decoded
    except (UnicodeDecodeError, AttributeError):
        # If decoding fails, try regex replacement as fallback
        try:
            return re.sub(r'\\u([0-9a-fA-F]{4})',
                        lambda m: chr(int(m.group(1), 16)),
                        text)
        except Exception:
            return text


def parse_api_error(status_code: int, response_text: str) -> Dict[str, Any]:
    """
    Parse API error response and generate user-friendly error information

    Args:
        status_code: HTTP status code
        response_text: Raw response text from API

    Returns:
        Dictionary containing error information with friendly messages
    """
    result = {
        "success": False,
        "status_code": status_code,
        "raw_message": response_text,
        "error_type": "unknown_error",
        "friendly_message": "请求失败",
        "suggestion": "请稍后重试或联系系统管理员",
        "actions": ["重试"]
    }

    # Try to parse JSON response
    try:
        error_data = json.loads(response_text)
        error_code = error_data.get("code", "")
        error_message = error_data.get("message", "")

        # Decode unicode in message
        decoded_message = decode_unicode(error_message)

        result["raw_code"] = error_code
        result["raw_message"] = decoded_message

        # Look up error mapping
        error_info = None

        if error_code in ERROR_MAPPING:
            # Check for specific message mapping
            if decoded_message in ERROR_MAPPING[error_code]:
                error_info = ERROR_MAPPING[error_code][decoded_message]
            else:
                # Use default mapping for this error code
                error_info = ERROR_MAPPING[error_code].get("default")

        # Fallback to unknown error
        if not error_info:
            error_info = ERROR_MAPPING.get("Unknown.SerComError", {}).get("default", {
                "error_type": "unknown_error",
                "friendly_message": f"服务返回错误: {decoded_message}",
                "suggestion": "请检查请求参数或联系系统管理员",
                "actions": ["重试", "联系管理员"]
            })

        result["error_type"] = error_info["error_type"]
        result["friendly_message"] = error_info["friendly_message"]
        result["suggestion"] = error_info["suggestion"]
        result["actions"] = error_info["actions"]

    except json.JSONDecodeError:
        # Not a JSON response
        decoded_text = decode_unicode(response_text)
        result["friendly_message"] = f"API返回错误 (HTTP {status_code})"
        result["raw_message"] = decoded_text[:200]  # Limit length
        result["suggestion"] = "API返回了非标准格式的错误信息，请检查网络连接或联系管理员"

    except Exception as e:
        result["friendly_message"] = "解析错误响应时出现问题"
        result["raw_message"] = str(response_text)[:200]
        result["suggestion"] = f"系统错误: {str(e)}"

    return result


def format_error_message(error_info: Dict[str, Any]) -> str:
    """
    Format error information into a readable message string

    Args:
        error_info: Error information dictionary from parse_api_error

    Returns:
        Formatted error message string
    """
    parts = [
        f"❌ {error_info.get('friendly_message', '请求失败')}",
        "",
        f"详情: {error_info.get('raw_message', '')}",
        "",
        f"💡 建议: {error_info.get('suggestion', '请稍后重试')}"
    ]

    actions = error_info.get('actions', [])
    if actions:
        parts.append("")
        parts.append(f"可操作: {' • '.join(actions)}")

    return "\n".join(parts)


def is_retryable_error(error_info: Dict[str, Any]) -> bool:
    """
    Check if an error is retryable

    Args:
        error_info: Error information dictionary

    Returns:
        True if the error can be retried
    """
    retryable_types = {
        "rate_limit_error",
        "service_error",
        "unknown_error"
    }
    return error_info.get("error_type") in retryable_types
