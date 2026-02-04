# Flux - AI-Driven Security Operations Platform

Flux is an intelligent security operations platform that leverages Large Language Models (LLMs) to automate security configuration, incident response, and operational workflows. It provides a unified interface for managing security assets, analyzing incidents, blocking threats, and orchestrating response scenarios.

## Project Overview

Flux 集成了大语言模型（LLM）能力，实现了从"业务意图"到"技术配置"的自动转换，提供智能化的安全运营体验。

### Core Features / 核心功能

1. **Security Cockpit Dashboard / 安全驾驶舱** - Real-time monitoring, statistics visualization, and scenario execution
2. **Intelligent Chat Interface / AI 对话助手** - Natural language interaction with 30+ pre-configured operational prompts
3. **Asset Management / 资产管理** - Create and manage assets with AI-powered parameter inference
4. **Security Incidents Management / 安全事件管理** - Query, analyze, and batch update security incidents
5. **IP Blocking Operations / IP封禁** - Check blocking status and execute threat mitigation commands
6. **Network Log Statistics / 日志统计** - Query and analyze network security logs with multi-dimensional filtering
7. **Scenario Orchestration / 场景编排** - Automated incident response workflows with SSE streaming
8. **LLM Integration / 大模型集成** - Multi-provider support (Zhipu AI, OpenAI, Azure, DeepSeek, Custom)
9. **Connectivity Testing / 连通性测试** - Real-time HTTP/HTTPS connectivity testing with WebSocket

## Technology Stack / 技术栈

### Frontend / 前端
- **Framework**: React 19.2.0 + TypeScript 5.9.3
- **Build Tool**: Vite 7.2.4
- **UI Library**: Material-UI (MUI) v7.3.7
- **Routing**: React Router v7.13.0
- **State Management**: React Hooks (useState, useEffect, useCallback)
- **HTTP Client**: Axios 1.13.3
- **Real-time Communication**: WebSocket + Server-Sent Events (SSE)
- **Styling**: Emotion (CSS-in-JS) v11.14.0

### Backend / 后端
- **Framework**: FastAPI 0.104.1
- **ASGI Server**: Uvicorn 0.24.0
- **Python Version**: 3.11+
- **WebSocket**: websockets 12.0
- **Data Validation**: Pydantic 2.5.0
- **HTTP Client**: httpx 0.25.2
- **Cryptography**: pycryptodome 3.19.0

## Project Structure / 项目结构

### Frontend Structure
```
frontend/
├── src/
│   ├── components/
│   │   ├── chat/                    # Chat interface components (20+ files)
│   │   │   ├── ChatInterface.tsx     # Main chat container
│   │   │   ├── SkillsPanel/          # Skills button and dialog
│   │   │   ├── AssetConfirmationDialog.tsx
│   │   │   ├── IPBlockConfirmationDialog.tsx
│   │   │   ├── ScenarioProgressDialog.tsx
│   │   │   └── *Table.tsx            # Data display tables
│   │   ├── cockpit/                 # Security cockpit dashboard
│   │   │   ├── SecurityCockpit.tsx   # Main dashboard container
│   │   │   ├── panels/               # Cockpit panels
│   │   │   ├── cards/                # Dashboard cards
│   │   │   └── ModeToggleButton.tsx
│   │   ├── landing/                 # Landing page components
│   │   ├── tool/                    # Tool page components
│   │   └── common/                  # Shared components
│   ├── pages/
│   │   ├── HomePage.tsx             # Landing page with login
│   │   ├── DashboardPage.tsx        # Main dashboard (chat + cockpit)
│   │   └── SettingsPage.tsx         # Settings configuration
│   ├── services/
│   │   ├── api.ts                   # Base API client
│   │   ├── connectivity.ts          # Connectivity test service
│   │   └── cockpitService.ts        # Dashboard data service
│   ├── types/                       # TypeScript type definitions
│   ├── theme/                       # MUI theme configuration
│   ├── config/                      # Configuration files (skills, etc.)
│   ├── hooks/                       # Custom React hooks
│   ├── utils/                       # Utility functions
│   └── assets/                      # Static assets
└── package.json
```

### Backend Structure
```
backend/
├── app/
│   ├── api/v1/endpoints/
│   │   ├── auth.py                  # Authentication endpoints
│   │   ├── connectivity.py          # Connectivity testing
│   │   ├── llm.py                   # LLM integration
│   │   ├── assets.py                # Asset management
│   │   ├── ipblock.py               # IP blocking
│   │   ├── incidents.py             # Security incidents
│   │   ├── logs.py                  # Network logs
│   │   └── dashboard.py             # Dashboard data
│   ├── services/                    # Business logic (9 services)
│   ├── websocket/                   # WebSocket manager
│   │   └── manager.py
│   ├── utils/
│   │   └── sdk/                     # Flux SDK integration
│   │       └── aksk_py3.py
│   └── main.py                      # FastAPI entry
├── venv/                            # Python virtual environment
└── requirements.txt
```

