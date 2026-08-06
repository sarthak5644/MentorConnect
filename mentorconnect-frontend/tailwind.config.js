/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: {
          DEFAULT: '#1B2430',
          50: '#F4F5F7', 100: '#E4E7EB', 200: '#C4CAD3', 300: '#9AA4B2',
          400: '#6B7686', 500: '#4A5568', 600: '#374151', 700: '#252E3B',
          800: '#1B2430', 900: '#10151D',
        },
        paper: { DEFAULT: '#FAF7F2', dark: '#10151D' },
        accent: {
          DEFAULT: '#D97706', 50: '#FFFBEB', 100: '#FEF3C7', 200: '#FDE68A',
          300: '#FCD34D', 400: '#FBBF24', 500: '#D97706', 600: '#B45309',
          700: '#92400E',
        },
        mentor: {
          DEFAULT: '#0F766E', 50: '#F0FDFA', 100: '#CCFBF1', 500: '#0F766E', 700: '#115E59',
        },
        success: '#15803D',
        danger: '#B91C1C',
        warn: '#B45309',
      },
      fontFamily: {
        display: ['Fraunces', 'Georgia', 'serif'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      borderRadius: { xl: '0.75rem', '2xl': '1rem' },
    },
  },
  plugins: [],
};