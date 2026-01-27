/**
 * Asset parameter types for confirmation dialog
 */

export interface AssetParams {
  ip: string;
  branchId: number;
  mac?: string;
  assetName?: string;
  hostName?: string;
  type?: string;
  magnitude?: string;
  tags?: string[];
  classify1Id?: number;
  classifyId?: number;
  comment?: string;
  users?: any[];
}

/**
 * Asset summary data for success messages
 */
export interface AssetSummary {
  ip: string;
  assetName?: string;
  type?: string;
  classify1Id?: number;
  classifyId?: number;
  magnitude?: string;
  branchId?: number;
}

