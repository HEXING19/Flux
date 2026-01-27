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

            # 如果不是添加资产的意图，或者置信度太低，按普通聊天处理
            if intent != "add_asset" or confidence < 0.7:
                chat_result = await self.chat(messages, provider, api_key, base_url)
                chat_result["type"] = "text"
                return chat_result

            # Step 2: 提取资产参数
            try:
                extracted_params = await self._extract_asset_params(
                    user_message, messages, provider, api_key, base_url
                )
            except Exception:
                # 参数提取失败，按普通聊天处理
                chat_result = await self.chat(messages, provider, api_key, base_url)
                chat_result["type"] = "text"
                return chat_result

            # Step 3: 使用 AssetService 验证和补充参数
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

            # Step 4: 返回确认信息（不直接创建资产）
            confirmation_msg = "我识别到您想添加一个资产。请确认以下信息："

            return {
                "success": True,
                "type": "asset_confirmation",
                "message": confirmation_msg,
                "asset_params": validated_params
            }

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
        intent_prompt = f"""你是一个意图识别助手。判断用户消息是否是要添加资产到安全平台。

用户消息: {user_message}

分析用户是否想要：
- 添加新资产
- 创建新服务器
- 注册新设备

返回 JSON 格式（只返回 JSON，不要其他内容）:
{{
  "intent": "add_asset" | "general_chat",
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
