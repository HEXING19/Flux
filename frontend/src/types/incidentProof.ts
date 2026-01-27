/**
 * Security Incident Proof Type Definitions
 * Types for incident detail and timeline data
 */

export interface AlertTimeline {
  name: string;
  alertId: string;
  severity: number;
  lastTime: number;
  threatSubTypeDesc: string;
  stage: number;
  devSourceNames: string[];
}

export interface IncidentProofData {
  uuId: string;
  name: string;
  severity: number;
  endTime: number;
  dealStatus?: number; // 处置状态: 0=待处置, 10=处置中, 30=已防护, 40=已处置, 50=已挂起, 60=接受风险, 70=已遏制
  eventThreatDefine: string[];
  dataSource: string[];
  riskTag: string[];
  alertTimeLine: AlertTimeline[];
}

export interface IncidentProofTableProps {
  data: IncidentProofData;
}
