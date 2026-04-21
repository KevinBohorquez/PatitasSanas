// src/components/admin/ServicesManagement.jsx - CÓDIGO FINAL COMPLETO
import React, { useState, useEffect } from 'react';
import Table from '../common/Table';
import Modal from '../common/Modal';
import './ServicesManagement.css';

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
      return '/api/v1/catalogos';
    }
    // En otros casos, usar la URL completa
    return 'https://veterinariaclinicabackend-production.up.railway.app/api/v1/catalogos';
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
      console.log('🔗 Intentando conectar a:', TIPOS_SERVICIO_URL);
      const response = await fetch(TIPOS_SERVICIO_URL);
      console.log('📡 Respuesta recibida:', response.status, response.statusText);
      
      if (!response.ok) {
        throw new Error(`Error: ${response.status} ${response.statusText}`);
      }
      const data = await response.json();
      console.log('✅ Tipos de servicio obtenidos:', data);
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
      // Forzar HTTPS en todas las peticiones
      const secureUrl = SERVICIOS_URL.replace('http://', 'https://');
      console.log('🔗 Conectando a servicios (HTTPS):', secureUrl);
      
      const response = await fetch(secureUrl, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });
      
      console.log('📡 Respuesta de servicios:', {
        status: response.status,
        statusText: response.statusText,
        ok: response.ok,
        url: response.url
      });
      
      if (!response.ok) {
        throw new Error(`HTTP Error: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('✅ Datos de servicios obtenidos:', data);
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
      const response = await fetch(SERVICIOS_URL, {
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
      console.log('Servicio creado:', data);
      return { success: true, data };
    } catch (error) {
      console.error('Error creando servicio:', error);
      return { success: false, message: error.message };
    }
  };

  // Actualizar servicio
  const updateServicio = async (servicioId, servicioData) => {
    try {
      const response = await fetch(`${SERVICIOS_URL}/${servicioId}`, {
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
      console.log('Servicio actualizado:', data);
      return { success: true, data };
    } catch (error) {
      console.error('Error actualizando servicio:', error);
      return { success: false, message: error.message };
    }
  };

  // Eliminar servicio
  const deleteServicio = async (servicioId) => {
    try {
      const response = await fetch(`${SERVICIOS_URL}/${servicioId}`, {
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
  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
  };

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
    if (!window.confirm(`¿Está seguro de eliminar el servicio "${service.nombre_servicio}"?`)) {
      return;
    }

    const result = await deleteServicio(service.id_servicio);
    if (result.success) {
      alert('Servicio eliminado exitosamente');
      fetchServicios(); // Recargar lista
    } else {
      alert(`Error al eliminar: ${result.message}`);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Validaciones básicas
      if (!formData.nombre_servicio.trim()) {
        alert('El nombre del servicio es obligatorio');
        return;
      }

      if (!formData.precio || parseFloat(formData.precio) <= 0) {
        alert('El precio debe ser mayor a 0');
        return;
      }

      if (!formData.id_tipo_servicio) {
        alert('Debe seleccionar un tipo de servicio');
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
        alert(modalType === 'add' ? 'Servicio creado exitosamente' : 'Servicio actualizado exitosamente');
      } else {
        alert(`Error: ${result.message}`);
      }
    } catch (error) {
      console.error('Error en submit:', error);
      alert('Error al guardar servicio');
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
      <div style={styles.errorContainer}>
        <h3>Error</h3>
        <p>{error}</p>
        <button onClick={() => { fetchTiposServicio(); fetchServicios(); }}>
          Reintentar
        </button>
      </div>
    );
  }

  const serviciosPaginados = getPaginatedServicios();
  const paginationInfo = getPaginationInfo();

  return (
    <>
    <style jsx>{`
  .services-management table th {
    background: #68c1da !important;
    color: white !important;
    padding: 12px 15px;
    text-align: left;
    font-weight: 600;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
`}</style>
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
        <div className="loading-container">
          Cargando servicios...
        </div>
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
/*// src/components/admin/ServicesManagement.jsx - CÓDIGO FINAL COMPLETO
import React, { useState, useEffect } from 'react';
import Table from '../common/Table';
import Modal from '../common/Modal';

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
      return '/api/v1/catalogos';
    }
    // En otros casos, usar la URL completa
    return 'https://veterinariaclinicabackend-production.up.railway.app/api/v1/catalogos';
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
      console.log('🔗 Intentando conectar a:', TIPOS_SERVICIO_URL);
      const response = await fetch(TIPOS_SERVICIO_URL);
      console.log('📡 Respuesta recibida:', response.status, response.statusText);
      
      if (!response.ok) {
        throw new Error(`Error: ${response.status} ${response.statusText}`);
      }
      const data = await response.json();
      console.log('✅ Tipos de servicio obtenidos:', data);
      setTiposServicio(data.tipos_servicio || data || []);
    } catch (error) {
      console.error('❌ Error detallado al obtener tipos de servicio:', error);
      console.error('❌ Nombre del error:', error.name);
      console.error('❌ Mensaje del error:', error.message);
      setError('Error al cargar tipos de servicio: ' + error.message);
    }
  };

  // Obtener servicios con debugging mejorado
  const fetchServicios = async () => {
    setLoading(true);
    try {
      console.log('🔗 Intentando conectar a servicios:', SERVICIOS_URL);
      
      const response = await fetch(SERVICIOS_URL, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });
      
      console.log('📡 Respuesta de servicios:', {
        status: response.status,
        statusText: response.statusText,
        ok: response.ok,
        url: response.url
      });
      
      if (!response.ok) {
        throw new Error(`HTTP Error: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('✅ Datos de servicios obtenidos:', data);
      setServicios(data.servicios || data || []);
      setError(null);
    } catch (error) {
      console.error('❌ Error detallado al obtener servicios:', {
        name: error.name,
        message: error.message,
        stack: error.stack
      });
      
      // Si falla el proxy, intentar con URL directa
      if (SERVICIOS_URL.startsWith('/api') && !error.message.includes('HTTP Error')) {
        console.log('🔄 Reintentando servicios con URL directa...');
        await fetchServiciosDirecto();
      } else {
        setError('Error al cargar servicios: ' + error.message);
      }
    } finally {
      setLoading(false);
    }
  };

  // Función de respaldo para servicios con URL directa
  const fetchServiciosDirecto = async () => {
    try {
      const directUrl = 'https://veterinariaclinicabackend-production.up.railway.app/api/v1/catalogos/servicios';
      console.log('🔗 Intentando conexión directa a servicios:', directUrl);
      
      const response = await fetch(directUrl);
      
      if (!response.ok) {
        throw new Error(`HTTP Error: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('✅ Servicios obtenidos con URL directa:', data);
      setServicios(data.servicios || data || []);
      setError(null);
    } catch (error) {
      console.error('❌ Error con URL directa de servicios también:', error);
      setError('Error al cargar servicios. Verifique su conexión.');
    }
  };

  // Crear nuevo servicio
  const createServicio = async (servicioData) => {
    try {
      const response = await fetch(SERVICIOS_URL, {
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
      console.log('Servicio creado:', data);
      return { success: true, data };
    } catch (error) {
      console.error('Error creando servicio:', error);
      return { success: false, message: error.message };
    }
  };

  // Actualizar servicio
  const updateServicio = async (servicioId, servicioData) => {
    try {
      const response = await fetch(`${SERVICIOS_URL}/${servicioId}`, {
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
      console.log('Servicio actualizado:', data);
      return { success: true, data };
    } catch (error) {
      console.error('Error actualizando servicio:', error);
      return { success: false, message: error.message };
    }
  };

  // Eliminar servicio
  const deleteServicio = async (servicioId) => {
    try {
      const response = await fetch(`${SERVICIOS_URL}/${servicioId}`, {
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
  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
  };

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
    if (!window.confirm(`¿Está seguro de eliminar el servicio "${service.nombre_servicio}"?`)) {
      return;
    }

    const result = await deleteServicio(service.id_servicio);
    if (result.success) {
      alert('Servicio eliminado exitosamente');
      fetchServicios(); // Recargar lista
    } else {
      alert(`Error al eliminar: ${result.message}`);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Validaciones básicas
      if (!formData.nombre_servicio.trim()) {
        alert('El nombre del servicio es obligatorio');
        return;
      }

      if (!formData.precio || parseFloat(formData.precio) <= 0) {
        alert('El precio debe ser mayor a 0');
        return;
      }

      if (!formData.id_tipo_servicio) {
        alert('Debe seleccionar un tipo de servicio');
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
        alert(modalType === 'add' ? 'Servicio creado exitosamente' : 'Servicio actualizado exitosamente');
      } else {
        alert(`Error: ${result.message}`);
      }
    } catch (error) {
      console.error('Error en submit:', error);
      alert('Error al guardar servicio');
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
  const styles = {
    container: {
      padding: '20px',
      backgroundColor: '#f5f5f5',
      minHeight: '100vh'
    },
    header: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: '20px'
    },
    filterSection: {
      display: 'flex',
      alignItems: 'center',
      gap: '20px'
    },
    tipoFilter: {
      backgroundColor: '#e0e0e0',
      border: 'none',
      padding: '10px 15px',
      borderRadius: '4px',
      fontWeight: 'bold',
      fontSize: '14px',
      cursor: 'pointer',
      minWidth: '150px'
    },
    additionalFilters: {
      display: 'flex',
      gap: '15px'
    },
    filterSpan: {
      color: '#666',
      fontSize: '14px',
      cursor: 'pointer'
    },
    btnAgregar: {
      backgroundColor: '#00bcd4',
      color: 'white',
      border: 'none',
      padding: '12px 24px',
      borderRadius: '25px',
      fontWeight: 'bold',
      fontSize: '14px',
      cursor: 'pointer'
    },
    searchSection: {
      marginBottom: '20px'
    },
    searchContainer: {
      position: 'relative',
      maxWidth: '400px'
    },
    searchInput: {
      width: '100%',
      padding: '12px 15px 12px 45px',
      border: '1px solid #ddd',
      borderRadius: '25px',
      backgroundColor: 'white',
      color: '#333',
      fontSize: '14px',
      fontWeight: 'normal'
    },
    searchIcon: {
      position: 'absolute',
      left: '15px',
      top: '50%',
      transform: 'translateY(-50%)',
      color: '#666',
      fontSize: '16px'
    },
    tableContainer: {
      backgroundColor: 'white',
      borderRadius: '8px',
      boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
      overflow: 'hidden'
    },
    loadingIndicator: {
      textAlign: 'center',
      padding: '20px',
      color: '#666',
      fontStyle: 'italic'
    },
    errorContainer: {
      textAlign: 'center',
      padding: '40px 20px',
      backgroundColor: 'white',
      borderRadius: '8px',
      boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
      margin: '20px 0'
    },
    formGroup: {
      display: 'flex',
      flexDirection: 'column',
      gap: '8px',
      marginBottom: '15px'
    },
    formLabel: {
      fontWeight: 'bold',
      color: '#333',
      fontSize: '14px'
    },
    formInput: {
      padding: '12px',
      border: '1px solid #ddd',
      borderRadius: '4px',
      fontSize: '14px'
    },
    btnGuardar: {
      backgroundColor: '#6c757d',
      color: 'white',
      border: 'none',
      padding: '12px 30px',
      borderRadius: '4px',
      fontWeight: 'bold',
      fontSize: '14px',
      cursor: 'pointer',
      alignSelf: 'center'
    },
    // Estilos para paginación
    paginationContainer: {
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      gap: '10px',
      marginTop: '20px',
      padding: '20px'
    },
    paginationButton: {
      backgroundColor: '#00bcd4',
      color: 'white',
      border: 'none',
      padding: '8px 16px',
      borderRadius: '4px',
      cursor: 'pointer',
      fontSize: '14px'
    },
    paginationButtonDisabled: {
      backgroundColor: '#ccc',
      color: '#666',
      border: 'none',
      padding: '8px 16px',
      borderRadius: '4px',
      cursor: 'not-allowed',
      fontSize: '14px'
    },
    paginationInfo: {
      color: '#666',
      fontSize: '14px',
      margin: '0 15px'
    }
  };

  if (error) {
    return (
      <div style={styles.errorContainer}>
        <h3>Error</h3>
        <p>{error}</p>
        <button onClick={() => { fetchTiposServicio(); fetchServicios(); }}>
          Reintentar
        </button>
      </div>
    );
  }

  const serviciosPaginados = getPaginatedServicios();
  const paginationInfo = getPaginationInfo();

  return (
    <div style={styles.container}>
    
      <div style={styles.header}>
        <div style={styles.filterSection}>
          <select 
            style={styles.tipoFilter}
            value={selectedTipoFilter} 
            onChange={(e) => setSelectedTipoFilter(e.target.value)}
          >
            <option value="">IMÁGENES</option>
            {tiposServicio.map(tipo => (
              <option key={tipo.id_tipo_servicio} value={tipo.id_tipo_servicio}>
                {tipo.descripcion?.toUpperCase()}
              </option>
            ))}
          </select>
          
          <div style={styles.additionalFilters}>
            <span style={styles.filterSpan}>Laboratorio</span>
            <span style={styles.filterSpan}>Medicina Preventiva</span>
          </div>
        </div>

        <button 
          onClick={handleAdd} 
          style={styles.btnAgregar}
          disabled={loading}
        >
          AGREGAR +
        </button>
      </div>

   
      <div style={styles.searchSection}>
        <div style={styles.searchContainer}>
          <span style={styles.searchIcon}>🔍</span>
          <input
            type="text"
            placeholder="NOMBRE O CÓDIGO"
            style={styles.searchInput}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>


      {loading && (
        <div style={styles.loadingIndicator}>
          Cargando servicios...
        </div>
      )}

    
      <div style={styles.tableContainer}>
        <Table 
          columns={columns}
          data={serviciosPaginados}
          actions={actions}
          emptyMessage="No hay servicios registrados"
        />
      </div>

     
      {paginationInfo.totalPages > 1 && (
        <div style={styles.paginationContainer}>
          <button
            onClick={handlePrevPage}
            disabled={!paginationInfo.hasPrev}
            style={paginationInfo.hasPrev ? styles.paginationButton : styles.paginationButtonDisabled}
          >
            Anterior
          </button>
          
          <span style={styles.paginationInfo}>
            Página {paginationInfo.currentPage} de {paginationInfo.totalPages} 
            ({paginationInfo.totalItems} servicios)
          </span>
          
          <button
            onClick={handleNextPage}
            disabled={!paginationInfo.hasNext}
            style={paginationInfo.hasNext ? styles.paginationButton : styles.paginationButtonDisabled}
          >
            Siguiente
          </button>
        </div>
      )}

      <Modal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        title={modalType === 'add' ? 'AGREGAR' : 'EDITAR'}
      >
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
          <div style={styles.formGroup}>
            <label style={styles.formLabel}>Tipo de servicio</label>
            <select
              name="id_tipo_servicio"
              value={formData.id_tipo_servicio}
              onChange={handleInputChange}
              required
              disabled={loading}
              style={styles.formInput}
            >
              {modalType === 'add' && <option value="">elija un tipo</option>}
              {tiposServicio.map(tipo => (
                <option key={tipo.id_tipo_servicio} value={tipo.id_tipo_servicio}>
                  {tipo.descripcion}
                </option>
              ))}
            </select>
          </div>

          <div style={styles.formGroup}>
            <label style={styles.formLabel}>NOMBRES (*)</label>
            <input
              type="text"
              name="nombre_servicio"
              value={formData.nombre_servicio}
              onChange={handleInputChange}
              placeholder="RADIOGRAFIA"
              required
              disabled={loading}
              style={styles.formInput}
            />
          </div>

          <div style={styles.formGroup}>
            <label style={styles.formLabel}>PRECIO (*)</label>
            <input
              type="number"
              name="precio"
              value={formData.precio}
              onChange={handleInputChange}
              placeholder="S/..."
              step="0.01"
              min="0"
              required
              disabled={loading}
              style={styles.formInput}
            />
          </div>

          <div style={{ display: 'flex', justifyContent: 'center', marginTop: '20px' }}>
            <button 
              type="submit"
              disabled={loading}
              style={styles.btnGuardar}
            >
              {loading ? 'Guardando...' : 'GUARDAR'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default ServicesManagement; */
/*
// src/components/admin/ServicesManagement.jsx - CÓDIGO FINAL COMPLETO
import React, { useState, useEffect } from 'react';
import Table from '../common/Table';
import Modal from '../common/Modal';

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

  // URLs de la API - SIN barras finales
  const API_BASE = 'https://veterinariaclinicabackend-production.up.railway.app/api/v1/catalogos';
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
      const response = await fetch(TIPOS_SERVICIO_URL);
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      const data = await response.json();
      console.log('Tipos de servicio:', data);
      setTiposServicio(data.tipos_servicio || data || []);
    } catch (error) {
      console.error('Error al obtener tipos de servicio:', error);
      setError('Error al cargar tipos de servicio');
    }
  };

  // Obtener servicios
  const fetchServicios = async () => {
    setLoading(true);
    try {
      const response = await fetch(SERVICIOS_URL);
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      const data = await response.json();
      console.log('Servicios:', data);
      setServicios(data.servicios || data || []);
      setError(null);
    } catch (error) {
      console.error('Error al obtener servicios:', error);
      setError('Error al cargar servicios');
    } finally {
      setLoading(false);
    }
  };

  // Crear nuevo servicio
  const createServicio = async (servicioData) => {
    try {
      const response = await fetch(SERVICIOS_URL, {
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
      console.log('Servicio creado:', data);
      return { success: true, data };
    } catch (error) {
      console.error('Error creando servicio:', error);
      return { success: false, message: error.message };
    }
  };

  // Actualizar servicio
  const updateServicio = async (servicioId, servicioData) => {
    try {
      const response = await fetch(`${SERVICIOS_URL}/${servicioId}`, {
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
      console.log('Servicio actualizado:', data);
      return { success: true, data };
    } catch (error) {
      console.error('Error actualizando servicio:', error);
      return { success: false, message: error.message };
    }
  };

  // Eliminar servicio
  const deleteServicio = async (servicioId) => {
    try {
      const response = await fetch(`${SERVICIOS_URL}/${servicioId}`, {
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
  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
  };

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
    if (!window.confirm(`¿Está seguro de eliminar el servicio "${service.nombre_servicio}"?`)) {
      return;
    }

    const result = await deleteServicio(service.id_servicio);
    if (result.success) {
      alert('Servicio eliminado exitosamente');
      fetchServicios(); // Recargar lista
    } else {
      alert(`Error al eliminar: ${result.message}`);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Validaciones básicas
      if (!formData.nombre_servicio.trim()) {
        alert('El nombre del servicio es obligatorio');
        return;
      }

      if (!formData.precio || parseFloat(formData.precio) <= 0) {
        alert('El precio debe ser mayor a 0');
        return;
      }

      if (!formData.id_tipo_servicio) {
        alert('Debe seleccionar un tipo de servicio');
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
        alert(modalType === 'add' ? 'Servicio creado exitosamente' : 'Servicio actualizado exitosamente');
      } else {
        alert(`Error: ${result.message}`);
      }
    } catch (error) {
      console.error('Error en submit:', error);
      alert('Error al guardar servicio');
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
  const styles = {
    container: {
      padding: '20px',
      backgroundColor: '#f5f5f5',
      minHeight: '100vh'
    },
    header: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: '20px'
    },
    filterSection: {
      display: 'flex',
      alignItems: 'center',
      gap: '20px'
    },
    tipoFilter: {
      backgroundColor: '#e0e0e0',
      border: 'none',
      padding: '10px 15px',
      borderRadius: '4px',
      fontWeight: 'bold',
      fontSize: '14px',
      cursor: 'pointer',
      minWidth: '150px'
    },
    additionalFilters: {
      display: 'flex',
      gap: '15px'
    },
    filterSpan: {
      color: '#666',
      fontSize: '14px',
      cursor: 'pointer'
    },
    btnAgregar: {
      backgroundColor: '#00bcd4',
      color: 'white',
      border: 'none',
      padding: '12px 24px',
      borderRadius: '25px',
      fontWeight: 'bold',
      fontSize: '14px',
      cursor: 'pointer'
    },
    searchSection: {
      marginBottom: '20px'
    },
    searchContainer: {
      position: 'relative',
      maxWidth: '400px'
    },
    searchInput: {
      width: '100%',
      padding: '12px 15px 12px 45px',
      border: '1px solid #ddd',
      borderRadius: '25px',
      backgroundColor: 'white',
      color: '#333',
      fontSize: '14px',
      fontWeight: 'bold'
    },
    searchIcon: {
      position: 'absolute',
      left: '15px',
      top: '50%',
      transform: 'translateY(-50%)',
      color: '#666',
      fontSize: '16px'
    },
    tableContainer: {
      backgroundColor: 'white',
      borderRadius: '8px',
      boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
      overflow: 'hidden'
    },
    loadingIndicator: {
      textAlign: 'center',
      padding: '20px',
      color: '#666',
      fontStyle: 'italic'
    },
    errorContainer: {
      textAlign: 'center',
      padding: '40px 20px',
      backgroundColor: 'white',
      borderRadius: '8px',
      boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
      margin: '20px 0'
    },
    formGroup: {
      display: 'flex',
      flexDirection: 'column',
      gap: '8px',
      marginBottom: '15px'
    },
    formLabel: {
      fontWeight: 'bold',
      color: '#333',
      fontSize: '14px'
    },
    formInput: {
      padding: '12px',
      border: '1px solid #ddd',
      borderRadius: '4px',
      fontSize: '14px'
    },
    btnGuardar: {
      backgroundColor: '#6c757d',
      color: 'white',
      border: 'none',
      padding: '12px 30px',
      borderRadius: '4px',
      fontWeight: 'bold',
      fontSize: '14px',
      cursor: 'pointer',
      alignSelf: 'center'
    },
    // Estilos para paginación
    paginationContainer: {
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      gap: '10px',
      marginTop: '20px',
      padding: '20px'
    },
    paginationButton: {
      backgroundColor: '#00bcd4',
      color: 'white',
      border: 'none',
      padding: '8px 16px',
      borderRadius: '4px',
      cursor: 'pointer',
      fontSize: '14px'
    },
    paginationButtonDisabled: {
      backgroundColor: '#ccc',
      color: '#666',
      border: 'none',
      padding: '8px 16px',
      borderRadius: '4px',
      cursor: 'not-allowed',
      fontSize: '14px'
    },
    paginationInfo: {
      color: '#666',
      fontSize: '14px',
      margin: '0 15px'
    }
  };

  if (error) {
    return (
      <div style={styles.errorContainer}>
        <h3>Error</h3>
        <p>{error}</p>
        <button onClick={() => { fetchTiposServicio(); fetchServicios(); }}>
          Reintentar
        </button>
      </div>
    );
  }

  const serviciosPaginados = getPaginatedServicios();
  const paginationInfo = getPaginationInfo();

  return (
    <div style={styles.container}>
     
      <div style={styles.header}>
        <div style={styles.filterSection}>
          <select 
            style={styles.tipoFilter}
            value={selectedTipoFilter} 
            onChange={(e) => setSelectedTipoFilter(e.target.value)}
          >
            <option value="">TODOS</option>
            {tiposServicio.map(tipo => (
              <option key={tipo.id_tipo_servicio} value={tipo.id_tipo_servicio}>
                {tipo.descripcion?.toUpperCase()}
              </option>
            ))}
          </select>
          
          <div style={styles.additionalFilters}>
          </div>
        </div>

        <button 
          onClick={handleAdd} 
          style={styles.btnAgregar}
          disabled={loading}
        >
          AGREGAR +
        </button>
      </div>

 
      <div style={styles.searchSection}>
        <div style={styles.searchContainer}>
          <span style={styles.searchIcon}>🔍</span>
          <input
            type="text"
            placeholder="NOMBRE O CÓDIGO"
            style={styles.searchInput}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

    
      {loading && (
        <div style={styles.loadingIndicator}>
          Cargando servicios...
        </div>
      )}

    
      <div style={styles.tableContainer}>
        <Table 
          columns={columns}
          data={serviciosPaginados}
          actions={actions}
          emptyMessage="No hay servicios registrados"
        />
      </div>

   
      {paginationInfo.totalPages > 1 && (
        <div style={styles.paginationContainer}>
          <button
            onClick={handlePrevPage}
            disabled={!paginationInfo.hasPrev}
            style={paginationInfo.hasPrev ? styles.paginationButton : styles.paginationButtonDisabled}
          >
            Anterior
          </button>
          
          <span style={styles.paginationInfo}>
            Página {paginationInfo.currentPage} de {paginationInfo.totalPages} 
            ({paginationInfo.totalItems} servicios)
          </span>
          
          <button
            onClick={handleNextPage}
            disabled={!paginationInfo.hasNext}
            style={paginationInfo.hasNext ? styles.paginationButton : styles.paginationButtonDisabled}
          >
            Siguiente
          </button>
        </div>
      )}

  
      <Modal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        title={modalType === 'add' ? 'AGREGAR' : 'EDITAR'}
      >
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
          <div style={styles.formGroup}>
            <label style={styles.formLabel}>Tipo de servicio</label>
            <select
              name="id_tipo_servicio"
              value={formData.id_tipo_servicio}
              onChange={handleInputChange}
              required
              disabled={loading}
              style={styles.formInput}
            >
              {modalType === 'add' && <option value="">Elija un tipo</option>}
              {tiposServicio.map(tipo => (
                <option key={tipo.id_tipo_servicio} value={tipo.id_tipo_servicio}>
                  {tipo.descripcion}
                </option>
              ))}
            </select>
          </div>

          <div style={styles.formGroup}>
            <label style={styles.formLabel}>NOMBRES (*)</label>
            <input
              type="text"
              name="nombre_servicio"
              value={formData.nombre_servicio}
              onChange={handleInputChange}
              placeholder="Nombre del servicio"
              required
              disabled={loading}
              style={styles.formInput}
            />
          </div>

          <div style={styles.formGroup}>
            <label style={styles.formLabel}>PRECIO (*)</label>
            <input
              type="number"
              name="precio"
              value={formData.precio}
              onChange={handleInputChange}
              placeholder="S/..."
              step="0.01"
              min="0"
              required
              disabled={loading}
              style={styles.formInput}
            />
          </div>

          <div style={{ display: 'flex', justifyContent: 'center', marginTop: '20px' }}>
            <button 
              type="submit"
              disabled={loading}
              style={styles.btnGuardar}
            >
              {loading ? 'Guardando...' : 'GUARDAR'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default ServicesManagement; */