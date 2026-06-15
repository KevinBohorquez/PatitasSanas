// pages/RoleSelection.jsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/RoleSelection.css';

const RoleSelection = () => {
  const navigate = useNavigate();

  const handleRoleSelect = (role) => {
    navigate(`/login/${role}`);
  };

  return (
    <div className="role-selection-container">
      <div className="role-selection-card">
        <div className="role-header">
          <h1>PATITAS SANAS</h1>
          <h2>Sistema veterinario</h2>
          <img 
            src="https://i.ibb.co/rG8YQzjQ/Logo-Veterinaria-Sin-Letras-Recorte.png" 
            alt="Logo o decoración"
            className="role-header-img"
          />
        </div>
        
        <div className="role-content">
          <h3 className="textoEscritura">📌Seleccione cómo desea ingresar:</h3>
          
          <div className="role-buttons">
            <button 
              className="role-btn recepcionista"
              onClick={() => handleRoleSelect('recepcionista')}
            >
              RECEPCIONISTA
            </button>
            
            <button 
              className="role-btn veterinario"
              onClick={() => handleRoleSelect('veterinario')}
            >
              VETERINARIO
            </button>
            
            <button 
              className="role-btn administrador"
              onClick={() => handleRoleSelect('administrador')}
            >
              ADMINISTRADOR
            </button>
          </div>
        </div>
        
        <div className="role-info">
          <p>Tras elegir una opción de ingreso, será redirigido al login</p>
        </div>
      </div>
    </div>
  );
};

export default RoleSelection;