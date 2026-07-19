// pages/VeterinarioDashboard.jsx
import React, { useState, useEffect } from 'react';
import { apiFetch } from '../api/client';
import { useAuth } from '../context/AuthContext';
import DashboardLayout from '../layouts/DashboardLayout';
import { getUserDisplayName } from '../utils/userDisplay';
import SolicitudesAtencion from '../components/veterinario/SolicitudesAtencion';
import CitasProgramadas from '../components/veterinario/CitasProgramadas';
import ListadoMascotas from '../components/veterinario/ListadoMascotas';

const formatFechaHora = (valor) => (valor ? new Date(valor).toLocaleString() : '--');

// Panel de inicio del veterinario, con datos reales del backend.
const InicioVeterinario = ({ user, onNavigate }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDashboard = async () => {
      if (!user?.id) return;
      try {
        setLoading(true);
        setError(null);
        const res = await apiFetch(`/veterinarios/dashboard/${user.id}`);
        if (!res.ok) throw new Error('No se pudo cargar el panel');
        setData(await res.json());
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, [user?.id]);

  if (loading) return <div className="welcome-content"><p>Cargando panel...</p></div>;
  if (error) return <div className="welcome-content"><p>Error: {error}</p></div>;
  if (!data) return null;

  const { veterinario, proxima_cita, pendientes_atender, solicitudes_asignadas, ultimas_atenciones } = data;

  return (
    <div className="vet-dashboard">
      <div className="vet-dashboard-header">
        <h2>Bienvenido, {veterinario?.nombre || user?.username}</h2>
        <p>
          Especialidad: {veterinario?.especialidad || 'No registrada'}
          {veterinario?.turno ? ` · Turno: ${veterinario.turno}` : ''}
          {veterinario?.disposicion ? ` · ${veterinario.disposicion}` : ''}
        </p>
      </div>

      <div className="vet-cards">
        {/* Próxima cita */}
        <div className="stat-card stat-blue">
          <h3>Próxima cita</h3>
          {proxima_cita ? (
            <>
              <p className="stat-highlight">{formatFechaHora(proxima_cita.fecha_hora_programada)}</p>
              <small>
                Mascota: {proxima_cita.mascota || '--'}
                {proxima_cita.servicio ? ` · ${proxima_cita.servicio}` : ''}
                {proxima_cita.requiere_ayuno ? ' · Requiere ayuno' : ''}
              </small>
            </>
          ) : (
            <p>No hay citas próximas.</p>
          )}
        </div>

        {/* Pendientes de atender */}
        <div
          className="stat-card stat-orange stat-clickable"
          onClick={() => onNavigate('citas')}
          role="button"
          tabIndex={0}
        >
          <h3>Pendientes de atender</h3>
          <p className="stat-number">{pendientes_atender}</p>
          <small>Citas programadas asignadas · ver todas</small>
        </div>

        {/* Solicitudes asignadas */}
        <div
          className="stat-card stat-purple stat-clickable"
          onClick={() => onNavigate('solicitudes')}
          role="button"
          tabIndex={0}
        >
          <h3>Solicitudes asignadas ({solicitudes_asignadas?.total ?? 0})</h3>
          {solicitudes_asignadas?.items?.length > 0 ? (
            <div className="attention-list">
              {solicitudes_asignadas.items.map((s) => (
                <div key={s.id_solicitud} className="attention-item">
                  <span>{s.mascota || 'Mascota'} · {s.tipo_solicitud}</span>
                  <span className={`estado-badge estado-${(s.estado || '').toLowerCase().replace(/\s+/g, '-')}`}>
                    {s.estado}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p>Sin solicitudes asignadas.</p>
          )}
        </div>

        {/* Últimas atenciones */}
        <div className="stat-card stat-green">
          <h3>Últimas atenciones</h3>
          {ultimas_atenciones?.length > 0 ? (
            <div className="attention-list">
              {ultimas_atenciones.map((a) => (
                <div key={a.id_cita} className="attention-item">
                  <span>{formatFechaHora(a.fecha)} · {a.mascota || '--'}{a.servicio ? ` · ${a.servicio}` : ''}</span>
                </div>
              ))}
            </div>
          ) : (
            <p>Aún no hay atenciones registradas.</p>
          )}
        </div>
      </div>
    </div>
  );
};

const VeterinarioDashboard = () => {
  const { user } = useAuth();
  const [activeView, setActiveView] = useState('inicio');

  const sidebarItems = [
    { id: 'inicio', label: 'Inicio', icon: '🏠' },
    { id: 'solicitudes', label: 'Solicitudes de atención', icon: '📋' },
    { id: 'citas', label: 'Citas programadas', icon: '📅' },
    { id: 'mascotas', label: 'Mascotas', icon: '🐕' }
  ];

  const renderContent = () => {
    switch (activeView) {
      case 'solicitudes':
        return <SolicitudesAtencion />;
      case 'citas':
        return <CitasProgramadas />;
      case 'mascotas':
        return <ListadoMascotas />;
      default:
        return <InicioVeterinario user={user} onNavigate={setActiveView} />;
    }
  };

  return (
    <DashboardLayout
      sidebarItems={sidebarItems}
      activeView={activeView}
      onViewChange={setActiveView}
      userName={getUserDisplayName(user, 'VETERINARIO')}
    >
      {renderContent()}
    </DashboardLayout>
  );
};

export default VeterinarioDashboard;
