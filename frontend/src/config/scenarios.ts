/**
 * Scenarios Configuration
 * Metadata for automated scenario tasks
 */

import type { ScenarioConfig } from '../types/scenario';

export const SCENARIOS_CONFIG: ScenarioConfig[] = [
  {
    id: 'daily-high-risk-closure',
    name: '每日高危事件闭环',
    description: '自动查询今日未处置的高危事件，分析Top 1事件，提供一键封禁和处置建议',
    icon: '🛡️',
    steps: 4,
    estimatedTime: '2-3分钟',
  },
];

/**
 * Get scenario by ID
 */
export const getScenarioById = (id: string): ScenarioConfig | undefined => {
  return SCENARIOS_CONFIG.find(scenario => scenario.id === id);
};

/**
 * Get all scenarios
 */
export const getAllScenarios = (): ScenarioConfig[] => {
  return SCENARIOS_CONFIG;
};
