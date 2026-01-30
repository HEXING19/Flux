import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2', // Material Blue
      light: '#42a5f5',
      dark: '#1565c0',
      contrastText: '#fff',
    },
    secondary: {
      main: '#ff4081', // Material Pink
      light: '#ff79b0',
      dark: '#c60055',
      contrastText: '#fff',
    },
    background: {
      default: '#fafafa',
      paper: '#ffffff',
    },
    error: {
      main: '#d32f2f',
    },
    warning: {
      main: '#ed6c02',
    },
    info: {
      main: '#0288d1',
    },
    success: {
      main: '#2e7d32',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 500,
      lineHeight: 1.2,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 500,
      lineHeight: 1.3,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 500,
      lineHeight: 1.4,
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 500,
      lineHeight: 1.4,
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 500,
      lineHeight: 1.5,
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 500,
      lineHeight: 1.5,
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.6,
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.5,
    },
  },
  spacing: 8,
  shape: {
    borderRadius: 16, // MD3 风格：更大的圆角
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none', // 去除大写
          borderRadius: 12, // MD3 风格
          fontWeight: 600,
          px: 3,
          py: 1.5,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)',
          borderRadius: 16,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none', // 移除默认背景
          borderRadius: 16,
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 12,
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
      },
    },
  },
});

/**
 * AI Security Cockpit Dark Theme
 * Material Design 3 compliant dark theme
 */
export const cockpitTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#6750A4', // MD3 Primary Purple
      light: '#9F7AEA',
      dark: '#4A3B69',
      contrastText: '#fff',
    },
    secondary: {
      main: '#625B71', // MD3 Secondary
      light: '#8D8199',
      dark: '#453F55',
      contrastText: '#fff',
    },
    background: {
      default: '#1C1B1F', // MD3 Dark Background
      paper: '#2B2930',   // MD3 Dark Surface
    },
    error: {
      main: '#B3261E', // MD3 Error
    },
    warning: {
      main: '#F2B8B5', // MD3 Warning tone
    },
    info: {
      main: '#8E8D93', // MD3 Outline
    },
    success: {
      main: '#527A50', // MD3 Success Green
    },
    text: {
      primary: '#E6E1E5', // MD3 On Primary
      secondary: '#CAC4D0', // MD3 On Surface
      disabled: '#49454F', // MD3 Outline Variant
    },
    divider: '#49454F', // MD3 Outline Variant
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 400, // MD3 uses lighter font weights
      lineHeight: 1.2,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 400,
      lineHeight: 1.3,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 400,
      lineHeight: 1.4,
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 400,
      lineHeight: 1.4,
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 400,
      lineHeight: 1.5,
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 500, // Medium for headings
      lineHeight: 1.5,
    },
    body1: {
      fontSize: '1rem',
      fontWeight: 400,
      lineHeight: 1.5,
    },
    body2: {
      fontSize: '0.875rem',
      fontWeight: 400,
      lineHeight: 1.5,
    },
    button: {
      textTransform: 'none', // MD3: No uppercase
      fontWeight: 500,
    },
  },
  spacing: 8, // MD3: 8px base unit
  shape: {
    borderRadius: 16, // MD3 large components
  },
  shadows: [
    'none',
    '0px 1px 3px 1px rgba(0, 0, 0, 0.15), 0px 1px 2px 0px rgba(0, 0, 0, 0.3)',
    '0px 2px 6px 2px rgba(0, 0, 0, 0.15), 0px 1px 2px 0px rgba(0, 0, 0, 0.3)',
    '0px 4px 8px 3px rgba(0, 0, 0, 0.15), 0px 1px 3px 0px rgba(0, 0, 0, 0.3)',
    '0px 6px 10px 4px rgba(0, 0, 0, 0.15), 0px 1px 3px 0px rgba(0, 0, 0, 0.3)',
    '0px 6px 10px 4px rgba(0, 0, 0, 0.15), 0px 2px 4px 0px rgba(0, 0, 0, 0.3)',
    '0px 8px 12px 6px rgba(0, 0, 0, 0.15), 0px 2px 4px 0px rgba(0, 0, 0, 0.3)',
    '0px 9px 14px 8px rgba(0, 0, 0, 0.15), 0px 3px 5px 0px rgba(0, 0, 0, 0.3)',
  ],
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 20, // MD3 pill-shaped buttons
          fontWeight: 500,
          textTransform: 'none',
          px: 3,
          py: 1.5,
          transition: 'all 150ms ease-in-out', // MD3 standard transition
        },
        contained: {
          boxShadow: 'none', // MD3: No shadow on contained buttons
          '&:hover': {
            boxShadow: 'none',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 3, // 16px in spacing units
          boxShadow: '0px 1px 3px 1px rgba(0, 0, 0, 0.15), 0px 1px 2px 0px rgba(0, 0, 0, 0.3)', // MD3 elevation 2
          backgroundColor: '#2B2930', // MD3 Surface
          transition: 'box-shadow 150ms ease-in-out',
          '&:hover': {
            boxShadow: '0px 4px 8px 3px rgba(0, 0, 0, 0.15), 0px 1px 3px 0px rgba(0, 0, 0, 0.3)', // MD3 elevation 4
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          borderRadius: 3, // 16px
          backgroundColor: '#2B2930', // MD3 Surface
        },
        elevation1: {
          boxShadow: '0px 1px 3px 1px rgba(0, 0, 0, 0.15), 0px 1px 2px 0px rgba(0, 0, 0, 0.3)',
        },
        elevation2: {
          boxShadow: '0px 2px 6px 2px rgba(0, 0, 0, 0.15), 0px 1px 2px 0px rgba(0, 0, 0, 0.3)',
        },
        elevation3: {
          boxShadow: '0px 4px 8px 3px rgba(0, 0, 0, 0.15), 0px 1px 3px 0px rgba(0, 0, 0, 0.3)',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 2, // 8px
          fontWeight: 500,
        },
        filled: {
          backgroundColor: '#49454F', // MD3 Surface Container High
        },
      },
    },
  },
});
