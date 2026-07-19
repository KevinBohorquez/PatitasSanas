// components/common/ProtectedRoute.jsx
import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import Loader from '../ui/Loader/Loader';

const ProtectedRoute = ({ children, allowedRoles = [] }) => {
  const { isAuthenticated, user, loading } = useAuth();

  if (loading) {
    return (
      <div className="loading-container">
        <Loader message="Cargando" />
      </div>
    );
  }

  // Redirigir a login si no está autenticado
  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  // Verificar si el usuario está activo
  if (user.active === false) {
    return (
      <div className="access-denied-container">
        <div className="access-denied-card">
          <h2>⚠️ Cuenta Inactiva</h2>
          <p>Su cuenta ha sido desactivada. Contacte al administrador.</p>
          <button onClick={() => window.location.href = '/'}>
            Volver al inicio
          </button>
        </div>
      </div>
    );
  }

  // Normalizar roles para comparación 
  const userRole = user?.role?.toLowerCase();
  const normalizedAllowedRoles = allowedRoles.map(role => role.toLowerCase());

  // Verificar si el rol del usuario está permitido
  if (allowedRoles.length > 0 && !normalizedAllowedRoles.includes(userRole)) {
    // Redirigir al dashboard correspondiente 
    const dashboardRoutes = {
      administrador: '/admin',
      veterinario: '/veterinario',
      recepcionista: '/recepcionista'
    };
    
    const userDashboard = dashboardRoutes[userRole];
    if (userDashboard) {
      return <Navigate to={userDashboard} replace />;
    }
    
    // Si no tiene un dashboard definido, mostrar acceso denegado
    return (
      <div className="access-denied-container">
        <div className="access-denied-card">
          <h2>🚫 Acceso Denegado</h2>
          <p>No tiene permisos para acceder a esta sección.</p>
          <p>Su rol actual: <strong>{user.role}</strong></p>
          <button onClick={() => window.location.href = userDashboard || '/'}>
            Ir a mi dashboard
          </button>
        </div>
      </div>
    );
  }

  return children;
};

export default ProtectedRoute;
/*
import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import Loader from '../ui/Loader/Loader';

const ProtectedRoute = ({ children, allowedRoles = [] }) => {
  const { isAuthenticated, user, loading } = useAuth();

  // Mostrar loading mientras se verifica la autenticación
  if (loading) {
    return (
      <div className="loading-container">
        <Loader message="Cargando" />
      </div>
    );
  }

  // Redirigir a login si no está autenticado
  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  // Verificar si el rol del usuario está permitido
  if (allowedRoles.length > 0 && !allowedRoles.includes(user?.role)) {
    // Redirigir al dashboard correspondiente según el rol
    const dashboardRoutes = {
      admin: '/admin',
      veterinario: '/veterinario',
      recepcionista: '/recepcionista'
    };
    
    const userDashboard = dashboardRoutes[user?.role];
    if (userDashboard) {
      return <Navigate to={userDashboard} replace />;
    }
    
    // Si no tiene un dashboard definido, redirigir a login
    return <Navigate to="/" replace />;
  }

  // Si todo está bien, renderizar el componente hijo
  return children;
};

export default ProtectedRoute; */