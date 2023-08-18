/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './.cache/**/*.html',
    './content/**/*.mdx',
    './components/**/*.{jinja,js}',
    './theme/**/*.{jinja,js}',
    './static/**/*.js',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        'sans': ['silka', 'sans-serif'],
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
}
