// components/recepcionista/CitasManagement.jsx
import React, { useState, useEffect } from 'react';
import Table from '../common/Table';
import Modal from '../common/Modal';
import './CitasManagement.css';
import { toast } from '../../utils/toast';
import Loader from '../common/Loader/Loader';
import { confirm } from '../../utils/confirm';

const CitasManagement = () => {
  const [citas, setCitas] = useState([]);
  const [filteredCitas, setFilteredCitas] = useState([]);
  const [mascotas, setMascotas] = useState([]);
  const [veterinariosDisponibles, setVeterinariosDisponibles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingVeterinarios, setLoadingVeterinarios] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [selectedMascota, setSelectedMascota] = useState(null);
  const [serviciosSolicitados, setServiciosSolicitados] = useState([]);
  
  // Estados para filtros
  const [searchTerm, setSearchTerm] = useState('');
  const [estadoFilter, setEstadoFilter] = useState('todos');
  
  // Estados para validaciones
  const [validationErrors, setValidationErrors] = useState({});
  
  const [formData, setFormData] = useState({
    id_mascota: '',
    id_servicio_solicitado: '',
    id_veterinario: '',
    fecha_hora_programada: '',
    requiere_ayuno: false,
    observaciones: ''
  });

  const BASE_URL = '/api/v1';

  // Cargar datos
  useEffect(() => {
    fetchCitas();
    fetchMascotas();
  }, []);

  // Aplicar filtros
  useEffect(() => {
    applyFilters();
  }, [citas, searchTerm, estadoFilter]);

  const applyFilters = () => {
    let filtered = [...citas];

    // Filtro por búsqueda (nombre de mascota)
    if (searchTerm.trim()) {
      const term = searchTerm.toLowerCase().trim();
      filtered = filtered.filter(cita => {
        const nombreMascota = cita.nombre_mascota?.toLowerCase() || '';
        return nombreMascota.includes(term);
      });
    }

    // Filtro por estado
    if (estadoFilter !== 'todos') {
      filtered = filtered.filter(cita => cita.estado_cita === estadoFilter);
    }

    setFilteredCitas(filtered);
  };

  const fetchCitas = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${BASE_URL}/consultas/cita`, {
        method: 'GET',
        mode: 'cors',
        headers: {
          'Accept': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        const citasConDetalles = await Promise.all(
          data.map(async (cita) => {
            try {
              // Obtener información de mascota, servicio y veterinario
              const requests = [
                fetch(`${BASE_URL}/mascotas/${cita.id_mascota}`, {
                  method: 'GET',
                  mode: 'cors',
                  headers: { 'Accept': 'application/json' },
                }),
                fetch(`${BASE_URL}/consultas/citaServicio/${cita.id_cita}`, {
                  method: 'GET',
                  mode: 'cors',
                  headers: { 'Accept': 'application/json' },
                }),
              ];

              // Obtener veterinario solo si está asignado
              if (cita.id_veterinario) {
                requests.push(
                  fetch(`${BASE_URL}/veterinarios/${cita.id_veterinario}`, {
                    method: 'GET',
                    mode: 'cors',
                    headers: { 'Accept': 'application/json' },
                  })
                );
              }

              const [mascotaResponse, servicioResponse, veterinarioResponse] = await Promise.all(requests);

              let nombreMascota = 'Desconocida';
              let nombreServicio = 'Sin servicio';
              let nombreVeterinario = 'Sin asignar';

              if (mascotaResponse.ok) {
                const mascotaData = await mascotaResponse.json();
                nombreMascota = mascotaData.nombre || 'Desconocida';
              }

              if (servicioResponse.ok) {
                const servicioData = await servicioResponse.json();
                nombreServicio = servicioData.nombre_servicio || 'Sin servicio';
              }

              if (veterinarioResponse && veterinarioResponse.ok) {
                const vetData = await veterinarioResponse.json();
                nombreVeterinario = `${vetData.nombre || ''} ${vetData.apellido_paterno || ''}`.trim() || 'Sin asignar';
              }

              return {
                ...cita,
                nombre_mascota: nombreMascota,
                nombre_servicio: nombreServicio,
                nombre_veterinario: nombreVeterinario,
                fecha_formateada: new Date(cita.fecha_hora_programada).toLocaleDateString('es-ES'),
                hora_formateada: new Date(cita.fecha_hora_programada).toLocaleTimeString('es-ES', { 
                  hour: '2-digit', 
                  minute: '2-digit' 
                })
              };
            } catch (error) {
              console.error('Error al obtener detalles de cita:', error);
              return {
                ...cita,
                nombre_mascota: 'Error',
                nombre_servicio: 'Error',
                nombre_veterinario: 'Error',
                fecha_formateada: 'N/A',
                hora_formateada: 'N/A'
              };
            }
          })
        );

        setCitas(citasConDetalles);
      } else {
        console.error('Error al cargar citas:', response.statusText);
        toast.error('Error al cargar las citas');
      }
    } catch (error) {
      console.error('Error:', error);
      toast.error('Error de conexión al cargar citas');
    } finally {
      setLoading(false);
    }
  };

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
        
        const mascotasConDueño = await Promise.all(
          mascotasData.map(async (mascota) => {
            try {
              const clienteResponse = await fetch(`${BASE_URL}/catalogos/cliente-mascota/mascota/${mascota.id_mascota}`, {
                method: 'GET',
                mode: 'cors',
                headers: { 'Accept': 'application/json' },
              });
              
              let nombreDueño = 'Sin dueño';
              if (clienteResponse.ok) {
                const clienteData = await clienteResponse.json();
                if (clienteData.clientes && clienteData.clientes.length > 0) {
                  nombreDueño = clienteData.clientes[0].nombre_completo;
                }
              }
              
              return {
                ...mascota,
                nombre_dueño: nombreDueño
              };
            } catch (error) {
              return {
                ...mascota,
                nombre_dueño: 'Error'
              };
            }
          })
        );
        
        setMascotas(mascotasConDueño);
      }
    } catch (error) {
      console.error('Error al cargar mascotas:', error);
    }
  };

  const fetchServiciosSolicitados = async (mascotaId) => {
    try {
      const response = await fetch(`${BASE_URL}/mascotas/mascota_cliente_servicio/${mascotaId}`, {
        method: 'GET',
        mode: 'cors',
        headers: {
          'Accept': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        if (Array.isArray(data) && data.length > 0) {
          // Verificar si ya existe una cita para alguno de estos servicios
          const serviciosDisponibles = await Promise.all(
            data.map(async (servicio) => {
              try {
                const citasResponse = await fetch(`${BASE_URL}/consultas/cita?mascota_id=${mascotaId}`, {
                  method: 'GET',
                  mode: 'cors',
                  headers: { 'Accept': 'application/json' },
                });

                if (citasResponse.ok) {
                  const citasData = await citasResponse.json();
                  const tieneCita = citasData.some(cita => 
                    cita.id_servicio_solicitado === servicio.id_servicio_solicitado
                  );
                  
                  return tieneCita ? null : servicio;
                }
                return servicio;
              } catch (error) {
                return servicio;
              }
            })
          );

          const serviciosFiltrados = serviciosDisponibles.filter(s => s !== null);
          setServiciosSolicitados(serviciosFiltrados);
          
          if (serviciosFiltrados.length === 0) {
            toast.info('Esta mascota no tiene servicios solicitados disponibles para agendar citas.');
            return false;
          }
          return true;
        } else {
          setServiciosSolicitados([]);
          toast.warning('Esta mascota no tiene servicios solicitados. Debe tener al menos un servicio solicitado para agendar una cita.');
          return false;
        }
      }
      return false;
    } catch (error) {
      console.error('Error al cargar servicios solicitados:', error);
      return false;
    }
  };

  const fetchVeterinariosDisponibles = async () => {
    setLoadingVeterinarios(true);
    try {
      const response = await fetch(`${BASE_URL}/veterinarios/disponibles`, {
        method: 'GET',
        mode: 'cors',
        headers: { 'Accept': 'application/json' },
      });

      if (response.ok) {
        const data = await response.json();
        setVeterinariosDisponibles(data.veterinarios_disponibles || []);
      } else {
        console.error('Error al cargar veterinarios disponibles:', response.statusText);
        setVeterinariosDisponibles([]);
      }
    } catch (error) {
      console.error('Error al cargar veterinarios disponibles:', error);
      setVeterinariosDisponibles([]);
    } finally {
      setLoadingVeterinarios(false);
    }
  };

  const handleAdd = () => {
    setFormData({
      id_mascota: '',
      id_servicio_solicitado: '',
      id_veterinario: '',
      fecha_hora_programada: '',
      requiere_ayuno: false,
      observaciones: ''
    });
    setSelectedMascota(null);
    setServiciosSolicitados([]);
    setValidationErrors({});
    fetchVeterinariosDisponibles();
    setShowModal(true);
  };

  const handleMascotaChange = async (e) => {
    const mascotaId = e.target.value;
    setFormData(prev => ({
      ...prev,
      id_mascota: mascotaId,
      id_servicio_solicitado: ''
    }));

    if (mascotaId) {
      const mascota = mascotas.find(m => m.id_mascota === parseInt(mascotaId));
      setSelectedMascota(mascota);
      
      const tieneServicios = await fetchServiciosSolicitados(mascotaId);
      if (!tieneServicios) {
        setFormData(prev => ({ ...prev, id_mascota: '' }));
        setSelectedMascota(null);
      }
    } else {
      setSelectedMascota(null);
      setServiciosSolicitados([]);
    }
  };

  const validateForm = () => {
    const errors = {};

    if (!formData.id_mascota) {
      errors.id_mascota = 'Debe seleccionar una mascota';
    }

    if (!formData.id_servicio_solicitado) {
      errors.id_servicio_solicitado = 'Debe seleccionar un servicio';
    }

    if (!formData.fecha_hora_programada) {
      errors.fecha_hora_programada = 'Debe seleccionar una fecha y hora';
    } else {
      const fechaSeleccionada = new Date(formData.fecha_hora_programada);
      const hoy = new Date();
      
      // Verificar que no sea el día actual
      if (fechaSeleccionada.toDateString() === hoy.toDateString()) {
        errors.fecha_hora_programada = 'No se puede programar una cita para el día actual';
      }
      
      // Verificar que sea una fecha futura
      if (fechaSeleccionada <= hoy) {
        errors.fecha_hora_programada = 'La fecha debe ser futura';
      }
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const checkConflictoCitas = async () => {
    try {
      const response = await fetch(`${BASE_URL}/consultas/cita`, {
        method: 'GET',
        mode: 'cors',
        headers: { 'Accept': 'application/json' },
      });

      if (response.ok) {
        const citasExistentes = await response.json();
        const fechaSeleccionada = new Date(formData.fecha_hora_programada);
        
        const hayConflicto = citasExistentes.some(cita => {
          const fechaCita = new Date(cita.fecha_hora_programada);
          return fechaCita.getTime() === fechaSeleccionada.getTime() &&
                 cita.id_servicio_solicitado === parseInt(formData.id_servicio_solicitado);
        });

        if (hayConflicto) {
          setValidationErrors(prev => ({
            ...prev,
            fecha_hora_programada: 'Ya existe una cita para este servicio en la fecha y hora seleccionada'
          }));
          return false;
        }
      }
      return true;
    } catch (error) {
      console.error('Error al verificar conflictos:', error);
      return true;
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    const noHayConflicto = await checkConflictoCitas();
    if (!noHayConflicto) {
      return;
    }

    setLoading(true);
    try {
      const citaData = {
        id_mascota: parseInt(formData.id_mascota),
        id_servicio_solicitado: parseInt(formData.id_servicio_solicitado),
        fecha_hora_programada: formData.fecha_hora_programada,
        estado_cita: 'Programada',
        requiere_ayuno: formData.requiere_ayuno,
        observaciones: formData.observaciones || ''
      };

      // Agregar veterinario si fue seleccionado
      if (formData.id_veterinario) {
        citaData.id_veterinario = parseInt(formData.id_veterinario);
      }

      const response = await fetch(`${BASE_URL}/consultas/cita`, {
        method: 'POST',
        mode: 'cors',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify(citaData)
      });

      if (response.ok) {
        toast.success('Cita registrada exitosamente');
        setShowModal(false);
        fetchCitas(); // Recargar la lista
      } else {
        const errorData = await response.json();
        toast.error(`Error al registrar la cita: ${errorData.detail || 'Error desconocido'}`);
      }
    } catch (error) {
      console.error('Error:', error);
      toast.error('Error de conexión al registrar la cita');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (cita) => {
    if (cita.estado_cita !== 'Programada') {
      toast.info('Solo se pueden eliminar citas con estado "Programada"');
      return;
    }

    if (!(await confirm({ variant: 'danger', message: `¿Está seguro de eliminar la cita de ${cita.nombre_mascota}?` }))) {
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${BASE_URL}/consultas/cita/${cita.id_cita}`, {
        method: 'DELETE',
        mode: 'cors',
        headers: {
          'Accept': 'application/json',
        },
      });

      if (response.ok) {
        toast.success('Cita eliminada exitosamente');
        fetchCitas(); // Recargar la lista
      } else {
        const errorData = await response.json();
        toast.error(`Error al eliminar la cita: ${errorData.detail || 'Error desconocido'}`);
      }
    } catch (error) {
      console.error('Error:', error);
      toast.error('Error de conexión al eliminar la cita');
    } finally {
      setLoading(false);
    }
  };

  const clearFilters = () => {
    setSearchTerm('');
    setEstadoFilter('todos');
  };

  const columns = [
    { key: 'id_cita', header: 'N°' },
    { key: 'nombre_mascota', header: 'MASCOTA' },
    { key: 'nombre_servicio', header: 'SERVICIO' },
    {
      key: 'nombre_veterinario',
      header: 'VETERINARIO',
      render: (cita) => (
        <span className={`vet-badge ${
          cita.nombre_veterinario && cita.nombre_veterinario !== 'Sin asignar'
            ? 'vet-badge--asignado'
            : 'vet-badge--sin-asignar'
        }`}>
          {cita.nombre_veterinario || 'Sin asignar'}
        </span>
      )
    },
    { key: 'fecha_formateada', header: 'FECHA' },
    { key: 'hora_formateada', header: 'HORA' },
    { 
      key: 'estado_cita', 
      header: 'ESTADO',
      render: (cita) => (
        <span className={`status-badge status-${cita.estado_cita.toLowerCase()}`}>
          {cita.estado_cita}
        </span>
      )
    }
  ];

  const actions = [
    {
      label: <img src="https://i.ibb.co/LdbzttTC/Icono-Eliminar-Comprimida.png" alt="Eliminar" className="action-icon" />,
      type: 'delete',
      onClick: handleDelete,
      title: 'Eliminar cita'
    }
  ];

  return (
    <div className="citas-management">
      <div className="section-header">
        <h2>Gestión de Citas</h2>
        <button onClick={handleAdd} className="btn-add" disabled={loading}>
          + Añadir Cita
        </button>
      </div>

      <div className="citas-table-section">
        <div className="table-header">
          <h3>REGISTROS DE CITAS</h3>
          <div className="filters-container">
            <div className="search-container">
              <input
                type="text"
                placeholder="Buscar por nombre de mascota..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="search-input"
              />
            </div>
            
            <select
              value={estadoFilter}
              onChange={(e) => setEstadoFilter(e.target.value)}
              className="filter-select"
            >
              <option value="todos">Todos los estados</option>
              <option value="Programada">Programada</option>
              <option value="Atendida">Atendida</option>
              <option value="Cancelada">Cancelada</option>
            </select>
            
            {(searchTerm || estadoFilter !== 'todos') && (
              <button onClick={clearFilters} className="btn-clear-filters">
                Limpiar filtros
              </button>
            )}
          </div>
        </div>

        {loading ? (
          <Loader message="Cargando citas" />
        ) : (
          <>
            <div className="results-info">
              <p>Mostrando {filteredCitas.length} de {citas.length} citas</p>
            </div>
            
            <Table 
              columns={columns}
              data={filteredCitas}
              actions={actions}
              emptyMessage="No hay citas registradas"
            />
          </>
        )}
      </div>

      {/* Modal Nueva Cita */}
      <Modal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        title="REGISTRO DE UNA NUEVA CITA"
        size="medium"
      >
        <form onSubmit={handleSubmit} className="cita-form">
          <div className="form-section">
            <h3>DATOS DE LA CITA</h3>
            <div className="form-row">
              <div className="form-group">
                <label>MASCOTA (*)</label>
                <select
                  value={formData.id_mascota}
                  onChange={handleMascotaChange}
                  className={validationErrors.id_mascota ? 'error' : ''}
                  required
                >
                  <option value="">Seleccionar mascota</option>
                  {mascotas.map(mascota => (
                    <option key={mascota.id_mascota} value={mascota.id_mascota}>
                      {mascota.nombre}
                    </option>
                  ))}
                </select>
                {validationErrors.id_mascota && (
                  <span className="error-message">{validationErrors.id_mascota}</span>
                )}
              </div>

              <div className="form-group">
                <label>DUEÑO</label>
                <input
                  type="text"
                  value={selectedMascota?.nombre_dueño || ''}
                  readOnly
                  placeholder="Se llena automáticamente"
                  className="readonly-input"
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>SERVICIO SOLICITADO (*)</label>
                <select
                  value={formData.id_servicio_solicitado}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    id_servicio_solicitado: e.target.value
                  }))}
                  className={validationErrors.id_servicio_solicitado ? 'error' : ''}
                  disabled={!selectedMascota || serviciosSolicitados.length === 0}
                  required
                >
                  <option value="">Seleccionar servicio</option>
                  {serviciosSolicitados.map(servicio => (
                    <option key={servicio.id_servicio_solicitado} value={servicio.id_servicio_solicitado}>
                      {servicio.nombre_servicio}
                    </option>
                  ))}
                </select>
                {validationErrors.id_servicio_solicitado && (
                  <span className="error-message">{validationErrors.id_servicio_solicitado}</span>
                )}
              </div>

              <div className="form-group">
                <label>FECHA PROGRAMADA (*)</label>
                <input
                  type="datetime-local"
                  value={formData.fecha_hora_programada}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    fecha_hora_programada: e.target.value
                  }))}
                  className={validationErrors.fecha_hora_programada ? 'error' : ''}
                  min={new Date(Date.now() + 86400000).toISOString().slice(0, 16)} // Mínimo mañana
                  required
                />
                {validationErrors.fecha_hora_programada && (
                  <span className="error-message">{validationErrors.fecha_hora_programada}</span>
                )}
              </div>
            </div>

            {/* Selector de Veterinario */}
            <div className="form-row">
              <div className="form-group full-width">
                <label>VETERINARIO ASIGNADO</label>
                <select
                  id="select-veterinario"
                  value={formData.id_veterinario}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    id_veterinario: e.target.value
                  }))}
                  disabled={loadingVeterinarios}
                >
                  <option value="">
                    {loadingVeterinarios ? 'Cargando veterinarios...' : 'Sin asignar (opcional)'}
                  </option>
                  {veterinariosDisponibles.map(vet => (
                    <option key={vet.id_veterinario} value={vet.id_veterinario}>
                      {`${vet.nombre} ${vet.apellido_paterno}`} — {vet.tipo_veterinario} · Turno {vet.turno}
                    </option>
                  ))}
                </select>
                {veterinariosDisponibles.length === 0 && !loadingVeterinarios && (
                  <span className="vet-info-msg">No hay veterinarios con disposición "Libre" en este momento.</span>
                )}
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={formData.requiere_ayuno}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      requiere_ayuno: e.target.checked
                    }))}
                  />
                  REQUIERE AYUNO
                </label>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group full-width">
                <label>OBSERVACIONES</label>
                <textarea
                  value={formData.observaciones}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    observaciones: e.target.value
                  }))}
                  placeholder="Observaciones adicionales..."
                  rows="3"
                  className="textarea-input"
                />
              </div>
            </div>
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
              disabled={loading}
            >
              {loading ? 'CREANDO...' : 'CREAR CITA'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default CitasManagement;