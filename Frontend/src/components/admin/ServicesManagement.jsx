// src/components/admin/ServicesManagement.jsx - CÓDIGO FINAL COMPLETO
import React, { useState, useEffect } from 'react';
import { apiFetch } from '../../api/client';
import Table from '../common/Table';
import Modal from '../common/Modal';
import './ServicesManagement.css';
import { toast } from '../../utils/toast';
import Loader from '../common/Loader/Loader';
import { confirm } from '../../utils/confirm';

const ServicesManagement = () => {
  const [servicios, setServicios] = useState([]);
  const [tiposServicio, setTiposServicio] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [modalType, setModalType] = useState('add');
  const [selectedService, setSelectedService] = useState(null);
  const [selectedTipoFilter, setSelectedTipoFilter] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  
  // Estados para paginación
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 6;
  
  const [formData, setFormData] = useState({
    nombre_servicio: '',
    precio: '',
    id_tipo_servicio: ''
  });

  // URLs de la API - Configuración dinámica según entorno
  const getApiBaseUrl = () => {
    // Si estamos en Netlify, usar proxy local
    if (window.location.hostname.includes('netlify.app')) {
      return '/catalogos';
    }
    // En otros casos, usar la URL completa
    return '/catalogos';
  };
  
  const API_BASE = getApiBaseUrl();
  const SERVICIOS_URL = `${API_BASE}/servicios`;
  const TIPOS_SERVICIO_URL = `${API_BASE}/tipos-servicio`;

  // Cargar datos al montar el componente
  useEffect(() => {
    fetchTiposServicio();
    fetchServicios();
  }, []);

  // Obtener tipos de servicio
  const fetchTiposServicio = async () => {
    try {
      const response = await apiFetch(`${TIPOS_SERVICIO_URL}/`);
      
      if (!response.ok) {
        throw new Error(`Error: ${response.status} ${response.statusText}`);
      }
      const data = await response.json();
      setTiposServicio(data.tipos_servicio || data || []);
    } catch (error) {
      console.error('❌ Error detallado al obtener tipos de servicio:', error);
      console.error('❌ Nombre del error:', error.name);
      console.error('❌ Mensaje del error:', error.message);
      setError('Error al cargar tipos de servicio: ' + error.message);
    }
  };

  // Obtener servicios con HTTPS forzado
  const fetchServicios = async () => {
    setLoading(true);
    try {
      
      const response = await apiFetch(`${SERVICIOS_URL}/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });
      
      
      if (!response.ok) {
        throw new Error(`HTTP Error: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      setServicios(data.servicios || data || []);
      setError(null);
    } catch (error) {
      console.error('❌ Error detallado al obtener servicios:', {
        name: error.name,
        message: error.message,
        stack: error.stack
      });
      
      setError('Error al cargar servicios: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // Crear nuevo servicio
  const createServicio = async (servicioData) => {
    try {
      const response = await apiFetch(`${SERVICIOS_URL}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(servicioData)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || `Error: ${response.status}`);
      }

      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      console.error('Error creando servicio:', error);
      return { success: false, message: error.message };
    }
  };

  // Actualizar servicio
  const updateServicio = async (servicioId, servicioData) => {
    try {
      const response = await apiFetch(`${SERVICIOS_URL}/${servicioId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(servicioData)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || `Error: ${response.status}`);
      }

      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      console.error('Error actualizando servicio:', error);
      return { success: false, message: error.message };
    }
  };

  // Eliminar servicio
  const deleteServicio = async (servicioId) => {
    try {
      const response = await apiFetch(`${SERVICIOS_URL}/${servicioId}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || `Error: ${response.status}`);
      }

      return { success: true };
    } catch (error) {
      console.error('Error eliminando servicio:', error);
      return { success: false, message: error.message };
    }
  };

  // Filtrar servicios por tipo y aplicar paginación
  const getFilteredServicios = () => {
    let filtered = servicios;

    // Filtrar por tipo si está seleccionado
    if (selectedTipoFilter) {
      filtered = filtered.filter(servicio => 
        servicio.id_tipo_servicio === parseInt(selectedTipoFilter)
      );
    }

    // Filtrar por término de búsqueda
    if (searchTerm.trim()) {
      const searchLower = searchTerm.toLowerCase();
      filtered = filtered.filter(servicio =>
        servicio.nombre_servicio?.toLowerCase().includes(searchLower) ||
        servicio.id_servicio?.toString().includes(searchTerm)
      );
    }

    return filtered;
  };

  // Obtener servicios para la página actual
  const getPaginatedServicios = () => {
    const filtered = getFilteredServicios();
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    return filtered.slice(startIndex, endIndex);
  };

  // Calcular información de paginación
  const getPaginationInfo = () => {
    const filtered = getFilteredServicios();
    const totalItems = filtered.length;
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    
    return {
      totalItems,
      totalPages,
      currentPage,
      itemsPerPage,
      hasNext: currentPage < totalPages,
      hasPrev: currentPage > 1
    };
  };

  // Obtener nombre del tipo de servicio
  const getNombreTipoServicio = (idTipo) => {
    const tipo = tiposServicio.find(t => t.id_tipo_servicio === idTipo);
    return tipo ? tipo.descripcion : 'N/A';
  };

  // Manejadores de eventos
  const handleAdd = () => {
    setModalType('add');
    setSelectedService(null);
    setFormData({
      nombre_servicio: '',
      precio: '',
      id_tipo_servicio: ''
    });
    setShowModal(true);
  };

  const handleEdit = (service) => {
    setModalType('edit');
    setSelectedService(service);
    setFormData({
      nombre_servicio: service.nombre_servicio || '',
      precio: service.precio?.toString() || '',
      id_tipo_servicio: service.id_tipo_servicio?.toString() || ''
    });
    setShowModal(true);
  };

  // Manejadores de paginación
  const handleNextPage = () => {
    const paginationInfo = getPaginationInfo();
    if (paginationInfo.hasNext) {
      setCurrentPage(currentPage + 1);
    }
  };

  const handlePrevPage = () => {
    const paginationInfo = getPaginationInfo();
    if (paginationInfo.hasPrev) {
      setCurrentPage(currentPage - 1);
    }
  };

  // Resetear página cuando cambien los filtros
  useEffect(() => {
    setCurrentPage(1);
  }, [selectedTipoFilter, searchTerm]);

  const handleDelete = async (service) => {
    if (!(await confirm({ variant: 'danger', message: `¿Está seguro de eliminar el servicio "${service.nombre_servicio}"?` }))) {
      return;
    }

    const result = await deleteServicio(service.id_servicio);
    if (result.success) {
      toast.success('Servicio eliminado exitosamente');
      fetchServicios(); // Recargar lista
    } else {
      toast.error(`Error al eliminar: ${result.message}`);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Validaciones básicas
      if (!formData.nombre_servicio.trim()) {
        toast.warning('El nombre del servicio es obligatorio');
        return;
      }

      if (!formData.precio || parseFloat(formData.precio) <= 0) {
        toast.warning('El precio debe ser mayor a 0');
        return;
      }

      if (!formData.id_tipo_servicio) {
        toast.warning('Debe seleccionar un tipo de servicio');
        return;
      }

      // Preparar datos para envío
      const servicioData = {
        nombre_servicio: formData.nombre_servicio.trim(),
        precio: parseFloat(formData.precio),
        id_tipo_servicio: parseInt(formData.id_tipo_servicio),
        activo: true // Por defecto activo
      };

      let result;
      if (modalType === 'add') {
        result = await createServicio(servicioData);
      } else {
        result = await updateServicio(selectedService.id_servicio, servicioData);
      }

      if (result.success) {
        setShowModal(false);
        fetchServicios(); // Recargar lista
        toast.success(modalType === 'add' ? 'Servicio creado exitosamente' : 'Servicio actualizado exitosamente');
      } else {
        toast.error(`Error: ${result.message}`);
      }
    } catch (error) {
      console.error('Error en submit:', error);
      toast.error('Error al guardar servicio');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Configuración de columnas exacta a la imagen
  const columns = [
    { 
      key: 'id_servicio', 
      header: 'ID',
      style: { textAlign: 'center', width: '80px' }
    },
    { 
      key: 'tipo_servicio', 
      header: 'TIPO DE SERVICIO',
      render: (service) => getNombreTipoServicio(service.id_tipo_servicio),
      style: { textAlign: 'center', fontWeight: 'bold' }
    },
    { 
      key: 'nombre_servicio', 
      header: 'NOMBRE',
      style: { textAlign: 'center', fontWeight: 'bold' }
    },
    { 
      key: 'precio', 
      header: 'PRECIO',
      render: (service) => `S/${parseFloat(service.precio || 0).toFixed(0)}`,
      style: { textAlign: 'center', fontWeight: 'bold' }
    }
  ];

  const actions = [
    { 
      label: '✏️', 
      type: 'edit', 
      onClick: handleEdit,
      style: { color: '#28a745', cursor: 'pointer', fontSize: '18px' }
    },
    { 
      label: '🗑️', 
      type: 'delete', 
      onClick: handleDelete,
      style: { color: '#dc3545', cursor: 'pointer', fontSize: '18px' }
    }
  ];

  // Estilos inline para coincidir con el diseño


  if (error) {
    return (
      <div className="error-message">
        <h3>Error</h3>
        <p>{error}</p>
        <button className="btn-retry" onClick={() => { fetchTiposServicio(); fetchServicios(); }}>
          Reintentar
        </button>
      </div>
    );
  }

  const serviciosPaginados = getPaginatedServicios();
  const paginationInfo = getPaginationInfo();

  return (
    <>
    <div className="services-management">
    {/* Cabecera principal */}
    <div className="section-header">
      <h2>GESTIÓN DE SERVICIOS</h2>
      <button
        onClick={handleAdd}
        className="btn-add"
        disabled={loading}
      >
        + AÑADIR SERVICIO
      </button>
    </div>

    {/* Contenedor de la tabla y filtros */}
    <div className="services-table-section">
      <div className="table-header">
        <h3>LISTA DE SERVICIOS</h3>

        <div className="filters-container">
          {/* Filtro por tipo */}
          <select
            value={selectedTipoFilter}
            onChange={(e) => setSelectedTipoFilter(e.target.value)}
            className="filter-select"
          >
            <option value="">Todos los tipos</option>
            {tiposServicio.map(tipo => (
              <option key={tipo.id_tipo_servicio} value={tipo.id_tipo_servicio}>
                {tipo.descripcion}
              </option>
            ))}
          </select>

          {/* Buscador */}
          <input
            type="text"
            placeholder="Buscar por nombre o código..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
      </div>

      {/* Información de resultados */}
      <div className="results-info">
        <span>Total: {paginationInfo.totalItems} servicios</span>
        <span>Página {paginationInfo.currentPage} de {paginationInfo.totalPages}</span>
        <span>Mostrando: {serviciosPaginados.length} registros</span>
      </div>

      {loading && (
        <Loader message="Cargando servicios" />
      )}

      {error && (
        <div className="error-message">
          <p>{error}</p>
          <button
            onClick={() => {
              fetchTiposServicio();
              fetchServicios();
            }}
            className="btn-retry"
          >
            Reintentar
          </button>
        </div>
      )}

      <Table
        columns={columns}
        mobileTitle={(servicio) => (
          <>
            <span className="card-hd-side">{servicio.id_servicio}</span>
            <span className="card-hd-main">{servicio.nombre_servicio || 'Sin nombre'}</span>
          </>
        )}
        data={serviciosPaginados}
        actions={actions}
        emptyMessage="No hay servicios registrados"
      />

      {/* Paginación */}
      {paginationInfo.totalPages > 1 && (
        <div className="pagination">
          <button
            onClick={handlePrevPage}
            disabled={!paginationInfo.hasPrev}
            className="pagination-btn"
          >
            ← Anterior
          </button>

          <span className="pagination-info">
            Página {paginationInfo.currentPage} de {paginationInfo.totalPages}
          </span>

          <button
            onClick={handleNextPage}
            disabled={!paginationInfo.hasNext}
            className="pagination-btn"
          >
            Siguiente →
          </button>
        </div>
      )}
    </div>

    {/* Modal */}
    <Modal
      isOpen={showModal}
      onClose={() => setShowModal(false)}
      title={modalType === 'add' ? 'AGREGAR SERVICIO' : 'EDITAR SERVICIO'}
      size="large"
    >
      <form onSubmit={handleSubmit} className="service-form">
        <div className="form-group">
          <label>Tipo de servicio (*)</label>
          <select
            name="id_tipo_servicio"
            value={formData.id_tipo_servicio}
            onChange={handleInputChange}
            required
          >
            {modalType === 'add' && <option value="">Seleccione un tipo</option>}
            {tiposServicio.map(tipo => (
              <option key={tipo.id_tipo_servicio} value={tipo.id_tipo_servicio}>
                {tipo.descripcion}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label>Nombre (*)</label>
          <input
            type="text"
            name="nombre_servicio"
            value={formData.nombre_servicio}
            onChange={handleInputChange}
            required
          />
        </div>

        <div className="form-group">
          <label>Precio (*)</label>
          <input
            type="number"
            name="precio"
            value={formData.precio}
            onChange={handleInputChange}
            min="0"
            required
          />
        </div>

        <div className="form-actions">
          <button
            type="submit"
            className="btn-submit"
            disabled={loading}
          >
            {loading ? 'Guardando...' : 'GUARDAR'}
          </button>
        </div>
      </form>
    </Modal>
  </div>
  </>
  );
};

export default ServicesManagement;
