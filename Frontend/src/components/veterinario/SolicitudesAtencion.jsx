// components/veterinario/SolicitudesAtencion.jsx
import React, { useState, useEffect } from 'react';
import Table from '../common/Table';
import Modal from '../common/Modal';
import FichaTriaje from './FichaTriaje';
import FichaConsulta from './FichaConsulta';
import { useAuth } from '../../context/AuthContext';
import './SolicitudesAtencion.css';

const SolicitudesAtencion = () => {
  const { user } = useAuth(); // Obtener usuario del contexto
  const [solicitudes, setSolicitudes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedSolicitud, setSelectedSolicitud] = useState(null);
  const [showTriaje, setShowTriaje] = useState(false);
  const [showConsulta, setShowConsulta] = useState(false);
  const [filtroUrgencia, setFiltroUrgencia] = useState('todas');
  const [procesandoAtencion, setProcesandoAtencion] = useState(false);

  // Función para actualizar la disposición del veterinario
  const updateVeterinarioDisposicion = async (idUsuario) => {
    try {
      console.log('🔄 Actualizando disposición para usuario ID:', idUsuario);
      
      const response = await fetch(
        `/api/v1/veterinarios/veterinario/usuario/${idUsuario}/disposicion`,
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
        throw new Error(errorData.detail || `Error ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('✅ Disposición actualizada exitosamente:', data);
      console.log(`📍 Veterinario ${data.nombre} ${data.apellido_paterno} ahora está: ${data.disposicion}`);
      return data;
    } catch (error) {
      console.error('❌ Error al actualizar disposición:', error);
      throw error;
    }
  };

  // Función para obtener datos de mascota por ID
  const fetchMascota = async (mascotaId) => {
    try {
      const response = await fetch(`/api/v1/mascotas/${mascotaId}`);
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
      const response = await fetch(`/api/v1/clientes/${clienteId}`);
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

        const response = await fetch(
          `/api/v1/solicitudes/veterinario/${user.id}`
        );

        if (!response.ok) {
          throw new Error('Error al obtener las solicitudes');
        }

        const data = await response.json();

        // Obtener datos de mascotas y clientes para cada solicitud
        const solicitudesConDatos = await Promise.all(
          data.map(async (solicitud) => {
            const mascota = await fetchMascota(solicitud.id_mascota);
            const cliente = mascota ? await fetchCliente(mascota.id_cliente || solicitud.id_mascota) : null;

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
      console.log('👤 Usuario logueado:', user);
      console.log('🆔 ID de usuario para endpoint:', user.id);
    }
  }, [user]);

  // Función para refrescar los datos
  const handleRefresh = () => {
    fetchSolicitudes();
  };

  // Función modificada para manejar la atención
  const handleAtender = async (solicitud) => {
  console.log('🎯 Iniciando proceso de atención para solicitud:', solicitud.id);

  // Extraer el id_consulta si existe
  if (solicitud._original && solicitud._original.id_consulta) {
    console.log('📝 Esta solicitud tiene consulta_id:', solicitud._original.id_consulta);
  } else {
    console.log('📝 Esta solicitud NO tiene un consulta_id asociado.');
  }

  if (!user || !user.id) {
    console.error('❌ No se pudo obtener la información del usuario');
    alert('Error: No se pudo obtener la información del usuario. Por favor, inicie sesión nuevamente.');
    return;
  }

  try {
    setProcesandoAtencion(true);
    console.log('⏳ Procesando atención...');

    // Primero actualizar la disposición del veterinario a "Ocupado"
    await updateVeterinarioDisposicion(user.id);

    // Si todo sale bien, proceder con el triaje
    console.log('✅ Abriendo modal de triaje...');
    setSelectedSolicitud(solicitud);
    setShowTriaje(true);

  } catch (error) {
    console.error('❌ Error en handleAtender:', error);
    alert(`Error al iniciar la atención: ${error.message}`);
  } finally {
    setProcesandoAtencion(false);
  }
};

  const handleTriajeComplete = () => {
    setShowTriaje(false);
    setShowConsulta(true);
  };

  const handleConsultaComplete = () => {
    setShowConsulta(false);
    setSelectedSolicitud(null);
    // Actualizar estado de la solicitud
    setSolicitudes(prev =>
      prev.map(s =>
        s.id === selectedSolicitud.id
          ? { ...s, estado: 'Atendida' }
          : s
      )
    );
    // Opcionalmente, actualizar en la API también
    // updateSolicitudEstado(selectedSolicitud.id, 'En atencion');
  };

  const solicitudesFiltradas = solicitudes.filter(s =>
    filtroUrgencia === 'todas' || s.urgencia.toLowerCase() === filtroUrgencia
  );

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
        <div className="loading-message">
          <p>Cargando solicitudes...</p>
        </div>
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