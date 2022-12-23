/** @type {import('tailwindcss').Config} */
const colors = require('tailwindcss/colors')

module.exports = {
  content: [
    './content/**/*.md',
    './content/**/*.jinja',
    './components/**/*.jinja',
    './theme/**/*.jinja',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        'accent': 'var(--accent)',
        'accent-darker': 'var(--accent-darker)',
      },
      screens: {
        'tall': { 'raw': '(min-height: 768px)' },
      },
      transitionTimingFunction: {
        '3': 'var(--ease-3)',
        'out-5': 'var(--ease-out-5)',
        'elastic-3': 'var(--ease-elastic-3)',
        'elastic-4': 'var(--ease-elastic-4)',
      }
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
