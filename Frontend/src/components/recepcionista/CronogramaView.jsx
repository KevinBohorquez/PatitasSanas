import React, { useState, useEffect } from 'react';
import '../veterinario/HistorialClinico.css';

const hoyISO = () => new Date().toISOString().slice(0, 10);

const CronogramaView = () => {
  const [fecha, setFecha] = useState(hoyISO());
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDia = async (f) => {
    try {
      setLoading(true);
      setError(null);
      const res = await fetch(`/api/v1/horarios/dia/${f}`);
      if (!res.ok) throw new Error('No se pudo cargar el cronograma');
      setData(await res.json());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchDia(fecha); }, [fecha]);

  return (
    <div className="form-section">
      <h2>Veterinarios que trabajan</h2>

      <div className="form-group" style={{ maxWidth: 260 }}>
        <label>Fecha:</label>
        <input type="date" value={fecha} onChange={(e) => setFecha(e.target.value)} />
      </div>

      {loading && <p>Cargando...</p>}
      {error && <p>Error: {error}</p>}

      {data && !loading && (
        <>
          <p><strong>{data.dia_semana}</strong> · {data.total} veterinario(s) en turno</p>
          {data.veterinarios.length > 0 ? (
            <div className="consulta-list">
              <table>
                <thead>
                  <tr>
                    <th>Veterinario</th>
                    <th>Especialidad</th>
                    <th>Turno</th>
                    <th>Estado</th>
                    <th>Origen</th>
                  </tr>
                </thead>
                <tbody>
                  {data.veterinarios.map((v) => (
                    <tr key={`${v.id_veterinario}-${v.turno}`}>
                      <td>{v.veterinario || '--'}</td>
                      <td>{v.especialidad || '--'}</td>
                      <td>{v.turno}</td>
                      <td>
                        <span className={`estado-badge ${v.estado === 'Activo' ? 'estado-completada' : 'estado-cancelada'}`}>
                          {v.estado || '--'}
                        </span>
                      </td>
                      <td>{v.origen === 'excepcion' ? 'Excepción' : 'Recurrente'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p>No hay veterinarios programados para esta fecha.</p>
          )}
        </>
      )}
    </div>
  );
};

export default CronogramaView;
