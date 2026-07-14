import React, { useState, useEffect } from 'react';
import './Cronograma.css';

const TURNOS = ['Mañana', 'Tarde', 'Noche', 'Madrugada'];
const hoyISO = () => new Date().toISOString().slice(0, 10);
const fmt = (iso) => {
  const d = new Date(iso + 'T00:00:00');
  return d.toLocaleDateString('es-PE', { day: '2-digit', month: '2-digit' });
};

// Grilla semanal Lunes-Domingo: turnos en filas, días en columnas.
const CronogramaSemana = () => {
  const [fecha, setFecha] = useState(hoyISO());
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    (async () => {
      try {
        setLoading(true); setError(null);
        const r = await fetch(`/api/v1/horarios/semana/${fecha}`);
        if (!r.ok) throw new Error('No se pudo cargar la semana');
        setData(await r.json());
      } catch (e) { setError(e.message); } finally { setLoading(false); }
    })();
  }, [fecha]);

  const cambiarSemana = (dias) => {
    const d = new Date(fecha + 'T00:00:00');
    d.setDate(d.getDate() + dias);
    setFecha(d.toISOString().slice(0, 10));
  };

  return (
    <div>
      <div className="cro-toolbar">
        <button className="cro-nav" onClick={() => cambiarSemana(-7)}>◀ Semana anterior</button>
        <label>Semana de:
          <input type="date" value={fecha} onChange={(e) => setFecha(e.target.value)} />
        </label>
        <button className="cro-nav" onClick={() => cambiarSemana(7)}>Semana siguiente ▶</button>
      </div>

      {loading && <p>Cargando...</p>}
      {error && <p>Error: {error}</p>}

      {data && !loading && (
        <div className="cro-grid-wrap">
          <table className="cro-grid">
            <thead>
              <tr>
                <th className="cro-corner"></th>
                {data.dias.map((d) => (
                  <th key={d.fecha} className="cro-dia-head">
                    <div>{d.dia_semana}</div>
                    <small>{fmt(d.fecha)}</small>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {TURNOS.map((turno) => (
                <tr key={turno}>
                  <th className="cro-turno-head">{turno}</th>
                  {data.dias.map((d) => {
                    const vets = d.veterinarios.filter((v) => v.turno === turno);
                    return (
                      <td key={d.fecha + turno} className="cro-cell">
                        {vets.map((v) => (
                          <div key={v.id_veterinario}
                               className={`cro-vet ${v.estado !== 'Activo' ? 'cro-vet-inactivo' : ''} ${v.origen === 'excepcion' ? 'cro-vet-exc' : ''}`}
                               title={v.origen === 'excepcion' ? 'Excepción' : 'Recurrente'}>
                            {v.veterinario}{v.estado !== 'Activo' ? ' (inactivo)' : ''}
                          </div>
                        ))}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default CronogramaSemana;
