// layouts/DashboardLayout.jsx
// Estructura maestra de los paneles internos (admin, veterinario, recepcionista):
// barra lateral + cabecera + área de contenido. Antes estaba duplicada en los tres
// dashboards; ahora cada uno solo aporta sus items de menú, el nombre a mostrar y
// el contenido de la vista activa.
import React from 'react';
import AppBar from '../components/common/AppBar/AppBar';
import Sidebar from '../components/common/Sidebar';
import '../styles/Dashboard.css';

const DashboardLayout = ({ sidebarItems, activeView, onViewChange, userName, children }) => {
  return (
    <div className="dashboard-layout">
      <Sidebar
        items={sidebarItems}
        activeItem={activeView}
        onItemClick={onViewChange}
      />

      <div className="main-content">
        <AppBar
          title="🟢 Cuenta de:"
          subtitle={userName}
        />

        <div className="dashboard-content">
          {children}
        </div>
      </div>
    </div>
  );
};

export default DashboardLayout;
