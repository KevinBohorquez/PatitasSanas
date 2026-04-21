// src/components/admin/Dashboard.jsx
import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import './Dashboard.css';

const Dashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    totalUsuarios: 0,
    veterinarios: 0,
    recepcionistas: 0,
    administradores: 0,
    servicios: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // URL base de la API
  const API_BASE_URL = 'https://veterinariaclinicabackend-production.up.railway.app/api/v1';

  // Fetch de datos del dashboard
  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // 1. Obtener TODOS los usuarios por tipo y filtrar manualmente por estado activo
      const [
        adminResponse,
        vetResponse, 
        recepResponse,
        serviciosResponse
      ] = await Promise.all([
        // Administradores
        fetch(`${API_BASE_URL}/usuarios/tipo/Administrador?activos_solo=false`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
        }),
        // Veterinarios  
        fetch(`${API_BASE_URL}/usuarios/tipo/Veterinario?activos_solo=false`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
        }),
        // Recepcionistas
        fetch(`${API_BASE_URL}/usuarios/tipo/Recepcionista?activos_solo=false`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
        }),
        // Servicios (obtener todos, no confiar en el filtrado del backend)
        fetch(`${API_BASE_URL}/catalogos/servicios/?activos_solo=false`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
        })
      ]);

      // Verificar respuestas y obtener datos
      const adminData = adminResponse.ok ? await adminResponse.json() : { usuarios: [] };
      const vetData = vetResponse.ok ? await vetResponse.json() : { usuarios: [] };
      const recepData = recepResponse.ok ? await recepResponse.json() : { usuarios: [] };
      const serviciosData = serviciosResponse.ok ? await serviciosResponse.json() : [];

      console.log('📊 Datos obtenidos (todos):');
      console.log('👑 Administradores (todos):', adminData);
      console.log('👨‍⚕️ Veterinarios (todos):', vetData);
      console.log('👩‍💼 Recepcionistas (todos):', recepData);
      console.log('🏥 Servicios (todos):', serviciosData);

      // 2. FILTRAR MANUALMENTE por estado = "Activo" (usuarios) y activo = true (servicios)
      const administradoresActivos = adminData.usuarios ? 
        adminData.usuarios.filter(user => user.estado === 'Activo') : [];
      
      const veterinariosActivos = vetData.usuarios ? 
        vetData.usuarios.filter(user => user.estado === 'Activo') : [];
      
      const recepcionistasActivos = recepData.usuarios ? 
        recepData.usuarios.filter(user => user.estado === 'Activo') : [];

      // FILTRAR SERVICIOS MANUALMENTE por activo = true
      const serviciosActivos = Array.isArray(serviciosData) ? 
        serviciosData.filter(servicio => servicio.activo === true) : [];

      console.log('✅ FILTRADOS POR ESTADO ACTIVO:');
      console.log('👑 Administradores activos:', administradoresActivos.length, administradoresActivos);
      console.log('👨‍⚕️ Veterinarios activos:', veterinariosActivos.length, veterinariosActivos);
      console.log('👩‍💼 Recepcionistas activos:', recepcionistasActivos.length, recepcionistasActivos);
      console.log('🏥 Servicios activos (activo=true):', serviciosActivos.length, serviciosActivos);

      // Mostrar usuarios inactivos para debugging
      const administradoresInactivos = adminData.usuarios ? 
        adminData.usuarios.filter(user => user.estado !== 'Activo') : [];
      const veterinariosInactivos = vetData.usuarios ? 
        vetData.usuarios.filter(user => user.estado !== 'Activo') : [];
      const recepcionistasInactivos = recepData.usuarios ? 
        recepData.usuarios.filter(user => user.estado !== 'Activo') : [];
      
      // Mostrar servicios inactivos para debugging
      const serviciosInactivos = Array.isArray(serviciosData) ? 
        serviciosData.filter(servicio => servicio.activo === false || servicio.activo === null) : [];

      if (administradoresInactivos.length > 0) {
        console.log('❌ Administradores INACTIVOS (NO CONTADOS):', administradoresInactivos.length, administradoresInactivos);
      }
      if (veterinariosInactivos.length > 0) {
        console.log('❌ Veterinarios INACTIVOS (NO CONTADOS):', veterinariosInactivos.length, veterinariosInactivos);
      }
      if (recepcionistasInactivos.length > 0) {
        console.log('❌ Recepcionistas INACTIVOS (NO CONTADOS):', recepcionistasInactivos.length, recepcionistasInactivos);
      }
      if (serviciosInactivos.length > 0) {
        console.log('❌ Servicios INACTIVOS (NO CONTADOS):', serviciosInactivos.length, serviciosInactivos);
      }

      // 3. Calcular totales de solo usuarios activos y servicios activos
      const administradores = administradoresActivos.length;
      const veterinarios = veterinariosActivos.length;
      const recepcionistas = recepcionistasActivos.length;
      const totalUsuarios = administradores + veterinarios + recepcionistas;
      const servicios = serviciosActivos.length; // Solo servicios con activo = true

      // 4. Actualizar estados con conteos de solo usuarios activos
      setStats({
        totalUsuarios,
        veterinarios,
        recepcionistas,
        administradores,
        servicios
      });

      console.log('🎯 STATS FINALES (SOLO USUARIOS CON ESTADO = "Activo" Y SERVICIOS CON ACTIVO = true):');
      console.log('Total usuarios activos:', totalUsuarios);
      console.log('Veterinarios activos:', veterinarios);
      console.log('Recepcionistas activos:', recepcionistas);
      console.log('Administradores activos:', administradores);
      console.log('Servicios activos:', servicios);

    } catch (error) {
      console.error('❌ Error fetching dashboard data:', error);
      setError('Error al cargar datos del dashboard. Inténtalo de nuevo.');
    } finally {
      setLoading(false);
    }
  };

  // Cargar datos al montar el componente
  useEffect(() => {
    fetchDashboardData();
  }, []);

  // Obtener nombre del usuario logueado
  const getUserDisplayName = () => {
    if (user?.name && user.name !== user?.username) {
      return user.name;
    }
    if (user?.session_info?.nombre_completo) {
      return user.session_info.nombre_completo;
    }
    return user?.username || 'ADMINISTRADOR';
  };

  const dashboardData = [
    { 
      title: 'Usuarios Activos', 
      value: loading ? '...' : stats.totalUsuarios.toString().padStart(2, '0'), 
      icon: 'https://i.ibb.co/mVjXndWF/Cliente1-Comprimido.png',
      color: 'blue' 
    },
    { 
      title: 'Veterinarios Activos', 
      value: loading ? '...' : stats.veterinarios.toString().padStart(2, '0'), 
      icon: 'https://i.ibb.co/qYHnQGk9/cita1-Comprimido.png',
      color: 'green' 
    },
    { 
      title: 'Recepcionistas Activos', 
      value: loading ? '...' : stats.recepcionistas.toString().padStart(2, '0'), 
      icon: 'https://i.ibb.co/S7tyCF7B/Recepcionista1-Comprimido.png',
      color: 'purple' 
    },
    { 
      title: 'Administradores Activos', 
      value: loading ? '...' : stats.administradores.toString().padStart(2, '0'), 
      icon: 'https://i.ibb.co/qFFFykJk/Solicitud2-Comprimido.png',
      color: 'orange' 
    },
    { 
      title: 'Servicios Disponibles', 
      value: loading ? '...' : stats.servicios.toString().padStart(2, '0'), 
      icon: 'https://i.ibb.co/bj9tRhYK/Mascota1-Comprimido.png',
      color: 'cyan' 
    }
  ];

  return (
    <div className="dashboard-recepcionista">
      <div className="welcome-section">
        <div className="welcome-content">
          <div className="welcome-text">
            <h2 className="welcome-title">BIENVENIDO/A 👑</h2>
            <h3 className="user-name">{getUserDisplayName()}</h3>
            <p className="role-description">Administrador - Colitas Felices - Veterinaria 🛡️</p>
          </div>
          <div className="welcome-image">
            <img 
              src="https://i.ibb.co/qFFFykJk/Solicitud2-Comprimido.png" 
              alt="Administrador" 
              className="pet-icon"
            />
          </div>
        </div>
      </div>

      {error && (
        <div className="error-message">
          <p>{error}</p>
          <button onClick={fetchDashboardData} className="retry-button">
            Reintentar
          </button>
        </div>
      )}

      <div className="stats-grid">
        {dashboardData.map((stat, index) => (
          <div key={index} className={`stat-card stat-${stat.color}`}>
            <div className="stat-content two-columns">
              <div className="left-column">
                <h3 className="stat-title">{stat.title}</h3>
                <div className="stat-value">{stat.value}</div>
              </div>
              <div className="right-column">
                <div className="stat-icon-container">
                  <img 
                    src={stat.icon} 
                    alt={stat.title}
                    className="stat-icon"
                    onError={(e) => {
                      e.target.style.display = 'none';
                    }}
                  />
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="dashboard-footer">
        <p>Última actualización: {new Date().toLocaleString('es-PE', {
          timeZone: 'America/Lima',
          day: '2-digit',
          month: '2-digit',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        })}</p>
      </div>
    </div>
  );
};

export default Dashboard;