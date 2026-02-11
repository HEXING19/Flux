import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  IconButton,
  Box,
  TextField,
  Chip,
  Grid,
  Typography,
} from '@mui/material';
import { Close as CloseIcon, Search as SearchIcon } from '@mui/icons-material';
import type { SkillMetadata, SkillFilterType } from '../../../types/skill';
import { CATEGORY_NAMES } from '../../../config/skills';
import { SkillCard } from './SkillCard';

interface SkillsDialogProps {
  open: boolean;
  onClose: () => void;
  skills: SkillMetadata[];
  selectedCategory: SkillFilterType;
  onCategoryChange: (category: SkillFilterType) => void;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  onPromptSelect: (prompt: string) => void;
}

export const SkillsDialog: React.FC<SkillsDialogProps> = ({
  open,
  onClose,
  skills,
  selectedCategory,
  onCategoryChange,
  searchQuery,
  onSearchChange,
  onPromptSelect,
}) => {
  // Filter skills based on category and search query
  const filteredSkills = skills.filter((skill) => {
    const matchesCategory =
      selectedCategory === 'all' || skill.category === selectedCategory;

    const matchesSearch =
      !searchQuery ||
      skill.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      skill.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      skill.examplePrompts.some((p) =>
        p.chinese.toLowerCase().includes(searchQuery.toLowerCase())
      );

    return matchesCategory && matchesSearch;
  });

  // Sort skills by order
  const sortedSkills = [...filteredSkills].sort((a, b) => a.order - b.order);

  const categories: Array<{ value: SkillFilterType; label: string }> = [
    { value: 'all', label: CATEGORY_NAMES.all },
    { value: 'incident', label: CATEGORY_NAMES.incident },
    { value: 'asset', label: CATEGORY_NAMES.asset },
    { value: 'network', label: CATEGORY_NAMES.network },
    { value: 'general', label: CATEGORY_NAMES.general },
  ];

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="lg"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 3,
          maxHeight: '80vh',
        },
      }}
    >
      {/* Header */}
      <DialogTitle
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          pb: 2,
        }}
      >
        <Typography variant="h6" component="div" sx={{ fontWeight: 600 }}>
          技能能力
        </Typography>
        <IconButton onClick={onClose} size="small">
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      <DialogContent sx={{ pb: 3 }}>
        {/* Search Bar */}
        <Box sx={{ mb: 2 }}>
          <TextField
            fullWidth
            size="small"
            placeholder="搜索技能或示例提问..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            InputProps={{
              startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
            }}
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 2,
              },
            }}
          />
        </Box>

        {/* Category Tabs */}
        <Box sx={{ display: 'flex', gap: 1, mb: 3, flexWrap: 'wrap' }}>
          {categories.map((category) => (
            <Chip
              key={category.value}
              label={category.label}
              onClick={() => onCategoryChange(category.value)}
              sx={{
                borderRadius: 1.5,
                px: 0.5,
                backgroundColor:
                  selectedCategory === category.value ? 'primary.main' : 'action.hover',
                color:
                  selectedCategory === category.value ? 'white' : 'text.primary',
                fontWeight: selectedCategory === category.value ? 600 : 400,
                transition: 'all 0.2s',
                '&:hover': {
                  backgroundColor:
                    selectedCategory === category.value
                      ? 'primary.dark'
                      : 'action.selected',
                },
              }}
            />
          ))}
        </Box>

        {/* Skills Grid */}
        {sortedSkills.length > 0 ? (
          <Grid container spacing={2}>
            {sortedSkills.map((skill) => (
              <Grid size={{ xs: 12, sm: 6, md: 4 }} key={skill.id}>
                <SkillCard skill={skill} onPromptSelect={onPromptSelect} />
              </Grid>
            ))}
          </Grid>
        ) : (
          <Box
            sx={{
              textAlign: 'center',
              py: 8,
              color: 'text.secondary',
            }}
          >
            <Typography variant="body1">
              {searchQuery ? '未找到匹配的技能' : '该分类下暂无技能'}
            </Typography>
          </Box>
        )}
      </DialogContent>
    </Dialog>
  );
};
