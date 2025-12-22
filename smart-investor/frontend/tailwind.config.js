/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "var(--bg-main)",
        card: "var(--bg-card)",
        muted: "var(--bg-muted)",

        primary: "var(--text-primary)",
        secondary: "var(--text-secondary)",
        mutedText: "var(--text-muted)",

        borderColor: "var(--border-color)",

        accent: "var(--accent)",
        buy: "var(--buy)",
        sell: "var(--sell)",
        warning: "var(--warning)",
      },
    },
  },
  plugins: [],
};
