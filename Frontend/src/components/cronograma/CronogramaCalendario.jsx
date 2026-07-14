import React, { useState, useEffect } from 'react';
import './Cronograma.css';

const MESES = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio',
  'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
const DIAS_CAB = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'];

// Vista calendario mensual: cada día muestra cuántos veterinarios trabajan.
const CronogramaCalendario = () => {
  const now = new Date();
  const [anio, setAnio] = useState(now.getFullYear());
  const [mes, setMes] = useState(now.getMonth() + 1); // 1-12
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    (async () => {
      try {
        setLoading(true); setError(null);
        const r = await fetch(`/api/v1/horarios/mes/${anio}/${mes}`);
        if (!r.ok) throw new Error('No se pudo cargar el mes');
        setData(await r.json());
      } catch (e) { setError(e.message); } finally { setLoading(false); }
    })();
  }, [anio, mes]);

  const cambiarMes = (delta) => {
    let m = mes + delta, a = anio;
    if (m < 1) { m = 12; a -= 1; }
    if (m > 12) { m = 1; a += 1; }
    setMes(m); setAnio(a);
  };

  // Construir la grilla del mes (Lunes primero).
  const primero = new Date(anio, mes - 1, 1);
  const offset = (primero.getDay() + 6) % 7; // 0 = Lunes
  const porDia = {};
  if (data) data.dias.forEach((d) => { porDia[Number(d.fecha.slice(8, 10))] = d; });
  const totalDias = data ? data.dias.length : 0;

  const celdas = [];
  for (let i = 0; i < offset; i++) celdas.push(null);
  for (let d = 1; d <= totalDias; d++) celdas.push(d);

  return (
    <div>
      <div className="cro-toolbar">
        <button className="cro-nav" onClick={() => cambiarMes(-1)}>◀</button>
        <strong>{MESES[mes - 1]} {anio}</strong>
        <button className="cro-nav" onClick={() => cambiarMes(1)}>▶</button>
      </div>

      {loading && <p>Cargando...</p>}
      {error && <p>Error: {error}</p>}

      {data && !loading && (
        <div className="cro-cal">
          <div className="cro-cal-head">
            {DIAS_CAB.map((d) => <div key={d} className="cro-cal-hcell">{d}</div>)}
          </div>
          <div className="cro-cal-grid">
            {celdas.map((d, i) => {
              if (d === null) return <div key={`b${i}`} className="cro-cal-cell cro-cal-empty" />;
              const info = porDia[d];
              const total = info ? info.total : 0;
              return (
                <div key={d} className={`cro-cal-cell ${total > 0 ? 'cro-cal-activo' : ''}`}>
                  <div className="cro-cal-num">{d}</div>
                  {total > 0 && <div className="cro-cal-badge">{total} vet</div>}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default CronogramaCalendario;
