/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./src/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    theme: {
        extend: {
            colors: {
                background: "var(--background)",
                foreground: "var(--text-primary)",
                primary: "var(--primary)",
                secondary: "var(--secondary)",
            },
        },
    },
    plugins: [],
    darkMode: 'class',
};
