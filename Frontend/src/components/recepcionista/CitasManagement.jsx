// components/recepcionista/CitasManagement.jsx
import React, { useState, useEffect } from 'react';
import { apiFetch } from '../../api/client';
import Table from '../common/Table';
import Modal from '../ui/Modal/Modal';
import './CitasManagement.css';
import { toast } from '../../utils/toast';
import { formatApiError } from '../../utils/apiError';
import Loader from '../ui/Loader/Loader';
import { confirm } from '../../utils/confirm';

const CitasManagement = () => {
  const [citas, setCitas] = useState([]); // página actual, ya enriquecida por el backend
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCitas, setTotalCitas] = useState(0);
  const [refreshKey, setRefreshKey] = useState(0); // fuerza recarga tras crear/eliminar
  const [mascotas, setMascotas] = useState([]);
  const [veterinariosDisponibles, setVeterinariosDisponibles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingVeterinarios, setLoadingVeterinarios] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [selectedMascota, setSelectedMascota] = useState(null);
  const [serviciosSolicitados, setServiciosSolicitados] = useState([]);
  
  // Estados para filtros (server-side)
  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
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

  const BASE_URL = '';

  const ITEMS_POR_PAGINA = 10;

  // Cargar catálogo de mascotas al montar
  useEffect(() => {
    fetchMascotas();
  }, []);

  // Debounce del término de búsqueda para no consultar en cada tecla
  useEffect(() => {
    const t = setTimeout(() => setDebouncedSearch(searchTerm), 350);
    return () => clearTimeout(t);
  }, [searchTerm]);

  // Al cambiar la búsqueda o el filtro de estado, volver a la primera página
  useEffect(() => {
    setCurrentPage(1);
  }, [debouncedSearch, estadoFilter]);

  // Cargar la página actual desde el servidor (paginación + filtro server-side).
  // refreshKey fuerza la recarga tras crear/eliminar aunque no cambien página/filtros.
  useEffect(() => {
    fetchCitas();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentPage, debouncedSearch, estadoFilter, refreshKey]);

  // Obtener la página actual de citas, ya enriquecida por el backend (una sola petición
  // con JOINs en lugar del antiguo patrón N+1 de 1 + N*3 peticiones).
  const fetchCitas = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: String(currentPage),
        per_page: String(ITEMS_POR_PAGINA),
      });
      if (debouncedSearch.trim()) params.set('search', debouncedSearch.trim());
      if (estadoFilter !== 'todos') params.set('estado', estadoFilter);

      const response = await apiFetch(`${BASE_URL}/consultas/citas/enriquecidas?${params.toString()}`, {
        method: 'GET',
        mode: 'cors',
        headers: { 'Accept': 'application/json' },
      });

      if (response.ok) {
        const data = await response.json();
        const rows = (data.citas || []).map((cita) => ({
          ...cita,
          fecha_formateada: new Date(cita.fecha_hora_programada).toLocaleDateString('es-ES'),
          hora_formateada: new Date(cita.fecha_hora_programada).toLocaleTimeString('es-ES', {
            hour: '2-digit',
            minute: '2-digit',
          }),
        }));
        setCitas(rows);
        setTotalCitas(data.total || 0);
        setTotalPages(data.total_pages || 1);
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

  // Mascotas con su dueño ya enriquecidas por el backend (1 sola petición en vez de
  // 1 + N a /catalogos/cliente-mascota/mascota/{id}).
  const fetchMascotas = async () => {
    try {
      const response = await apiFetch(`${BASE_URL}/mascotas/selector`, {
        method: 'GET',
        mode: 'cors',
        headers: {
          'Accept': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setMascotas(data.mascotas || []);
      }
    } catch (error) {
      console.error('Error al cargar mascotas:', error);
    }
  };

  const fetchServiciosSolicitados = async (mascotaId) => {
    try {
      const response = await apiFetch(`${BASE_URL}/mascotas/mascota_cliente_servicio/${mascotaId}`, {
        method: 'GET',
        mode: 'cors',
        headers: {
          'Accept': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        // El backend ya devuelve únicamente los servicios en estado 'Solicitado' (los que
        // aún se pueden citar), resueltos por la cadena Consulta→Triaje→Solicitud. No hace
        // falta recomprobar citas por servicio (se eliminó ese fan-out).
        const servicios = Array.isArray(data) ? data : [];
        setServiciosSolicitados(servicios);

        if (servicios.length === 0) {
          toast.warning('Esta mascota no tiene servicios solicitados disponibles para agendar una cita.');
          return false;
        }
        return true;
      }
      return false;
    } catch (error) {
      console.error('Error al cargar servicios solicitados:', error);
      toast.error('No se pudieron cargar los servicios de la mascota. Intente nuevamente.');
      return false;
    }
  };

  const fetchVeterinariosDisponibles = async () => {
    setLoadingVeterinarios(true);
    try {
      const response = await apiFetch(`${BASE_URL}/veterinarios/disponibles`, {
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
        toast.error('No se pudieron cargar los veterinarios disponibles.');
      }
    } catch (error) {
      console.error('Error al cargar veterinarios disponibles:', error);
      setVeterinariosDisponibles([]);
      toast.error('No se pudieron cargar los veterinarios disponibles.');
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
      const response = await apiFetch(`${BASE_URL}/consultas/cita`, {
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
        // La BD exige observaciones NULL o con >= 3 caracteres; enviar null si está vacío
        observaciones: formData.observaciones?.trim() || null
      };

      // Agregar veterinario si fue seleccionado
      if (formData.id_veterinario) {
        citaData.id_veterinario = parseInt(formData.id_veterinario);
      }

      const response = await apiFetch(`${BASE_URL}/consultas/cita`, {
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
        // Volver a la primera página (la nueva cita aparece arriba, orden desc)
        setCurrentPage(1);
        setRefreshKey(k => k + 1);
      } else {
        const errorData = await response.json();
        toast.error(formatApiError(errorData, 'No se pudo registrar la cita'));
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
      const response = await apiFetch(`${BASE_URL}/consultas/cita/${cita.id_cita}`, {
        method: 'DELETE',
        mode: 'cors',
        headers: {
          'Accept': 'application/json',
        },
      });

      if (response.ok) {
        toast.success('Cita eliminada exitosamente');
        setRefreshKey(k => k + 1);
      } else {
        const errorData = await response.json();
        toast.error(formatApiError(errorData, 'No se pudo eliminar la cita'));
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
            {totalCitas > 0 && (
              <div className="results-info">
                <p>Mostrando {citas.length} de {totalCitas} citas</p>
              </div>
            )}

            <Table
              columns={columns}
              mobileTitle={(cita) => {
                const serv = (cita.nombre_servicio || '').trim().split(' ')[0];
                return (
                  <>
                    <span className="card-hd-side">{cita.nombre_mascota || 'S/mascota'}</span>
                    <span className="card-hd-mid">{serv || 'S/servicio'}</span>
                    <span className="card-hd-side card-hd-right">{cita.fecha_formateada || ''}</span>
                  </>
                );
              }}
              data={citas}
              actions={actions}
              emptyMessage="No hay citas registradas"
            />
          </>
        )}

        {!loading && totalPages > 1 && (
          <div
            className="pagination-controls"
            style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '12px', marginTop: '12px' }}
          >
            <button
              className="btn btn-secondary"
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
            >
              Anterior
            </button>
            <span>Página {currentPage} de {totalPages}</span>
            <button
              className="btn btn-secondary"
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
            >
              Siguiente
            </button>
          </div>
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