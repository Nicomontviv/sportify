/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        sportify: {
          blue: '#1E90FF',      // Azul Eléctrico (Primario) 
          green: '#32CD32',     // Verde Vibrante (Éxito/Acción) 
          deepSea: '#008080',   // Verde Mar Profundo (Contraste) [cite: 330]
          cyan: '#00CED1',      // Cian Brillante (Hover/Progreso) [cite: 331]
          lime: '#ADFF2F',      // Verde Lima (Resaltados/Badges) [cite: 332]
          dark: '#212121',      // Gris Oscuro (Texto principal) [cite: 333]
          white: '#FFFFFF',     // Blanco Puro (Fondo general) 
          light: '#F5F5F5',     // Gris Claro Neutral (Cards/Formularios) 
        }
      }
    },
  },
  plugins: [],
}