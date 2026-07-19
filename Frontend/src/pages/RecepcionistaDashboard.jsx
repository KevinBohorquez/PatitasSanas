// pages/RecepcionistaDashboard.jsx
import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import DashboardLayout from '../layouts/DashboardLayout';
import { getUserDisplayName } from '../utils/userDisplay';
import Dashboard from '../components/recepcionista/Dashboard';
import ClientesManagement from '../components/recepcionista/ClientesManagement';
import MascotasManagement from '../components/recepcionista/MascotasManagement';
import SolicitudesManagement from '../components/recepcionista/SolicitudesManagement';
import CitasManagement from '../components/recepcionista/CitasManagement';
import VeterinariosView from '../components/recepcionista/VeterinariosView';
import ServiciosView from '../components/recepcionista/ServiciosView';
import Reportes from '../components/recepcionista/Reportes';
import CronogramaView from '../components/recepcionista/CronogramaView';

const RecepcionistaDashboard = () => {
  const { user } = useAuth();
  const [activeView, setActiveView] = useState('inicio');

  const sidebarItems = [
    { id: 'inicio', label: 'Inicio', icon: '🏠' },
    { id: 'clientes', label: 'Clientes', icon: '👥' },
    { id: 'mascotas', label: 'Mascotas', icon: '🐕' },
    { id: 'solicitudes', label: 'Solicitudes', icon: '📋' },
    { id: 'citas', label: 'Citas', icon: '📅' },
    { id: 'veterinarios', label: 'Veterinarios', icon: '👨‍⚕️' },
    { id: 'cronograma', label: 'Cronograma', icon: '📅' },
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
      case 'cronograma':
        return <CronogramaView />;
      case 'servicios':
        return <ServiciosView />;
      case 'reportes':
        return <Reportes />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <DashboardLayout
      sidebarItems={sidebarItems}
      activeView={activeView}
      onViewChange={setActiveView}
      userName={getUserDisplayName(user, 'RECEPCIONISTA')}
    >
      {renderContent()}
    </DashboardLayout>
  );
};

export default RecepcionistaDashboard;
