# Flux Landing 页面

## 项目概述

Flux 是一个 AI 驱动的配置工具 Landing 页面，实现了从"业务意图"到"技术配置"的自动转换演示。

### 核心功能

1. **登录验证** - 使用联动码进行身份验证
2. **连通性测试** - 对目标 API 进行 HTTP/HTTPS 连通性实时测试
3. **Material Design** - 遵循 Google Material Design 设计规范

## 技术栈

### 前端
- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **UI 库**: Material-UI (MUI) v5
- **路由**: React Router v6
- **HTTP 客户端**: Axios
- **实时通信**: WebSocket

### 后端
- **框架**: FastAPI (Python 3.11+)
- **ASGI 服务器**: Uvicorn
- **WebSocket**: websockets
- **SDK**: 复用现有的 `aksk_py3.py` 签名认证

## 项目结构

```
/Users/hexing/Flux/
├── frontend/                # 前端项目 (React + Vite + MUI)
│   ├── src/
│   │   ├── components/      # React 组件
│   │   ├── pages/           # 页面组件
│   │   ├── services/        # API 服务
│   │   ├── hooks/           # 自定义 Hooks
│   │   ├── theme/           # MUI 主题配置
│   │   └── main.tsx         # 应用入口
│   └── package.json
│
├── backend/                 # 后端项目 (FastAPI)
│   ├── app/
│   │   ├── api/             # API 路由
│   │   ├── services/        # 业务逻辑
│   │   ├── websocket/       # WebSocket 管理
│   │   ├── utils/           # 工具函数和 SDK
│   │   └── main.py          # FastAPI 入口
│   └── requirements.txt
│
└── OpenAPIDocument 3/       # 现有 SDK (保持不变)
```

## 快速开始

### 1. 启动后端服务器

```bash
cd /Users/hexing/Flux/backend

# 激活虚拟环境 (首次运行)
source venv/bin/activate

# 启动服务器
venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端将在 `http://localhost:8000` 运行

### 2. 启动前端服务器

```bash
cd /Users/hexing/Flux/frontend

# 安装依赖 (首次运行)
npm install

# 启动开发服务器
npm run dev
```

前端将在 `http://localhost:5173` 运行

### 3. 访问应用

打开浏览器访问:
- **Landing 页面**: http://localhost:5173/
- **工具页面**: http://localhost:5173/tool
- **API 文档**: http://localhost:8000/docs

## 使用说明

### 测试流程

1. **获取联动码**
   - 从平台页面获取联动码（配置管理 → 系统设置 → 开放性 → 联动码管理）

2. **打开工具页面**
   - 访问 http://localhost:5173/tool

3. **输入信息**
   - 联动码: 输入从平台获取的联动码
   - 目标 API 地址: 输入要测试的 API 地址，例如 `https://10.10.10.10/api/xdr/v1/assets/list`

4. **开始测试**
   - 点击"登录并测试"按钮
   - 系统会验证联动码
   - 验证成功后自动启动连通性测试
   - 实时查看测试进度和结果

## API 端点

### 后端 API

- `POST /api/v1/auth/login` - 登录验证
- `POST /api/v1/connectivity/test` - 启动连通性测试
- `WS /api/v1/connectivity/ws/test/{task_id}` - WebSocket 实时推送

### WebSocket 事件

**服务器推送 → 客户端**:
- `test_start`: 测试开始
- `test_progress`: 测试进度更新
- `test_complete`: 测试完成

## 开发说明

### 前端开发

```bash
cd frontend

# 开发模式
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

### 后端开发

```bash
cd backend

# 开发模式 (自动重载)
venv/bin/uvicorn app.main:app --reload

# 生产模式
venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 技术特点

### 1. Material Design 实现
- 使用 MUI v5 组件库
- 遵循 Google Material Design 规范
- 主色调: Material Blue (#1976d2)
- 次要色调: Material Pink (#ff4081)
- 响应式布局: 支持移动端和桌面端

### 2. 实时通信
- WebSocket 实时推送测试进度
- 异步任务处理
- 连接状态管理

### 3. SDK 集成
- 复用现有的 `aksk_py3.py` SDK
- 签名认证机制
- 错误处理和验证

## 故障排除

### 后端启动失败

```bash
# 重新安装依赖
cd backend
venv/bin/pip install -r requirements.txt
```

### 前端启动失败

```bash
# 重新安装依赖
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### WebSocket 连接失败

- 确保后端服务器正在运行
- 检查 CORS 配置
- 查看浏览器控制台错误信息

## 后续扩展

当前实现的核心功能可以进一步扩展：

1. **配置文件生成** - 根据测试结果生成配置文件
2. **多种协议支持** - 添加数据库、Redis 等协议测试
3. **AI 辅助配置** - 集成 LLM API 进行智能配置
4. **用户系统** - 添加完整的用户认证和管理
5. **测试历史** - 保存和查看历史测试记录

## 联系方式

如有问题或建议，请通过以下方式联系:
- 提交 Issue
- 发送邮件

## 许可证

[MIT License](LICENSE)
