/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        "gpt-dark": "#343541", // Nền chính
        "gpt-sidebar": "#202123", // Nền sidebar
        "gpt-input": "#40414F", // Nền ô nhập liệu
        "gpt-bot": "#444654", // Nền tin nhắn bot
        "gpt-hover": "#2A2B32", // Màu hover sidebar
      },
      fontFamily: {
        sans: ["Inter", "Söhne", "sans-serif"],
      },
    },
  },
  plugins: [],
};
