// pages/AdminDashboard.jsx
import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import DashboardLayout from '../layouts/DashboardLayout';
import { getUserDisplayName } from '../utils/userDisplay';
import Dashboard from '../components/admin/Dashboard';
import UserManagement from '../components/admin/UserManagement';
import VetManagement from '../components/admin/VetManagement';
import ReceptionistManagement from '../components/admin/ReceptionistManagement';
import ServicesManagement from '../components/admin/ServicesManagement';
import ReportsManagement from '../components/admin/ReportsManagement';
import AnalyticsDashboard from '../components/admin/AnalyticsDashboard';
import FlujoCaja from '../components/admin/FlujoCaja';
import BalanceFinanciero from '../components/admin/BalanceFinanciero';
import CronogramaAdmin from '../components/admin/CronogramaAdmin';

const AdminDashboard = () => {
  const { user } = useAuth();
  const [activeView, setActiveView] = useState('inicio');

  const sidebarItems = [
    { id: 'inicio', label: 'Inicio', icon: '🏠' },
    { id: 'usuarios', label: 'Usuarios', icon: '👥' },
    { id: 'veterinarios', label: 'Veterinarios', icon: '👨‍⚕️' },
    { id: 'recepcionistas', label: 'Recepcionistas', icon: '👩‍💼' },
    { id: 'cronograma', label: 'Cronograma', icon: '📅' },
    { id: 'servicios', label: 'Servicios', icon: '🏥' },
    { id: 'reportes', label: 'Reportes', icon: '📄' },
    { id: 'analytics', label: 'Analíticas', icon: '📊' },
    { id: 'flujocaja', label: 'Flujo de Caja', icon: '💰' },
    { id: 'balance', label: 'Balance Financiero', icon: '📈' }
  ];

  const renderContent = () => {
    switch (activeView) {
      case 'usuarios':
        return <UserManagement />;
      case 'veterinarios':
        return <VetManagement />;
      case 'recepcionistas':
        return <ReceptionistManagement />;
      case 'cronograma':
        return <CronogramaAdmin />;
      case 'servicios':
        return <ServicesManagement />;
      case 'reportes':
        return <ReportsManagement />;
      case 'analytics':
        return <AnalyticsDashboard />;
      case 'flujocaja':
        return <FlujoCaja />;
      case 'balance':
        return <BalanceFinanciero />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <DashboardLayout
      sidebarItems={sidebarItems}
      activeView={activeView}
      onViewChange={setActiveView}
      userName={getUserDisplayName(user, 'ADMINISTRADOR')}
    >
      {renderContent()}
    </DashboardLayout>
  );
};

export default AdminDashboard;
