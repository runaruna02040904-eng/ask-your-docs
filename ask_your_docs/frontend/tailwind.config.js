/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        display: ["Kanit", "sans-serif"],
        body: ["Noto Sans SC", "sans-serif"],
      },
      colors: {
        dark: "#0C0C0C",
        "dark-text": "#D7E2EA",
        "gradient-from": "#646973",
        "gradient-to": "#BBCCD7",
      },
      keyframes: {
        "fade-rise": {
          from: { opacity: "0", transform: "translateY(24px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        "fade-rise": "fade-rise 0.8s ease-out both",
        "fade-rise-delay": "fade-rise 0.8s ease-out 0.2s both",
        "fade-rise-delay-2": "fade-rise 0.8s ease-out 0.4s both",
      },
    },
  },
  plugins: [],
}
