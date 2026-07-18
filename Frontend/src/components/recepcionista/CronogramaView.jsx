import React, { useState } from 'react';
import { useFetch } from '../../hooks/useFetch';
import '../veterinario/HistorialClinico.css';
import '../cronograma/Cronograma.css';
import CronogramaSemana from '../cronograma/CronogramaSemana';
import CronogramaCalendario from '../cronograma/CronogramaCalendario';

const hoyISO = () => new Date().toISOString().slice(0, 10);

const CronogramaView = () => {
  const [tab, setTab] = useState('dia');
  const [fecha, setFecha] = useState(hoyISO());
  const { data, loading, error } = useFetch(`/horarios/dia/${fecha}`, {
    deps: [fecha, tab],
    enabled: tab === 'dia',
    errorMessage: 'No se pudo cargar el cronograma',
  });

  return (
    <div className="form-section">
      <h2>Cronograma de veterinarios</h2>

      <div className="cro-tabs">
        <button className={`cro-tab ${tab === 'dia' ? 'active' : ''}`} onClick={() => setTab('dia')}>Día</button>
        <button className={`cro-tab ${tab === 'semana' ? 'active' : ''}`} onClick={() => setTab('semana')}>Semana</button>
        <button className={`cro-tab ${tab === 'calendario' ? 'active' : ''}`} onClick={() => setTab('calendario')}>Calendario</button>
      </div>

      {tab === 'dia' && (
        <>
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
                      <tr><th>Veterinario</th><th>Especialidad</th><th>Turno</th><th>Estado</th><th>Origen</th></tr>
                    </thead>
                    <tbody>
                      {data.veterinarios.map((v) => (
                        <tr key={`${v.id_veterinario}-${v.turno}`}>
                          <td>{v.veterinario || '--'}</td>
                          <td>{v.especialidad || '--'}</td>
                          <td>{v.turno}</td>
                          <td><span className={`estado-badge ${v.estado === 'Activo' ? 'estado-completada' : 'estado-cancelada'}`}>{v.estado || '--'}</span></td>
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
        </>
      )}

      {tab === 'semana' && <CronogramaSemana />}
      {tab === 'calendario' && <CronogramaCalendario />}
    </div>
  );
};

export default CronogramaView;
