/**
 * Type definitions for Skills Display feature
 */

export interface ExamplePrompt {
  chinese: string;
  english?: string;
  category?: string;
}

export interface SkillCapability {
  title: string;
  description: string;
}

export type SkillCategory = 'incident' | 'asset' | 'network' | 'general';

export interface SkillMetadata {
  id: string;
  name: string;
  nameEn: string;
  description: string;
  icon: string;
  category: SkillCategory;
  capabilities: SkillCapability[];
  examplePrompts: ExamplePrompt[];
  requiredParams?: string[];
  color: string;
  order: number;
}

export type SkillFilterType = 'all' | SkillCategory;
