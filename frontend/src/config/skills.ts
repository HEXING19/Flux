import type { SkillMetadata } from '../types/skill';

/**
 * Skills configuration for the Flux AI assistant
 * Contains metadata for all 6 supported skills
 */
export const SKILLS_CONFIG: SkillMetadata[] = [
  {
    id: 'get-incidents',
    name: '查询安全事件',
    nameEn: 'Get Incidents',
    description: '查询和筛选安全事件，支持时间范围、严重程度、处置状态等多维度筛选',
    icon: '🔍',
    category: 'incident',
    capabilities: [
      { title: '自然语言查询', description: '使用自然语言描述查询条件' },
      { title: '智能时间解析', description: '支持"最近7天"、"今天"等表达' },
      { title: '多维度筛选', description: '按严重程度、处置状态、威胁类型筛选' },
    ],
    examplePrompts: [
      { chinese: '最近7天的高危事件', english: 'High severity incidents in last 7 days' },
      { chinese: '今天未处置的事件', english: 'Undisposed incidents today' },
      { chinese: '本周所有中危及以上事件', english: 'Medium+ severity incidents this week' },
      { chinese: '查询IP 192.168.1.100的事件', english: 'Incidents for IP 192.168.1.100' },
      { chinese: '24小时内的严重事件', english: 'Critical incidents in last 24 hours' },
    ],
    color: '#1976d2',
    order: 1,
  },
  {
    id: 'get-incident-entities',
    name: '查看IP实体',
    nameEn: 'Get Incident Entities',
    description: '获取事件关联的外网IP实体，包含威胁等级、地理位置、处置状态等情报',
    icon: '🌐',
    category: 'incident',
    capabilities: [
      { title: '威胁情报', description: '显示威胁等级和情报标签' },
      { title: '地理位置', description: 'IP归属地和运营商信息' },
      { title: '处置状态', description: '端侧和网侧处置状态' },
    ],
    examplePrompts: [
      { chinese: '查看事件incident-xxx的外网IP实体', english: 'Show IP entities for incident-xxx' },
      { chinese: '第一个事件有哪些IP实体', english: 'What IP entities does incident #1 have' },
      { chinese: '显示需要封禁的威胁IP', english: 'Show threat IPs that need blocking' },
      { chinese: '这个IP的威胁等级是什么', english: 'What is the threat level of this IP' },
    ],
    color: '#2e7d32',
    order: 2,
  },
  {
    id: 'get-incident-proof',
    name: '事件详细举证',
    nameEn: 'Get Incident Proof',
    description: '获取事件的详细举证信息和攻击时间线，支持完整的攻击链分析',
    icon: '📋',
    category: 'incident',
    capabilities: [
      { title: '攻击时间线', description: '按时间顺序展示告警和攻击阶段' },
      { title: '攻击链分析', description: 'MITRE ATT&CK kill chain可视化' },
      { title: '详细举证', description: '网络、端点、WebShell等多维度证据' },
    ],
    examplePrompts: [
      { chinese: '查看事件incident-xxx的详细举证', english: 'Show detailed proof for incident-xxx' },
      { chinese: '第一个事件的攻击链是什么', english: 'What is the attack chain for incident #1' },
      { chinese: '显示事件的时间线', english: 'Show the incident timeline' },
      { chinese: '这个事件的攻击阶段有哪些', english: 'What are the attack stages of this incident' },
    ],
    color: '#ed6c02',
    order: 3,
  },
  {
    id: 'update-incident-status',
    name: '更新事件状态',
    nameEn: 'Update Incident Status',
    description: '批量更新安全事件的处置状态，支持处置备注和智能批量操作',
    icon: '🔄',
    category: 'incident',
    capabilities: [
      { title: '批量更新', description: '一次更新多个事件状态' },
      { title: '智能引用', description: '从上下文中自动选择事件' },
      { title: '状态映射', description: '自然语言状态到系统值映射' },
    ],
    examplePrompts: [
      { chinese: '把这些事件标记为已处置', english: 'Mark these incidents as disposed' },
      { chinese: '前5个事件标记为处置中', english: 'Mark first 5 incidents as in progress' },
      { chinese: '把高危的设为处置中，备注：需要重点处理', english: 'Set high severity to in progress, note: priority' },
      { chinese: '标记为接受风险', english: 'Mark as accept risk' },
    ],
    color: '#9c27b0',
    order: 4,
  },
  {
    id: 'ip-block',
    name: 'IP封禁管理',
    nameEn: 'IP Block Management',
    description: '查询IP封禁状态、执行IP封禁操作，支持永久和临时封禁',
    icon: '🚫',
    category: 'network',
    capabilities: [
      { title: '状态查询', description: '检查IP是否已被封禁' },
      { title: '智能封禁', description: '先检查后封禁，避免重复操作' },
      { title: '灵活配置', description: '支持永久/临时、不同封禁类型' },
    ],
    examplePrompts: [
      { chinese: '使用AF1封禁192.168.1.50', english: 'Block 192.168.1.50 using AF1' },
      { chinese: '查询100.200.1.200是否被封禁', english: 'Check if 100.200.1.200 is blocked' },
      { chinese: '封禁1.2.3.4，封禁7天，备注：恶意扫描', english: 'Block 1.2.3.4 for 7 days, reason: malicious scan' },
      { chinese: '检查并封禁10.0.0.100，如果没有封禁的话', english: 'Check and block 10.0.0.100 if not blocked' },
    ],
    color: '#d32f2f',
    order: 5,
  },
  {
    id: 'add-asset',
    name: '添加资产',
    nameEn: 'Add Asset',
    description: '向平台添加新资产，支持服务器、终端、网络设备等多种资产类型',
    icon: '➕',
    category: 'asset',
    capabilities: [
      { title: '智能推断', description: '从描述中推断资产类型和系统' },
      { title: '灵活配置', description: '支持资产名称、标签、重要性等配置' },
      { title: '参数验证', description: '自动验证必填字段和格式' },
    ],
    examplePrompts: [
      { chinese: '添加一个Linux服务器，IP是192.168.1.100', english: 'Add a Linux server, IP 192.168.1.100' },
      { chinese: '添加生产数据库服务器，IP 10.0.0.50，名称DB-Primary', english: 'Add production DB server, IP 10.0.0.50, name DB-Primary' },
      { chinese: '注册一台Windows桌面终端，IP 172.16.0.100', english: 'Register a Windows desktop, IP 172.16.0.100' },
      { chinese: '添加核心资产Web服务器，IP 192.168.1.200', english: 'Add core asset web server, IP 192.168.1.200' },
    ],
    color: '#0288d1',
    order: 6,
  },
];

/**
 * Category display names
 */
export const CATEGORY_NAMES: Record<string, string> = {
  all: '全部',
  incident: '事件',
  asset: '资产',
  network: '联动处置',
  general: '通用',
};
