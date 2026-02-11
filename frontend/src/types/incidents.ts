/**
 * Security Incident Type Definitions
 * Types for security incident operations and responses
 */

export interface Incident {
  uuId: string;
  name: string;
  incidentSeverity: number; // 0=信息, 1=低危, 2=中危, 3=高危, 4=严重
  hostIp: string;
  endTime: number;
  dealStatus: number; // 处置状态: 0=待处置, 10=处置中, 30=已遏制, 40=已处置, 50=已挂起, 60=接受风险, 70=已遏制(兼容)
  dealAction?: string; // 处置动作文本（可选）
  startTime?: number;
  auditTime?: number;
  updateTime?: number;
  threatDefines?: number[];
  dataSources?: string[];
  incidentSources?: string[];
}

export interface IncidentsListData {
  total: number;
  items: Incident[];
}

export interface IncidentsListTableProps {
  incidents: Incident[];
  total: number;
}
