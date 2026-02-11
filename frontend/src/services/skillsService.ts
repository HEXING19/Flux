import api from './api';
import type { SkillMetadata } from '../types/skill';

interface SkillsResponse {
  skills: SkillMetadata[];
}

export async function fetchSkillsMetadata(): Promise<SkillMetadata[]> {
  const result = (await api.get<SkillsResponse>('/api/v1/llm/skills')) as unknown as SkillsResponse;
  return Array.isArray(result.skills) ? result.skills : [];
}
