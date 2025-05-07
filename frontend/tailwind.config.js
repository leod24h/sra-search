// tailwind.config.js
module.exports = {
    // purge: [],
    purge: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
    darkMode: false, // or 'media' or 'class'
    theme: {
      extend: {
        colors: {
          'custom-purple': '#5559a6',
          'custom-dark-purple': 'rgb(70, 68, 81)',
        }
      },
    },
    variants: {
      extend: {},
    },
    plugins: [],
  }