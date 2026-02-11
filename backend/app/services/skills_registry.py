"""
Skills registry shared by frontend capability display and backend intent routing.
"""

from typing import List, Dict, Any


SKILLS_REGISTRY: List[Dict[str, Any]] = [
    {
        "id": "get-incidents",
        "intent": "get_incidents",
        "intent_description": "查询事件列表、筛选安全事件",
        "name": "查询安全事件",
        "nameEn": "Get Incidents",
        "description": "查询和筛选安全事件，支持时间范围、严重程度、处置状态等多维度筛选",
        "icon": "🔍",
        "category": "incident",
        "capabilities": [
            {"title": "自然语言查询", "description": "使用自然语言描述查询条件"},
            {"title": "智能时间解析", "description": "支持最近7天、今天等表达"},
            {"title": "多维度筛选", "description": "按严重程度、处置状态、威胁类型筛选"},
        ],
        "examplePrompts": [
            {"chinese": "最近7天的高危事件", "english": "High severity incidents in last 7 days"},
            {"chinese": "今天未处置的事件", "english": "Undisposed incidents today"},
            {"chinese": "24小时内的严重事件", "english": "Critical incidents in last 24 hours"},
        ],
        "color": "#1976d2",
        "order": 1,
    },
    {
        "id": "get-incident-entities",
        "intent": "get_incident_entities",
        "intent_description": "查询事件外网IP实体和威胁情报",
        "name": "查看IP实体",
        "nameEn": "Get Incident Entities",
        "description": "获取事件关联的外网IP实体，包含威胁等级、地理位置、处置状态等情报",
        "icon": "🌐",
        "category": "incident",
        "capabilities": [
            {"title": "威胁情报", "description": "显示威胁等级和情报标签"},
            {"title": "地理位置", "description": "IP归属地和运营商信息"},
            {"title": "处置状态", "description": "网侧处置状态可视化"},
        ],
        "examplePrompts": [
            {"chinese": "查看事件incident-xxx的外网IP实体", "english": "Show IP entities for incident-xxx"},
            {"chinese": "第一个事件有哪些IP实体", "english": "What IP entities does incident #1 have"},
        ],
        "color": "#2e7d32",
        "order": 2,
    },
    {
        "id": "get-incident-proof",
        "intent": "get_incident_proof",
        "intent_description": "查看事件详情、举证和攻击时间线",
        "name": "事件详细举证",
        "nameEn": "Get Incident Proof",
        "description": "获取事件的详细举证信息和攻击时间线，支持攻击链分析",
        "icon": "📋",
        "category": "incident",
        "capabilities": [
            {"title": "攻击时间线", "description": "按时间顺序展示告警和攻击阶段"},
            {"title": "详细举证", "description": "网络、端点等多维度证据"},
        ],
        "examplePrompts": [
            {"chinese": "查看事件incident-xxx的详细举证", "english": "Show detailed proof for incident-xxx"},
            {"chinese": "显示事件的时间线", "english": "Show the incident timeline"},
        ],
        "color": "#ed6c02",
        "order": 3,
    },
    {
        "id": "update-incident-status",
        "intent": "update_incident_status",
        "intent_description": "批量更新事件处置状态",
        "name": "更新事件状态",
        "nameEn": "Update Incident Status",
        "description": "批量更新安全事件的处置状态，支持处置备注和智能批量操作",
        "icon": "🔄",
        "category": "incident",
        "capabilities": [
            {"title": "批量更新", "description": "一次更新多个事件状态"},
            {"title": "状态映射", "description": "自然语言状态到系统值映射"},
        ],
        "examplePrompts": [
            {"chinese": "把这些事件标记为已处置", "english": "Mark these incidents as disposed"},
            {"chinese": "前5个事件标记为处置中", "english": "Mark first 5 incidents as in progress"},
        ],
        "color": "#9c27b0",
        "order": 4,
    },
    {
        "id": "ip-block",
        "intent": "ipblock",
        "intent_description": "查询IP封禁状态、检查并封禁IP",
        "name": "IP封禁管理",
        "nameEn": "IP Block Management",
        "description": "查询IP封禁状态、执行IP封禁操作，支持永久和临时封禁",
        "icon": "🚫",
        "category": "network",
        "capabilities": [
            {"title": "状态查询", "description": "检查IP是否已被封禁"},
            {"title": "智能封禁", "description": "先检查后封禁，避免重复操作"},
            {"title": "灵活配置", "description": "支持永久/临时、不同封禁类型"},
        ],
        "examplePrompts": [
            {"chinese": "查询100.200.1.200是否被封禁", "english": "Check if 100.200.1.200 is blocked"},
            {"chinese": "封禁1.2.3.4，封禁7天", "english": "Block 1.2.3.4 for 7 days"},
        ],
        "color": "#d32f2f",
        "order": 5,
    },
    {
        "id": "add-asset",
        "intent": "add_asset",
        "intent_description": "创建资产并推断资产参数",
        "name": "添加资产",
        "nameEn": "Add Asset",
        "description": "向平台添加新资产，支持服务器、终端、网络设备等多种资产类型",
        "icon": "➕",
        "category": "asset",
        "capabilities": [
            {"title": "智能推断", "description": "从描述中推断资产类型和系统"},
            {"title": "参数验证", "description": "自动验证必填字段和格式"},
        ],
        "examplePrompts": [
            {"chinese": "添加一个Linux服务器，IP是192.168.1.100", "english": "Add a Linux server, IP 192.168.1.100"},
            {"chinese": "注册一台Windows终端，IP 172.16.0.100", "english": "Register a Windows endpoint, IP 172.16.0.100"},
        ],
        "color": "#0288d1",
        "order": 6,
    },
    {
        "id": "get-log-count",
        "intent": "get_log_count",
        "intent_description": "查询网络安全日志数量、分布和趋势",
        "name": "日志统计分析",
        "nameEn": "Network Log Analytics",
        "description": "统计网络安全日志数量，支持趋势、分布、异常分析",
        "icon": "📈",
        "category": "network",
        "capabilities": [
            {"title": "总量统计", "description": "按时间范围统计日志总数"},
            {"title": "趋势对比", "description": "支持环比上周、上月"},
            {"title": "分布分析", "description": "按严重度、访问方向、产品类型分布"},
        ],
        "examplePrompts": [
            {"chinese": "统计最近7天日志总量", "english": "Count logs in the last 7 days"},
            {"chinese": "分析本周日志趋势和分布", "english": "Analyze weekly log trends and distributions"},
        ],
        "color": "#1565c0",
        "order": 7,
    },
    {
        "id": "daily-high-risk-closure",
        "intent": "daily_high_risk_closure",
        "intent_description": "执行每日高危事件自动闭环场景",
        "name": "每日高危事件闭环",
        "nameEn": "Daily High-Risk Closure",
        "description": "自动分析今日高危事件并联动封禁与处置",
        "icon": "🛡️",
        "category": "general",
        "capabilities": [
            {"title": "自动编排", "description": "查询、分析、确认、执行四步闭环"},
            {"title": "联动处置", "description": "批量封禁威胁IP并更新事件状态"},
        ],
        "examplePrompts": [
            {"chinese": "执行每日高危事件闭环场景", "english": "Run daily high-risk closure scenario"},
            {"chinese": "启动自动处置高危事件", "english": "Start automatic high-risk incident response"},
        ],
        "color": "#455a64",
        "order": 8,
    },
]


def get_skills_metadata() -> List[Dict[str, Any]]:
    """Return metadata for frontend skills panel."""
    skills = sorted(SKILLS_REGISTRY, key=lambda item: item.get("order", 999))
    result: List[Dict[str, Any]] = []
    for skill in skills:
        result.append({
            "id": skill["id"],
            "name": skill["name"],
            "nameEn": skill["nameEn"],
            "description": skill["description"],
            "icon": skill["icon"],
            "category": skill["category"],
            "capabilities": skill["capabilities"],
            "examplePrompts": skill["examplePrompts"],
            "color": skill["color"],
            "order": skill["order"],
        })
    return result


def get_intent_catalog() -> List[Dict[str, str]]:
    """Return intent definitions used by LLM intent-detection prompt."""
    skills = sorted(SKILLS_REGISTRY, key=lambda item: item.get("order", 999))
    return [
        {
            "intent": skill["intent"],
            "description": skill["intent_description"],
        }
        for skill in skills
    ]
