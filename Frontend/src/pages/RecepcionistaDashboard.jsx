// pages/RecepcionistaDashboard.jsx
import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import AppBar from '../components/common/AppBar';
import Sidebar from '../components/common/Sidebar';
import Dashboard from '../components/recepcionista/Dashboard';
import ClientesManagement from '../components/recepcionista/ClientesManagement';
import MascotasManagement from '../components/recepcionista/MascotasManagement';
import SolicitudesManagement from '../components/recepcionista/SolicitudesManagement';
import CitasManagement from '../components/recepcionista/CitasManagement';
import VeterinariosView from '../components/recepcionista/VeterinariosView';
import ServiciosView from '../components/recepcionista/ServiciosView';
import Reportes from '../components/recepcionista/Reportes';
import '../styles/Dashboard.css';

const RecepcionistaDashboard = () => {
  const { user } = useAuth();
  const [activeView, setActiveView] = useState('inicio');

  // Función para obtener el nombre del usuario logueado
  const getUserDisplayName = () => {
    if (user?.name && user.name !== user?.username) {
      return user.name;
    }
    if (user?.session_info?.nombre_completo) {
      return user.session_info.nombre_completo;
    }
    return user?.username || 'RECEPCIONISTA';
  };

  const sidebarItems = [
    { id: 'inicio', label: 'Inicio', icon: '🏠' },
    { id: 'clientes', label: 'Clientes', icon: '👥' },
    { id: 'mascotas', label: 'Mascotas', icon: '🐕' },
    { id: 'solicitudes', label: 'Solicitudes', icon: '📋' },
    { id: 'citas', label: 'Citas', icon: '📅' },
    { id: 'veterinarios', label: 'Veterinarios', icon: '👨‍⚕️' },
    { id: 'servicios', label: 'Servicios', icon: '🏥' },
    { id: 'reportes', label: 'Reportes', icon: '📊' }
  ];

  const renderContent = () => {
    switch (activeView) {
      case 'clientes':
        return <ClientesManagement />;
      case 'mascotas':
        return <MascotasManagement />;
      case 'solicitudes':
        return <SolicitudesManagement />;
      case 'citas':
        return <CitasManagement />;
      case 'veterinarios':
        return <VeterinariosView />;
      case 'servicios':
        return <ServiciosView />;
      case 'reportes':
        return <Reportes />;
      default:
        return <Dashboard />;
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

export default RecepcionistaDashboard;