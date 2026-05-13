import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        zomato: {
          red: "#E23744",
          "red-hover": "#CB2F3B",
          dark: "#121212",
          card: "#1A1A1A",
          border: "#2A2A2A",
          muted: "#9CA3AF",
        },
        brand: {
          green: "#26D367",
          "green-dim": "#1FA855",
        },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