## Quick Start / 快速开始

### Prerequisites / 前置要求
- Node.js 18+ and npm
- Python 3.11+
- Flux platform credentials (auth code and base URL)

### 1. Backend Setup / 启动后端

```bash
cd /Users/hexing/Flux/backend

# Create virtual environment (first time)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start backend server
venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will run at `http://localhost:8000`

API documentation available at `http://localhost:8000/docs`

### 2. Frontend Setup / 启动前端

```bash
cd /Users/hexing/Flux/frontend

# Install dependencies (first time)
npm install

# Start development server
npm run dev
```

Frontend will run at `http://localhost:5173`

### 3. Access the Application / 访问应用

Open browser and navigate to:
- **Home Page / 首页**: http://localhost:5173/
- **Dashboard / 仪表板**: http://localhost:5173/dashboard
- **Settings / 设置**: http://localhost:5173/settings
- **API Docs / API文档**: http://localhost:8000/docs

## Usage Scenarios / 使用场景

### Scenario 1: First-Time Setup and Login / 首次设置和登录

1. **Obtain Flux Credentials / 获取 Flux 凭据**
   - Login to Flux platform
   - Navigate to: Configuration Management → System Settings → Open Platform → Link Code Management
   - Generate and copy your authentication code
   - Note your Flux API base URL (e.g., `https://10.10.10.10`)

2. **Login to Flux AI / 登录 Flux AI**
   - Open http://localhost:5173
   - Enter your authentication code
   - Enter your Flux API base URL
   - Click "Login / 登录" to authenticate

### Scenario 2: Configure LLM Provider / 配置大模型

1. **Navigate to Settings / 进入设置**
   - From dashboard, click "Settings" button in top-right corner

2. **Configure LLM / 配置大模型**
   - Select provider (Zhipu AI / 智谱AI, OpenAI, Azure OpenAI, DeepSeek, or Custom / 自定义)
   - Enter API Key
   - (Optional) Enter custom Base URL for custom provider
   - Click "Test Connection / 测试连接" to verify
   - Click "Save Configuration / 保存配置" when successful

### Scenario 3: Adding Assets via Natural Language / 自然语言添加资产

1. **Open Chat Interface / 打开对话界面**
   - Navigate to dashboard
   - In chat input, type: "Add a new asset with IP 192.168.1.100, name it WebServer, type is Linux"

2. **Review Extracted Parameters / 查看提取的参数**
   - AI will display extracted parameters in a confirmation dialog
   - Review: IP, Asset Name, OS Type, Asset Group, etc.
   - Click "Confirm / 确认" to create asset or "Cancel / 取消" to modify

### Scenario 4: Querying Security Incidents / 查询安全事件

1. **Using Natural Language / 使用自然语言**
   - Type: "Show me high-severity incidents from today"
   - AI automatically filters by severity (3-4) and time range

2. **Review Incident List / 查看事件列表**
   - Incidents displayed in table format
   - View severity, status, source, and time

3. **Update Incident Status / 更新事件状态**
   - Type: "Mark incidents [id1, id2, id3] as disposed"
   - Confirmation dialog shown
   - Bulk update executed after confirmation

### Scenario 5: IP Blocking Workflow / IP封禁流程

1. **Check IP Status / 检查IP状态**
   - Type: "Check if IP 203.0.113.50 is blocked"
   - AI queries blocking status
   - Current blocking rules displayed (if any)

2. **Block Malicious IP / 封禁恶意IP**
   - Type: "Block IP 203.0.113.50 on device AF-Device-01"
   - AI shows available devices
   - Confirmation dialog with blocking parameters
   - Confirm to execute blocking command

### Scenario 6: Executing Automated Scenario / 执行自动化场景

1. **From Security Cockpit / 从安全驾驶舱**
   - Toggle view mode to "Cockpit / 驾驶舱"
   - View dashboard statistics and monitoring
   - Click on scenario card (e.g., "Automated Incident Response")

2. **Scenario Execution / 场景执行**
   - Progress dialog shows step-by-step execution
   - Step 1: Query high-severity incidents
   - Step 2: AI analyzes incidents
   - Step 3: Prepare confirmation for threat mitigation
   - Step 4: Execute bulk IP blocking (after confirmation)

## API Endpoints / API 端点

### Authentication Module / 认证模块
- `POST /api/v1/auth/login` - Authenticate with Flux platform
  - Headers: `X-Auth-Code`, `X-Base-Url`

### LLM Integration Module / 大模型模块
- `POST /api/v1/llm/test` - Test LLM API connectivity
- `POST /api/v1/llm/chat` - Chat with AI assistant
- `POST /api/v1/llm/confirm-asset` - Confirm and create asset
- `GET /api/v1/llm/providers` - Get supported providers
- `GET /api/v1/llm/scenario/stream` - Execute scenario with SSE streaming

