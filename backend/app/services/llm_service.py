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

    def _extract_incident_uuids_from_text(self, text: str) -> List[str]:
        """从文本中提取 incident UUID 列表（按出现顺序去重）"""
        if not text:
            return []

        pattern = r'incident-[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}'
        matches = re.findall(pattern, text, flags=re.IGNORECASE)

        unique_matches: List[str] = []
        seen = set()
        for match in matches:
            normalized = match.lower()
            if normalized in seen:
                continue
            seen.add(normalized)
            unique_matches.append(match)

        return unique_matches

    def _extract_first_incident_uuid_from_text(self, text: str) -> Optional[str]:
        """从文本中提取第一个 incident UUID"""
        uuids = self._extract_incident_uuids_from_text(text)
        return uuids[0] if uuids else None

    def _extract_ipv4s_from_text(self, text: str) -> List[str]:
        """从文本中提取 IPv4 地址列表（按出现顺序去重）"""
        if not text:
            return []

        # Use lookarounds instead of \b so it still matches in Chinese text like “查询1.2.3.4是否封禁”
        pattern = r'(?<![\d.])(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)(?![\d.])'
        matches = re.findall(pattern, text)

        unique_matches: List[str] = []
        seen = set()
        for match in matches:
            if match in seen:
                continue
            seen.add(match)
            unique_matches.append(match)

        return unique_matches

    def _has_referential_ip_phrase(self, text: str) -> bool:
        """判断文本是否包含“这个IP/该IP”等指代表达"""
        if not text:
            return False
        return bool(re.search(r'(这个IP|该IP|这个ip|该ip|这个地址|该地址|此IP|它)', text))

    def _resolve_recent_ip_from_messages(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """从最近对话消息中回溯一个可用IP"""
        for msg in reversed(messages[-20:]):
            content = msg.get("content", "")
            ips = self._extract_ipv4s_from_text(content)
            if ips:
                return ips[0]
        return None

    def _normalize_device_name(self, device_name: str) -> str:
        """归一化设备名称，便于匹配"""
        if not device_name:
            return ""
        normalized = str(device_name).strip().strip('“”"\'`')
        normalized = re.sub(r'^\s*(?:设备|防火墙|网关)\s*', '', normalized, flags=re.IGNORECASE)
        normalized = re.sub(r'\s+', '', normalized)
        return normalized.lower()

    def _sanitize_device_name_candidate(self, candidate: str) -> Optional[str]:
        """清洗候选设备名称，过滤“这个设备”等无效占位词"""
        if not candidate:
            return None

        value = str(candidate).strip().strip('“”"\'`')
        value = re.sub(r'^\s*(?:设备|防火墙|网关)\s*', '', value, flags=re.IGNORECASE)
        value = re.sub(r'^\s*(?:这个|该|此)\s*', '', value)
        value = re.sub(r'\s*(?:封禁|进行封禁|联动封禁|操作)\s*$', '', value, flags=re.IGNORECASE)

        # 英文/编号设备常见“AF_002设备”写法可安全去除后缀
        if re.fullmatch(r'[A-Za-z0-9_-]{2,80}(?:设备|防火墙|网关)', value):
            value = re.sub(r'(?:设备|防火墙|网关)$', '', value, flags=re.IGNORECASE)

        value = value.strip().strip('“”"\'`')

        placeholders = {
            "这个", "该", "此", "它",
            "设备", "防火墙", "网关",
            "这个设备", "该设备", "此设备",
            "这个防火墙", "该防火墙", "此防火墙",
            "这个网关", "该网关", "此网关",
        }
        if re.fullmatch(r'第[一二两三四五六七八九十\d]+个?(?:设备|防火墙|网关)?', value):
            return None

        if not value or value in placeholders or len(value) < 2:
            return None

        return value

    def _extract_recent_offered_devices(self, messages: List[Dict[str, str]]) -> List[str]:
        """从最近助手消息中提取可选设备列表（用于上下文追问）"""
        seen = set()
        devices: List[str] = []

        for msg in reversed(messages[-12:]):
            if msg.get("role") != "assistant":
                continue

            content = msg.get("content", "")
            if not content or ("可用防火墙设备" not in content and "可用设备" not in content):
                continue

            for line in content.splitlines():
                line = line.strip()
                if not line:
                    continue

                match = re.match(r'^[•\-\*]\s*(.+?)\s*$', line)
                if not match:
                    continue

                cleaned = self._sanitize_device_name_candidate(match.group(1))
                if not cleaned:
                    continue

                normalized = self._normalize_device_name(cleaned)
                if normalized and normalized not in seen:
                    seen.add(normalized)
                    devices.append(cleaned)

            if devices:
                break

        return devices

    def _extract_device_ordinal(self, text: str) -> Optional[int]:
        """提取“第N个设备”中的序号（1-based）"""
        if not text:
            return None

        digit_match = re.search(r'第\s*(\d{1,2})\s*(?:个|台)?(?:设备|防火墙|网关)?', text)
        if digit_match:
            try:
                value = int(digit_match.group(1))
                return value if value > 0 else None
            except ValueError:
                return None

        cn_match = re.search(r'第\s*([零一二两三四五六七八九十]{1,3})\s*(?:个|台)?(?:设备|防火墙|网关)?', text)
        if not cn_match:
            return None

        token = cn_match.group(1)
        mapping = {
            "零": 0, "一": 1, "二": 2, "两": 2, "三": 3, "四": 4,
            "五": 5, "六": 6, "七": 7, "八": 8, "九": 9
        }
        if token == "十":
            return 10
        if "十" in token:
            left, right = token.split("十", 1)
            tens = mapping.get(left, 1 if left == "" else None)
            ones = mapping.get(right, 0 if right == "" else None)
            if tens is None or ones is None:
                return None
            value = tens * 10 + ones
            return value if value > 0 else None

        value = mapping.get(token)
        return value if value and value > 0 else None

    def _resolve_device_name_from_messages(self, messages: List[Dict[str, str]], user_message: str) -> Optional[str]:
        """根据最近“可用设备列表”上下文解析设备名称"""
        devices = self._extract_recent_offered_devices(messages)
        if not devices:
            return None

        normalized_user_text = self._normalize_device_name(user_message)
        for device in devices:
            normalized_device = self._normalize_device_name(device)
            if not normalized_device:
                continue
            if normalized_device in normalized_user_text:
                return device

        ordinal = self._extract_device_ordinal(user_message)
        if ordinal and 1 <= ordinal <= len(devices):
            return devices[ordinal - 1]

        return None

    def _has_recent_ipblock_prompt(self, messages: List[Dict[str, str]]) -> bool:
        """判断最近对话是否进入“选择联动设备”阶段"""
        recent_text = "\n".join(
            msg.get("content", "")
            for msg in messages[-10:]
            if msg.get("role") == "assistant"
        )
        if not recent_text:
            return False

        return bool(re.search(
            r'(准备执行联动封禁|请先指定防火墙设备名称|可用防火墙设备|使用“.+”封禁这个IP|回复：使用“)',
            recent_text
        ))

    def _extract_device_name_from_text(self, text: str) -> Optional[str]:
        """从文本中提取设备名称（支持中文引号和自然语言短语）"""
        if not text:
            return None

        patterns = [
            r'(?:使用|用|选择|指定)[\s:：]*[“"\'`]([^”"\'`]{2,80})[”"\'`]',
            r'(?:设备|防火墙|网关)\s*(?:名称)?[\s:：]+([^\s，。,；;]{2,80})',
            r'(?:使用|用|选择|指定)\s*([^\s，。,；;]{2,80})\s*(?:这个|该)?(?:设备|防火墙|网关)?',
            r'\b(AF[_-]?\d+|EDR[_-]?\d+|[A-Za-z]+[_-]?\d+)\b',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                candidate = self._sanitize_device_name_candidate((match.group(1) or "").strip())
                if candidate:
                    return candidate

        return None

    def _infer_device_type_from_name(self, device_name: str) -> str:
        """根据设备名称推断设备类型"""
        if not device_name:
            return "AF"
        if "EDR" in device_name.upper():
            return "EDR"
        return "AF"

    def _is_ipblock_direct_intent(self, messages: List[Dict[str, str]], user_message: str) -> bool:
        """判断是否是明确的IP封禁相关意图（无需依赖LLM意图识别）"""
        if not user_message:
            return False

        has_ip = len(self._extract_ipv4s_from_text(user_message)) > 0
        has_referential_ip = self._has_referential_ip_phrase(user_message)
        has_recent_ip = bool(self._resolve_recent_ip_from_messages(messages))
        block_words = bool(re.search(r'(封禁|拉黑|阻断|拦截|解封|放行|黑名单|白名单)', user_message))
        status_words = bool(re.search(r'(查询|检查|状态|是否被封禁|有没有封禁|封禁情况)', user_message))

        if has_ip and (block_words or status_words):
            return True

        if has_referential_ip and has_recent_ip and (block_words or status_words):
            return True

        return False

    def _is_ipblock_followup_intent(self, messages: List[Dict[str, str]], user_message: str) -> bool:
        """判断是否属于IP封禁的上下文追问（避免落入普通聊天）"""
        if not user_message:
            return False

        block_words = bool(re.search(r'(封禁|拉黑|阻断|拦截|解封|放行|黑名单|白名单)', user_message))
        has_ip = len(self._extract_ipv4s_from_text(user_message)) > 0
        has_referential_ip = self._has_referential_ip_phrase(user_message)
        has_recent_ip = bool(self._resolve_recent_ip_from_messages(messages))
        has_recent_prompt = self._has_recent_ipblock_prompt(messages)
        direct_device_name = self._extract_device_name_from_text(user_message)
        context_device_name = self._resolve_device_name_from_messages(messages, user_message)
        has_device_words = bool(re.search(r'(设备|防火墙|网关|联动)', user_message))
        has_use_words = bool(re.search(r'(使用|用|选择|指定)', user_message))
        has_block_status_words = bool(re.search(r'(是否被封禁|封禁状态|封禁情况|查询封禁|检查封禁)', user_message))

        # 显式封禁语义 + IP，直接判定为 ipblock
        if block_words and has_ip:
            return True
        if has_ip and has_block_status_words:
            return True

        # “封禁这个IP”之类：无显式IP但有历史IP
        if block_words and has_referential_ip and has_recent_ip:
            return True

        # “使用某设备/防火墙”追问：只要近期已进入设备选择阶段，直接走ipblock
        if has_recent_prompt and (direct_device_name or context_device_name):
            return True

        if has_recent_prompt and has_use_words and has_device_words:
            return True

        if has_device_words and has_recent_ip and (block_words or has_use_words):
            return True

        return False

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
            # 先检查场景确认关键词（优先级最高，避免误识别）
            if "确认执行" in user_message or "confirm" in user_message.lower():
                # 场景确认消息，直接识别为场景意图
                intent = "daily_high_risk_closure"
                confidence = 1.0
            elif self._is_ipblock_direct_intent(messages, user_message):
                # 明确封禁/查询IP状态，不依赖LLM意图识别
                intent = "ipblock"
                confidence = 1.0
            elif self._is_ipblock_followup_intent(messages, user_message):
                # 强上下文兜底：设备名追问/代词追问直接走ip封禁
                intent = "ipblock"
                confidence = 1.0
            else:
                # 其他情况，使用LLM进行意图识别
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
            elif intent == "get_incident_entities":
                return await self._handle_get_incident_entities_intent(
                    user_message, messages, provider, api_key, base_url,
                    auth_code, flux_base_url
                )
            elif intent == "update_incident_status":
                return await self._handle_update_incident_status_intent(
                    user_message, messages, provider, api_key, base_url,
                    auth_code, flux_base_url
                )
            elif intent == "get_log_count":
                return await self._handle_get_log_count_intent(
                    user_message, messages, provider, api_key, base_url,
                    auth_code, flux_base_url
                )
            elif intent == "daily_high_risk_closure":
                return await self._handle_scenario_intent(
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
        from .skills_registry import get_intent_catalog

        intent_catalog = get_intent_catalog()
        intent_lines = []
        allowed_intents = []

        for idx, intent_def in enumerate(intent_catalog, start=1):
            intent_name = intent_def["intent"]
            intent_desc = intent_def["description"]
            intent_lines.append(f"{idx}. {intent_desc} ({intent_name})")
            allowed_intents.append(f"\"{intent_name}\"")

        # Keep general_chat as explicit fallback
        intent_lines.append(f"{len(intent_lines) + 1}. 普通聊天 (general_chat) - 其他对话")
        allowed_intents.append("\"general_chat\"")

        intent_prompt = f"""你是一个意图识别助手。判断用户消息的意图类型。

用户消息: {user_message}

分析用户是否想要：
{chr(10).join(intent_lines)}

返回 JSON 格式（只返回 JSON，不要其他内容）:
{{
  "intent": {" | ".join(allowed_intents)},
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

        # 规范化 action：当用户表达“封禁/阻断”意图时，不应回落为仅查询状态
        action = extracted_params.get("action", "check")
        has_block_intent = bool(re.search(r'(封禁|拉黑|阻断|拦截|联动封禁|封掉)', user_message))
        has_status_query_intent = bool(re.search(r'(查询|检查|状态|是否被封禁|有没有封禁|封禁情况)', user_message))
        has_recent_ipblock_prompt = self._has_recent_ipblock_prompt(messages)
        if action == "check" and has_block_intent and not has_status_query_intent:
            action = "check_and_block"
            extracted_params["action"] = action

        # 优先使用规则提取用户消息中的显式IP（比LLM提取更稳定）
        direct_ips = self._extract_ipv4s_from_text(user_message)
        if direct_ips:
            extracted_params["ip_address"] = direct_ips[0]

        # 清洗LLM提取的设备名称（防止“这个设备”这类无效值）
        if extracted_params.get("device_name"):
            cleaned_device_name = self._sanitize_device_name_candidate(str(extracted_params.get("device_name")))
            if cleaned_device_name:
                extracted_params["device_name"] = cleaned_device_name
            else:
                extracted_params.pop("device_name", None)

        # 设备名称规则提取（避免仅依赖LLM抽取）
        if not extracted_params.get("device_name"):
            direct_device_name = self._extract_device_name_from_text(user_message)
            if direct_device_name:
                extracted_params["device_name"] = direct_device_name
                extracted_params["device_type"] = extracted_params.get("device_type") or self._infer_device_type_from_name(direct_device_name)

        # 设备上下文回填：支持“使用第一个设备/使用这个设备”这类追问
        if not extracted_params.get("device_name"):
            context_device_name = self._resolve_device_name_from_messages(messages, user_message)
            if context_device_name:
                extracted_params["device_name"] = context_device_name
                extracted_params["device_type"] = extracted_params.get("device_type") or self._infer_device_type_from_name(context_device_name)

        # 处理“封禁这个IP”或“使用某防火墙封禁”这类语句：从最近对话中回溯IP
        should_resolve_recent_ip = (
            self._has_referential_ip_phrase(user_message)
            or action in ["block", "check_and_block"]
            or bool(extracted_params.get("device_name"))
            or has_recent_ipblock_prompt
        )
        if ("ip_address" not in extracted_params or not extracted_params["ip_address"]) and should_resolve_recent_ip:
            recent_ip = self._resolve_recent_ip_from_messages(messages)
            if recent_ip:
                extracted_params["ip_address"] = recent_ip

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
        ip_address = extracted_params["ip_address"]

        if action == "check" and has_recent_ipblock_prompt and not has_status_query_intent:
            action = "check_and_block"
            extracted_params["action"] = action

        # 若已指定设备但action仍是check，升格为联动封禁流程
        if action == "check" and extracted_params.get("device_name") and not has_status_query_intent:
            action = "check_and_block"
            extracted_params["action"] = action

        # 封禁意图但未提供设备名：先引导用户选择联动防火墙
        if action in ["block", "check_and_block"] and not extracted_params.get("device_name"):
            device_type = extracted_params.get("device_type", "AF")
            devices_result = ipblock_service.get_available_devices(device_type=device_type)

            if devices_result.get("success"):
                devices = devices_result.get("devices", [])
                if devices:
                    online_devices = [d for d in devices if str(d.get("device_status", "")).lower() == "online"]
                    preferred_devices = online_devices if online_devices else devices
                    preview_devices = preferred_devices[:8]
                    device_names = [d.get("device_name", "未知设备") for d in preview_devices if d.get("device_name")]

                    suggestion_name = device_names[0] if device_names else None
                    device_lines = "\n".join([f"• {name}" for name in device_names]) if device_names else "• 暂无可展示设备"
                    suffix = f"\n\n例如：使用“{suggestion_name}”封禁这个IP" if suggestion_name else "\n\n请回复：使用“某防火墙名称”封禁这个IP"

                    return {
                        "success": True,
                        "type": "text",
                        "message": f"已定位目标IP：{ip_address}。\n准备执行联动封禁，请先指定防火墙设备名称。\n\n可用防火墙设备：\n{device_lines}{suffix}"
                    }

                return {
                    "success": True,
                    "type": "text",
                    "message": f"已定位目标IP：{ip_address}，但当前未查询到可用防火墙设备，请先检查联动设备配置。"
                }

            error_info = devices_result.get("error_info", {})
            return {
                "success": True,
                "type": "text",
                "message": error_info.get("friendly_message", "查询可用防火墙设备失败，请稍后重试。")
            }

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
                block_params = result["block_params"]
                auto_execute = bool(re.search(r'(封禁|拉黑|阻断|拦截|联动|使用|用)', user_message)) and not has_status_query_intent

                if auto_execute:
                    # 用户已明确设备，直接执行封禁
                    block_result = ipblock_service.block_ip(
                        ip_address=block_params["ip"],
                        device_id=block_params["device_id"],
                        device_name=block_params["device_name"],
                        device_type=block_params.get("device_type", "AF"),
                        device_version=block_params.get("device_version", ""),
                        block_type=block_params.get("block_type", "SRC_IP"),
                        time_type=block_params.get("time_type", "forever"),
                        time_value=block_params.get("time_value"),
                        time_unit=block_params.get("time_unit", "d"),
                        reason=block_params.get("reason", "")
                    )

                    if block_result.get("success"):
                        import time
                        return {
                            "success": True,
                            "type": "ipblock_summary",
                            "message": f"已执行联动封禁：IP {ip_address} -> 设备 {block_params['device_name']}",
                            "ipblock_summary_data": {
                                "ip": block_params["ip"],
                                "device_name": block_params["device_name"],
                                "device_type": block_params.get("device_type", "AF"),
                                "block_type": block_params.get("block_type", "SRC_IP"),
                                "time_type": block_params.get("time_type", "forever"),
                                "time_value": block_params.get("time_value"),
                                "time_unit": block_params.get("time_unit", "d"),
                                "reason": block_params.get("reason", ""),
                                "rule_count": block_result.get("rule_count", 0),
                                "timestamp": int(time.time() * 1000)
                            }
                        }

                    error_info = block_result.get("error_info", {})
                    return {
                        "success": True,
                        "type": "text",
                        "message": error_info.get("friendly_message", block_result.get("message", "联动封禁失败"))
                    }

                # 未明确执行，走确认对话框
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
- device_name: 设备名称（如 物联网安全网关）
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

解析规则补充：
- 若用户消息包含明确IP，优先提取该IP
- 若用户说“这个IP/该IP/这个地址”等指代词，请从对话历史中选择最近提及的IP作为 ip_address
- 若既无明确IP也无法从历史定位，则返回 null

返回 JSON 格式（只返回 JSON，不要其他内容）:
{{
  "ip_address": "192.168.1.100" | null,
  "device_name": "物联网安全网关" | null,
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

        # If name filter is specified, increase page size to get more results for filtering
        name_filter = extracted_params.get("name")
        if name_filter:
            extracted_params["page_size"] = 200  # Get more results for client-side filtering
            extracted_params["page"] = 1

        # 调用查询接口
        result = await incidents_service.get_incidents(
            auth_code=auth_code,
            base_url=flux_base_url,
            **extracted_params
        )

        if result.get("success"):
            data = result.get("data", {})
            items = data.get("item", [])

            # Client-side filtering by name
            if name_filter and items:
                filtered_items = [
                    item for item in items
                    if name_filter.lower() in item.get("name", "").lower()
                ]

                # Update total and items
                total_filtered = len(filtered_items)
                original_total = data.get("total", 0)

                return {
                    "success": True,
                    "type": "incidents_list",
                    "message": f"查询成功！找到 {total_filtered} 条名称包含'{name_filter}'的安全事件（共筛选 {original_total} 条）。",
                    "incidents_data": {
                        "total": total_filtered,
                        "items": filtered_items
                    }
                }
            else:
                total = data.get("total", 0)

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
        # 优先使用正则直接提取，避免上下文序号场景完全依赖 LLM
        uuid = self._extract_first_incident_uuid_from_text(user_message)
        name = None

        if not uuid:
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

    async def _handle_get_incident_entities_intent(
        self,
        user_message: str,
        messages: List[Dict[str, str]],
        provider: str,
        api_key: str,
        base_url: Optional[str] = None,
        auth_code: Optional[str] = None,
        flux_base_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """处理查看事件外网IP实体意图"""
        # 优先使用正则直接提取，避免上下文序号场景完全依赖 LLM
        uuid = self._extract_first_incident_uuid_from_text(user_message)
        name = None

        if not uuid:
            try:
                # 提取事件ID
                extracted_params = await self._extract_incident_entities_params(
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
                "message": "我识别到您想查看事件的外网IP实体，但没有找到事件ID。请提供事件ID（格式：incident-xxx）或事件名称。"
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

        # 调用外网IP实体查询接口
        result = await incidents_service.get_incident_entities_ip(
            auth_code=auth_code,
            base_url=flux_base_url,
            uuid=uuid
        )

        # DEBUG: 检查API调用结果
        print(f"DEBUG incident_entities: API result success={result.get('success')}, result keys={list(result.keys())}")

        if result.get("success"):
            data = result.get("data", {})

            # DEBUG LOG
            print(f"DEBUG incident_entities: Returning type=incident_entities, data keys={list(data.keys())}, item count={len(data.get('item', []))}")
            print(f"DEBUG incident_entities: Full return dict will have entities_data key")

            return {
                "success": True,
                "type": "incident_entities",
                "message": f"事件外网IP实体：找到 {len(data.get('item', []))} 个IP实体",
                "entities_data": data
            }
        else:
            print(f"DEBUG incident_entities: API call failed, returning type=text")
            return {
                "success": True,
                "type": "text",
                "message": f"获取外网IP实体失败：{result.get('message', '未知错误')}"
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
        direct_uuids = self._extract_incident_uuids_from_text(user_message)

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

        uuids = direct_uuids or extracted_params.get("uuids", [])
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
                30: "已遏制",
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
        from datetime import datetime

        # Get current time for LLM reference
        current_time = datetime.now()
        current_timestamp = int(current_time.timestamp())

        history_text = "\n".join([
            f"{msg.get('role', 'user')}: {msg.get('content', '')}"
            for msg in messages[-5:]
        ])

        extraction_prompt = f"""你是一个安全事件查询参数提取助手。从用户消息中提取查询参数。

【重要】时间字段说明：
- startTimestamp/endTimestamp 这两个参数是按"最近发生时间"筛选的
- timeField：如果不特别指定，请在JSON中省略该字段（不要设置为null）
- 系统会自动使用endTime（最近发生时间）进行筛选
- 切勿设置为startTime（会导致按"最早发生时间"筛选，可能查不到事件）

当前时间：{current_time.strftime('%Y-%m-%d %H:%M:%S')}
当前时间戳：{current_timestamp}

用户消息: {user_message}
对话历史: {history_text}

请提取以下信息：
- startTimestamp: 起始时间戳（Unix时间戳）
  • 如果用户说"近X天"/"最近X天"/"过去X天"（如"近30天"），必须计算：当前时间戳 - (X * 86400秒)
  • 例如"近30天" = {current_timestamp} - (30 * 86400) = {current_timestamp - 30*86400}
  • 例如"近7天" = {current_timestamp} - (7 * 86400) = {current_timestamp - 7*86400}
  • 如果未指定时间范围，返回null（系统会默认使用近7天）

- endTimestamp: 结束时间戳（Unix时间戳）
  • 通常为当前时间戳：{current_timestamp}
  • 如果用户指定了结束时间，计算对应时间戳

- timeField: 时间字段（仅当用户明确指定时才设置）
  • 默认省略该字段，系统会使用endTime筛选
  • 切勿设置为startTime（会导致按最早发生时间筛选，可能查不到事件）

- severities: 严重等级数组（1=低危, 2=中危, 3=高危, 4=严重）
- dealStatus: 处置状态数组（0=未处置, 10=处置中, 30=已遏制, 40=已处置, 50=已挂起, 60=接受风险, 70=已遏制(兼容)）
- name: 事件名称（用于客户端过滤，如 "主机存在挖矿病毒"）
- pageSize: 每页条数（默认20，建议当有name过滤时增加到100-200）
- page: 页码（默认1）
- sort: 排序规则（默认 "endTime:desc,severity:desc"）

计算示例（请参考）：
• "近30天" → startTimestamp = {current_timestamp - 30*86400}, endTimestamp = {current_timestamp}
• "近7天" → startTimestamp = {current_timestamp - 7*86400}, endTimestamp = {current_timestamp}
• "近24小时" → startTimestamp = {current_timestamp - 86400}, endTimestamp = {current_timestamp}

返回 JSON 格式（只返回 JSON，不要其他内容）:
{{
  "startTimestamp": 1706745600 | null,
  "endTimestamp": 1706832000 | null,
  "severities": [1, 2, 3] | [],
  "dealStatus": [0] | [],
  "name": "主机存在挖矿病毒" | null,
  "pageSize": 20 | null,
  "page": 1 | null,
  "sort": "endTime:desc,severity:desc" | null
}}
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
                # Use a more robust method to extract JSON with nested arrays/objects
                # Find matching outermost braces
                start_idx = response_text.find('{')
                json_text = None
                if start_idx != -1:
                    # Find matching closing brace by counting
                    count = 1
                    idx = start_idx + 1
                    while idx < len(response_text) and count > 0:
                        if response_text[idx] == '{':
                            count += 1
                        elif response_text[idx] == '}':
                            count -= 1
                        idx += 1
                    if count == 0:
                        json_text = response_text[start_idx:idx]

                if json_text:
                    try:
                        params = json.loads(json_text)

                        # Map camelCase parameter names to snake_case for function signature
                        param_mapping = {
                            "startTimestamp": "start_timestamp",
                            "endTimestamp": "end_timestamp",
                            "timeField": "time_field",
                            "pageSize": "page_size",
                            "dealStatus": "deal_status",
                            "severities": "severities",
                            "name": "name",
                            "page": "page",
                            "sort": "sort"
                        }

                        mapped_params = {}
                        for key, value in params.items():
                            # Skip null values
                            if value is None:
                                continue
                            # Skip empty arrays (but keep empty strings if needed)
                            if isinstance(value, list) and len(value) == 0:
                                continue

                            mapped_key = param_mapping.get(key, key)
                            mapped_params[mapped_key] = value

                        return mapped_params
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

    async def _extract_incident_entities_params(
        self,
        user_message: str,
        messages: List[Dict[str, str]],
        provider: str,
        api_key: str,
        base_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """从用户消息中提取事件外网IP实体查询参数（支持UUID或事件名称）"""
        history_text = "\n".join([
            f"{msg.get('role', 'user')}: {msg.get('content', '')}"
            for msg in messages[-10:]
        ])

        extraction_prompt = f"""你是一个事件外网IP实体查询参数提取助手。从用户消息中提取事件ID或事件名称。

用户消息: {user_message}
对话历史: {history_text}

请按优先级提取以下信息：
1. **uuid**: 事件ID（格式：incident-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx）
   - 直接提供完整UUID
   - 引用格式: "第一个事件", "事件 #1", "incident-xxx"

2. **name**: 事件名称（当没有UUID时使用）
   - 从用户消息中提取引用的事件名称
   - 通常是引号内的文本，如 "查看'主机存在通用JAVA反序列化攻击'这个事件的外网实体"
   - 事件名称可能完整或部分匹配

返回 JSON 格式（只返回 JSON，不要其他内容）:
{{
  "uuid": "incident-528fdb4e-6720-4b42-8db1-be2e8ba76bec" | null,
  "name": "主机存在通用JAVA反序列化攻击" | null
}}

注意：
- 如果有明确的UUID，优先返回uuid
- 如果用户引用了事件名称（用引号括起或明确表达），提取到name
- 如果用户说"第一个"/"事件#1"等，尝试从对话历史的incidents_list数据中提取对应UUID
- 关键词"外网实体"、"IP实体"、"外网IP"表示这是实体查询请求
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

3. **deal_status**: 处置状态（0=待处置, 10=处置中, 30=已遏制, 40=已处置, 50=已挂起, 60=接受风险, 70=已遏制(兼容)）
4. **deal_comment**: 操作备注/说明

状态映射规则：
- "已处置" / "处置完成" / "完成" / "fixed" / "resolved" → 40
- "处置中" / "处理中" / "进行中" / "in progress" → 10
- "已挂起" / "暂停" / "挂起" / "suspended" → 50
- "接受风险" / "风险接受" / "accept risk" → 60
- "已遏制" / "已控制" / "contained" → 30
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

    async def _extract_log_count_params(
        self,
        user_message: str,
        messages: List[Dict[str, str]],
        provider: str,
        api_key: str,
        base_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """从用户消息中提取日志统计参数"""
        from datetime import datetime

        # Get current time for LLM reference
        current_time = datetime.now()
        current_timestamp = int(current_time.timestamp())

        # Format conversation history
        history_text = "\n".join([
            f"{msg.get('role', 'user')}: {msg.get('content', '')}"
            for msg in messages[-5:]
        ])

        # Determine if user wants analysis (趋势、分布、异常)
        user_message_lower = user_message.lower()
        include_comparison = False
        include_distribution = False
        include_trend = False

        if any(keyword in user_message_lower for keyword in ["趋势", "对比", "trend", "compare", "增长", "下降", "变化"]):
            include_comparison = True
            include_trend = True
        elif any(keyword in user_message_lower for keyword in ["分布", "占比", "比例"]):
            include_distribution = True
        elif any(keyword in user_message_lower for keyword in ["异常", "突增", "骤降", "anomaly"]):
            include_comparison = True
            include_distribution = True
            include_trend = True

        extraction_prompt = f"""你是一个日志统计参数提取助手。从用户消息中提取日志统计参数。

当前时间：{current_time.strftime('%Y-%m-%d %H:%M:%S')}
当前时间戳：{current_timestamp}

用户消息: {user_message}
对话历史: {history_text}

请提取以下信息：
- startTimestamp: 起始时间戳（Unix时间戳，近X天 = current_timestamp - X*86400）
- endTimestamp: 结束时间戳（通常为当前时间戳）
- productTypes: 产品类型 ["EDR", "AC", "NTA", "STA", "CWPP", "SSL VPN", "Logger"]
- accessDirections: 访问方向 [1=外对内, 2=内对外, 3=内对内]
- threatClasses: 威胁一级分类 ["94"=Web攻击, "214"=暴力破解, "500"=病毒, "400"=扫描, "300"=DDoS]
- srcIps: 源IP数组
- dstIps: 目的IP数组
- attackStates: 攻击状态 [0=尝试, 1=失败, 2=成功, 3=失陷]
- severities: 严重等级 [0=信息, 1=低危, 2=中危, 3=高危, 4=严重]
- includeComparison: {str(include_comparison).lower()}
- includeDistribution: {str(include_distribution).lower()}
- includeTrend: {str(include_trend).lower()}

返回 JSON 格式（只返回 JSON）:
{{"startTimestamp": 1706745600 | null, "endTimestamp": 1706832000 | null, "productTypes": ["EDR"] | null, "accessDirections": [1] | null, "threatClasses": ["94"] | null, "srcIps": ["192.168.1.100"] | null, "dstIps": ["8.8.8.8"] | null, "attackStates": [0] | null, "severities": [3, 4] | null}}
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
                        
                        # Map camelCase to snake_case
                        param_mapping = {
                            "startTimestamp": "start_timestamp",
                            "endTimestamp": "end_timestamp",
                            "productTypes": "product_types",
                            "accessDirections": "access_directions",
                            "threatClasses": "threat_classes",
                            "srcIps": "src_ips",
                            "dstIps": "dst_ips",
                            "attackStates": "attack_states",
                            "severities": "severities",
                            "includeComparison": "include_comparison",
                            "includeDistribution": "include_distribution",
                            "includeTrend": "include_trend"
                        }
                        
                        mapped_params = {}
                        for key, value in params.items():
                            mapped_key = param_mapping.get(key, key)
                            mapped_params[mapped_key] = value

                        # 添加分析标志位（不依赖LLM返回，使用关键词检测结果）
                        mapped_params["include_comparison"] = include_comparison
                        mapped_params["include_distribution"] = include_distribution
                        mapped_params["include_trend"] = include_trend

                        return mapped_params
                    except json.JSONDecodeError:
                        pass
            
            return {}
        
        except Exception:
            return {}

    async def _handle_get_log_count_intent(
        self,
        user_message: str,
        messages: List[Dict[str, str]],
        provider: str,
        api_key: str,
        base_url: Optional[str] = None,
        auth_code: Optional[str] = None,
        flux_base_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """处理日志统计意图"""
        try:
            # Extract parameters
            extracted_params = await self._extract_log_count_params(
                user_message, messages, provider, api_key, base_url
            )
        except Exception:
            # Fallback to normal chat
            chat_result = await self.chat(messages, provider, api_key, base_url)
            chat_result["type"] = "text"
            return chat_result
        
        # Validate auth
        if not auth_code or not flux_base_url:
            return {
                "success": True,
                "type": "text",
                "message": "缺少 Flux 认证信息。请先登录系统。"
            }
        
        # Call service
        from .network_logs_service import NetworkLogsService
        service = NetworkLogsService()
        
        result = await service.get_log_count(
            auth_code=auth_code,
            base_url=flux_base_url,
            **extracted_params
        )
        
        # Return result
        if result.get("success"):
            data = result.get("data", {})
            total = data.get("total", 0)
            
            # Build message
            filters = data.get("filters", {})
            filter_desc = []
            
            if filters.get("productTypes"):
                filter_desc.append(f"产品类型: {', '.join(filters['productTypes'])}")
            if filters.get("severities"):
                sev_names = {0: "信息", 1: "低危", 2: "中危", 3: "高危", 4: "严重"}
                filter_desc.append(f"严重等级: {', '.join([sev_names.get(s, str(s)) for s in filters['severities']])}")
            if filters.get("accessDirections"):
                dir_names = {1: "外对内", 2: "内对外", 3: "内对内"}
                filter_desc.append(f"访问方向: {', '.join([dir_names.get(d, str(d)) for d in filters['accessDirections']])}")
            
            is_enhanced = data.get("comparisons") or data.get("distributions") or data.get("trend")
            
            if is_enhanced:
                msg = f"查询成功！符合条件的日志总数：{total:,} 条\n\n"
                if filter_desc:
                    msg += "查询条件：\n  • " + "\n  • ".join(filter_desc) + "\n"
                
                if data.get("comparisons"):
                    msg += "\n趋势对比：\n"
                    if "last_week" in data["comparisons"]:
                        lw = data["comparisons"]["last_week"]
                        msg += f"  环比上周: {lw['change_percent']:+.1f}%\n"
                    if "last_month" in data["comparisons"]:
                        lm = data["comparisons"]["last_month"]
                        msg += f"  环比上月: {lm['change_percent']:+.1f}%\n"
            else:
                msg = f"查询成功！符合条件的日志总数：{total:,} 条"
                if filter_desc:
                    msg += "\n\n查询条件：\n  • " + "\n  • ".join(filter_desc)
            
            return {
                "success": True,
                "type": "log_count",
                "message": msg,
                "log_count_data": data
            }
        else:
            return {
                "success": True,
                "type": "text",
                "message": f"查询失败：{result.get('message', '未知错误')}"
            }

    async def _handle_scenario_intent(
        self,
        user_message: str,
        messages: List[Dict[str, str]],
        provider: str,
        api_key: str,
        base_url: Optional[str] = None,
        auth_code: Optional[str] = None,
        flux_base_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """处理每日高危事件闭环场景意图"""
        try:
            # 检查用户消息中是否包含场景确认指令
            # 例如："确认执行场景处置：事件ID xxx，封禁IP yyy"
            if "确认执行" in user_message or "confirm" in user_message.lower():
                # 这是步骤4的确认指令，提取参数并执行
                return await self._handle_scenario_confirm(
                    user_message, auth_code, flux_base_url
                )
            else:
                # 这是步骤1-3的启动指令
                return await self._handle_scenario_start(
                    auth_code, flux_base_url, provider, api_key, base_url
                )
        except Exception as e:
            # 出错时回退到普通聊天
            chat_result = await self.chat(messages, provider, api_key, base_url)
            chat_result["type"] = "text"
            return chat_result

    async def _handle_scenario_start(
        self,
        auth_code: str,
        flux_base_url: str,
        provider: str,
        api_key: str,
        llm_base_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """启动场景任务（步骤1-3）"""
        if not auth_code or not flux_base_url:
            return {
                "success": True,
                "type": "text",
                "message": "缺少 Flux 认证信息。请先登录系统。"
            }

        try:
            from .scenario_orchestration_service import ScenarioOrchestrationService

            service = ScenarioOrchestrationService()

            result = await service.execute_daily_high_risk_closure(
                auth_code=auth_code,
                base_url=flux_base_url,
                provider=provider,
                api_key=api_key,
                llm_base_url=llm_base_url
            )

            if result.get("success"):
                if result.get("completed") and result.get("step") == 1:
                    # 无事件需要处理
                    return {
                        "success": True,
                        "type": "text",
                        "message": result.get("message", "✅ 今日暂无未处置的高危事件")
                    }
                elif result.get("awaiting_confirmation"):
                    # 需要用户确认，返回场景数据
                    return {
                        "success": True,
                        "type": "scenario_start",
                        "message": result.get("message", "已分析事件，等待确认"),
                        "scenario_data": result.get("data", {})
                    }
                else:
                    # 其他情况
                    return {
                        "success": True,
                        "type": "text",
                        "message": result.get("message", "场景执行完成")
                    }
            else:
                # 场景执行失败
                return {
                    "success": True,
                    "type": "text",
                    "message": f"场景执行失败: {result.get('message', '未知错误')}"
                }
        except Exception as e:
            return {
                "success": True,
                "type": "text",
                "message": f"场景执行失败: {str(e)}"
            }

    async def _handle_scenario_confirm(
        self,
        user_message: str,
        auth_code: str,
        flux_base_url: str
    ) -> Dict[str, Any]:
        """确认并执行场景任务（步骤4）"""
        if not auth_code or not flux_base_url:
            return {
                "success": True,
                "type": "text",
                "message": "缺少 Flux 认证信息。请先登录系统。"
            }

        try:
            import re
            from .scenario_orchestration_service import ScenarioOrchestrationService

            # 从用户消息中提取参数
            # 格式: "确认执行场景处置：事件ID xxx,yyy,zzz，封禁IP aaa.bbb.ccc.ddd, eee.fff.ggg.hhh"
            incident_ids_match = re.search(r'事件ID\s+([^\s，]+(?:\s*,\s*[^\s，]+)*)', user_message)
            # 匹配IP地址到字符串结尾（允许点号和逗号）
            ips_match = re.search(r'封禁IP\s+(.+?)$', user_message)

            incident_ids_str = incident_ids_match.group(1) if incident_ids_match else ""
            ips_str = ips_match.group(1) if ips_match else ""

            # 解析事件ID列表
            incident_ids = [iid.strip() for iid in incident_ids_str.split(',') if iid.strip()] if incident_ids_str else []

            # 解析IP列表
            ips_to_block = [ip.strip() for ip in ips_str.split(',') if ip.strip()] if ips_str else []

            if not incident_ids:
                return {
                    "success": True,
                    "type": "text",
                    "message": "未找到事件ID，无法执行场景处置"
                }

            service = ScenarioOrchestrationService()

            result = await service.confirm_and_execute(
                auth_code=auth_code,
                base_url=flux_base_url,
                incident_ids=incident_ids,
                ips_to_block=ips_to_block,
                device_name="物联网安全网关",
                block_duration_days=7
            )

            if result.get("success"):
                scenario_result = result.get("results", {}) or {}
                scenario_result["partial_success"] = bool(result.get("partial_success", False))

                return {
                    "success": True,
                    "type": "scenario_completed",
                    "message": result.get("message", "场景执行完成"),
                    "scenario_result": scenario_result
                }
            else:
                return {
                    "success": True,
                    "type": "text",
                    "message": result.get("message", "场景执行失败")
                }
        except Exception as e:
            return {
                "success": True,
                "type": "text",
                "message": f"场景执行失败: {str(e)}"
            }
