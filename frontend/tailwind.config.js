/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}"
  ],
  theme: {
    extend: {
      colors: {
        krishna: {
          blue: "#1e3a8a",      // deep peacock blue
          light: "#e0f2fe",     // sky blue
          gold: "#facc15",      // divine gold
          white: "#ffffff",
          soft: "#f8fafc",      // calm background
        },
      },
    },
  },
  
  plugins: [],
}
