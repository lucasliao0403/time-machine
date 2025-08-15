/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Ultra-dark grayscale palette - NO WHITE
        glass: {
          50: '#9ca3af',    // Light gray (lightest allowed)
          100: '#6b7280',   // Medium light gray
          200: '#4b5563',   // Medium gray
          300: '#374151',   // Dark gray
          400: '#1f2937',   // Darker gray
          500: '#111827',   // Very dark gray
          600: '#0f172a',   // Extra dark gray
          700: '#0d1321',   // Near black
          800: '#0a0e1a',   // Very near black
          850: '#080b14',   // Almost black
          900: '#050711',   // Deepest black
          950: '#030409',   // Pure dark
        },
        // Pure grayscale accent (no blue)
        accent: {
          400: '#6b7280',   // Medium light gray
          500: '#4b5563',   // Medium gray
          600: '#374151',   // Dark gray
          700: '#1f2937',   // Darker gray
          800: '#111827',   // Very dark gray
          900: '#0f172a',   // Extra dark gray
        },
        // Semantic colors (grayscale only)
        success: '#6b7280',
        warning: '#9ca3af', 
        error: '#6b7280',
        info: '#6b7280',
      },
      backgroundImage: {
        'glass-gradient': 'linear-gradient(135deg, rgba(156, 163, 175, 0.08), rgba(107, 114, 128, 0.03))',
        'frosted-gradient': 'linear-gradient(135deg, rgba(156, 163, 175, 0.12), rgba(107, 114, 128, 0.06))',
        'ultra-glass': 'linear-gradient(135deg, rgba(156, 163, 175, 0.15), rgba(107, 114, 128, 0.08))',
        'apple-glass': 'linear-gradient(135deg, rgba(156, 163, 175, 0.06), rgba(107, 114, 128, 0.02))',
        'shimmer-glass': 'linear-gradient(135deg, rgba(156, 163, 175, 0.10), rgba(209, 213, 219, 0.04), rgba(156, 163, 175, 0.08))',
        'crystal-glass': 'linear-gradient(135deg, rgba(156, 163, 175, 0.04), rgba(209, 213, 219, 0.02), rgba(156, 163, 175, 0.06))',
        'subtle-gradient': 'linear-gradient(180deg, rgba(5, 7, 17, 1), rgba(3, 4, 9, 1))',
        'ambient-gradient': 'radial-gradient(ellipse at top, rgba(107, 114, 128, 0.12), transparent 60%)',
        'depth-gradient': 'linear-gradient(135deg, rgba(156, 163, 175, 0.10), rgba(107, 114, 128, 0.05))',
      },
      backdropBlur: {
        xs: '2px',
        '4xl': '72px',
        '5xl': '96px',
        '6xl': '128px',
        'ultra': '160px',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        glow: {
          '0%': { boxShadow: '0 0 5px rgb(59 130 246 / 0.5)' },
          '100%': { boxShadow: '0 0 20px rgb(59 130 246 / 0.8), 0 0 30px rgb(59 130 246 / 0.4)' },
        },
      },
      boxShadow: {
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.12)',
        'glass-lg': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
        'frosted': '0 8px 32px 0 rgba(0, 0, 0, 0.18), inset 0 1px 0 rgba(255, 255, 255, 0.08)',
        'minimal': '0 4px 16px 0 rgba(0, 0, 0, 0.08)',
        'subtle': '0 2px 8px 0 rgba(0, 0, 0, 0.06)',
        'accent-glow': '0 0 20px rgba(30, 64, 175, 0.15)',
      },
    },
  },
  plugins: [],
}
