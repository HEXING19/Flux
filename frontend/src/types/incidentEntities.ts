/**
 * Incident IP Entities Type Definitions
 * Represents external IP entities associated with security incidents
 */

export interface IncidentEntitiesData {
  item?: IPEntity[];
}

export interface IncidentEntitiesTableProps {
  entities: IPEntity[];
  incidentId?: string;
  onBlockIP?: (ip: string) => void;
  onViewDetails?: (entity: IPEntity) => void;
}

export interface IncidentEntitiesResponse {
  success: boolean;
  message: string;
  data?: {
    item?: IPEntity[];
  };
}

export interface IPEntity {
  /** Entity ID */
  id?: string;
  /** IP address */
  ip: string;
  /** Port number */
  port: number;
  /** Threat level: 0=Unknown, 1=White/Low, 2=Gray/Medium, 3=Black/High */
  threatLevel: number;
  /** Geographic location */
  location: string;
  /** ISP/ASN label */
  asLabel: string;
  /** Threat intelligence tags */
  intelligenceTag: string[];
  /** Network mapping tag */
  mappingTag: string;
  /** Alert role description */
  alertRole: string;
  /** Disposal suggestions */
  dealSuggestion: string;
  /** Business impact description */
  businessAffection: string;
  /** Associated source processes */
  srcProcess?: SrcProcess[];
  /** EDR (endpoint) disposition status info */
  edrDealStatusInfo?: DealStatusInfo | null;
  /** NDR (network) disposition status info */
  ndrDealStatusInfo?: DealStatusInfo;
}

export interface SrcProcess {
  /** Process MD5 hash */
  md5: string;
  /** Process ID */
  pid: number;
  /** Process name */
  pName: string;
}

export interface DealStatusInfo {
  /** Disposition status */
  status?: string;
  /** Whether the block is permanent */
  isPermanent?: boolean;
  /** Expiration time (unix timestamp) */
  expireTime?: number;
}

/**
 * Threat level display mapping
 */
export const ThreatLevelMap: Record<number, { label: string; color: string; emoji: string }> = {
  0: { label: '未知', color: 'gray', emoji: '⚪' },
  1: { label: '低危', color: 'green', emoji: '🟢' },
  2: { label: '中危', color: 'yellow', emoji: '🟡' },
  3: { label: '高危', color: 'red', emoji: '🔴' },
};

/**
 * NDR disposition status mapping
 */
export const NDRStatusMap: Record<string, { label: string; icon: string }> = {
  WAIT_DEAL: { label: '待处置', icon: '⏳' },
  BLOCK_SUCCESS: { label: '已封禁', icon: '✓' },
  BLOCK_FAILED: { label: '封禁失败', icon: '✗' },
  UNBLOCK_SUCCESS: { label: '已解封', icon: '↩️' },
  PARTIAL_BLOCK_SUCCESS: { label: '部分封禁成功', icon: '⚠️' },
  PARTIAL_UNBLOCK_SUCCESS: { label: '部分解封成功', icon: '⚠️' },
};

/**
 * Helper function to get threat level display info
 */
export function getThreatLevelInfo(level: number): { label: string; color: string; emoji: string } {
  return ThreatLevelMap[level] || ThreatLevelMap[0];
}

/**
 * Helper function to get NDR status display info
 */
export function getNDRStatusInfo(status?: string): { label: string; icon: string } {
  if (!status) return { label: '暂无', icon: '-' };
  return NDRStatusMap[status] || { label: status, icon: '?' };
}

/**
 * Helper function to format expiration time
 */
export function formatExpireTime(timestamp?: number): string {
  if (!timestamp) return '永久';
  const date = new Date(timestamp * 1000);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
}

/**
 * Helper function to check if IP is blocked
 */
export function isIPBlocked(entity: IPEntity): boolean {
  if (entity.ndrDealStatusInfo?.status) {
    return ['BLOCK_SUCCESS', 'PARTIAL_BLOCK_SUCCESS'].includes(entity.ndrDealStatusInfo.status);
  }
  return false;
}

/**
 * Helper function to check if IP needs action
 */
export function isIPNeedsAction(entity: IPEntity): boolean {
  // High threat level and not blocked
  if (entity.threatLevel >= 2 && !isIPBlocked(entity)) {
    return true;
  }
  return false;
}
