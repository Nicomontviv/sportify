import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Html5Qrcode } from 'html5-qrcode';

const Asistencia = ({ userSession, onVolver }) => {
  // Número de reserva ingresado a mano
  const [numeroReserva, setNumeroReserva] = useState('');
  // Datos del titular cuando la validación da OK
  const [titular, setTitular] = useState(null);
  // Mensaje de error de validación (reserva cancelada, ya asistió, etc.)
  const [errorValidacion, setErrorValidacion] = useState('');
  // Mensaje de éxito al marcar asistencia
  const [exito, setExito] = useState('');
  // Si la cámara está abierta o no
  const [camaraAbierta, setCamaraAbierta] = useState(false);
  // Mensaje de fallback si la cámara falla
  const [errorCamara, setErrorCamara] = useState('');

  // Referencia a la instancia del lector de QR (para poder apagarlo)
  const scannerRef = useRef(null);
  // Evita que un mismo escaneo dispare la consulta dos veces
  const yaLeyoRef = useRef(false);
  // id del div donde se monta la cámara
  const QR_REGION_ID = 'qr-region';

  const API = 'http://127.0.0.1:5000/api/asistencia';

  // --- Consulta al backend con un número de reserva ---
  const consultarReserva = async (id) => {
    setErrorValidacion('');
    setExito('');
    setTitular(null);

    if (!id) {
      setErrorValidacion('Ingresá un número de reserva');
      return;
    }

    try {
      const response = await axios.get(`${API}/${id}`);
      if (response.data.status === 'success') {
        setTitular(response.data.titular);
      }
    } catch (error) {
      setErrorValidacion(error.response?.data?.message || 'Error al consultar la reserva');
    }
  };

  // --- Botón "Buscar" del input manual ---
  const handleBuscarManual = () => {
    consultarReserva(numeroReserva.trim());
  };

  // --- Marcar asistencia (PUT) ---
  const handleMarcarAsistencia = async () => {
    if (!titular) return;
    setErrorValidacion('');
    setExito('');
    try {
      const response = await axios.put(`${API}/${titular.reserva_id}`);
      if (response.data.status === 'success') {
        setExito(`Asistencia registrada: ${titular.nombre} ${titular.apellido}`);
        setTitular(null);
        setNumeroReserva('');
      }
    } catch (error) {
      setErrorValidacion(error.response?.data?.message || 'Error al marcar asistencia');
    }
  };

  // --- Apagado seguro del scanner ---
  // Solo intenta frenar si realmente está corriendo, y siempre limpia
  // el recuadro. Todo envuelto para que un fallo acá no rompa nada.
  const detenerScanner = async () => {
    const scanner = scannerRef.current;
    scannerRef.current = null;
    if (!scanner) return;
    try {
      // getState(): 2 = SCANNING, 3 = PAUSED. Solo en esos casos se puede frenar.
      const estado = scanner.getState ? scanner.getState() : null;
      if (estado === 2 || estado === 3) {
        await scanner.stop();
      }
    } catch (e) {
      // si falla el stop no importa, igual seguimos
    }
    try {
      await scanner.clear();
    } catch (e) {
      // idem
    }
  };

  // --- Abrir / cerrar cámara ---
  const abrirCamara = () => {
    setErrorCamara('');
    yaLeyoRef.current = false;
    setCamaraAbierta(true);
  };

  const cerrarCamara = async () => {
    await detenerScanner();
    setCamaraAbierta(false);
  };

  // Cuando se abre la cámara, arrancamos el lector.
  // Todo el flujo está protegido: si no hay cámara o falla cualquier cosa,
  // mostramos el mensaje de fallback y el sistema sigue con el input manual.
  useEffect(() => {
    if (!camaraAbierta) return;

    let activo = true;

    const iniciar = async () => {
      try {
        // Chequeo previo: ¿hay alguna cámara disponible?
        // Si no hay (o se deniega el permiso), esto falla y vamos al catch
        // SIN haber inyectado nada en el DOM.
        const camaras = await Html5Qrcode.getCameras();
        if (!camaras || camaras.length === 0) {
          throw new Error('sin-camara');
        }
        if (!activo) return;

        const scanner = new Html5Qrcode(QR_REGION_ID);
        scannerRef.current = scanner;

        await scanner.start(
          { facingMode: 'environment' }, // cámara trasera si hay; si no, la que haya
          { fps: 10, qrbox: { width: 250, height: 250 } },
          (textoDecodificado) => {
            // Se leyó un QR: el texto es el id de la reserva.
            if (yaLeyoRef.current) return;
            yaLeyoRef.current = true;
            setNumeroReserva(textoDecodificado);
            cerrarCamara();
            consultarReserva(textoDecodificado.trim());
          },
          () => {
            // "no se detectó QR en este frame": lo ignoramos
          }
        );
      } catch (e) {
        // Cualquier fallo (sin cámara, permiso denegado, navegador la bloquea):
        // limpiamos, mostramos fallback y cerramos. El sistema no se rompe.
        await detenerScanner();
        if (activo) {
          setErrorCamara('No se pudo acceder a la cámara, usá el ingreso manual');
          setCamaraAbierta(false);
        }
      }
    };

    iniciar();

    // Cleanup: al cerrar la cámara o salir de la pantalla, apagamos el lector
    return () => {
      activo = false;
      detenerScanner();
    };
  }, [camaraAbierta]);

  return (
    <div className="min-h-screen bg-[#F5F5F5] p-6">
      <div className="max-w-2xl mx-auto bg-white p-8 rounded-lg shadow-md">
        {/* Encabezado */}
        <div className="flex justify-between items-center border-b pb-4 mb-6">
          <h1 className="text-2xl font-bold text-[#212121]">Registrar asistencia</h1>
          <button
            onClick={onVolver}
            className="bg-gray-200 hover:bg-gray-300 text-[#212121] font-bold py-2 px-4 rounded transition"
          >
            ← Volver
          </button>
        </div>

        {/* Mensaje de éxito */}
        {exito && (
          <div className="mb-4 p-3 rounded bg-green-100 text-green-800 border border-green-300">
            ✓ {exito}
          </div>
        )}

        {/* Botón QR */}
        <div className="mb-4">
          {!camaraAbierta ? (
            <button
              onClick={abrirCamara}
              className="bg-[#1E90FF] hover:bg-[#00CED1] text-white font-bold py-3 px-6 rounded-lg transition"
            >
              📷 Escanear QR
            </button>
          ) : (
            <button
              onClick={cerrarCamara}
              className="bg-red-500 hover:bg-red-600 text-white font-bold py-3 px-6 rounded-lg transition"
            >
              ✕ Cerrar cámara
            </button>
          )}
        </div>

        {/* Recuadro de la cámara (POV).
            SIEMPRE montado, solo se oculta con CSS cuando la cámara está cerrada.
            Esto evita que React choque con el HTML que inyecta la librería. */}
        <div className={camaraAbierta ? 'mb-4' : 'hidden'}>
          <div id={QR_REGION_ID} className="w-full max-w-sm mx-auto rounded-lg overflow-hidden border-2 border-[#1E90FF]" />
          <p className="text-sm text-gray-500 text-center mt-2">Apuntá la cámara al código QR</p>
        </div>

        {/* Fallback si la cámara falla */}
        {errorCamara && (
          <div className="mb-4 p-3 rounded bg-yellow-100 text-yellow-800 border border-yellow-300">
            {errorCamara}
          </div>
        )}

        {/* Input manual: método principal, siempre presente */}
        <div className="mb-4">
          <label className="block text-sm font-semibold text-[#212121] mb-2">
            N° de reserva (ingreso manual)
          </label>
          <div className="flex gap-2">
            <input
              type="number"
              value={numeroReserva}
              onChange={(e) => setNumeroReserva(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter') handleBuscarManual(); }}
              placeholder="Ej: 42"
              className="flex-1 border border-gray-300 rounded px-3 py-2 focus:outline-none focus:border-[#1E90FF]"
            />
            <button
              onClick={handleBuscarManual}
              className="bg-[#1E90FF] hover:bg-[#00CED1] text-white font-bold py-2 px-6 rounded transition"
            >
              Buscar
            </button>
          </div>
        </div>

        {/* Mensaje de error de validación */}
        {errorValidacion && (
          <div className="mb-4 p-3 rounded bg-red-100 text-red-800 border border-red-300">
            {errorValidacion}
          </div>
        )}

        {/* Tarjeta del titular (resultado OK) */}
        {titular && (
          <div className="mt-6 p-5 rounded-lg border-2 border-[#1E90FF] bg-blue-50">
            <h2 className="text-lg font-bold text-[#212121] mb-3">Datos del titular</h2>
            <div className="space-y-1 text-[#212121]">
              <p><span className="font-semibold">Nombre:</span> {titular.nombre} {titular.apellido}</p>
              <p><span className="font-semibold">DNI:</span> {titular.dni}</p>
              <p><span className="font-semibold">Actividad:</span> {titular.actividad}</p>
              <p><span className="font-semibold">Fecha:</span> {titular.fecha} ({titular.horario_inicio} - {titular.horario_fin})</p>
            </div>
            <p className="text-sm text-gray-600 mt-3 mb-3">
              Verificá que el DNI coincida con el documento físico antes de confirmar.
            </p>
            <button
              onClick={handleMarcarAsistencia}
              className="bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-6 rounded-lg transition w-full"
            >
              ✓ Marcar asistencia
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Asistencia;