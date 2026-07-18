import React, { useState } from 'react';
import './Cronograma.css';
import { CONFIG_VET } from './cronogramaConfig';
import { useFetch } from '../../hooks/useFetch';

const MESES = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio',
  'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
const DIAS_CAB = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'];
const TURNOS = ['Mañana', 'Tarde', 'Noche', 'Madrugada'];

// Vista calendario mensual (grande) con tooltip al pasar el mouse.
const CronogramaCalendario = ({ config = CONFIG_VET }) => {
  const now = new Date();
  const [anio, setAnio] = useState(now.getFullYear());
  const [mes, setMes] = useState(now.getMonth() + 1);
  const [hover, setHover] = useState(null); // { info, x, y }
  const { data, loading, error } = useFetch(`${config.base}/mes/${anio}/${mes}`, {
    deps: [anio, mes, config.base],
    errorMessage: 'No se pudo cargar el mes',
  });

  const cambiarMes = (delta) => {
    let m = mes + delta, a = anio;
    if (m < 1) { m = 12; a -= 1; }
    if (m > 12) { m = 1; a += 1; }
    setMes(m); setAnio(a);
  };

  const primero = new Date(anio, mes - 1, 1);
  const offset = (primero.getDay() + 6) % 7; // 0 = Lunes
  const porDia = {};
  if (data) data.dias.forEach((d) => { porDia[Number(d.fecha.slice(8, 10))] = d; });
  const totalDias = data ? data.dias.length : 0;

  const celdas = [];
  for (let i = 0; i < offset; i++) celdas.push(null);
  for (let d = 1; d <= totalDias; d++) celdas.push(d);

  const moverTooltip = (info, e) => {
    const cerca = e.clientX > window.innerWidth - 280;
    setHover({ info, x: cerca ? e.clientX - 270 : e.clientX + 14, y: e.clientY + 14 });
  };

  return (
    <div>
      <div className="cro-toolbar">
        <button className="cro-nav" onClick={() => cambiarMes(-1)}>◀</button>
        <strong style={{ fontSize: '1.15rem' }}>{MESES[mes - 1]} {anio}</strong>
        <button className="cro-nav" onClick={() => cambiarMes(1)}>▶</button>
      </div>

      {loading && <p>Cargando...</p>}
      {error && <p>Error: {error}</p>}

      {data && !loading && (
        <div className="cro-cal cro-cal-lg">
          <div className="cro-cal-head">
            {DIAS_CAB.map((d) => <div key={d} className="cro-cal-hcell">{d}</div>)}
          </div>
          <div className="cro-cal-grid">
            {celdas.map((d, i) => {
              if (d === null) return <div key={`b${i}`} className="cro-cal-cell cro-cal-empty" />;
              const info = porDia[d];
              const total = info ? info.total : 0;
              return (
                <div
                  key={d}
                  className={`cro-cal-cell ${total > 0 ? 'cro-cal-activo' : ''}`}
                  onMouseEnter={total > 0 ? (e) => moverTooltip(info, e) : undefined}
                  onMouseMove={total > 0 ? (e) => moverTooltip(info, e) : undefined}
                  onMouseLeave={() => setHover(null)}
                >
                  <div className="cro-cal-num">{d}</div>
                  {total > 0 && <div className="cro-cal-badge">{total} {config.label === 'recepcionista' ? 'rec' : 'vet'}</div>}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {hover && (
        <div className="cro-cal-tip" style={{ left: hover.x, top: hover.y }}>
          <div className="cro-cal-tip-head">{hover.info.dia_semana} {hover.info.fecha.slice(8, 10)}/{hover.info.fecha.slice(5, 7)}</div>
          {TURNOS.map((t) => {
            const vs = (hover.info[config.rosterKey] || []).filter((v) => v.turno === t);
            if (vs.length === 0) return null;
            return (
              <div key={t} className="cro-cal-tip-row">
                <span className="cro-cal-tip-turno">{t}:</span>{' '}
                {vs.map((v) => `${v[config.nameKey]}${v.estado !== 'Activo' ? ' (inactivo)' : ''}`).join(', ')}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default CronogramaCalendario;
