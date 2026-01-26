from ..utils.sdk.aksk_py3 import Signature


class AuthService:
    """认证服务 - 验证联动码"""

    def verify_auth_code(self, auth_code: str) -> tuple[bool, str]:
        """
        验证联动码

        Args:
            auth_code: 用户提供的联动码

        Returns:
            (是否成功, 消息)
        """
        try:
            # SDK 会自动解码联动码，如果格式错误会抛出异常
            signature = Signature(auth_code=auth_code)
            return True, "验证成功"
        except Exception as e:
            return False, f"联动码验证失败: {str(e)}"
