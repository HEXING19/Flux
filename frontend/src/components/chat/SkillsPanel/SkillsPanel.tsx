import React, { useState } from 'react';
import { Box } from '@mui/material';
import type { SkillFilterType } from '../../../types/skill';
import { SKILLS_CONFIG } from '../../../config/skills';
import { SkillsButton } from './SkillsButton';
import { SkillsDialog } from './SkillsDialog';

interface SkillsPanelProps {
  onPromptSelect: (prompt: string) => void;
}

export const SkillsPanel: React.FC<SkillsPanelProps> = ({ onPromptSelect }) => {
  const [open, setOpen] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<SkillFilterType>('all');
  const [searchQuery, setSearchQuery] = useState('');

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
        skills={SKILLS_CONFIG}
        selectedCategory={selectedCategory}
        onCategoryChange={setSelectedCategory}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        onPromptSelect={handlePromptSelect}
      />
    </Box>
  );
};
