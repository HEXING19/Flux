import os
import httpx
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
