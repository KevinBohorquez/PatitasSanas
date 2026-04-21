import React, { useState, useEffect } from 'react';
import Table from '../common/Table';
import Modal from '../common/Modal';
import './MascotasManagement.css';

const MascotasManagement = () => {
  const [mascotas, setMascotas] = useState([]);
  const [filteredMascotas, setFilteredMascotas] = useState([]);
  const [clientes, setClientes] = useState([]);
  const [razas, setRazas] = useState([]);
  const [tiposAnimal, setTiposAnimal] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [modalType, setModalType] = useState('add'); 
  const [selectedMascota, setSelectedMascota] = useState(null);
  const [clienteDetails, setClienteDetails] = useState(null);
  
  // Estados para filtros
  const [searchTerm, setSearchTerm] = useState('');
  const [tipoFilter, setTipoFilter] = useState('todos');
  
  // Estados para validaciones
  const [validationErrors, setValidationErrors] = useState({});
  
  const [formData, setFormData] = useState({
    nombre: '',
    sexo: 'Macho',
    color: '',
    edad_anios: '',
    edad_meses: '',
    esterilizado: false,
    imagen: '',
    id_raza: '',
    id_cliente: '',
    tipo_animal: '' 
  });

  const BASE_URL = 'https://veterinariaclinicabackend-production.up.railway.app/api/v1';

  // Cargar datos 
  useEffect(() => {
    fetchMascotas();
    fetchClientes();
    fetchRazas();
    fetchTiposAnimal();
  }, []);

  // Aplicar filtros
  useEffect(() => {
    applyFilters();
  }, [mascotas, searchTerm, tipoFilter]);

  const applyFilters = () => {
    let filtered = [...mascotas];

    if (searchTerm.trim()) {
      const term = searchTerm.toLowerCase().trim();
      filtered = filtered.filter(mascota => {
        const nombreMascota = mascota.nombre?.toLowerCase() || '';
        const nombreDueño = `${mascota.cliente?.nombre || ''}`.toLowerCase();
        
        return nombreMascota.includes(term) || nombreDueño.includes(term);
      });
    }

    // Filtro por tipo de animal
    if (tipoFilter !== 'todos') {
      filtered = filtered.filter(mascota => {
        const tipoAnimal = tiposAnimal.find(t => t.id_raza === mascota.id_raza);
        if (!tipoAnimal) return false;
        
        if (tipoFilter === 'perros') {
          return tipoAnimal.descripcion === 'Perro';
        } else if (tipoFilter === 'gatos') {
          return tipoAnimal.descripcion === 'Gato';
        }
        return true;
      });
    }

    setFilteredMascotas(filtered);
  };

  // Obtener todas las mascotas
  const fetchMascotas = async () => {
    setLoading(true);
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
        setMascotas(data.mascotas || data || []);
      } else {
        const errorData = await response.json().catch(() => ({}));
        console.error('Error al cargar mascotas:', response.status, errorData);
        
        if (response.status === 404) {
          setMascotas([]);
        } else {
          alert(`Error al cargar las mascotas: ${errorData.detail || response.statusText}`);
        }
      }
    } catch (error) {
      console.error('Error de conexión:', error);
      alert('Error de conexión al cargar mascotas. Verifique su conexión a internet.');
      setMascotas([]);
    } finally {
      setLoading(false);
    }
  };

  // Obtener todos los clientes
  const fetchClientes = async () => {
    try {
      const response = await fetch(`${BASE_URL}/clientes/`, {
        method: 'GET',
        mode: 'cors',
        headers: {
          'Accept': 'application/json',
        },
      });
      if (response.ok) {
        const data = await response.json();
        setClientes(data.clientes || data || []);
      } else {
        console.error('Error al cargar clientes:', response.status);
        setClientes([]);
      }
    } catch (error) {
      console.error('Error al cargar clientes:', error);
      setClientes([]);
    }
  };

  // Obtener todas las razas
  const fetchRazas = async () => {
    try {
      const response = await fetch(`${BASE_URL}/catalogos/razas/`, {
        method: 'GET',
        mode: 'cors',
        headers: {
          'Accept': 'application/json',
        },
      });
      if (response.ok) {
        const data = await response.json();
        console.log('Razas cargadas:', data); 
        setRazas(data || []);
      } else {
        console.error('Error al cargar razas:', response.status);
        setRazas([]);
      }
    } catch (error) {
      console.error('Error al cargar razas:', error);
      setRazas([]);
    }
  };

  // Obtener todos los tipos de animal
  const fetchTiposAnimal = async () => {
    try {
      const response = await fetch(`${BASE_URL}/catalogos/tipos-animal/`, {
        method: 'GET',
        mode: 'cors',
        headers: {
          'Accept': 'application/json',
        },
      });
      if (response.ok) {
        const data = await response.json();
        setTiposAnimal(data || []);
      } else {
        console.error('Error al cargar tipos de animal:', response.status);
        setTiposAnimal([]);
      }
    } catch (error) {
      console.error('Error al cargar tipos de animal:', error);
      setTiposAnimal([]);
    }
  };

  // Obtener detalles del cliente de una mascota
  const fetchClienteDetails = async (clienteId) => {
    try {
      const response = await fetch(`${BASE_URL}/clientes/${clienteId}`, {
        method: 'GET',
        mode: 'cors',
        headers: {
          'Accept': 'application/json',
        },
      });
      if (response.ok) {
        const data = await response.json();
        setClienteDetails(data);
      }
    } catch (error) {
      console.error('Error al cargar detalles del cliente:', error);
      setClienteDetails(null);
    }
  };

  const handleAdd = () => {
    setModalType('add');
    setFormData({
      nombre: '',
      sexo: 'Macho',
      color: '',
      edad_anios: '',
      edad_meses: '',
      esterilizado: false,
      imagen: '',
      id_raza: '',
      id_cliente: '',
      tipo_animal: ''
    });
    setValidationErrors({});
    setClienteDetails(null);
    setShowModal(true);
  };

  // Editar información de la mascota
  const handleEdit = async (mascota) => {
    setModalType('edit');
    setSelectedMascota(mascota);
    
    // Encontrar el tipo de animal de la mascota
    const tipoAnimal = tiposAnimal.find(t => t.id_raza === mascota.id_raza);
    
    setFormData({
      nombre: mascota.nombre || '',
      sexo: mascota.sexo || 'Macho',
      color: mascota.color || '',
      edad_anios: mascota.edad_anios || '',
      edad_meses: mascota.edad_meses || '',
      esterilizado: mascota.esterilizado || false,
      imagen: mascota.imagen || '',
      id_raza: mascota.id_raza || '',
      id_cliente: mascota.cliente?.id_cliente || '',
      tipo_animal: tipoAnimal?.descripcion || ''
    });
    setValidationErrors({});
    if (mascota.cliente?.id_cliente) {
      await fetchClienteDetails(mascota.cliente.id_cliente);
    }
    setShowModal(true);
  };

  // Ver información de mascota
  const handleView = async (mascota) => {
    setModalType('view');
    setSelectedMascota(mascota);
    if (mascota.cliente?.id_cliente) {
      await fetchClienteDetails(mascota.cliente.id_cliente);
    }
    setShowModal(true);
  };

  // Eliminar mascota
  const handleDelete = async (mascota) => {
    if (window.confirm(`¿Está seguro de eliminar a la mascota ${mascota.nombre}?`)) {
      setLoading(true);
      try {
        const response = await fetch(`${BASE_URL}/mascotas/${mascota.id_mascota}`, {
          method: 'DELETE',
          mode: 'cors',
          headers: {
            'Accept': 'application/json',
          },
        });
        
        if (response.ok) {
          alert('Mascota eliminada exitosamente');
          fetchMascotas(); // Recargar la lista
        } else {
          const errorData = await response.json();
          alert(`Error al eliminar mascota: ${errorData.detail || 'Error desconocido'}`);
        }
      } catch (error) {
        console.error('Error:', error);
        alert('Error de conexión al eliminar mascota');
      } finally {
        setLoading(false);
      }
    }
  };

  // Validaciones
  const validateForm = () => {
    const errors = {};

    if (!formData.nombre.trim()) {
      errors.nombre = 'El nombre es obligatorio';
    } else if (formData.nombre.trim().length < 2) {
      errors.nombre = 'El nombre debe tener al menos 2 caracteres';
    }

    if (!formData.id_cliente) {
      errors.id_cliente = 'Debe seleccionar un dueño';
    }

    if (!formData.color.trim()) {
      errors.color = 'El color es obligatorio';
    }

    if (!formData.tipo_animal) {
      errors.tipo_animal = 'Debe seleccionar el tipo de animal';
    }

    if (!formData.id_raza) {
      errors.id_raza = 'Debe seleccionar una raza';
    }

    if (formData.edad_anios && (isNaN(formData.edad_anios) || formData.edad_anios < 0 || formData.edad_anios > 30)) {
      errors.edad_anios = 'La edad en años debe ser un número válido entre 0 y 30';
    }

    if (formData.edad_meses && (isNaN(formData.edad_meses) || formData.edad_meses < 0 || formData.edad_meses > 11)) {
      errors.edad_meses = 'Los meses deben estar entre 0 y 11';
    }

    if (formData.imagen && formData.imagen.trim() && !isValidUrl(formData.imagen)) {
      errors.imagen = 'Debe ser una URL válida';
    }

    // Validar correspondencia de raza
    if (formData.tipo_animal && formData.id_raza) {
      const tipoAnimalObj = tiposAnimal.find(t => 
        t.descripcion === formData.tipo_animal && 
        t.id_raza === parseInt(formData.id_raza)
      );
      
      if (!tipoAnimalObj) {
        errors.id_raza = 'La raza seleccionada no corresponde al tipo de animal';
      }
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const isValidUrl = (string) => {
    try {
      const url = new URL(string);
      if (!['http:', 'https:'].includes(url.protocol)) {
        return false;
      }
      const validExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'];
      const pathname = url.pathname.toLowerCase();
      const hasValidExtension = validExtensions.some(ext => pathname.includes(ext));
      const validImageHosts = ['i.ibb.co', 'imgur.com', 'i.imgur.com', 'images.unsplash.com', 'picsum.photos'];
      const isValidHost = validImageHosts.some(host => url.hostname.includes(host));
      
      return hasValidExtension || isValidHost;
    } catch (_) {
      return false;
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      // Encontrar el tipo de animal seleccionado
      const tipoAnimalObj = tiposAnimal.find(t => 
        t.descripcion === formData.tipo_animal && 
        t.id_raza === parseInt(formData.id_raza)
      );

      if (!tipoAnimalObj) {
        alert('Error: No se encontró el tipo de animal correspondiente');
        setLoading(false);
        return;
      }

      // Intentar sin imagen si hay URL 
      let mascotaData = {
        nombre: formData.nombre.trim(),
        sexo: formData.sexo,
        color: formData.color.trim(),
        edad_anios: parseInt(formData.edad_anios) || 0,
        edad_meses: parseInt(formData.edad_meses) || 0,
        esterilizado: Boolean(formData.esterilizado),
        imagen: null, // Primero null
        id_raza: parseInt(formData.id_raza)
      };

      // Agregar campos adicionales
      console.log('Iniciando proceso de creación de mascota...');

      const url = modalType === 'add' 
        ? `${BASE_URL}/mascotas/?cliente_id=${formData.id_cliente}`
        : `${BASE_URL}/mascotas/${selectedMascota.id_mascota}?cliente_id=${formData.id_cliente}`;
      
      const method = modalType === 'add' ? 'POST' : 'PUT';

      console.log('URL:', url, 'Method:', method);

      // Petición sin imagen
      console.log('Registrando mascota...');

      let response = await fetch(url, {
        method: method,
        mode: 'cors',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(mascotaData)
      });

      let responseData = await response.json();
      console.log('Estado de registro:', response.status === 201 ? 'Éxito' : 'Error');

      if (response.ok) {
        if (formData.imagen && formData.imagen.trim()) {
          try {
            console.log('Intentando agregar imagen...');
            mascotaData.imagen = formData.imagen.trim();
            
            const updateUrl = modalType === 'add' 
              ? `${BASE_URL}/mascotas/${responseData.id_mascota}?cliente_id=${formData.id_cliente}`
              : url;
            
            const imageResponse = await fetch(updateUrl, {
              method: 'PUT',
              mode: 'cors',
              headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
              },
              body: JSON.stringify(mascotaData)
            });

            const imageResponseData = await imageResponse.json();
            console.log('Estado de imagen:', imageResponse.status === 200 ? 'Agregada' : 'Error');

            if (imageResponse.ok) {
              alert(`Mascota ${modalType === 'add' ? 'registrada' : 'actualizada'} exitosamente con imagen`);
            } else {
              alert(`Mascota ${modalType === 'add' ? 'registrada' : 'actualizada'} exitosamente, pero hubo un problema con la imagen. Error: ${imageResponseData.detail || 'Error desconocido'}`);
            }
          } catch (imageError) {
            console.error('Error al agregar imagen:', imageError);
            alert(`Mascota ${modalType === 'add' ? 'registrada' : 'actualizada'} exitosamente, pero no se pudo agregar la imagen debido a problemas de conexión.`);
          }
        } else {
          alert(`Mascota ${modalType === 'add' ? 'registrada' : 'actualizada'} exitosamente`);
        }
        setShowModal(false);
        fetchMascotas(); 
      } else {
        console.error('Error del servidor');
        alert(`Error: ${responseData.detail || 'Error desconocido al procesar la solicitud'}`);
      }
    } catch (error) {
      console.error('Error de conexión');
      alert(`Error de conexión: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    if (name === 'tipo_animal') {
      setFormData(prev => ({
        ...prev,
        [name]: value,
        id_raza: '' 
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: type === 'checkbox' ? checked : value
      }));
    }
    
    if (validationErrors[name]) {
      setValidationErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  // Función para obtener las razas filtradas
  const getRazasByTipo = () => {
    if (!formData.tipo_animal) return [];
    
    return tiposAnimal
      .filter(tipo => tipo.descripcion === formData.tipo_animal)
      .map(tipo => {
        const raza = razas.find(r => r.id_raza === tipo.id_raza);
        return raza;
      })
      .filter(raza => raza !== undefined);
  };

  const clearFilters = () => {
    setSearchTerm('');
    setTipoFilter('todos');
  };

  const columns = [
    { key: 'nombre', header: 'NOMBRE' },
    { 
      key: 'cliente', 
      header: 'DUEÑO',
      render: (mascota) => mascota.cliente?.nombre || 'Sin dueño'
    },
    { key: 'sexo', header: 'SEXO' },
    { 
      key: 'tipo_animal', 
      header: 'TIPO',
      render: (mascota) => {
        const tipoAnimal = tiposAnimal.find(t => t.id_raza === mascota.id_raza);
        return tipoAnimal?.descripcion || 'Sin tipo';
      }
    },
    { 
      key: 'raza', 
      header: 'RAZA',
      render: (mascota) => {
        const raza = razas.find(r => r.id_raza === mascota.id_raza);
        return raza?.nombre_raza || 'Sin raza';
      }
    },
    { key: 'color', header: 'COLOR' },
    { 
      key: 'edad', 
      header: 'EDAD',
      render: (mascota) => {
        const años = mascota.edad_anios || 0;
        const meses = mascota.edad_meses || 0;
        return `${años}a ${meses}m`;
      }
    }
  ];

  const actions = [
    { 
      label: <img src="https://i.ibb.co/1YfTT2c1/Icono-Ver-Comprimida.png" alt="Ver" className="action-icon" />, 
      type: 'view', 
      onClick: handleView,
      title: 'Ver información'
    },
    { 
      label: <img src="https://i.ibb.co/8nRGkFKS/Icono-Editar-Comprimida.png" alt="Editar" className="action-icon" />, 
      type: 'edit', 
      onClick: handleEdit,
      title: 'Editar mascota'
    },
    { 
      label: <img src="https://i.ibb.co/LdbzttTC/Icono-Eliminar-Comprimida.png" alt="Eliminar" className="action-icon" />, 
      type: 'delete', 
      onClick: handleDelete,
      title: 'Eliminar mascota'
    }
  ];

  if (loading && mascotas.length === 0) {
    return (
      <div className="loading-container">
        <p>Cargando mascotas...</p>
      </div>
    );
  }

  return (
    <div className="mascotas-management">
      <div className="section-header">
        <h2>SECCIÓN MASCOTAS 🐶🐱</h2>
        <button onClick={handleAdd} className="btn-add" disabled={loading}>
          + Añadir Mascota
        </button>
      </div>

      <div className="mascotas-table-section">
        <div className="table-header">
          <h3>MASCOTAS REGISTRADAS</h3>
          <div className="filters-container">
            <div className="search-container">
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Buscar por nombre de mascota o dueño..."
                className="search-input"
              />
              <button className="search-btn">
                <img src="https://i.ibb.co/3mvthkJT/Icono-Buscar-Comprimida.png" alt="search" className="search-icon" />
              </button>
            </div>
            <div className="filter-container">
              <select 
                value={tipoFilter} 
                onChange={(e) => setTipoFilter(e.target.value)}
                className="filter-select"
              >
                <option value="todos">Todos</option>
                <option value="perros">Perros</option>
                <option value="gatos">Gatos</option>
              </select>
            </div>
            {(searchTerm || tipoFilter !== 'todos') && (
              <button onClick={clearFilters} className="clear-filters-btn">
                Limpiar filtros
              </button>
            )}
          </div>
        </div>

        {(searchTerm || tipoFilter !== 'todos') && (
          <div className="results-info">
            <span>
              {filteredMascotas.length} de {mascotas.length} mascotas 
              {searchTerm && ` que coinciden con "${searchTerm}"`}
              {tipoFilter !== 'todos' && ` (filtrado por ${tipoFilter})`}
            </span>
          </div>
        )}

        <Table 
          columns={columns}
          data={filteredMascotas}
          actions={actions}
          emptyMessage="No hay mascotas registradas"
        />
      </div>

      <Modal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        title={
          modalType === 'add' ? 'Nueva Mascota' : 
          modalType === 'edit' ? 'Editar Mascota' : 
          'Información de la Mascota'
        }
        size="large"
      >
        {modalType === 'view' ? (
          <div className="mascota-view">
            <div className="form-section">
              <h3>DATOS GENERALES DE LA MASCOTA</h3>
              <div className="info-grid">
                <div><strong>NOMBRE:</strong> {selectedMascota?.nombre}</div>
                <div><strong>SEXO:</strong> {selectedMascota?.sexo}</div>
                <div><strong>COLOR:</strong> {selectedMascota?.color}</div>
                <div><strong>EDAD:</strong> {selectedMascota?.edad_anios || 0} años, {selectedMascota?.edad_meses || 0} meses</div>
                <div><strong>ESTERILIZADO:</strong> {selectedMascota?.esterilizado ? 'Sí' : 'No'}</div>
                <div><strong>TIPO:</strong> {tiposAnimal.find(t => t.id_raza === selectedMascota?.id_raza)?.descripcion || 'Sin tipo'}</div>
                <div className="full-width">
                  <strong>RAZA:</strong> {razas.find(r => r.id_raza === selectedMascota?.id_raza)?.nombre_raza || 'Sin raza'}
                </div>
              </div>

              {selectedMascota?.imagen && (
                <div className="form-section">
                  <h3>FOTO DE LA MASCOTA</h3>
                  <div className="mascota-image-container">
                    <img 
                      src={selectedMascota.imagen} 
                      alt={`Foto de ${selectedMascota.nombre}`}
                      className="mascota-image"
                      onError={(e) => {
                        e.target.style.display = 'none';
                      }}
                    />
                  </div>
                </div>
              )}

              {clienteDetails && (
                <div className="form-section">
                  <h3>INFORMACIÓN DEL DUEÑO</h3>
                  <div className="info-grid">
                    <div><strong>NOMBRE:</strong> {clienteDetails.nombre}</div>
                    <div><strong>APELLIDOS:</strong> {clienteDetails.apellido_paterno} {clienteDetails.apellido_materno}</div>
                    <div><strong>DNI:</strong> {clienteDetails.dni}</div>
                    <div><strong>TELÉFONO:</strong> {clienteDetails.telefono}</div>
                    <div><strong>EMAIL:</strong> {clienteDetails.email}</div>
                    <div className="full-width"><strong>DIRECCIÓN:</strong> {clienteDetails.direccion}</div>
                  </div>
                </div>
              )}
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="mascota-form">
            <div className="form-section">
              <h3>DATOS GENERALES DE LA MASCOTA</h3>
              <div className="form-row">
                <div className="form-group">
                  <label>NOMBRE (*)</label>
                  <input
                    type="text"
                    name="nombre"
                    value={formData.nombre}
                    onChange={handleInputChange}
                    placeholder="Nombre de la mascota"
                    className={validationErrors.nombre ? 'error' : ''}
                    required
                  />
                  {validationErrors.nombre && (
                    <span className="error-message">{validationErrors.nombre}</span>
                  )}
                </div>
                <div className="form-group">
                  <label>DUEÑO (*)</label>
                  <select
                    name="id_cliente"
                    value={formData.id_cliente}
                    onChange={handleInputChange}
                    className={validationErrors.id_cliente ? 'error' : ''}
                    required
                  >
                    <option value="">Seleccionar dueño</option>
                    {clientes.map(cliente => (
                      <option key={cliente.id_cliente} value={cliente.id_cliente}>
                        {cliente.nombre} {cliente.apellido_paterno} - {cliente.dni}
                      </option>
                    ))}
                  </select>
                  {validationErrors.id_cliente && (
                    <span className="error-message">{validationErrors.id_cliente}</span>
                  )}
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>SEXO (*)</label>
                  <select
                    name="sexo"
                    value={formData.sexo}
                    onChange={handleInputChange}
                    required
                  >
                    <option value="Macho">Macho</option>
                    <option value="Hembra">Hembra</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>COLOR (*)</label>
                  <input
                    type="text"
                    name="color"
                    value={formData.color}
                    onChange={handleInputChange}
                    placeholder="Color del peludo"
                    className={validationErrors.color ? 'error' : ''}
                    required
                  />
                  {validationErrors.color && (
                    <span className="error-message">{validationErrors.color}</span>
                  )}
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>EDAD - AÑOS</label>
                  <input
                    type="number"
                    name="edad_anios"
                    value={formData.edad_anios}
                    onChange={handleInputChange}
                    placeholder="Años"
                    min="0"
                    className={validationErrors.edad_anios ? 'error' : ''}
                  />
                  {validationErrors.edad_anios && (
                    <span className="error-message">{validationErrors.edad_anios}</span>
                  )}
                </div>
                <div className="form-group">
                  <label>EDAD - MESES</label>
                  <input
                    type="number"
                    name="edad_meses"
                    value={formData.edad_meses}
                    onChange={handleInputChange}
                    placeholder="Meses"
                    min="0"
                    max="11"
                    className={validationErrors.edad_meses ? 'error' : ''}
                  />
                  {validationErrors.edad_meses && (
                    <span className="error-message">{validationErrors.edad_meses}</span>
                  )}
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>TIPO DE ANIMAL (*)</label>
                  <select
                    name="tipo_animal"
                    value={formData.tipo_animal}
                    onChange={handleInputChange}
                    className={validationErrors.tipo_animal ? 'error' : ''}
                    required
                  >
                    <option value="">Seleccionar tipo</option>
                    <option value="Perro">Perro</option>
                    <option value="Gato">Gato</option>
                  </select>
                  {validationErrors.tipo_animal && (
                    <span className="error-message">{validationErrors.tipo_animal}</span>
                  )}
                </div>
                <div className="form-group">
                  <label>RAZA (*)</label>
                  <select
                    name="id_raza"
                    value={formData.id_raza}
                    onChange={handleInputChange}
                    className={validationErrors.id_raza ? 'error' : ''}
                    required
                    disabled={!formData.tipo_animal}
                  >
                    <option value="">
                      {!formData.tipo_animal ? 'Primero selecciona el tipo' : 'Seleccionar raza'}
                    </option>
                    {getRazasByTipo().map(raza => (
                      <option key={raza.id_raza} value={raza.id_raza}>
                        {raza.nombre_raza}
                      </option>
                    ))}
                  </select>
                  {validationErrors.id_raza && (
                    <span className="error-message">{validationErrors.id_raza}</span>
                  )}
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>FOTO (URL - Opcional)</label>
                  <input
                    type="url"
                    name="imagen"
                    value={formData.imagen}
                    onChange={handleInputChange}
                    placeholder="https://ejemplo.com/foto.jpg"
                    className={validationErrors.imagen ? 'error' : ''}
                  />
                  {validationErrors.imagen && (
                    <span className="error-message">{validationErrors.imagen}</span>
                  )}
                </div>
                <div className="form-group">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      name="esterilizado"
                      checked={formData.esterilizado}
                      onChange={handleInputChange}
                    />
                    ESTERILIZADO
                  </label>
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
                {loading ? 'PROCESANDO...' : 'FINALIZAR REGISTRO'}
              </button>
            </div>
          </form>
        )}
      </Modal>
    </div>
  );
};

export default MascotasManagement;