/**
 * IP Block Type Definitions
 * Types for IP blocking operations and responses
 */

export interface IPBlockStatus {
  blocked: boolean;
  rules?: IPBlockRule[];
  devices?: IPBlockDevice[];
  total_rules?: number;
}

export interface IPBlockRule {
  id: string;
  name: string;
  status: string;
  createTime: number;
  updateTime: number;
  blockIpMethod: string;
  blockIpTimeRange: string;
  blockIpRule: {
    type: string;
    mode: string;
    view: string[];
  };
  reason?: string;
  createUser?: string;
}

export interface IPBlockDevice {
  device_id: number;
  deviceName: string;
  deviceType: string;
  deviceStatus: string;
  deviceVersion?: string;
  deviceIp?: string;
  remark?: string;
  gateway_id?: string;
  company_id?: string;
}

export interface IPBlockParams {
  ip: string;
  device_id: number;
  device_name: string;
  device_type: string;
  device_version: string;
  block_type: string;
  time_type: string;
  time_value?: number;
  time_unit: string;
  reason: string;
  device_status?: string;
}

export interface IPBlockCheckRequest {
  ip: string;
  auth_code?: string;
  ak?: string;
  sk?: string;
  flux_base_url: string;
}

export interface IPBlockDevicesRequest {
  device_type?: string;
  auth_code?: string;
  ak?: string;
  sk?: string;
  flux_base_url: string;
}

export interface IPBlockRequest {
  ip: string;
  device_id: number;
  device_name: string;
  device_type?: string;
  device_version?: string;
  block_type?: string;
  time_type?: string;
  time_value?: number;
  time_unit?: string;
  reason?: string;
  auth_code?: string;
  ak?: string;
  sk?: string;
  flux_base_url: string;
}

export interface IPBlockCheckAndBlockRequest {
  ip: string;
  device_name: string;
  device_type?: string;
  auth_code?: string;
  ak?: string;
  sk?: string;
  flux_base_url: string;
}

export interface IPBlockAPIResponse {
  success: boolean;
  message: string;
  data?: {
    action?: 'already_blocked' | 'need_block';
    blocked?: boolean;
    rules?: IPBlockRule[];
    devices?: IPBlockDevice[];
    total_rules?: number;
    block_params?: IPBlockParams;
    devices_count?: number;
    rule_ids?: string[];
    rule_count?: number;
  };
  error_info?: {
    error_type: string;
    friendly_message: string;
    raw_message: string;
    suggestion?: string;
    actions?: string[];
  };
}

export interface IPBlockConfirmationDialogProps {
  open: boolean;
  params: IPBlockParams | null;
  onConfirm: () => void;
  onCancel: () => void;
}

export interface IPBlockStatusTableProps {
  status: IPBlockStatus;
  ip: string;
}

export interface IPBlockSummary {
  ip: string;
  device_name: string;
  device_type: string;
  block_type: string;
  time_type: string;
  time_value?: number;
  time_unit: string;
  reason?: string;
  rule_count: number;
  timestamp: number;
}
