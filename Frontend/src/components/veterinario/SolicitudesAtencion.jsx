// components/veterinario/SolicitudesAtencion.jsx
import React, { useState, useEffect } from 'react';
import { apiFetch } from '../../api/client';
import Table from '../common/Table';
import Modal from '../ui/Modal/Modal';
import Loader from '../ui/Loader/Loader';
import FichaTriaje from './FichaTriaje';
import FichaConsulta from './FichaConsulta';
import { useAuth } from '../../context/AuthContext';
import './SolicitudesAtencion.css';
import { toast } from '../../utils/toast';
import { formatApiError } from '../../utils/apiError';

const SolicitudesAtencion = () => {
  const { user } = useAuth(); // Obtener usuario del contexto
  const [solicitudes, setSolicitudes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedSolicitud, setSelectedSolicitud] = useState(null);
  const [showTriaje, setShowTriaje] = useState(false);
  const [showConsulta, setShowConsulta] = useState(false);
  const [filtroUrgencia, setFiltroUrgencia] = useState('todas');
  const [filtroEstado, setFiltroEstado] = useState('todos');
  const [procesandoAtencion, setProcesandoAtencion] = useState(false);

  // Función para actualizar la disposición del veterinario
  const updateVeterinarioDisposicion = async (idUsuario) => {
    try {
      
      const response = await apiFetch(
        `/veterinarios/veterinario/usuario/${idUsuario}/disposicion`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(formatApiError(errorData, 'No se pudo actualizar la disposición del veterinario'));
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('❌ Error al actualizar disposición:', error);
      throw error;
    }
  };

  // Función para obtener datos de mascota por ID
  const fetchMascota = async (mascotaId) => {
    try {
      // SC-060 / F43: se usa /details (no /{id}) porque el endpoint simple NO
      // devuelve el cliente. Sin él, más abajo caíamos a un fallback erróneo que
      // usaba el id de la mascota como si fuera id de cliente (dueño equivocado).
      const response = await apiFetch(`/mascotas/${mascotaId}/details`);
      if (!response.ok) return null;
      return await response.json();
    } catch (error) {
      console.error(`Error al obtener mascota ${mascotaId}:`, error);
      return null;
    }
  };

  // Función para obtener datos de cliente por ID
  const fetchCliente = async (clienteId) => {
    try {
      const response = await apiFetch(`/clientes/${clienteId}`);
      if (!response.ok) return null;
      return await response.json();
    } catch (error) {
      console.error(`Error al obtener cliente ${clienteId}:`, error);
      return null;
    }
  };

  // Función para obtener datos de la API
  const fetchSolicitudes = async () => {
      try {
        if (!user || !user.id) {
          throw new Error('Usuario no autenticado. Por favor inicie sesión.');
        }

        setLoading(true);

        const response = await apiFetch(
          `/solicitudes/veterinario/${user.id}`
        );

        if (!response.ok) {
          throw new Error('Error al obtener las solicitudes');
        }

        const data = await response.json();

        // Obtener datos de mascotas y clientes para cada solicitud
        const solicitudesConDatos = await Promise.all(
          data.map(async (solicitud) => {
            const mascota = await fetchMascota(solicitud.id_mascota);
            // SC-060 / F43: el id del dueño viene anidado en mascota.cliente.id_cliente.
            // Ya NO se usa solicitud.id_mascota como fallback (era un id de mascota, no
            // de cliente, y mostraba un dueño ajeno).
            const idCliente = mascota?.cliente?.id_cliente;
            const cliente = idCliente ? await fetchCliente(idCliente) : null;

            return {
              id: solicitud.id_solicitud,
              mascota: mascota ? mascota.nombre : `Mascota ${solicitud.id_mascota}`,
              cliente: cliente ? `${cliente.nombre} ${cliente.apellido_paterno} ${cliente.apellido_materno}` : `Cliente ${solicitud.id_mascota}`,
              fecha: formatearFecha(solicitud.fecha_hora_solicitud),
              hora: formatearHora(solicitud.fecha_hora_solicitud),
              estado: mapearEstado(solicitud.estado),
              urgencia: mapearUrgencia(solicitud.tipo_solicitud),
              _original: solicitud,
              _mascota: mascota,
              _cliente: cliente
            };
          })
        );

        setSolicitudes(solicitudesConDatos);
      } catch (error) {
        setError(error.message);
        console.error('Error al cargar solicitudes:', error);
      } finally {
        setLoading(false);
      }
    };


  // Función para formatear la fecha
  const formatearFecha = (fechaISO) => {
    const fecha = new Date(fechaISO);
    return fecha.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  // Función para formatear la hora
  const formatearHora = (fechaISO) => {
    const fecha = new Date(fechaISO);
    return fecha.toLocaleTimeString('es-ES', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Función para mapear el estado de la API al formato del componente
  const mapearEstado = (estadoAPI) => {
    const mapeoEstados = {
      'Pendiente': 'Pendiente',
      'En triaje': 'En triaje',
      'En atencion': 'En atencion',
      'Completada': 'Completada',
      'Cancelada': 'Cancelada'
    };
    return mapeoEstados[estadoAPI] || estadoAPI;
  };

  // Función para mapear el tipo de solicitud a urgencia
  const mapearUrgencia = (tipoSolicitud) => {
    const mapeoUrgencia = {
      'Consulta urgente': 'Alta',
      'Consulta normal': 'Media',
      'Servicio programado': 'Baja'
    };
    return mapeoUrgencia[tipoSolicitud] || 'Media';
  };

  // Cargar datos al montar el componente
  useEffect(() => {
    fetchSolicitudes();
    
    // Mostrar información del usuario en consola para debug
    if (user) {
    }
  }, [user]);

  // Función para refrescar los datos
  const handleRefresh = () => {
    fetchSolicitudes();
  };

  // Función modificada para manejar la atención
  const handleAtender = async (solicitud) => {

  // Extraer el id_consulta si existe
  if (solicitud._original && solicitud._original.id_consulta) {
  } else {
  }

  if (!user || !user.id) {
    console.error('❌ No se pudo obtener la información del usuario');
    toast.error('Error: No se pudo obtener la información del usuario. Por favor, inicie sesión nuevamente.');
    return;
  }

  try {
    setProcesandoAtencion(true);

    // Primero actualizar la disposición del veterinario a "Ocupado"
    await updateVeterinarioDisposicion(user.id);

    // Si todo sale bien, proceder con el triaje
    setSelectedSolicitud(solicitud);
    setShowTriaje(true);

  } catch (error) {
    console.error('❌ Error en handleAtender:', error);
    toast.error(`Error al iniciar la atención: ${error.message}`);
  } finally {
    setProcesandoAtencion(false);
  }
};

  const handleTriajeComplete = () => {
    setShowTriaje(false);
    setShowConsulta(true);
  };

  const handleConsultaComplete = async (consultaId) => {
    setShowConsulta(false);
    setSelectedSolicitud(null);

    // SC-056 / F41: al terminar la consulta se FINALIZA la atención en el backend:
    // la solicitud pasa a "Completada" y el trigger libera al veterinario ("Libre").
    // Antes solo se marcaba "Atendida" en el estado local (sin persistir), por lo que
    // recepción no veía el cambio y se perdía al recargar.
    try {
      if (consultaId) {
        const resp = await apiFetch(`/consultas/${consultaId}/finalizar`, {
          method: 'PATCH'
        });
        if (resp.ok) {
          toast.success('Atención finalizada.');
        } else {
          const errBody = await resp.json().catch(() => null);
          toast.error(formatApiError(errBody, 'No se pudo finalizar la atención'));
        }
      }
    } catch (error) {
      console.error('Error al finalizar la atención:', error);
      toast.error('No se pudo finalizar la atención');
    }

    // Recargar los estados reales desde el backend (evita estados optimistas incorrectos).
    fetchSolicitudes();
  };

  const solicitudesFiltradas = solicitudes.filter((s) => {
    const okUrgencia = filtroUrgencia === 'todas' || s.urgencia.toLowerCase() === filtroUrgencia;
    const okEstado =
      filtroEstado === 'todos' ||
      (filtroEstado === 'completadas' && s.estado === 'Completada') ||
      (filtroEstado === 'pendientes' && s.estado !== 'Completada' && s.estado !== 'Cancelada');
    return okUrgencia && okEstado;
  });

  const columns = [
    { key: 'mascota', header: 'MASCOTA' },
    { key: 'cliente', header: 'CLIENTE' },
    { key: 'fecha', header: 'FECHA' },
    { key: 'hora', header: 'HORA' },
    {
      key: 'estado',
      header: 'ESTADO',
      render: (row) => (
        <span className={`status-badge status-${row.estado.toLowerCase().replace(' ', '-')}`}>
          {row.estado}
        </span>
      )
    }
  ];

  const actions = [
    {
      label: procesandoAtencion ? 'Procesando...' : 'Atender',
      type: 'primary',
      onClick: handleAtender,
      disabled: procesandoAtencion
    }
  ];

  // Mostrar loading
  if (loading) {
    return (
      <div className="solicitudes-atencion">
        <div className="section-header">
          <h2>Solicitudes de Atención</h2>
        </div>
        <Loader message="Cargando solicitudes" />
      </div>
    );
  }

  // Mostrar error
  if (error) {
    return (
      <div className="solicitudes-atencion">
        <div className="section-header">
          <h2>Solicitudes de Atención</h2>
        </div>
        <div className="error-message">
          <p>Error: {error}</p>
          <button onClick={handleRefresh} className="btn btn-secondary">
            Intentar de nuevo
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="solicitudes-atencion">
      <div className="section-header">
        <h2>Solicitudes de Atención</h2>
        <div className="header-actions">
          <button onClick={handleRefresh} className="btn btn-secondary">
            Actualizar
          </button>
          <div className="filters">
            <label>Filtrar por urgencia:</label>
            <select
              value={filtroUrgencia}
              onChange={(e) => setFiltroUrgencia(e.target.value)}
            >
              <option value="todas">Todas</option>
              <option value="alta">Alta</option>
              <option value="media">Media</option>
              <option value="baja">Baja</option>
            </select>
            <label>Estado:</label>
            <select value={filtroEstado} onChange={(e) => setFiltroEstado(e.target.value)}>
              <option value="todos">Ver todo</option>
              <option value="completadas">Completadas</option>
              <option value="pendientes">Por completar</option>
            </select>
          </div>
        </div>
      </div>

      <Table
        columns={columns}
        data={solicitudesFiltradas}
        actions={actions}
        emptyMessage="No hay solicitudes pendientes"
      />

      {/* Modal Ficha de Triaje */}
      <Modal
        isOpen={showTriaje}
        onClose={() => setShowTriaje(false)}
        title="Ficha Triaje"
        size="large"
      >
        <FichaTriaje
          solicitud={selectedSolicitud}
          onComplete={handleTriajeComplete}
          onCancel={() => setShowTriaje(false)}
        />
      </Modal>

      {/* Modal Ficha de Consulta */}
      <Modal
        isOpen={showConsulta}
        onClose={() => setShowConsulta(false)}
        title="Ficha Consulta"
        size="large"
      >
        <FichaConsulta
          solicitud={selectedSolicitud}
          onComplete={handleConsultaComplete}
          onCancel={() => setShowConsulta(false)}
        />
      </Modal>
    </div>
  );
};

export default SolicitudesAtencion;