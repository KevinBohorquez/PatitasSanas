// pages/AdminDashboard.jsx
import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import AppBar from '../components/common/AppBar';
import Sidebar from '../components/common/Sidebar';
import Dashboard from '../components/admin/Dashboard';
import UserManagement from '../components/admin/UserManagement';
import VetManagement from '../components/admin/VetManagement';
import ReceptionistManagement from '../components/admin/ReceptionistManagement';
import ServicesManagement from '../components/admin/ServicesManagement';
import '../styles/Dashboard.css';

const AdminDashboard = () => {
  const { user } = useAuth();
  const [activeView, setActiveView] = useState('inicio');

  const getUserDisplayName = () => {
    if (user?.name && user.name !== user?.username) {
      return user.name;
    }
    if (user?.session_info?.nombre_completo) {
      return user.session_info.nombre_completo;
    }
    return user?.username || 'ADMINISTRADOR';
  };

  const sidebarItems = [
    { id: 'inicio', label: 'Inicio', icon: '🏠' },
    { id: 'usuarios', label: 'Usuarios', icon: '👥' },
    { id: 'veterinarios', label: 'Veterinarios', icon: '👨‍⚕️' },
    { id: 'recepcionistas', label: 'Recepcionistas', icon: '👩‍💼' },
    { id: 'servicios', label: 'Servicios', icon: '🏥' }
  ];

  const renderContent = () => {
    switch (activeView) {
      case 'usuarios':
        return <UserManagement />;
      case 'veterinarios':
        return <VetManagement />;
      case 'recepcionistas':
        return <ReceptionistManagement />;
      case 'servicios':
        return <ServicesManagement />;
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

export default AdminDashboard;
/*
import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import AppBar from '../components/common/AppBar';
import Sidebar from '../components/common/Sidebar';
import UserManagement from '../components/admin/UserManagement';
import VetManagement from '../components/admin/VetManagement';
import ReceptionistManagement from '../components/admin/ReceptionistManagement';
import ServicesManagement from '../components/admin/ServicesManagement';
import '../styles/Dashboard.css';

const AdminDashboard = () => {
  const { user } = useAuth();
  const [activeView, setActiveView] = useState('inicio');

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
    { id: 'usuarios', label: 'Usuarios', icon: '👥' },
    { id: 'veterinarios', label: 'Veterinario', icon: '👨‍⚕️' },
    { id: 'recepcionistas', label: 'Recepcionistas', icon: '👩‍💼' },
    { id: 'servicios', label: 'Servicios', icon: '🏥' }
  ];

  const renderContent = () => {
    switch (activeView) {
      case 'usuarios':
        return <UserManagement />;
      case 'veterinarios':
        return <VetManagement />;
      case 'recepcionistas':
        return <ReceptionistManagement />;
      case 'servicios':
        return <ServicesManagement />;
      default:
        return (
          <div className="admin-inicio">
            <h2>Panel de Administración</h2>
            <div className="admin-stats">
              <div className="stat-card">
                <h3>Total Usuarios</h3>
                <p className="stat-number">15</p>
              </div>
              <div className="stat-card">
                <h3>Veterinarios</h3>
                <p className="stat-number">5</p>
              </div>
              <div className="stat-card">
                <h3>Recepcionistas</h3>
                <p className="stat-number">8</p>
              </div>
              <div className="stat-card">
                <h3>Servicios</h3>
                <p className="stat-number">12</p>
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

export default AdminDashboard; */