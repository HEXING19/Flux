/**
 * Scenario Task Types
 * Types for the daily high-risk incident closure scenario
 */

/**
 * Step status type
 */
export type StepStatus = 'idle' | 'loading' | 'completed' | 'error';

/**
 * Scenario state interface
 */
export interface ScenarioState {
  open: boolean;
  scenarioId: string | null;
  currentStep: number;
  step1Status: StepStatus;
  step2Status: StepStatus;
  step3Status: StepStatus;
  step1Data: Step1Data | null;
  step2Data: Step2Data | null;
  step3Data: Step3Data | null;
  incidentId: string | null;  // 向后兼容，单个事件ID
  incidentIds: string[];  // 新增，多个事件ID
  ipsToBlock: string[];
  error: string | null;

  // 新增：执行结果相关字段
  executionStatus: 'idle' | 'executing' | 'success' | 'partial_success' | 'error';
  executionResult: {
    partial_success?: boolean;
    // 注意：后端直接返回 ip_block 和 incident_updates，没有 results 嵌套层
    ip_block: {
      total: number;
      success: number;
      failed: number;
      details: Array<{ ip: string; success: boolean; error?: string }>;
    };
    incident_updates: {
      total: number;
      success: number;
      failed: number;
      details: Array<{
        success: boolean;
        total: number;
        succeededNum: number;
        failedNum: number;
        message?: string;
      }>;
    };
  } | null;
  executionError: string | null;
}

/**
 * Step 1: Query incidents result
 */
export interface Step1Data {
  incidents: IncidentItem[];
  total: number;
}

export interface IncidentItem {
  uuId: string;
  name: string;
  hostIp: string;
  severity: number;
  endTime: number;
  dealStatus: number;
}

/**
 * Step 2: Analyze incident result
 */
export interface Step2Data {
  // Top 10场景：多个事件的详情
  incident_details?: IncidentDetailItem[];
  // 单事件场景：向后兼容
  proof?: IncidentProofData | null;
  entities?: IncidentEntitiesData | null;
}

export interface IncidentDetailItem {
  incident: IncidentItem;
  proof?: IncidentProofData | null;
  entities?: IncidentEntitiesData | null;
  success: boolean;
  error?: string;
  risk_assessment?: RiskAssessment;
}

export interface RiskAssessment {
  risk_level: number;  // 0-4: 未知、低危、中危、高危、严重
  risk_reasoning: string;
  recommendation: string;
}

export interface IncidentProofData {
  name: string;
  uuId: string;
  hostIp: string;
  incidentTimeLines: IncidentTimeline[];
}

export interface IncidentTimeline {
  stage: string;
  time: string;
  score?: number;
  source?: string;
}

export interface IncidentEntitiesData {
  item: IPEntityItem[];
}

export interface IPEntityItem {
  ip: string;
  threatLevel: number;
  location: string;
  intelligenceTag: string[];
  ndrDealStatusInfo: {
    status: string;
  };
}

/**
 * Step 3: Prepare confirmation result
 */
export interface Step3Data {
  ips_to_block: string[];
  ip_details: IPDetailItem[];
  ai_summary: string;
  // 单事件场景：向后兼容
  incident_name?: string;
  incident_id?: string;
  // Top 10场景：多个事件的摘要
  incident_summaries?: IncidentSummaryItem[];
}

export interface IncidentSummaryItem {
  incident_id: string;
  incident_name: string;
  host_ip: string;
  severity: number;
  ip_count: number;
}

export interface IPDetailItem {
  ip: string;
  threat_level: number;
  location: string;
  tags: string[];
  ndr_status: string;
}

/**
 * Scenario start response from backend
 */
export interface ScenarioStartResponse {
  success: boolean;
  completed: boolean;
  awaiting_confirmation: boolean;
  message: string;
  data: {
    step1: Step1Data;
    step2: Step2Data;
    step3: Step3Data;
    incident_id: string;
    ips_to_block: string[];
  };
}

/**
 * Scenario confirm response from backend
 */
export interface ScenarioConfirmResponse {
  success: boolean;
  completed: boolean;
  message: string;
  partial_success?: boolean;
  results: {
    ip_block: IPBlockResult;
    incident_update: IncidentUpdateResult;
  };
}

export interface IPBlockResult {
  total: number;
  success: number;
  failed: number;
  details: IPBlockDetailItem[];
}

export interface IPBlockDetailItem {
  ip: string;
  success: boolean;
  rule_ids?: string[];
  message?: string;
  error?: string;
}

export interface IncidentUpdateResult {
  success: boolean;
  total: number;
  succeededNum: number;
  failedNum: number;
  message?: string;
}

/**
 * Scenario configuration
 */
export interface ScenarioConfig {
  id: string;
  name: string;
  description: string;
  icon: string;
  steps: number;
  estimatedTime: string;
}

/**
 * Severity level mapping
 */
export const SEVERITY_LEVELS: Record<number, string> = {
  0: '信息',
  1: '低危',
  2: '中危',
  3: '高危',
  4: '严重',
};

/**
 * Threat level mapping
 */
export const THREAT_LEVELS: Record<number, string> = {
  0: '未知',
  1: '低危',
  2: '中危',
  3: '高危',
  4: '严重',
};
