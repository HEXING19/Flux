import React, { useEffect, useState } from 'react';
import { Box } from '@mui/material';
import type { SkillFilterType } from '../../../types/skill';
import { SKILLS_CONFIG } from '../../../config/skills';
import { SkillsButton } from './SkillsButton';
import { SkillsDialog } from './SkillsDialog';
import { fetchSkillsMetadata } from '../../../services/skillsService';

interface SkillsPanelProps {
  onPromptSelect: (prompt: string) => void;
}

export const SkillsPanel: React.FC<SkillsPanelProps> = ({ onPromptSelect }) => {
  const [open, setOpen] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<SkillFilterType>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [skills, setSkills] = useState(SKILLS_CONFIG);

  useEffect(() => {
    let mounted = true;

    const loadSkills = async () => {
      try {
        const remoteSkills = await fetchSkillsMetadata();
        if (mounted && remoteSkills.length > 0) {
          setSkills(remoteSkills);
        }
      } catch (error) {
        // Keep local fallback list if backend skills API is unavailable
      }
    };

    loadSkills();

    return () => {
      mounted = false;
    };
  }, []);

  const handleOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    // Reset filters when closing
    setSelectedCategory('all');
    setSearchQuery('');
  };

  const handlePromptSelect = (prompt: string) => {
    onPromptSelect(prompt);
    handleClose();
  };

  return (
    <Box>
      {/* Skills Button */}
      <SkillsButton onClick={handleOpen} />

      {/* Skills Dialog */}
      <SkillsDialog
        open={open}
        onClose={handleClose}
        skills={skills}
        selectedCategory={selectedCategory}
        onCategoryChange={setSelectedCategory}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        onPromptSelect={handlePromptSelect}
      />
    </Box>
  );
};
