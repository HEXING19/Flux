from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ....services import AuthService


router = APIRouter()
auth_service = AuthService()


class LoginRequest(BaseModel):
    auth_code: str


class LoginResponse(BaseModel):
    success: bool
    message: str


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    登录验证 - 验证联动码

    Args:
        request: 包含联动码的请求

    Returns:
        验证结果
    """
    success, message = auth_service.verify_auth_code(request.auth_code)

    if not success:
        raise HTTPException(status_code=401, detail=message)

    return LoginResponse(success=True, message=message)
