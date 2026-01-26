import { Card, CardContent, Typography, Box } from '@mui/material';

interface FeatureCardProps {
  icon: string;
  title: string;
  description: string;
}

export const FeatureCard = ({ icon, title, description }: FeatureCardProps) => {
  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ fontSize: '3rem', mb: 2, textAlign: 'center' }}>
          {icon}
        </Box>
        <Typography variant="h6" component="h3" gutterBottom textAlign="center">
          {title}
        </Typography>
        <Typography variant="body2" color="text.secondary" textAlign="center">
          {description}
        </Typography>
      </CardContent>
    </Card>
  );
};
