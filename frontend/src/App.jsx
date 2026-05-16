import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';

const Login = () => {
  return (
    <div className="flex min-h-screen items-center justify-center bg-sportify-light px-4">
      <div className="w-full max-w-md space-y-6 rounded-2xl border border-gray-200 bg-sportify-white p-8 shadow-md">
        <div className="text-center">
          {/* Título usando el Azul Eléctrico de identidad primaria */}
          <h1 className="text-4xl font-extrabold tracking-tight text-sportify-blue">Sportify</h1>
          <p className="mt-2 text-sm text-sportify-dark opacity-70">Iniciá sesión para gestionar tus turnos</p>
        </div>
        <form className="space-y-4">
          <div>
            <label className="block text-sm font-semibold text-sportify-dark">Correo Electrónico</label>
            <input type="email" className="mt-1 w-full rounded-xl border border-gray-300 bg-sportify-light p-2.5 text-sm outline-none focus:border-sportify-blue" placeholder="ejemplo@unlp.edu.ar" />
          </div>
          <div>
            <label className="block text-sm font-semibold text-sportify-dark">Contraseña</label>
            <input type="password" className="mt-1 w-full rounded-xl border border-gray-300 bg-sportify-light p-2.5 text-sm outline-none focus:border-sportify-blue" />
          </div>
          {/* Botón Principal usando el Verde Vibrante para llamar a la acción */}
          <button type="button" className="w-full rounded-xl bg-sportify-green p-3 text-sm font-bold text-white hover:bg-sportify-deepSea transition-colors shadow-sm">
            Ingresar al Complejo
          </button>
        </form>
        <div className="text-center">
          <Link to="/dashboard" className="text-xs font-medium text-sportify-blue hover:text-sportify-cyan transition-colors">
            Ver Vista de Demostración del Panel →
          </Link>
        </div>
      </div>
    </div>
  );
};

const Dashboard = () => {
  return (
    <div className="flex min-h-screen bg-sportify-light">
      {/* Sidebar corporativo usando el Verde Mar Profundo */}
      <aside className="w-64 bg-sportify-deepSea p-6 text-white space-y-6">
        <h2 className="text-2xl font-black tracking-wider text-sportify-lime">SPORTIFY</h2>
        <nav className="space-y-2">
          <a href="#" className="block rounded-xl bg-sportify-blue p-3 text-sm font-bold transition-transform hover:scale-105">
            📅 Historial de Turnos
          </a>
          <a href="#" className="block rounded-xl p-3 text-sm font-medium hover:bg-white/10 transition-colors">
            👥 Gestión de Socios
          </a>
        </nav>
      </aside>
      
      {/* Área de Contenido Principal sobre Blanco Puro */}
      <main className="flex-1 bg-sportify-white p-8">
        <header className="flex justify-between items-center border-b border-sportify-light pb-4 mb-6">
          <h1 className="text-3xl font-black text-sportify-blue">Panel de Administración</h1>
          <Link to="/" className="text-sm font-bold text-red-500 hover:text-red-700 transition-colors">Cerrar Sesión</Link>
        </header>
        
        {/* Tarjeta contenedora usando Gris Claro Neutral para delimitar secciones */}
        <div className="rounded-2xl bg-sportify-light p-6 border border-gray-200">
          <h3 className="text-lg font-bold text-sportify-dark mb-2">Estado del Sistema</h3>
          <p className="text-sm text-sportify-dark opacity-80 leading-relaxed">
            Estructura base brandeada exitosamente. El entorno está listo para maquetar el calendario relacional de fútbol, básquet, vóley y pádel.
          </p>
        </div>
      </main>
    </div>
  );
};

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </Router>
  );
}

export default App;