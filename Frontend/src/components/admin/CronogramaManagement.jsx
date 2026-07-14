import React, { useState, useEffect } from 'react';
import '../veterinario/HistorialClinico.css';
import '../cronograma/Cronograma.css';
import CronogramaSemana from '../cronograma/CronogramaSemana';
import CronogramaCalendario from '../cronograma/CronogramaCalendario';

const DIAS = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo'];
const TURNOS = ['Mañana', 'Tarde', 'Noche', 'Madrugada'];
const hoyISO = () => new Date().toISOString().slice(0, 10);

const CronogramaManagement = () => {
  const [vets, setVets] = useState([]);
  const [recurrentes, setRecurrentes] = useState([]);
  const [excepciones, setExcepciones] = useState([]);
  const [roster, setRoster] = useState(null);
  const [tab, setTab] = useState('dia');
  const [filtroRecVet, setFiltroRecVet] = useState('');
  const [filtroExcVista, setFiltroExcVista] = useState('proximas');
  const [filtroExcVet, setFiltroExcVet] = useState('');
  const [rosterFecha, setRosterFecha] = useState(hoyISO());
  const [error, setError] = useState(null);

  // Formularios
  const [recForm, setRecForm] = useState({ id_veterinario: '', dia_semana: 'Lunes', turno: 'Mañana' });
  const [excForm, setExcForm] = useState({ id_veterinario: '', fecha: hoyISO(), trabaja: true, turno: 'Mañana' });

  const cargarVets = async () => {
    const r = await fetch('/api/v1/veterinarios/?limit=100');
    const d = await r.json();
    setVets(d.veterinarios || []);
  };
  const cargarRecurrentes = async () => {
    const r = await fetch('/api/v1/horarios/recurrente');
    setRecurrentes(await r.json());
  };
  const cargarExcepciones = async () => {
    const r = await fetch('/api/v1/horarios/excepcion');
    setExcepciones(await r.json());
  };
  const cargarRoster = async (f) => {
    const r = await fetch(`/api/v1/horarios/dia/${f}`);
    setRoster(await r.json());
  };

  useEffect(() => {
    cargarVets(); cargarRecurrentes(); cargarExcepciones();
  }, []);
  useEffect(() => { cargarRoster(rosterFecha); }, [rosterFecha]);

  const post = async (url, body) => {
    const r = await fetch(url, {
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
      if (!recForm.id_veterinario) throw new Error('Elige un veterinario');
      await post('/api/v1/horarios/recurrente', {
        id_veterinario: Number(recForm.id_veterinario),
        dia_semana: recForm.dia_semana, turno: recForm.turno,
      });
      await cargarRecurrentes(); await cargarRoster(rosterFecha);
    } catch (err) { setError(err.message); }
  };

  const agregarExcepcion = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      if (!excForm.id_veterinario) throw new Error('Elige un veterinario');
      await post('/api/v1/horarios/excepcion', {
        id_veterinario: Number(excForm.id_veterinario),
        fecha: excForm.fecha, trabaja: excForm.trabaja,
        turno: excForm.trabaja ? excForm.turno : null,
      });
      await cargarExcepciones(); await cargarRoster(rosterFecha);
    } catch (err) { setError(err.message); }
  };

  const borrar = async (url, recargar) => {
    await fetch(url, { method: 'DELETE' });
    await recargar(); await cargarRoster(rosterFecha);
  };

  // Filtros (client-side sobre lo ya cargado)
  const recurrentesFiltrados = filtroRecVet
    ? recurrentes.filter((h) => String(h.id_veterinario) === String(filtroRecVet))
    : recurrentes;

  const hoyStr = hoyISO();
  let excepcionesFiltradas = excepciones;
  if (filtroExcVista === 'proximas') excepcionesFiltradas = excepcionesFiltradas.filter((e) => e.fecha >= hoyStr);
  else if (filtroExcVista === 'libres') excepcionesFiltradas = excepcionesFiltradas.filter((e) => !e.trabaja);
  if (filtroExcVet) excepcionesFiltradas = excepcionesFiltradas.filter((e) => String(e.id_veterinario) === String(filtroExcVet));

  return (
    <div className="form-section">
      <h2>Cronograma de veterinarios</h2>

      <div className="cro-tabs">
        <button className={`cro-tab ${tab === 'dia' ? 'active' : ''}`} onClick={() => setTab('dia')}>Día y gestión</button>
        <button className={`cro-tab ${tab === 'semana' ? 'active' : ''}`} onClick={() => setTab('semana')}>Semana</button>
        <button className={`cro-tab ${tab === 'calendario' ? 'active' : ''}`} onClick={() => setTab('calendario')}>Calendario</button>
      </div>

      {tab === 'semana' && <CronogramaSemana />}
      {tab === 'calendario' && <CronogramaCalendario />}

      {tab === 'dia' && (
        <>
      {error && <p style={{ color: '#c62828' }}>Error: {error}</p>}

      {/* Roster del día */}
      <h3>Veterinarios en turno</h3>
      <div className="form-group" style={{ maxWidth: 260 }}>
        <label>Fecha:</label>
        <input type="date" value={rosterFecha} onChange={(e) => setRosterFecha(e.target.value)} />
      </div>
      {roster && (
        <div className="consulta-list">
          <p><strong>{roster.dia_semana}</strong> · {roster.total} en turno</p>
          <table>
            <thead><tr><th>Veterinario</th><th>Turno</th><th>Estado</th><th>Origen</th></tr></thead>
            <tbody>
              {roster.veterinarios.map((v) => (
                <tr key={`${v.id_veterinario}-${v.turno}`}>
                  <td>{v.veterinario}</td><td>{v.turno}</td>
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
          <label>Veterinario:</label>
          <select value={recForm.id_veterinario} onChange={(e) => setRecForm({ ...recForm, id_veterinario: e.target.value })}>
            <option value="">-- elegir --</option>
            {vets.map((v) => <option key={v.id_veterinario} value={v.id_veterinario}>{v.nombre} {v.apellido_paterno}</option>)}
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
        <label>Filtrar por veterinario:</label>
        <select value={filtroRecVet} onChange={(e) => setFiltroRecVet(e.target.value)}>
          <option value="">Todos</option>
          {vets.map((v) => <option key={v.id_veterinario} value={v.id_veterinario}>{v.nombre} {v.apellido_paterno}</option>)}
        </select>
      </div>
      <div className="consulta-list">
        <table>
          <thead><tr><th>Veterinario</th><th>Día</th><th>Turno</th><th></th></tr></thead>
          <tbody>
            {recurrentesFiltrados.map((h) => (
              <tr key={h.id_horario}>
                <td>{h.veterinario}</td><td>{h.dia_semana}</td><td>{h.turno}</td>
                <td><button className="btn-close" onClick={() => borrar(`/api/v1/horarios/recurrente/${h.id_horario}`, cargarRecurrentes)}>Quitar</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Excepciones */}
      <h3 style={{ marginTop: 24 }}>Excepciones por fecha</h3>
      <form onSubmit={agregarExcepcion} style={{ display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'flex-end' }}>
        <div className="form-group">
          <label>Veterinario:</label>
          <select value={excForm.id_veterinario} onChange={(e) => setExcForm({ ...excForm, id_veterinario: e.target.value })}>
            <option value="">-- elegir --</option>
            {vets.map((v) => <option key={v.id_veterinario} value={v.id_veterinario}>{v.nombre} {v.apellido_paterno}</option>)}
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
          <label>Veterinario:</label>
          <select value={filtroExcVet} onChange={(e) => setFiltroExcVet(e.target.value)}>
            <option value="">Todos</option>
            {vets.map((v) => <option key={v.id_veterinario} value={v.id_veterinario}>{v.nombre} {v.apellido_paterno}</option>)}
          </select>
        </div>
      </div>
      <div className="consulta-list">
        <table>
          <thead><tr><th>Veterinario</th><th>Fecha</th><th>¿Trabaja?</th><th>Turno</th><th></th></tr></thead>
          <tbody>
            {excepcionesFiltradas.map((ex) => (
              <tr key={ex.id_excepcion}>
                <td>{ex.veterinario}</td><td>{ex.fecha}</td>
                <td>{ex.trabaja ? 'Sí' : 'Día libre'}</td><td>{ex.turno || '--'}</td>
                <td><button className="btn-close" onClick={() => borrar(`/api/v1/horarios/excepcion/${ex.id_excepcion}`, cargarExcepciones)}>Quitar</button></td>
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
