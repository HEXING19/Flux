from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import auth, connectivity, llm


app = FastAPI(
    title="Flux API",
    description="Flux 连通性测试 API",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],  # Vite 默认端口
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(connectivity.router, prefix="/api/v1/connectivity", tags=["连通性测试"])
app.include_router(llm.router, prefix="/api/v1/llm", tags=["大模型"])


@app.get("/")
async def root():
    return {"message": "Flux API is running", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
