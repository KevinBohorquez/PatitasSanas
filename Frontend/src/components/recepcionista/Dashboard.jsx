import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import './Dashboard.css';

const Dashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    mascotas: 0,
    clientes: 0,
    citas: 0, 
    solicitudes: 0 
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const BASE_URL = 'https://veterinariaclinicabackend-production.up.railway.app/api/v1';

  // Obtener datos del backend
  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);

    try {
      const mascotasResponse = await fetch(`${BASE_URL}/mascotas/`, {
        method: 'GET',
        mode: 'cors',
        headers: {
          'Accept': 'application/json',
        },
      });

      const clientesResponse = await fetch(`${BASE_URL}/clientes/`, {
        method: 'GET',
        mode: 'cors',
        headers: {
          'Accept': 'application/json',
        },
      });

      const SolicitudesResponse = await fetch(`${BASE_URL}/solicitudes/`, {
        method: 'GET',
        mode: 'cors',
        headers: {
          'Accept': 'application/json',
        },
      });

      const CitasResponse = await fetch(`${BASE_URL}/consultas/cita`, {
        method: 'GET',
        mode: 'cors',
        headers: {
          'Accept': 'application/json',
        },
      });

      // Procesar respuesta de mascotas
      let mascotasCount = 0;
      if (mascotasResponse.ok) {
        const mascotasData = await mascotasResponse.json();
        // El endpoint puede devolver un array directo o un objeto con total/count
        if (Array.isArray(mascotasData)) {
          mascotasCount = mascotasData.length;
        } else if (mascotasData.total) {
          mascotasCount = mascotasData.total;
        } else if (mascotasData.mascotas) {
          mascotasCount = Array.isArray(mascotasData.mascotas) ? mascotasData.mascotas.length : 0;
        }
      } else {
        console.error('Error al cargar mascotas:', mascotasResponse.status);
      }

      // Procesar respuesta de clientes
      let clientesActivosCount = 0;
      if (clientesResponse.ok) {
        const clientesData = await clientesResponse.json();
        // Filtrar solo clientes activos
        if (Array.isArray(clientesData)) {
          clientesActivosCount = clientesData.filter(cliente => 
            cliente.estado === 'Activo' || cliente.estado === 'activo'
          ).length;
        } else if (clientesData.clientes) {
          const clientes = Array.isArray(clientesData.clientes) ? clientesData.clientes : [];
          clientesActivosCount = clientes.filter(cliente => 
            cliente.estado === 'Activo' || cliente.estado === 'activo'
          ).length;
        }
      } else {
        console.error('Error al cargar clientes:', clientesResponse.status);
      }

      let SolicitudesPendientesCount = 0;
      if (SolicitudesResponse.ok) {
        const SolicitudesData = await SolicitudesResponse.json();
        // Filtrar solo solicitudes pendientes
        if (Array.isArray(SolicitudesData)) {
          SolicitudesPendientesCount = SolicitudesData.filter(solicitud => 
            solicitud.estado === 'Pendiente' || solicitud.estado === 'pendiente'
          ).length;
        } else if (SolicitudesData.solicitudes) {
          const solicitudes = Array.isArray(SolicitudesData.solicitudes) ? SolicitudesData.solicitudes : [];
          SolicitudesPendientesCount = solicitudes.filter(solicitud => 
            solicitud.estado === 'Pendiente' || solicitud.estado === 'pendiente'
          ).length;
        }
      } else {
        console.error('Error al cargar solicitudes:', SolicitudesResponse.status);
      }

      let CitasHoyCount = 0;
      if (CitasResponse.ok) {
        const CitasData = await CitasResponse.json();

        // Obtener fecha actual en Lima (solo YYYY-MM-DD)
        const hoy = new Date().toLocaleDateString('es-PE', {
          timeZone: 'America/Lima',
          year: 'numeric',
          month: '2-digit',
          day: '2-digit'
        });
        const fechaHoyFormateada = hoy.split('/').reverse().join('-');

        // Verificamos si recibimos un array directo o una propiedad 'citas'
        const citas = Array.isArray(CitasData)
          ? CitasData
          : Array.isArray(CitasData.citas)
          ? CitasData.citas
          : [];

        // Filtramos por fecha
        CitasHoyCount = citas.filter(cita => {
          const fechaCita = cita.fecha_hora_programada.split('T')[0];
          return fechaCita === fechaHoyFormateada;
        }).length;

        console.log(`Número de citas para hoy (${fechaHoyFormateada}):`, CitasHoyCount);
      } else {
        console.error('Error al obtener las citas:', CitasResponse.status);
      }

      // Actualizar estado con los datos obtenidos
      setStats(prevStats => ({
        ...prevStats,
        mascotas: mascotasCount,
        clientes: clientesActivosCount,
        solicitudes: SolicitudesPendientesCount
      }));

    } catch (error) {
      console.error('Error al cargar datos del dashboard:', error);
      setError('Error al cargar los datos. Inténtalo de nuevo.');
    } finally {
      setLoading(false);
    }
  };

  // Obtener nombre del usuario logueado
  const getUserDisplayName = () => {
    if (user?.name && user.name !== user?.username) {
      return user.name;
    }
    if (user?.session_info?.nombre_completo) {
      return user.session_info.nombre_completo;
    }
    return user?.username || 'RECEPCIONISTA';
  };

  const dashboardData = [
    { 
      title: 'Mascotas registradas', 
      value: loading ? '...' : stats.mascotas.toString().padStart(2, '0'), 
      icon: 'https://i.ibb.co/bj9tRhYK/Mascota1-Comprimido.png',
      color: 'blue' 
    },
    { 
      title: 'Citas de hoy', 
      value: loading ? '...' : stats.citas.toString().padStart(2, '0'), 
      icon: 'https://i.ibb.co/qYHnQGk9/cita1-Comprimido.png',
      color: 'green' 
    },
    { 
      title: 'Clientes activos', 
      value: loading ? '...' : stats.clientes.toString().padStart(2, '0'), 
      icon: 'https://i.ibb.co/mVjXndWF/Cliente1-Comprimido.png',
      color: 'purple' 
    },
    { 
      title: 'Solicitudes pendientes', 
      value: loading ? '...' : stats.solicitudes.toString().padStart(2, '0'), 
      icon: 'https://i.ibb.co/qFFFykJk/Solicitud2-Comprimido.png',
      color: 'orange' 
    }
  ];

  return (
    <div className="dashboard-recepcionista">
      <div className="welcome-section">
        <div className="welcome-content">
          <div className="welcome-text">
            <h2 className="welcome-title">BIENVENIDO/A 🤓 </h2>
            <h3 className="user-name">{getUserDisplayName()}</h3>
            <p className="role-description">Recepcionista - Colitas Felices - Veterinaria 🧑🏻‍💻</p>
          </div>
          <div className="welcome-image">
            <img 
              src="https://i.ibb.co/S7tyCF7B/Recepcionista1-Comprimido.png" 
              alt="Mascota" 
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