import os
import httpx
import json
import re
from typing import Optional, Dict, Any, List


class LLMService:
    """大模型服务 - 测试与主流大模型的连通性"""

    def __init__(self):
        # 内置的模型提供商配置
        self.providers = {
            "zhipu": {
                "name": "智谱AI",
                "base_url": "https://open.bigmodel.cn/api/paas/v4/",
                "model": "glm-4-plus",
            },
            "openai": {
                "name": "OpenAI",
                "base_url": "https://api.openai.com/v1/",
                "model": "gpt-4",
            },
            "azure": {
                "name": "Azure OpenAI",
                "base_url": "https://{your-resource-name}.openai.azure.com/",
                "model": "gpt-4",
            },
            "deepseek": {
                "name": "DeepSeek",
                "base_url": "https://api.deepseek.com/v1/",
                "model": "deepseek-chat",
            },
        }

    async def test_connection(
        self,
        provider: str,
        api_key: str,
        base_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        测试与大模型API的连通性

        Args:
            provider: 模型提供商名称
            api_key: API密钥
            base_url: 自定义的API Base URL(可选)

        Returns:
            测试结果字典
        """
        try:
            # 确定使用的base_url
            if base_url:
                effective_base_url = base_url
            else:
                provider_config = self.providers.get(provider, {})
                effective_base_url = provider_config.get("base_url", "")

            if not effective_base_url:
                return {
                    "success": False,
                    "message": f"未知的提供商: {provider}",
                }

            # 根据提供商选择模型
            if provider == "zhipu":
                model = "glm-4-plus"
            elif provider == "openai":
                model = "gpt-4"
            elif provider == "deepseek":
                model = "deepseek-chat"
            else:
                model = "gpt-4"  # 默认

            # 构造测试请求
            endpoint = f"{effective_base_url.rstrip('/')}/chat/completions"

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }

            # 智谱AI需要特殊的Authorization格式
            if provider == "zhipu":
                headers["Authorization"] = f"Bearer {api_key}"

            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": "Hi"
                    }
                ],
                "max_tokens": 10,
                "temperature": 0.7,
            }

            # 发送请求
            async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
                response = await client.post(
                    endpoint,
                    headers=headers,
                    json=payload
                )

                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "message": f"连接成功! 提供商: {self.providers.get(provider, {}).get('name', provider)}, 模型: {model}",
                        "provider": provider,
                        "model": model,
                    }
                elif response.status_code == 401:
                    return {
                        "success": False,
                        "message": f"API Key验证失败,请检查您的密钥是否正确",
                    }
                elif response.status_code == 404:
                    return {
                        "success": False,
                        "message": f"API端点未找到,请检查Base URL是否正确",
                    }
                else:
                    return {
                        "success": False,
                        "message": f"连接失败: HTTP {response.status_code} - {response.text}",
                    }

        except httpx.TimeoutException:
            return {
                "success": False,
                "message": "连接超时,请检查网络连接或API地址是否正确",
            }
        except httpx.ConnectError:
            return {
                "success": False,
                "message": "无法连接到服务器,请检查Base URL是否正确",
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"连接失败: {str(e)}",
            }

    async def chat(
        self,
        messages: List[Dict[str, str]],
        provider: str,
        api_key: str,
        base_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        与大模型进行对话

        Args:
            messages: 对话历史列表
            provider: 模型提供商名称
            api_key: API密钥
            base_url: 自定义的API Base URL(可选)

        Returns:
            对话响应结果
        """
        try:
            # 确定使用的base_url
            if base_url:
                effective_base_url = base_url
            else:
                provider_config = self.providers.get(provider, {})
                effective_base_url = provider_config.get("base_url", "")

            if not effective_base_url:
                return {
                    "success": False,
                    "message": f"未知的提供商: {provider}",
                }

            # 根据提供商选择模型
            if provider == "zhipu":
                model = "glm-4-plus"
            elif provider == "openai":
                model = "gpt-4"
            elif provider == "deepseek":
                model = "deepseek-chat"
            else:
                model = "gpt-4"

            # 构造请求
            endpoint = f"{effective_base_url.rstrip('/')}/chat/completions"

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }

            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": 2000,
                "temperature": 0.7,
            }

            # 发送请求
            async with httpx.AsyncClient(timeout=60.0, verify=False) as client:
                response = await client.post(
                    endpoint,
                    headers=headers,
                    json=payload
                )

                if response.status_code == 200:
                    data = response.json()
                    assistant_message = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    return {
                        "success": True,
                        "message": assistant_message,
                    }
                else:
                    return {
                        "success": False,
                        "message": f"API错误: {response.status_code} - {response.text}",
                    }

        except httpx.TimeoutException:
            return {
                "success": False,
                "message": "请求超时,请稍后重试",
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"请求失败: {str(e)}",
            }

    def get_supported_providers(self) -> Dict[str, str]:
        """获取支持的模型提供商列表"""
        return {
            key: config["name"]
            for key, config in self.providers.items()
        }

    async def chat_with_asset_support(
        self,
        messages: List[Dict[str, str]],
        provider: str,
        api_key: str,
        base_url: Optional[str] = None,
        auth_code: Optional[str] = None,
        flux_base_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        支持资产添加的聊天功能

        流程：
        1. 获取最后一条用户消息
        2. 使用 LLM 检测意图（添加资产 vs 普通聊天）
        3. 如果是添加资产：
           a. 使用 LLM 提取资产参数
           b. 使用 AssetService 验证和补充参数
           c. 调用资产创建 API
           d. 返回结果
        4. 如果是普通聊天：
           a. 正常调用 LLM
           b. 返回回复

        Args:
            messages: 对话历史
            provider: LLM 提供商
            api_key: LLM API 密钥
            base_url: LLM API 基础 URL
            auth_code: Flux 认证码
            flux_base_url: Flux API 基础 URL

        Returns:
            对话响应结果
        """
        try:
            # 获取最后一条用户消息
            last_message = messages[-1] if messages else {}
            user_message = last_message.get("content", "")

            if not user_message:
                chat_result = await self.chat(messages, provider, api_key, base_url)
                chat_result["type"] = "text"
                return chat_result

            # Step 1: 检测意图
            try:
                intent_result = await self._detect_intent(
                    user_message, provider, api_key, base_url
                )
            except Exception:
                # 意图检测失败，按普通聊天处理
                chat_result = await self.chat(messages, provider, api_key, base_url)
                chat_result["type"] = "text"
                return chat_result

            intent = intent_result.get("intent", "general_chat")
            confidence = intent_result.get("confidence", 0.0)

            # 置信度太低，按普通聊天处理
            if confidence < 0.7:
                chat_result = await self.chat(messages, provider, api_key, base_url)
                chat_result["type"] = "text"
                return chat_result

            # 处理不同的意图
            if intent == "add_asset":
                return await self._handle_asset_intent(
                    user_message, messages, provider, api_key, base_url,
                    auth_code, flux_base_url
                )
            elif intent == "ipblock":
                return await self._handle_ipblock_intent(
                    user_message, messages, provider, api_key, base_url,
                    auth_code, flux_base_url
                )
            elif intent == "get_incidents":
                return await self._handle_get_incidents_intent(
                    user_message, messages, provider, api_key, base_url,
                    auth_code, flux_base_url
                )
            elif intent == "get_incident_proof":
                return await self._handle_get_incident_proof_intent(
                    user_message, messages, provider, api_key, base_url,
                    auth_code, flux_base_url
                )
            elif intent == "update_incident_status":
                return await self._handle_update_incident_status_intent(
                    user_message, messages, provider, api_key, base_url,
                    auth_code, flux_base_url
                )
            else:
                # 普通聊天
                chat_result = await self.chat(messages, provider, api_key, base_url)
                chat_result["type"] = "text"
                return chat_result

        except Exception as e:
            # 任何错误都回退到普通聊天
            try:
                chat_result = await self.chat(messages, provider, api_key, base_url)
                chat_result["type"] = "text"
                return chat_result
            except Exception as chat_error:
                # 如果聊天也失败了，返回错误信息
                return {
                    "success": False,
                    "type": "text",
                    "message": f"抱歉，我现在无法回复：{str(e)}"
                }

    async def _detect_intent(
        self,
        user_message: str,
        provider: str,
        api_key: str,
        base_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """检测用户意图"""
        intent_prompt = f"""你是一个意图识别助手。判断用户消息的意图类型。

用户消息: {user_message}

分析用户是否想要：
1. 添加资产 (add_asset) - 添加新资产、创建新服务器、注册新设备
2. IP封禁 (ipblock) - 查询IP封禁状态、封禁IP地址、检查并封禁IP
3. 查询安全事件 (get_incidents) - 查询事件列表、查看安全事件、找事件、显示事件
4. 查看事件详情 (get_incident_proof) - 查看事件详情、查看举证、查看攻击链、查看事件证据
5. 更新事件状态 (update_incident_status) - 标记事件状态、处置事件、修改处置状态、批量更新
6. 普通聊天 (general_chat) - 其他对话

返回 JSON 格式（只返回 JSON，不要其他内容）:
{{
  "intent": "add_asset" | "ipblock" | "get_incidents" | "get_incident_proof" | "update_incident_status" | "general_chat",
  "confidence": 0.0-1.0,
  "reasoning": "判断理由"
}}"""

        try:
            response = await self.chat(
                messages=[{"role": "user", "content": intent_prompt}],
                provider=provider,
                api_key=api_key,
                base_url=base_url
            )

            if response.get("success"):
                # 解析 LLM 返回的 JSON
                response_text = response.get("message", "")

                # 尝试提取 JSON
                json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
                if json_match:
                    try:
                        intent_result = json.loads(json_match.group())
                        return intent_result
                    except json.JSONDecodeError:
                        pass

            return {"intent": "general_chat", "confidence": 0.0}

        except Exception:
            return {"intent": "general_chat", "confidence": 0.0}

    async def _extract_asset_params(
        self,
        user_message: str,
        messages: List[Dict[str, str]],
        provider: str,
        api_key: str,
        base_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """从用户消息中提取资产参数"""
        # 格式化对话历史
        history_text = "\n".join([
            f"{msg.get('role', 'user')}: {msg.get('content', '')}"
            for msg in messages[-5:]  # 只使用最近 5 条消息
        ])

        extraction_prompt = f"""你是一个资产参数提取助手。从用户消息中提取资产信息。

用户消息: {user_message}
对话历史: {history_text}

请提取以下信息：
- ip: IP地址（必填）
- assetName: 资产名称
- type: 操作系统类型（Linux/Windows/OS X/iOS/Android/Unknown）
- classify1Id: 一级分类（0=未知, 1=服务器, 2=终端, 5=网络设备, 6=IoT, 7=移动设备, 8=安全设备）
- classifyId: 详细分类（如 100012=Web服务器, 100010=数据库）
- magnitude: 重要级别（normal/core）
- mac: MAC地址
- hostName: 主机名
- tags: 标签数组
- comment: 备注

返回 JSON 格式（只返回 JSON，不要其他内容）:
{{
  "ip": "192.168.1.100" | null,
  "assetName": "Web Server 1" | null,
  "type": "Linux" | null,
  "classify1Id": 1 | 0,
  "classifyId": 100012 | 100000,
  "magnitude": "normal" | "core",
  "mac": "fe:fc:fe:d7:04:91" | null,
  "hostName": "web-01.example.com" | null,
  "tags": ["production", "web"] | [],
  "comment": "Main web server" | null
}}"""

        try:
            response = await self.chat(
                messages=[{"role": "user", "content": extraction_prompt}],
                provider=provider,
                api_key=api_key,
                base_url=base_url
            )

            if response.get("success"):
                response_text = response.get("message", "")

                # 尝试提取 JSON
                json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
                if json_match:
                    try:
                        params = json.loads(json_match.group())
                        return params
                    except json.JSONDecodeError:
                        pass

            return {}

        except Exception:
            return {}

    def _format_confirmation_message(self, params: Dict[str, Any]) -> str:
        """格式化确认信息"""
        lines = ["我识别到您想添加一个资产。我已经提取了以下信息：\n"]

        if "ip" in params:
            lines.append(f"• IP 地址: {params['ip']}")

        if "assetName" in params and params["assetName"]:
            lines.append(f"• 资产名称: {params['assetName']}")

        if "type" in params and params["type"] and params["type"] != "Unknown":
            lines.append(f"• 操作系统: {params['type']}")

        if "classify1Id" in params:
            category_names = {
                0: "未知", 1: "服务器", 2: "终端", 5: "网络设备",
                6: "IoT设备", 7: "移动设备", 8: "安全设备"
            }
            category = category_names.get(params["classify1Id"], "未知")
            lines.append(f"• 资产分类: {category}")

        if "magnitude" in params:
            magnitude_text = "核心" if params["magnitude"] == "core" else "普通"
            lines.append(f"• 重要级别: {magnitude_text}")

        if "branchId" in params:
            lines.append(f"• 资产组: {params['branchId']}")

        return "\n".join(lines)

    def _format_asset_result(self, params: Dict[str, Any]) -> str:
        """格式化资产创建结果"""
        lines = ["资产信息：\n"]

        if "ip" in params:
            lines.append(f"• IP: {params['ip']}")

        if "assetName" in params and params["assetName"]:
            lines.append(f"• 名称: {params['assetName']}")

        if "type" in params and params["type"]:
            lines.append(f"• 类型: {params['type']}")

        if "classify1Id" in params:
            category_names = {
                0: "未知", 1: "服务器", 2: "终端", 5: "网络设备",
                6: "IoT设备", 7: "移动设备", 8: "安全设备"
            }
            category = category_names.get(params["classify1Id"], "未知")
            lines.append(f"• 分类: {category}")

        if "branchId" in params:
            lines.append(f"• 资产组: {params['branchId']}")

        return "\n".join(lines)

    async def _handle_asset_intent(
        self,
        user_message: str,
        messages: List[Dict[str, str]],
        provider: str,
        api_key: str,
        base_url: Optional[str] = None,
        auth_code: Optional[str] = None,
        flux_base_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """处理添加资产意图"""
        try:
            # 提取资产参数
            extracted_params = await self._extract_asset_params(
                user_message, messages, provider, api_key, base_url
            )
        except Exception:
            # 参数提取失败，按普通聊天处理
            chat_result = await self.chat(messages, provider, api_key, base_url)
            chat_result["type"] = "text"
            return chat_result

        # 使用 AssetService 验证和补充参数
        from .asset_service import AssetService

        if not auth_code or not flux_base_url:
            return {
                "success": True,
                "type": "text",
                "message": "缺少 Flux 认证信息。请先登录系统。"
            }

        asset_service = AssetService(
            base_url=flux_base_url,
            auth_code=auth_code
        )

        # 验证和补充参数
        validated_params = asset_service.infer_parameters(
            text=user_message,
            provided_params=extracted_params
        )

        # 设置默认 branchId
        if "branchId" not in validated_params:
            validated_params["branchId"] = 0

        # 检查必填字段
        if "ip" not in validated_params or not validated_params["ip"]:
            return {
                "success": True,
                "type": "text",
                "message": "我识别到您想添加资产，但是没有找到 IP 地址。请提供 IP 地址。"
            }

        # 返回确认信息（不直接创建资产）
        confirmation_msg = "我识别到您想添加一个资产。请确认以下信息："

        return {
            "success": True,
            "type": "asset_confirmation",
            "message": confirmation_msg,
            "asset_params": validated_params
        }

    async def _handle_ipblock_intent(
        self,
        user_message: str,
        messages: List[Dict[str, str]],
        provider: str,
        api_key: str,
        base_url: Optional[str] = None,
        auth_code: Optional[str] = None,
        flux_base_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """处理IP封禁意图"""
        try:
            # 提取IP封禁参数
            extracted_params = await self._extract_ipblock_params(
                user_message, messages, provider, api_key, base_url
            )
        except Exception as e:
            # 参数提取失败，按普通聊天处理
            chat_result = await self.chat(messages, provider, api_key, base_url)
            chat_result["type"] = "text"
            return chat_result

        # 使用 IpBlockService 验证和处理参数
        from .ipblock_service import IpBlockService

        if not auth_code or not flux_base_url:
            return {
                "success": True,
                "type": "text",
                "message": "缺少 Flux 认证信息。请先登录系统。"
            }

        ipblock_service = IpBlockService(
            base_url=flux_base_url,
            auth_code=auth_code
        )

        # 检查必填字段
        if "ip_address" not in extracted_params or not extracted_params["ip_address"]:
            return {
                "success": True,
                "type": "text",
                "message": "我识别到您想查询或封禁IP，但是没有找到 IP 地址。请提供 IP 地址。"
            }

        # 确定操作类型
        action = extracted_params.get("action", "check")
        ip_address = extracted_params["ip_address"]

        # 判断是检查还是封禁
        if "device_name" in extracted_params and extracted_params["device_name"]:
            # 有设备名称，说明是封禁操作
            device_name = extracted_params["device_name"]
            device_type = extracted_params.get("device_type", "AF")

            # 调用 check_and_block 方法
            result = ipblock_service.check_and_block(
                ip_address=ip_address,
                device_name=device_name,
                device_type=device_type
            )

            if result["action"] == "already_blocked":
                # 已封禁，返回状态
                return {
                    "success": True,
                    "type": "ipblock_status",
                    "message": f"IP {ip_address} 已被封禁",
                    "status": result["current_status"]
                }
            elif result["action"] == "need_block":
                # 需要封禁，返回确认对话框参数
                block_params = result["block_params"]
                return {
                    "success": True,
                    "type": "ipblock_confirmation",
                    "message": f"IP {ip_address} 未被封禁，是否使用设备 {device_name} 进行封禁？",
                    "block_params": block_params
                }
            else:
                # 错误
                error_info = result.get("error_info", {})
                return {
                    "success": True,
                    "type": "text",
                    "message": error_info.get("friendly_message", "操作失败")
                }
        else:
            # 没有设备名称，只查询状态
            result = ipblock_service.check_ip_blocked(ip_address)

            if result["success"]:
                if result["blocked"]:
                    return {
                        "success": True,
                        "type": "ipblock_status",
                        "message": f"IP {ip_address} 已被封禁",
                        "status": {
                            "blocked": True,
                            "rules": result.get("rules", []),
                            "devices": result.get("devices", []),
                            "total_rules": result.get("total_rules", 0)
                        }
                    }
                else:
                    return {
                        "success": True,
                        "type": "ipblock_status",
                        "message": f"IP {ip_address} 未被封禁",
                        "status": {
                            "blocked": False,
                            "rules": [],
                            "devices": []
                        }
                    }
            else:
                error_info = result.get("error_info", {})
                return {
                    "success": True,
                    "type": "text",
                    "message": error_info.get("friendly_message", "查询失败")
                }

    async def _extract_ipblock_params(
        self,
        user_message: str,
        messages: List[Dict[str, str]],
        provider: str,
        api_key: str,
        base_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """从用户消息中提取IP封禁参数"""
        # 格式化对话历史
        history_text = "\n".join([
            f"{msg.get('role', 'user')}: {msg.get('content', '')}"
            for msg in messages[-5:]  # 只使用最近 5 条消息
        ])

        extraction_prompt = f"""你是一个IP封禁参数提取助手。从用户消息中提取IP封禁相关信息。

用户消息: {user_message}
对话历史: {history_text}

请提取以下信息：
- ip_address: IP地址（必填，如 192.168.1.100）
- device_name: 设备名称（如 AF1, AF-01）
- device_type: 设备类型（AF=网侧设备, EDR=端侧设备，默认AF）
- action: 操作类型
  * "check" - 仅查询IP封禁状态
  * "block" - 直接封禁IP
  * "check_and_block" - 检查状态，如果未封禁则封禁
- block_type: 封禁类型（SRC_IP=源IP, DST_IP=目的IP, URL=链接, DNS=域名，默认SRC_IP）
- time_type: 封禁时长类型（forever=永久, temporary=临时，默认forever）
- time_value: 封禁时长数值（当time_type为temporary时必填）
- time_unit: 时间单位（d=天, h=小时, m=分钟）
- reason: 封禁原因/备注

返回 JSON 格式（只返回 JSON，不要其他内容）:
{{
  "ip_address": "192.168.1.100" | null,
  "device_name": "AF1" | null,
  "device_type": "AF" | "EDR" | null,
  "action": "check" | "block" | "check_and_block",
  "block_type": "SRC_IP" | "DST_IP" | "URL" | "DNS" | null,
  "time_type": "forever" | "temporary" | null,
  "time_value": 7 | null,
  "time_unit": "d" | "h" | "m" | null,
  "reason": "恶意攻击" | null
}}"""

        try:
            response = await self.chat(
                messages=[{"role": "user", "content": extraction_prompt}],
                provider=provider,
                api_key=api_key,
                base_url=base_url
            )

            if response.get("success"):
                # 解析 LLM 返回的 JSON
                response_text = response.get("message", "")

                # 尝试提取 JSON
                json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
                if json_match:
                    try:
                        params = json.loads(json_match.group())
                        return params
                    except json.JSONDecodeError:
                        pass

            # 如果解析失败，返回空参数
            return {}

        except Exception:
            return {}

    async def _handle_get_incidents_intent(
        self,
        user_message: str,
        messages: List[Dict[str, str]],
        provider: str,
        api_key: str,
        base_url: Optional[str] = None,
        auth_code: Optional[str] = None,
        flux_base_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """处理查询安全事件意图"""
        try:
            # 提取查询参数
            extracted_params = await self._extract_incidents_params(
                user_message, messages, provider, api_key, base_url
            )
        except Exception as e:
            # 参数提取失败，按普通聊天处理
            chat_result = await self.chat(messages, provider, api_key, base_url)
            chat_result["type"] = "text"
            return chat_result

        # 使用 SecurityIncidentsService
        from .security_incidents_service import SecurityIncidentsService

        if not auth_code or not flux_base_url:
            return {
                "success": True,
                "type": "text",
                "message": "缺少 Flux 认证信息。请先登录系统。"
            }

        incidents_service = SecurityIncidentsService()

        # 调用查询接口
        result = await incidents_service.get_incidents(
            auth_code=auth_code,
            base_url=flux_base_url,
            **extracted_params
        )

        if result.get("success"):
            data = result.get("data", {})
            total = data.get("total", 0)
            items = data.get("item", [])

            return {
                "success": True,
                "type": "incidents_list",
                "message": f"查询成功！找到 {total} 条安全事件。",
                "incidents_data": {
                    "total": total,
                    "items": items
                }
            }
        else:
            return {
                "success": True,
                "type": "text",
                "message": f"查询失败：{result.get('message', '未知错误')}"
            }

    async def _handle_get_incident_proof_intent(
        self,
        user_message: str,
        messages: List[Dict[str, str]],
        provider: str,
        api_key: str,
        base_url: Optional[str] = None,
        auth_code: Optional[str] = None,
        flux_base_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """处理查看事件举证意图"""
        try:
            # 提取事件ID
            extracted_params = await self._extract_incident_proof_params(
                user_message, messages, provider, api_key, base_url
            )
        except Exception as e:
            # 参数提取失败，按普通聊天处理
            chat_result = await self.chat(messages, provider, api_key, base_url)
            chat_result["type"] = "text"
            return chat_result

        uuid = extracted_params.get("uuid")
        name = extracted_params.get("name")

        # If name is provided but no UUID, search for it
        if not uuid and name:
            if not auth_code or not flux_base_url:
                return {
                    "success": True,
                    "type": "text",
                    "message": "缺少 Flux 认证信息。请先登录系统。"
                }

            # Search incident by name
            uuid = await self._search_incident_by_name(
                name=name,
                auth_code=auth_code,
                flux_base_url=flux_base_url
            )

            if not uuid:
                return {
                    "success": True,
                    "type": "text",
                    "message": f"未找到名称为 '{name}' 的安全事件。请确认事件名称是否正确，或先查询事件列表。"
                }

        # If still no UUID, ask user to provide it
        if not uuid:
            return {
                "success": True,
                "type": "text",
                "message": "我识别到您想查看事件详情，但没有找到事件ID。请提供事件ID（格式：incident-xxx）或事件名称。"
            }

        # 使用 SecurityIncidentsService
        from .security_incidents_service import SecurityIncidentsService

        if not auth_code or not flux_base_url:
            return {
                "success": True,
                "type": "text",
                "message": "缺少 Flux 认证信息。请先登录系统。"
            }

        incidents_service = SecurityIncidentsService()

        # 调用举证查询接口
        result = await incidents_service.get_incident_proof(
            auth_code=auth_code,
            base_url=flux_base_url,
            uuid=uuid
        )

        if result.get("success"):
            data = result.get("data", {})

            return {
                "success": True,
                "type": "incident_proof",
                "message": f"事件详情：{data.get('name', '未知')}",
                "proof_data": data
            }
        else:
            return {
                "success": True,
                "type": "text",
                "message": f"获取举证失败：{result.get('message', '未知错误')}"
            }

    async def _handle_update_incident_status_intent(
        self,
        user_message: str,
        messages: List[Dict[str, str]],
        provider: str,
        api_key: str,
        base_url: Optional[str] = None,
        auth_code: Optional[str] = None,
        flux_base_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """处理更新事件状态意图"""
        try:
            # 提取更新参数
            extracted_params = await self._extract_update_status_params(
                user_message, messages, provider, api_key, base_url
            )
        except Exception as e:
            # 参数提取失败，按普通聊天处理
            chat_result = await self.chat(messages, provider, api_key, base_url)
            chat_result["type"] = "text"
            return chat_result

        uuids = extracted_params.get("uuids", [])
        name = extracted_params.get("name")
        deal_status = extracted_params.get("deal_status")
        deal_comment = extracted_params.get("deal_comment", "处置完成")

        # If name is provided but no UUIDs, search for it
        if not uuids and name:
            if not auth_code or not flux_base_url:
                return {
                    "success": True,
                    "type": "text",
                    "message": "缺少 Flux 认证信息。请先登录系统。"
                }

            # Search incident by name (reuse existing method)
            searched_uuid = await self._search_incident_by_name(
                name=name,
                auth_code=auth_code,
                flux_base_url=flux_base_url
            )

            if not searched_uuid:
                return {
                    "success": True,
                    "type": "text",
                    "message": f"未找到名称为 '{name}' 的安全事件。\n\n建议：\n• 请确认事件名称是否正确\n• 使用'查询事件列表'查看所有可用事件\n• 提供完整的事件ID（格式：incident-xxx）"
                }

            # Convert single UUID to list format
            uuids = [searched_uuid]

        if not uuids:
            return {
                "success": True,
                "type": "text",
                "message": "我识别到您想更新事件状态，但没有找到事件ID。\n\n请提供以下信息之一：\n• 事件ID（格式：incident-xxx）\n• 事件名称（用引号括起，如：'主机存在漏洞'）\n• 事件编号（如：第一个事件、事件#1）"
            }

        if deal_status is None:
            return {
                "success": True,
                "type": "text",
                "message": "我识别到您想更新事件状态，但没有明确新的处置状态。请说明要更新为什么状态（如：已处置、处置中、已挂起等）。"
            }

        # 使用 SecurityIncidentsService
        from .security_incidents_service import SecurityIncidentsService

        if not auth_code or not flux_base_url:
            return {
                "success": True,
                "type": "text",
                "message": "缺少 Flux 认证信息。请先登录系统。"
            }

        incidents_service = SecurityIncidentsService()

        # 调用批量更新接口
        result = await incidents_service.update_incident_status(
            auth_code=auth_code,
            base_url=flux_base_url,
            uuids=uuids,
            deal_status=deal_status,
            deal_comment=deal_comment
        )

        if result.get("success"):
            data = result.get("data", {})
            total = data.get("total", 0)
            succeeded_num = data.get("succeededNum", 0)

            status_names = {
                0: "待处置",
                10: "处置中",
                40: "已处置",
                50: "已挂起",
                60: "接受风险",
                70: "已遏制"
            }

            status_name = status_names.get(deal_status, str(deal_status))

            message = f"批量更新成功！\n\n"
            message += f"• 总事件数: {total}\n"
            message += f"• 成功更新: {succeeded_num}\n"
            message += f"• 更新失败: {total - succeeded_num}\n\n"
            message += f"所有事件已标记为\"{status_name}\"。"

            return {
                "success": True,
                "type": "incident_status_updated",
                "message": message,
                "update_result": {
                    "total": total,
                    "succeededNum": succeeded_num,
                    "failedNum": total - succeeded_num,
                    "statusName": status_name,
                    "statusValue": deal_status
                }
            }
        else:
            return {
                "success": True,
                "type": "text",
                "message": f"批量更新失败：{result.get('message', '未知错误')}"
            }

    async def _extract_incidents_params(
        self,
        user_message: str,
        messages: List[Dict[str, str]],
        provider: str,
        api_key: str,
        base_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """从用户消息中提取事件查询参数"""
        history_text = "\n".join([
            f"{msg.get('role', 'user')}: {msg.get('content', '')}"
            for msg in messages[-5:]
        ])

        extraction_prompt = f"""你是一个安全事件查询参数提取助手。从用户消息中提取查询参数。

用户消息: {user_message}
对话历史: {history_text}

请提取以下信息：
- startTimestamp: 起始时间戳（Unix时间戳，如 1706745600），如果未指定则为最近7天
- endTimestamp: 结束时间戳（Unix时间戳，如 1706832000），如果未指定则为当前时间
- timeField: 时间字段（endTime/startTime/auditTime/updateTime，默认endTime）
- severities: 严重等级数组（1=低危, 2=中危, 3=高危, 4=严重）
- dealStatus: 处置状态数组（0=未处置, 10=处置中, 40=已处置, 50=已挂起, 60=接受风险, 70=已遏制）
- pageSize: 每页条数（默认20）
- page: 页码（默认1）
- sort: 排序规则（默认 "endTime:desc,severity:desc"）

返回 JSON 格式（只返回 JSON，不要其他内容）:
{{
  "startTimestamp": 1706745600 | null,
  "endTimestamp": 1706832000 | null,
  "timeField": "endTime" | null,
  "severities": [1, 2, 3] | [],
  "dealStatus": [0] | [],
  "pageSize": 20 | null,
  "page": 1 | null,
  "sort": "endTime:desc,severity:desc" | null
}}"""

        try:
            response = await self.chat(
                messages=[{"role": "user", "content": extraction_prompt}],
                provider=provider,
                api_key=api_key,
                base_url=base_url
            )

            if response.get("success"):
                response_text = response.get("message", "")
                json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
                if json_match:
                    try:
                        params = json.loads(json_match.group())
                        return params
                    except json.JSONDecodeError:
                        pass

            return {}

        except Exception:
            return {}

    async def _extract_incident_proof_params(
        self,
        user_message: str,
        messages: List[Dict[str, str]],
        provider: str,
        api_key: str,
        base_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """从用户消息中提取事件详情参数（支持UUID或事件名称）"""
        history_text = "\n".join([
            f"{msg.get('role', 'user')}: {msg.get('content', '')}"
            for msg in messages[-10:]
        ])

        extraction_prompt = f"""你是一个事件详情查询参数提取助手。从用户消息中提取事件ID或事件名称。

用户消息: {user_message}
对话历史: {history_text}

请按优先级提取以下信息：
1. **uuid**: 事件ID（格式：incident-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx）
   - 直接提供完整UUID
   - 引用格式: "第一个事件", "事件 #1", "incident-xxx"

2. **name**: 事件名称（当没有UUID时使用）
   - 从用户消息中提取引用的事件名称
   - 通常是引号内的文本，如 "查看'主机存在扫描工具nmap枚举域用户等内网横向行为'这个事件的详情"
   - 事件名称可能完整或部分匹配

返回 JSON 格式（只返回 JSON，不要其他内容）:
{{
  "uuid": "incident-528fdb4e-6720-4b42-8db1-be2e8ba76bec" | null,
  "name": "主机存在扫描工具nmap枚举域用户等内网横向行为" | null
}}

注意：
- 如果有明确的UUID，优先返回uuid
- 如果用户引用了事件名称（用引号括起或明确表达），提取到name
- 如果用户说"第一个"/"事件#1"等，尝试从对话历史的incidents_list数据中提取对应UUID
- 如果都提取不到，返回null
"""

        try:
            response = await self.chat(
                messages=[{"role": "user", "content": extraction_prompt}],
                provider=provider,
                api_key=api_key,
                base_url=base_url
            )

            if response.get("success"):
                response_text = response.get("message", "")
                json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
                if json_match:
                    try:
                        params = json.loads(json_match.group())
                        return {
                            "uuid": params.get("uuid"),
                            "name": params.get("name")
                        }
                    except json.JSONDecodeError:
                        pass

            return {"uuid": None, "name": None}

        except Exception:
            return {"uuid": None, "name": None}

    async def _search_incident_by_name(
        self,
        name: str,
        auth_code: str,
        flux_base_url: str
    ) -> Optional[str]:
        """根据事件名称搜索事件，返回匹配的UUID"""

        from .security_incidents_service import SecurityIncidentsService

        # Use expanded time range (last 30 days) for better search coverage
        import time
        end_timestamp = int(time.time())
        start_timestamp = end_timestamp - (30 * 24 * 60 * 60)  # 30 days ago

        incidents_service = SecurityIncidentsService()

        # Query incidents with expanded time range
        result = await incidents_service.get_incidents(
            auth_code=auth_code,
            base_url=flux_base_url,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            time_field="endTime",
            page_size=100,  # Get more results for better matching
            page=1,
            sort="endTime:desc"
        )

        if not result.get("success"):
            return None

        data = result.get("data", {})
        incidents = data.get("item", [])

        # Search for exact or partial name match
        best_match = None

        for incident in incidents:
            incident_name = incident.get("name", "")
            if name.strip() == incident_name:
                # Exact match - return immediately
                return incident.get("uuId")
            elif name.strip() in incident_name or incident_name in name.strip():
                # Partial match - store as fallback
                if not best_match:
                    best_match = incident.get("uuId")

        # Return best partial match if no exact match found
        return best_match

    async def _extract_update_status_params(
        self,
        user_message: str,
        messages: List[Dict[str, str]],
        provider: str,
        api_key: str,
        base_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """从用户消息中提取更新状态参数"""
        history_text = "\n".join([
            f"{msg.get('role', 'user')}: {msg.get('content', '')}"
            for msg in messages[-5:]
        ])

        extraction_prompt = f"""你是一个事件状态更新参数提取助手。从用户消息中提取更新参数。

用户消息: {user_message}
对话历史: {history_text}

请按优先级提取以下信息：
1. **uuids**: 事件ID列表（数组，格式：["incident-xxx", "incident-yyy"]）
   - 直接提供完整UUID列表
   - 引用格式: "第一个事件", "事件 #1, #2"

2. **name**: 单个事件名称（当没有UUID时使用）
   - 从用户消息中提取引用的事件名称
   - 通常是引号内的文本，如 "更改'主机存在Struts2-048远程命令执行漏洞（CVE-2017-9791）（企图）'事件处置状态"
   - 事件名称可能完整或部分匹配

3. **deal_status**: 处置状态（0=待处置, 10=处置中, 40=已处置, 50=已挂起, 60=接受风险, 70=已遏制）
4. **deal_comment**: 操作备注/说明

状态映射规则：
- "已处置" / "处置完成" / "完成" / "fixed" / "resolved" → 40
- "处置中" / "处理中" / "进行中" / "in progress" → 10
- "已挂起" / "暂停" / "挂起" / "suspended" → 50
- "接受风险" / "风险接受" / "accept risk" → 60
- "已遏制" / "已控制" / "contained" → 70
- "未处置" / "待处置" / "pending" → 0

返回 JSON 格式（只返回 JSON，不要其他内容）:
{{
  "uuids": ["incident-xxx", "incident-yyy"] | [],
  "name": "主机存在Struts2-048远程命令执行漏洞（CVE-2017-9791）（企图）" | null,
  "deal_status": 40 | null,
  "deal_comment": "处置完成" | null
}}

注意：
- 如果有明确的UUID列表，优先返回uuids
- 如果用户引用了单个事件名称（用引号括起或明确表达），提取到name
- 如果用户说"第一个"/"事件#1"等，尝试从对话历史的incidents_list数据中提取对应UUID
- uuids和name通常不会同时出现
"""

        try:
            response = await self.chat(
                messages=[{"role": "user", "content": extraction_prompt}],
                provider=provider,
                api_key=api_key,
                base_url=base_url
            )

            if response.get("success"):
                response_text = response.get("message", "")
                json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
                if json_match:
                    try:
                        params = json.loads(json_match.group())
                        return {
                            "uuids": params.get("uuids", []),
                            "name": params.get("name"),
                            "deal_status": params.get("deal_status"),
                            "deal_comment": params.get("deal_comment")
                        }
                    except json.JSONDecodeError:
                        pass

            return {}

        except Exception:
            return {}
