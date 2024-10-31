/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      animation: {
        "spin-slow": "spin 3s linear infinite",
      },
      colors: {
        primary: {
          light: "#DFF2EB",
          DEFAULT: "#B9E5E8",
          medium: "#7AB2D3",
          dark: "#4A628A",
        },
      },
    },
  },
  plugins: [],
};
