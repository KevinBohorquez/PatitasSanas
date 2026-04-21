// pages/VeterinarioDashboard.jsx
import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import AppBar from '../components/common/AppBar';
import Sidebar from '../components/common/Sidebar';
import SolicitudesAtencion from '../components/veterinario/SolicitudesAtencion';
import CitasProgramadas from '../components/veterinario/CitasProgramadas';
import ListadoMascotas from '../components/veterinario/ListadoMascotas';
import '../styles/Dashboard.css';

const VeterinarioDashboard = () => {
  const { user } = useAuth();
  const [activeView, setActiveView] = useState('inicio');

  const getUserDisplayName = () => {
    if (user?.name && user.name !== user?.username) {
      return user.name;
    }
    if (user?.session_info?.nombre_completo) {
      return user.session_info.nombre_completo;
    }
    return user?.username || 'VETERINARIO';
  };

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
        return (
          <div className="welcome-content">
            <div className="welcome-header">
              <h2>Bienvenido, veterinario</h2>
              <p>Especialidad: Medicina General</p>
            </div>
            
            <div className="quick-stats">
              <div className="stat-card">
                <h3>Próxima cita</h3>
                <p>Hoy - 14:30</p>
                <small>Mascota: Lucky</small>
              </div>
              
              <div className="stat-card">
                <h3>Últimas atenciones</h3>
                <div className="attention-tabs">
                  <button className="tab active">Fecha</button>
                  <button className="tab">Mascota</button>
                  <button className="tab">Cliente</button>
                </div>
                <div className="attention-list">
                  <div className="attention-item">
                    <span>15/01/2025 - Max - Consulta</span>
                  </div>
                  <div className="attention-item">
                    <span>14/01/2025 - Luna - Vacunación</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        );
    }
  };

  return (
    <div className="dashboard-layout">
      <Sidebar 
        items={sidebarItems} 
        activeItem={activeView}
        onItemClick={setActiveView}
      />
      
      <div className="main-content">
        <AppBar 
          title="🟢 Cuenta de:"
          subtitle={getUserDisplayName()}
        />
        
        <div className="dashboard-content">
          {renderContent()}
        </div>
      </div>
    </div>
  );
};

export default VeterinarioDashboard;