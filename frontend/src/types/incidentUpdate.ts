/**
 * Incident Status Update Type Definitions
 * Types for incident status update results
 */

export interface IncidentUpdateResult {
  total: number;
  succeededNum: number;
  statusName?: string;
}

export interface IncidentUpdateData {
  total: number;
  succeededNum: number;
  failedNum: number;
  statusName: string;
  statusValue: number;
}

export interface IncidentUpdateTableProps {
  data: IncidentUpdateData;
}