### Asset Management Module / 资产管理模块
- `POST /api/v1/assets/create` - Create new asset
- `POST /api/v1/assets/infer` - Infer parameters from natural language
- `GET /api/v1/assets/categories` - Get asset categories

### IP Blocking Module / IP封禁模块
- `POST /api/v1/ipblock/check` - Check IP blocking status
- `POST /api/v1/ipblock/devices` - Get available blocking devices
- `POST /api/v1/ipblock/block` - Execute IP blocking
- `POST /api/v1/ipblock/check-and-block` - Check and prepare block
- `POST /api/v1/ipblock/confirm-block` - Confirm blocking

### Security Incidents Module / 安全事件模块
- `POST /api/v1/incidents/list` - Query incidents with filters
- `GET /api/v1/incidents/{uuid}/proof` - Get incident evidence
- `POST /api/v1/incidents/update-status` - Batch update disposition
- `GET /api/v1/incidents/{uuid}/entities/ip` - Get IP entities

### Network Logs Module / 日志统计模块
- `POST /api/v1/logs/networksecurity/count` - Query log statistics

### Dashboard Module / 驾驶舱模块
- `GET /api/v1/dashboard/statistics` - Get dashboard stats
- `GET /api/v1/dashboard/monitoring` - Get monitoring data
- `GET /api/v1/dashboard/health` - Health check

### Connectivity Testing Module / 连通性测试模块
- `POST /api/v1/connectivity/test` - Start connectivity test
- `WS /api/v1/connectivity/ws/test/{task_id}` - WebSocket for real-time progress

## Development Guide / 开发指南

### Frontend Development / 前端开发

```bash
cd frontend

npm run dev          # Start Vite dev server (port 5173)
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
```

**Adding New Skills / 添加新技能:**
1. Edit `src/config/skills.ts`
2. Add skill definition with category, prompt, and description
3. Skills automatically appear in Skills Panel dialog

### Backend Development / 后端开发

```bash
cd backend
source venv/bin/activate
venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**API Documentation / API 文档:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Adding New Endpoints / 添加新端点:**
1. Create service in `app/services/your_service.py`
2. Create endpoint in `app/api/v1/endpoints/your_endpoint.py`
3. Register router in `app/main.py`

## Technical Highlights / 技术亮点

### Material Design 3 Implementation
- MUI v7 components with latest Material Design 3 guidelines
- Custom theme with light and dark modes
- Responsive layout supporting mobile and desktop

### Real-Time Communication / 实时通信
- **WebSocket**: For connectivity testing progress updates
- **Server-Sent Events (SSE)**: For scenario execution streaming
- **Async Processing**: Backend uses async/await for concurrent operations

### AI Integration / AI 集成
- **Multi-Provider Support**: Zhipu AI, OpenAI, Azure OpenAI, DeepSeek, Custom
- **Streaming Responses**: Real-time chat message streaming
- **Function Calling**: Structured data extraction and tool execution
- **Context Awareness**: Multi-turn conversation with message history

### Data Validation / 数据验证
- **Pydantic**: Request/response validation on backend
- **TypeScript**: Type safety on frontend
- **Custom Validators**: IP address, MAC address, asset parameters

## Troubleshooting / 故障排除

### Backend Issues / 后端问题

**Q: Backend fails to start with "ModuleNotFoundError"**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

**Q: CORS errors when accessing from frontend**
- Check `app/main.py` CORS configuration
- Ensure frontend URL is in `allow_origins`

### Frontend Issues / 前端问题

**Q: Frontend fails to start with "Cannot resolve dependency"**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Q: LLM test connection fails**
- Verify API key is correct
- Check base URL format
- Ensure network allows outbound HTTPS

**Q: Asset creation fails with "Asset already exists"**
- Check if IP already registered in Flux platform
- Use different IP or update existing asset

**Q: IP blocking fails with "Device not found"**
- Query available devices first
- Verify device name matches exactly
- Check device type (AF, etc.)

### WebSocket Issues / WebSocket 问题

**Q: WebSocket connection fails**
- Ensure backend is running on port 8000
- Check if firewall blocking WebSocket upgrade
- Verify WebSocket URL includes task ID

## Version History / 版本历史

### V2.1 (Current)
- Added scenario orchestration with SSE streaming
- Enhanced security cockpit with monitoring panel
- Added skills panel with 30+ pre-configured prompts
- Improved error handling and validation
- Added IP blocking check-and-block workflow

### V2.0
- Added LLM integration with multiple providers
- Added chat interface with AI assistant
- Added asset management with natural language
- Added security incidents management
- Added IP blocking operations
- Added network log statistics
- Added settings page

### V1.0
- Initial release
- Landing page with authentication
- Connectivity testing tool
- Material Design UI

## License / 许可证

[MIT License](LICENSE)
