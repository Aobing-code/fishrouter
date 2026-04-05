/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        bg: {
          primary: '#0a0a0f',
          secondary: 'rgba(20, 20, 30, 0.6)',
          tertiary: 'rgba(30, 30, 50, 0.5)',
          hover: 'rgba(40, 40, 70, 0.7)',
        },
        accent: {
          primary: '#00eeff',
          secondary: '#818cf8',
          glow: 'rgba(0, 238, 255, 0.15)',
        },
        success: '#00ff88',
        error: '#ff3344',
        warning: '#ffaa00',
        text: {
          primary: '#f0f4ff',
          secondary: '#8892b0',
          muted: '#5a6a8a',
        },
        border: 'rgba(100, 120, 160, 0.2)',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Consolas', 'monospace'],
      },
      animation: {
        'float': 'float 8s ease-in-out infinite',
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translate(0, 0) scale(1)' },
          '33%': { transform: 'translate(30px, -30px) scale(1.05)' },
          '66%': { transform: 'translate(-20px, 20px) scale(0.95)' },
        },
      },
    },
  },
  plugins: [],
}
