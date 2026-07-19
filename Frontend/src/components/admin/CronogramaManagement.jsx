import React, { useState, useEffect } from 'react';
import { apiFetch } from '../../api/client';
import '../veterinario/HistorialClinico.css';
import '../cronograma/Cronograma.css';
import CronogramaSemana from '../cronograma/CronogramaSemana';
import CronogramaCalendario from '../cronograma/CronogramaCalendario';
import { CONFIG_VET } from '../cronograma/cronogramaConfig';

const DIAS = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo'];
const TURNOS = ['Mañana', 'Tarde', 'Noche', 'Madrugada'];
const hoyISO = () => new Date().toISOString().slice(0, 10);
const cap = (s) => s.charAt(0).toUpperCase() + s.slice(1);

// Gestión del cronograma. Reutilizable para veterinarios o recepcionistas vía `config`.
const CronogramaManagement = ({ config = CONFIG_VET }) => {
  const { base, personUrl, personArrayKey, personIdKey, rosterKey, nameKey, label } = config;

  const [personas, setPersonas] = useState([]);
  const [recurrentes, setRecurrentes] = useState([]);
  const [excepciones, setExcepciones] = useState([]);
  const [roster, setRoster] = useState(null);
  const [rosterFecha, setRosterFecha] = useState(hoyISO());
  const [error, setError] = useState(null);
  const [tab, setTab] = useState('dia');
  const [filtroRecP, setFiltroRecP] = useState('');
  const [filtroExcVista, setFiltroExcVista] = useState('proximas');
  const [filtroExcP, setFiltroExcP] = useState('');

  const [recForm, setRecForm] = useState({ id: '', dia_semana: 'Lunes', turno: 'Mañana' });
  const [excForm, setExcForm] = useState({ id: '', fecha: hoyISO(), trabaja: true, turno: 'Mañana' });

  const cargarPersonas = async () => {
    const r = await apiFetch(personUrl);
    const d = await r.json();
    setPersonas(d[personArrayKey] || []);
  };
  const cargarRecurrentes = async () => setRecurrentes(await (await apiFetch(`${base}/recurrente`)).json());
  const cargarExcepciones = async () => setExcepciones(await (await apiFetch(`${base}/excepcion`)).json());
  const cargarRoster = async (f) => setRoster(await (await apiFetch(`${base}/dia/${f}`)).json());

  useEffect(() => {
    cargarPersonas(); cargarRecurrentes(); cargarExcepciones();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [base]);
  useEffect(() => { cargarRoster(rosterFecha); /* eslint-disable-line */ }, [rosterFecha, base]);

  const post = async (url, body) => {
    const r = await apiFetch(url, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
    });
    if (!r.ok) {
      const e = await r.json().catch(() => ({}));
      throw new Error(e.detail || 'Error al guardar');
    }
  };

  const agregarRecurrente = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      if (!recForm.id) throw new Error(`Elige un ${label}`);
      await post(`${base}/recurrente`, {
        [personIdKey]: Number(recForm.id), dia_semana: recForm.dia_semana, turno: recForm.turno,
      });
      await cargarRecurrentes(); await cargarRoster(rosterFecha);
    } catch (err) { setError(err.message); }
  };

  const agregarExcepcion = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      if (!excForm.id) throw new Error(`Elige un ${label}`);
      await post(`${base}/excepcion`, {
        [personIdKey]: Number(excForm.id), fecha: excForm.fecha, trabaja: excForm.trabaja,
        turno: excForm.trabaja ? excForm.turno : null,
      });
      await cargarExcepciones(); await cargarRoster(rosterFecha);
    } catch (err) { setError(err.message); }
  };

  const borrar = async (url, recargar) => {
    await apiFetch(url, { method: 'DELETE' });
    await recargar(); await cargarRoster(rosterFecha);
  };

  const opcionesPersona = personas.map((p) =>
    <option key={p[personIdKey]} value={p[personIdKey]}>{p.nombre} {p.apellido_paterno}</option>);

  // Filtros client-side
  const recurrentesFiltrados = filtroRecP
    ? recurrentes.filter((h) => String(h[personIdKey]) === String(filtroRecP))
    : recurrentes;

  const hoyStr = hoyISO();
  let excepcionesFiltradas = excepciones;
  if (filtroExcVista === 'proximas') excepcionesFiltradas = excepcionesFiltradas.filter((e) => e.fecha >= hoyStr);
  else if (filtroExcVista === 'libres') excepcionesFiltradas = excepcionesFiltradas.filter((e) => !e.trabaja);
  if (filtroExcP) excepcionesFiltradas = excepcionesFiltradas.filter((e) => String(e[personIdKey]) === String(filtroExcP));

  return (
    <div className="form-section">
      <h2>Cronograma de {config.labelPlural}</h2>

      <div className="cro-tabs">
        <button className={`cro-tab ${tab === 'dia' ? 'active' : ''}`} onClick={() => setTab('dia')}>Día y gestión</button>
        <button className={`cro-tab ${tab === 'semana' ? 'active' : ''}`} onClick={() => setTab('semana')}>Semana</button>
        <button className={`cro-tab ${tab === 'calendario' ? 'active' : ''}`} onClick={() => setTab('calendario')}>Calendario</button>
      </div>

      {tab === 'semana' && <CronogramaSemana config={config} />}
      {tab === 'calendario' && <CronogramaCalendario config={config} />}

      {tab === 'dia' && (
        <>
          {error && <p style={{ color: '#c62828' }}>Error: {error}</p>}

          {/* Roster del día */}
          <h3>{cap(config.labelPlural)} en turno</h3>
          <div className="form-group" style={{ maxWidth: 260 }}>
            <label>Fecha:</label>
            <input type="date" value={rosterFecha} onChange={(e) => setRosterFecha(e.target.value)} />
          </div>
          {roster && (
            <div className="consulta-list">
              <p><strong>{roster.dia_semana}</strong> · {roster.total} en turno</p>
              <table>
                <thead><tr><th>{cap(label)}</th><th>Turno</th><th>Estado</th><th>Origen</th></tr></thead>
                <tbody>
                  {(roster[rosterKey] || []).map((v) => (
                    <tr key={`${v[personIdKey]}-${v.turno}`}>
                      <td>{v[nameKey]}</td><td>{v.turno}</td>
                      <td><span className={`estado-badge ${v.estado === 'Activo' ? 'estado-completada' : 'estado-cancelada'}`}>{v.estado}</span></td>
                      <td>{v.origen === 'excepcion' ? 'Excepción' : 'Recurrente'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Horario recurrente */}
          <h3 style={{ marginTop: 24 }}>Horario semanal recurrente</h3>
          <form onSubmit={agregarRecurrente} style={{ display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'flex-end' }}>
            <div className="form-group">
              <label>{cap(label)}:</label>
              <select value={recForm.id} onChange={(e) => setRecForm({ ...recForm, id: e.target.value })}>
                <option value="">-- elegir --</option>{opcionesPersona}
              </select>
            </div>
            <div className="form-group">
              <label>Día:</label>
              <select value={recForm.dia_semana} onChange={(e) => setRecForm({ ...recForm, dia_semana: e.target.value })}>
                {DIAS.map((d) => <option key={d} value={d}>{d}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Turno:</label>
              <select value={recForm.turno} onChange={(e) => setRecForm({ ...recForm, turno: e.target.value })}>
                {TURNOS.map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <button type="submit" className="btn-diagnostico">Agregar</button>
          </form>
          <div className="form-group" style={{ maxWidth: 300 }}>
            <label>Filtrar por {label}:</label>
            <select value={filtroRecP} onChange={(e) => setFiltroRecP(e.target.value)}>
              <option value="">Todos</option>{opcionesPersona}
            </select>
          </div>
          <div className="consulta-list">
            <table>
              <thead><tr><th>{cap(label)}</th><th>Día</th><th>Turno</th><th></th></tr></thead>
              <tbody>
                {recurrentesFiltrados.map((h) => (
                  <tr key={h.id_horario}>
                    <td>{h[nameKey]}</td><td>{h.dia_semana}</td><td>{h.turno}</td>
                    <td><button className="btn-close" onClick={() => borrar(`${base}/recurrente/${h.id_horario}`, cargarRecurrentes)}>Quitar</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Excepciones */}
          <h3 style={{ marginTop: 24 }}>Excepciones por fecha</h3>
          <form onSubmit={agregarExcepcion} style={{ display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'flex-end' }}>
            <div className="form-group">
              <label>{cap(label)}:</label>
              <select value={excForm.id} onChange={(e) => setExcForm({ ...excForm, id: e.target.value })}>
                <option value="">-- elegir --</option>{opcionesPersona}
              </select>
            </div>
            <div className="form-group">
              <label>Fecha:</label>
              <input type="date" value={excForm.fecha} onChange={(e) => setExcForm({ ...excForm, fecha: e.target.value })} />
            </div>
            <div className="form-group">
              <label>¿Trabaja?</label>
              <select value={excForm.trabaja ? 'si' : 'no'} onChange={(e) => setExcForm({ ...excForm, trabaja: e.target.value === 'si' })}>
                <option value="si">Sí (turno extra/cambio)</option>
                <option value="no">No (día libre)</option>
              </select>
            </div>
            {excForm.trabaja && (
              <div className="form-group">
                <label>Turno:</label>
                <select value={excForm.turno} onChange={(e) => setExcForm({ ...excForm, turno: e.target.value })}>
                  {TURNOS.map((t) => <option key={t} value={t}>{t}</option>)}
                </select>
              </div>
            )}
            <button type="submit" className="btn-diagnostico">Agregar</button>
          </form>
          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'flex-end' }}>
            <div className="form-group">
              <label>Ver:</label>
              <select value={filtroExcVista} onChange={(e) => setFiltroExcVista(e.target.value)}>
                <option value="proximas">Próximas (vigentes)</option>
                <option value="libres">Días libres / faltas</option>
                <option value="todas">Todas</option>
              </select>
            </div>
            <div className="form-group">
              <label>{cap(label)}:</label>
              <select value={filtroExcP} onChange={(e) => setFiltroExcP(e.target.value)}>
                <option value="">Todos</option>{opcionesPersona}
              </select>
            </div>
          </div>
          <div className="consulta-list">
            <table>
              <thead><tr><th>{cap(label)}</th><th>Fecha</th><th>¿Trabaja?</th><th>Turno</th><th></th></tr></thead>
              <tbody>
                {excepcionesFiltradas.map((ex) => (
                  <tr key={ex.id_excepcion}>
                    <td>{ex[nameKey]}</td><td>{ex.fecha}</td>
                    <td>{ex.trabaja ? 'Sí' : 'Día libre'}</td><td>{ex.turno || '--'}</td>
                    <td><button className="btn-close" onClick={() => borrar(`${base}/excepcion/${ex.id_excepcion}`, cargarExcepciones)}>Quitar</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
};

export default CronogramaManagement;
