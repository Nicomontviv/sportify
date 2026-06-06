import React from 'react';

const Login = ({ loginEmail, setLoginEmail, loginPassword, setLoginPassword, loginError, handleLogin ,alCambiarVista,onOlvidePassword = () => {} }) => {
  return (
    <div className="flex min-h-screen items-center justify-center bg-sportify-light px-4">
      <div className="w-full max-w-md space-y-6 rounded-2xl border border-gray-200 bg-sportify-white p-8 shadow-md">
        <div className="text-center">
          <h1 className="text-4xl font-extrabold tracking-tight text-sportify-blue">Sportify</h1>
          <p className="mt-2 text-sm text-sportify-dark opacity-70">Inicio de sesion</p>
        </div>
        {loginError && <div className="rounded-xl bg-red-50 p-3 text-sm font-semibold text-red-600 border border-red-200">⚠️ {loginError}</div>}
        <form onSubmit={handleLogin} className="space-y-4" autoComplete="off">
          <div>
            <label className="block text-sm font-semibold text-sportify-dark">Email </label>
            <input type="email"  required value={loginEmail} onChange={(e) => setLoginEmail(e.target.value)} className="mt-1 w-full rounded-xl border border-gray-300 bg-sportify-light p-2.5 text-sm outline-none focus:border-sportify-blue"  />
          </div>
          <div>
            <label className="block text-sm font-semibold text-sportify-dark">Contraseña</label>
            <input type="password" required value={loginPassword} onChange={(e) => setLoginPassword(e.target.value)} className="mt-1 w-full rounded-xl border border-gray-300 bg-sportify-light p-2.5 text-sm outline-none focus:border-sportify-blue" placeholder="••••••••" />
          </div>
          <button type="submit" className="w-full rounded-xl bg-sportify-blue p-3 text-sm font-bold text-white hover:bg-sportify-deepSea transition-colors shadow-sm">Ingresar</button>
          
        </form>
       <div className="mt-4 text-center">
  <p className="text-sm text-gray-600">
    ¿No tenés cuenta?{' '}
    <button type="button" onClick={alCambiarVista} className="text-[#1E90FF] hover:underline font-medium">
      Registrate acá
    </button>
    <div className="text-right">
  <button 
    type="button" 
    onClick={onOlvidePassword}
    className="text-sm text-gray-500 hover:underline"
  >
    ¿Olvidaste tu contraseña?
  </button>
</div>
  </p>
</div>
      </div>
      
    </div>
    
  );
};

export default Login;