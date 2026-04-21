// components/common/AppBar.jsx
import React from 'react';
import { useAuth } from '../../context/AuthContext';
import '../../styles/AppBar.css';

const AppBar = ({ title, subtitle }) => {
  const { logout } = useAuth();

  const handleLogout = () => {
    if (window.confirm('¿Está seguro de cerrar sesión?')) {
      logout();
    }
  };

  return (
    <header className="app-bar">
      <div className="app-bar-content">
        <div className="app-bar-titles">
          <h1>{title}</h1>
          {subtitle && <h2>{subtitle}</h2>}
        </div>
        <div className="app-bar-actions">
          <button onClick={handleLogout} className="cerrar-sesion-btn">
            cerrar sesión
          </button>
        </div>
      </div>
    </header>
  );
};

export default AppBar;