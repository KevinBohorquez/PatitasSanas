import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import Table from '../common/Table';
import Modal from '../common/Modal';
import './SolicitudesManagement.css';

const SolicitudesManagement = () => {
  const { user } = useAuth();
  const [solicitudes, setSolicitudes] = useState([]);
  const [filteredSolicitudes, setFilteredSolicitudes] = useState([]);
  const [mascotas, setMascotas] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [recepcionistaInfo, setRecepcionistaInfo] = useState(null);
  
  const getRecepcionistaInfo = async () => {
    if (!user) return null;

    // console.log('Usuario logueado completo:', JSON.stringify(user, null, 2));

    // OPCIÓN 1: Si ya tenemos id_recepcionista
    if (user.id_recepcionista) {
      return { id_recepcionista: user.id_recepcionista };
    }

    if (user.session_info?.id_recepcionista) {
      return { id_recepcionista: user.session_info.id_recepcionista };
    }

    if (user.id) {
      try {
        // console.log('Buscando recepcionista por id_usuario:', user.id);
        
        const response = await fetch(`${BASE_URL}/recepcionistas/`, {
          method: 'GET',
          mode: 'cors',
          headers: {
            'Accept': 'application/json',
          },
        });

        if (response.ok) {
          const data = await response.json();
          const recepcionistas = data.recepcionistas || data;
          
          const recepcionistaEncontrada = recepcionistas.find(recep => 
            recep.id_usuario === user.id
          );

          if (recepcionistaEncontrada) {
            // console.log('Recepcionista encontrada:', recepcionistaEncontrada);
            return {
              id_recepcionista: recepcionistaEncontrada.id_recepcionista,
              nombre_completo: `${recepcionistaEncontrada.nombre} ${recepcionistaEncontrada.apellido_paterno}`
            };
          }
        }
      } catch (error) {
        console.error('Error buscando recepcionista:', error);
      }
    }

    if (user.username) {
      try {
        // console.log('Buscando recepcionista por username:', user.username);
        
        // Primero buscar el usuario por username para obtener su id_usuario
        const userResponse = await fetch(`${BASE_URL}/usuarios/`, {
          method: 'GET',
          mode: 'cors',
          headers: {
            'Accept': 'application/json',
          },
        });

        if (userResponse.ok) {
          const userData = await userResponse.json();
          const usuarios = userData.usuarios || userData;
          
          const usuarioEncontrado = usuarios.find(u => 
            u.username === user.username && u.tipo_usuario?.toLowerCase() === 'recepcionista'
          );

          if (usuarioEncontrado) {
            // console.log('Usuario encontrado:', usuarioEncontrado);
            
            const recepResponse = await fetch(`${BASE_URL}/recepcionistas/`, {
              method: 'GET',
              mode: 'cors',
              headers: {
                'Accept': 'application/json',
              },
            });

            if (recepResponse.ok) {
              const recepData = await recepResponse.json();
              const recepcionistas = recepData.recepcionistas || recepData;
              
              const recepcionistaEncontrada = recepcionistas.find(recep => 
                recep.id_usuario === usuarioEncontrado.id_usuario
              );

              if (recepcionistaEncontrada) {
                // console.log('Recepcionista encontrada por username:', recepcionistaEncontrada);
                return {
                  id_recepcionista: recepcionistaEncontrada.id_recepcionista,
                  nombre_completo: `${recepcionistaEncontrada.nombre} ${recepcionistaEncontrada.apellido_paterno}`
                };
              }
            }
          }
        }
      } catch (error) {
        console.error('Error buscando por username:', error);
      }
    }

    return null;
  };

  // Estados para filtros
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('todos');
  
  const [formData, setFormData] = useState({
    id_mascota: '',
    tipo_solicitud: '',
    dueño: ''
  });

  const BASE_URL = 'https://veterinariaclinicabackend-production.up.railway.app/api/v1';

  // Cargar datos al montar el componente
  useEffect(() => {
    fetchSolicitudes();
    fetchMascotas();
    loadRecepcionistaInfo();
  }, []);

  // Función para cargar información
  const loadRecepcionistaInfo = async () => {
    const info = await getRecepcionistaInfo();
    setRecepcionistaInfo(info);
    // console.log('Información del recepcionista cargada:', info);
  };

  // Aplicar filtros cuando cambien las solicitudes
  useEffect(() => {
    applyFilters();
  }, [solicitudes, searchTerm, statusFilter]);

  // Función para aplicar filtros
  const applyFilters = () => {
    let filtered = [...solicitudes];

    // Filtro por nombre de mascota o dueño
    if (searchTerm.trim()) {
      const term = searchTerm.toLowerCase().trim();
      filtered = filtered.filter(solicitud => {
        const nombreMascota = solicitud.nombre_mascota?.toLowerCase() || '';
        const nombreDueño = solicitud.nombre_dueño?.toLowerCase() || '';
        
        return nombreMascota.includes(term) || nombreDueño.includes(term);
      });
    }

    // Filtro por estado
    if (statusFilter !== 'todos') {
      filtered = filtered.filter(solicitud => solicitud.estado === statusFilter);
    }

    setFilteredSolicitudes(filtered);
  };

  // Función para obtener todas las solicitudes
  const fetchSolicitudes = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${BASE_URL}/solicitudes/`, {
        method: 'GET',
        mode: 'cors',
        headers: {
          'Accept': 'application/json',
        },
      });
      if (response.ok) {
        const data = await response.json();
        // console.log('Datos de solicitudes recibidos:', data); // Debug
        
        // Procesar los datos para incluir nombres de mascota y dueño
        const solicitudesConNombres = await Promise.all(
          (data.solicitudes || data).map(async (solicitud) => {
            // console.log('Procesando solicitud:', solicitud); // Debug
            
            try {
              const mascotaResponse = await fetch(`${BASE_URL}/mascotas/${solicitud.id_mascota}`, {
                method: 'GET',
                mode: 'cors',
                headers: { 'Accept': 'application/json' },
              });
              
              let nombreMascota = 'Desconocida';
              let nombreDueño = 'Desconocido';
              
              if (mascotaResponse.ok) {
                const mascotaData = await mascotaResponse.json();
                // console.log('Datos de mascota:', mascotaData); // Debug
                
                nombreMascota = mascotaData.nombre || 'Desconocida';
                
                // Obtener información del cliente usando el endpoint correcto
                const clienteResponse = await fetch(`${BASE_URL}/catalogos/cliente-mascota/mascota/${solicitud.id_mascota}`, {
                  method: 'GET',
                  mode: 'cors',
                  headers: { 'Accept': 'application/json' },
                });
                
                if (clienteResponse.ok) {
                  const clienteData = await clienteResponse.json();
                  // console.log('Datos de cliente-mascota:', JSON.stringify(clienteData, null, 2)); // Debug expandido
                  
                  // La estructura correcta es: clienteData.clientes[0].nombre_completo
                  if (clienteData.clientes && clienteData.clientes.length > 0) {
                    nombreDueño = clienteData.clientes[0].nombre_completo;
                  }
                } else {
                  // console.log('Error al obtener cliente, status:', clienteResponse.status);
                }
              }
              
              return {
                ...solicitud,
                nombre_mascota: nombreMascota,
                nombre_dueño: nombreDueño,
                fecha_hora_formateada: new Date(solicitud.fecha_hora_solicitud).toLocaleDateString('es-ES'),
                hora_formateada: new Date(solicitud.fecha_hora_solicitud).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
              };
            } catch (error) {
              console.error('Error al obtener datos de mascota/cliente:', error);
              return {
                ...solicitud,
                nombre_mascota: 'Error',
                nombre_dueño: 'Error',
                fecha_hora_formateada: new Date(solicitud.fecha_hora_solicitud).toLocaleDateString('es-ES'),
                hora_formateada: new Date(solicitud.fecha_hora_solicitud).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
              };
            }
          })
        );
        
        // console.log('Solicitudes procesadas:', solicitudesConNombres); // Debug
        setSolicitudes(solicitudesConNombres);
      } else {
        console.error('Error al cargar solicitudes:', response.statusText);
        alert('Error al cargar las solicitudes');
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Error de conexión al cargar solicitudes');
    } finally {
      setLoading(false);
    }
  };

  // Función para obtener todas las mascotas
  const fetchMascotas = async () => {
    try {
      const response = await fetch(`${BASE_URL}/mascotas/`, {
        method: 'GET',
        mode: 'cors',
        headers: {
          'Accept': 'application/json',
        },
      });
      if (response.ok) {
        const data = await response.json();
        const mascotasData = data.mascotas || data;
        // console.log('Datos de mascotas recibidos:', mascotasData); // Debug
        
        const mascotasConDueño = await Promise.all(
          mascotasData.map(async (mascota) => {
            // console.log(`Procesando mascota ID: ${mascota.id_mascota}`); // Debug
            
            try {
              // Usar el endpoint correcto para obtener información del cliente
              const clienteMascotaResponse = await fetch(`${BASE_URL}/catalogos/cliente-mascota/mascota/${mascota.id_mascota}`, {
                method: 'GET',
                mode: 'cors',
                headers: { 'Accept': 'application/json' },
              });
              
              if (clienteMascotaResponse.ok) {
                const clienteMascotaData = await clienteMascotaResponse.json();
                // console.log(`Datos cliente-mascota para ${mascota.id_mascota}:`, JSON.stringify(clienteMascotaData, null, 2)); // Debug expandido
                
                let nombreDueño = 'Sin dueño asignado';
                
                // La estructura correcta es: clienteMascotaData.clientes[0].nombre_completo
                if (clienteMascotaData.clientes && clienteMascotaData.clientes.length > 0) {
                  nombreDueño = clienteMascotaData.clientes[0].nombre_completo;
                }
                
                return {
                  ...mascota,
                  nombre_dueño: nombreDueño
                };
              } else {
                // console.log(`Error al obtener cliente para mascota ${mascota.id_mascota}, status:`, clienteMascotaResponse.status);
                return { ...mascota, nombre_dueño: 'Sin dueño asignado' };
              }
            } catch (error) {
              console.error(`Error al obtener cliente para mascota ${mascota.id_mascota}:`, error);
              return { ...mascota, nombre_dueño: 'Error al cargar' };
            }
          })
        );
        
        // console.log('Mascotas procesadas:', mascotasConDueño); // Debug
        setMascotas(mascotasConDueño);
      } else {
        console.error('Error al cargar mascotas:', response.statusText);
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  // Función para eliminar solicitud
  const handleDelete = async (solicitud) => {
    if (solicitud.estado !== 'Pendiente') {
      alert('Solo se pueden eliminar solicitudes en estado "Pendiente"');
      return;
    }

    if (window.confirm(`¿Está seguro de eliminar la solicitud de ${solicitud.nombre_mascota}?`)) {
      setLoading(true);
      try {
        const response = await fetch(`${BASE_URL}/solicitudes/${solicitud.id_solicitud}`, {
          method: 'DELETE',
          mode: 'cors',
          headers: {
            'Accept': 'application/json',
          },
        });

        if (response.ok) {
          alert('Solicitud eliminada exitosamente');
          fetchSolicitudes();
        } else {
          const errorData = await response.json();
          alert(`Error: ${errorData.detail || 'Error desconocido'}`);
        }
      } catch (error) {
        console.error('Error:', error);
        alert('Error de conexión al eliminar solicitud');
      } finally {
        setLoading(false);
      }
    }
  };

  const handleMascotaChange = (e) => {
    const mascotaId = e.target.value;
    const mascotaSeleccionada = mascotas.find(m => m.id_mascota.toString() === mascotaId);
    
    setFormData({
      ...formData,
      id_mascota: mascotaId,
      dueño: mascotaSeleccionada ? mascotaSeleccionada.nombre_dueño : ''
    });
  };

  const handleAdd = () => {
    setFormData({
      id_mascota: '',
      tipo_solicitud: '',
      dueño: ''
    });
    setShowModal(true);
  };

  // Crear solicitud
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    // Validaciones básicas
    if (!formData.id_mascota || !formData.tipo_solicitud) {
      alert('Por favor, complete todos los campos requeridos');
      setLoading(false);
      return;
    }

    // Obtener información del recepcionista
    let recepcionistaActual = recepcionistaInfo;
    
    // Si no tenemos la info cargada, intentar obtenerla ahora
    if (!recepcionistaActual) {
      recepcionistaActual = await getRecepcionistaInfo();
      setRecepcionistaInfo(recepcionistaActual);
    }

    if (!recepcionistaActual || !recepcionistaActual.id_recepcionista) {
      alert('Error: No se pudo identificar al recepcionista actual. Verifique que su usuario esté correctamente configurado como recepcionista.');
      console.error('Error de recepcionista:', {
        user: user,
        recepcionistaInfo: recepcionistaActual
      });
      setLoading(false);
      return;
    }

    const fechaUTC = new Date();
    const fechaPeru = new Date(fechaUTC.getTime() - (5 * 60 * 60 * 1000)); 

    const solicitudData = {
      id_mascota: parseInt(formData.id_mascota),
      id_recepcionista: parseInt(recepcionistaActual.id_recepcionista),
      fecha_hora_solicitud: fechaPeru.toISOString(),
      tipo_solicitud: formData.tipo_solicitud,
      estado: 'Pendiente'
    };

    // console.log('Usuario logueado:', JSON.stringify(user, null, 2)); // Debug del usuario
    // console.log('Info del recepcionista:', recepcionistaActual); // Debug
    // console.log('Datos a enviar:', JSON.stringify(solicitudData, null, 2)); // Debug

    try {
      const response = await fetch(`${BASE_URL}/solicitudes/`, {
        method: 'POST',
        mode: 'cors',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify(solicitudData),
      });

      if (response.ok) {
        const responseData = await response.json();
        // console.log('Respuesta del servidor:', responseData);
        alert('Solicitud agregada exitosamente');
        setShowModal(false);
        fetchSolicitudes(); 
      } else {
        const errorData = await response.json().catch(() => ({}));
        console.error('Error del servidor:', JSON.stringify(errorData, null, 2));
        console.error('Status de respuesta:', response.status);
        alert(`Error: ${errorData.detail || errorData.message || 'Error desconocido al crear solicitud'}`);
      }
    } catch (error) {
      console.error('Error de conexión al guardar solicitud:', error);
      alert('Error de conexión al guardar solicitud');
    } finally {
      setLoading(false);
    }
  };

  // Limpiar filtros
  const clearFilters = () => {
    setSearchTerm('');
    setStatusFilter('todos');
  };

  const columns = [
    { key: 'nombre_mascota', header: 'MASCOTA' },
    { key: 'nombre_dueño', header: 'CLIENTE' },
    { key: 'fecha_hora_formateada', header: 'FECHA' },
    { key: 'hora_formateada', header: 'HORA' },
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
      label: <img src="https://i.ibb.co/LdbzttTC/Icono-Eliminar-Comprimida.png" alt="Eliminar" className="action-icon" />, 
      type: 'delete', 
      onClick: (row) => handleDelete(row),
      condition: (row) => row.estado === 'Pendiente'
    }
  ];

  return (
    <div className="solicitudes-management">
      <div className="section-header">
        <h2>Solicitudes / Nueva solicitud</h2>
        <button onClick={handleAdd} className="btn-add" disabled={loading}>
          + Añadir Solicitud
        </button>
      </div>

      {/* Debug: Mostrar información del recepcionista */}
      {/* {recepcionistaInfo && (
        <div style={{padding: '10px', backgroundColor: '#f0f0f0', margin: '10px 0', fontSize: '12px'}}>
          <strong>Debug - Recepcionista:</strong> ID: {recepcionistaInfo.id_recepcionista} 
          {recepcionistaInfo.nombre_completo && ` - ${recepcionistaInfo.nombre_completo}`}
        </div>
      )} */}

      <div className="solicitudes-table-section">
        <div className="table-header">
          <h3>LISTA DE SOLICITUDES</h3>
          <div className="filters-container">
            <input
              type="text"
              placeholder="Buscar por mascota o dueño..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="filter-select"
            >
              <option value="todos">Todos los estados</option>
              <option value="Pendiente">Pendiente</option>
              <option value="En triaje">En triaje</option>
              <option value="En atencion">En atención</option>
              <option value="Completada">Completada</option>
            </select>
            {(searchTerm || statusFilter !== 'todos') && (
              <button onClick={clearFilters} className="btn-clear">
                Limpiar filtros
              </button>
            )}
          </div>
        </div>

        {filteredSolicitudes.length > 0 && (
          <div className="results-info">
            <span>
              Mostrando {filteredSolicitudes.length} de {solicitudes.length} solicitudes
            </span>
          </div>
        )}

        {loading ? (
          <div className="loading-container">
            Cargando solicitudes...
          </div>
        ) : (
          <Table 
            columns={columns}
            data={filteredSolicitudes}
            actions={actions}
            emptyMessage="No hay solicitudes registradas"
          />
        )}
      </div>

      <Modal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        title="REGISTRO DE SOLICITUD DE ATENCIÓN"
        size="medium"
      >
        <form onSubmit={handleSubmit} className="solicitud-form">
          <div className="form-group">
            <label>MASCOTA (*)</label>
            <select
              value={formData.id_mascota}
              onChange={handleMascotaChange}
              required
            >
              <option value="">Seleccionar mascota...</option>
              {mascotas.map(mascota => (
                <option key={mascota.id_mascota} value={mascota.id_mascota}>
                  {mascota.nombre} - {mascota.especie}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>DUEÑO</label>
            <input
              type="text"
              value={formData.dueño}
              placeholder="Se completa automáticamente"
              readOnly
              disabled
            />
          </div>

          <div className="form-group">
            <label>TIPO DE SOLICITUD (*)</label>
            <select
              value={formData.tipo_solicitud}
              onChange={(e) => setFormData({...formData, tipo_solicitud: e.target.value})}
              required
            >
              <option value="">Seleccionar tipo...</option>
              <option value="Consulta urgente">Consulta urgente</option>
              <option value="Consulta normal">Consulta normal</option>
              <option value="Servicio programado">Servicio programado</option>
            </select>
          </div>

          <div className="form-actions">
            <button 
              type="button" 
              onClick={() => setShowModal(false)} 
              className="btn-cancel"
              disabled={loading}
            >
              CANCELAR
            </button>
            <button 
              type="submit" 
              className="btn-submit"
              disabled={loading || !recepcionistaInfo}
            >
              {loading ? 'PROCESANDO...' : 'CREAR SOLICITUD'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default SolicitudesManagement;