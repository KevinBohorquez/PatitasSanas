// src/components/admin/ReceptionistManagement.jsx - CÓDIGO LIMPIO SIGUIENDO PATRÓN USERMANAGEMENT
import React, { useState, useEffect } from 'react';
import Table from '../common/Table';
import Modal from '../common/Modal';
import './ReceptionistManagement.css';

const ReceptionistManagement = () => {
  const [recepcionistas, setRecepcionistas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [modalType, setModalType] = useState('add');
  const [selectedReceptionist, setSelectedReceptionist] = useState(null);
  const [submitLoading, setSubmitLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTurno, setSelectedTurno] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalRecords, setTotalRecords] = useState(0);

  // Estados para el formulario
  const [formData, setFormData] = useState({
    dni: '',
    nombre: '',
    apellido_paterno: '',
    apellido_materno: '',
    telefono: '',
    email: '',
    genero: 'F',
    turno: '',
    contraseña: '',
    username: ''
  });

  const [formErrors, setFormErrors] = useState({});

  // URL base de tu backend
  const BASE_URL = 'https://veterinariaclinicabackend-production.up.railway.app/api/v1';

  // Función para generar username automático
  const generateUsername = (nombre) => {
    if (!nombre.trim()) return '';
    const primerNombre = nombre.trim().split(' ')[0].toLowerCase();
    return `recep_${primerNombre}`;
  };

  // Función para crear usuario base
  const createUser = async (userData) => {
    try {
      const response = await fetch(`${BASE_URL}/usuarios/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || `Error: ${response.status}`);
      }

      const data = await response.json();
      console.log('Usuario creado:', data);
      return { success: true, data };
    } catch (error) {
      console.error('Error creando usuario:', error);
      return { success: false, message: error.message };
    }
  };

  // Función para crear recepcionista (requiere id_usuario)
  const createRecepcionista = async (recepData) => {
    try {
      const response = await fetch(`${BASE_URL}/recepcionistas/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(recepData)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || `Error: ${response.status}`);
      }

      const data = await response.json();
      console.log('Recepcionista creado:', data);
      return { success: true, data };
    } catch (error) {
      console.error('Error creando recepcionista:', error);
      return { success: false, message: error.message };
    }
  };

  // Función para crear recepcionista completo (usuario + perfil)
  const createRecepcionistaCompleto = async (formData) => {
    try {
      // PASO 1: Crear usuario
      console.log('🔸 Paso 1: Creando usuario...');
      const userData = {
        username: formData.username.trim(),
        contraseña: formData.contraseña.trim(),
        tipo_usuario: 'Recepcionista',
        estado: 'Activo'
      };

      const userResult = await createUser(userData);
      if (!userResult.success) {
        throw new Error(`Error creando usuario: ${userResult.message}`);
      }

      const userId = userResult.data.id_usuario;
      console.log('✅ Usuario creado con ID:', userId);

      // PASO 2: Crear recepcionista con el id_usuario
      console.log('🔸 Paso 2: Creando perfil de recepcionista...');
      const recepData = {
        id_usuario: userId, // ← Campo requerido
        dni: formData.dni.trim(),
        nombre: formData.nombre.trim(),
        apellido_paterno: formData.apellido_paterno.trim(),
        apellido_materno: formData.apellido_materno.trim() || null,
        telefono: formData.telefono.trim(),
        email: formData.email.trim(),
        genero: formData.genero,
        turno: formData.turno,
        fecha_ingreso: new Date().toISOString().split('T')[0]
      };

      const recepResult = await createRecepcionista(recepData);
      if (!recepResult.success) {
        // Si falla crear recepcionista, intentar limpiar el usuario creado
        console.warn('⚠️ Fallo crear recepcionista, pero usuario ya fue creado');
        throw new Error(`Error creando recepcionista: ${recepResult.message}`);
      }

      console.log('✅ Recepcionista creado exitosamente');
      return { success: true, data: recepResult.data };

    } catch (error) {
      console.error('❌ Error en proceso completo:', error);
      return { success: false, message: error.message };
    }
  };

  // Función para actualizar recepcionista
  const updateRecepcionista = async (recepId, recepData) => {
    try {
      const response = await fetch(`${BASE_URL}/recepcionistas/${recepId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(recepData)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || `Error: ${response.status}`);
      }

      const data = await response.json();
      console.log('Recepcionista actualizado:', data);
      return { success: true, data };
    } catch (error) {
      console.error('Error actualizando recepcionista:', error);
      return { success: false, message: error.message };
    }
  };

  // Función para actualizar usuario (username)
  const updateUser = async (userId, userData) => {
    try {
      const response = await fetch(`${BASE_URL}/usuarios/${userId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || `Error: ${response.status}`);
      }

      const data = await response.json();
      console.log('Usuario actualizado:', data);
      return { success: true, data };
    } catch (error) {
      console.error('Error actualizando usuario:', error);
      return { success: false, message: error.message };
    }
  };

  // Función para cambiar contraseña (usando endpoint de usuarios)
  const changePassword = async (userId, newPassword) => {
    try {
      const response = await fetch(`${BASE_URL}/usuarios/${userId}/reset-password`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          new_password: newPassword
        })
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || `Error: ${response.status}`);
      }

      const data = await response.json();
      console.log('Contraseña cambiada:', data);
      return { success: true, data };
    } catch (error) {
      console.error('Error cambiando contraseña:', error);
      return { success: false, message: error.message };
    }
  };

  // Función para desactivar usuario (soft delete)
  const deactivateUser = async (userId) => {
    try {
      const response = await fetch(`${BASE_URL}/usuarios/${userId}/deactivate`, {
        method: 'PATCH'
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || `Error: ${response.status}`);
      }

      return { success: true };
    } catch (error) {
      console.error('Error desactivando usuario:', error);
      return { success: false, message: error.message };
    }
  };

  // Función para obtener información de usuario
  const fetchUserInfo = async (userId) => {
    try {
      const response = await fetch(`${BASE_URL}/usuarios/${userId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      const userData = await response.json();
      return userData;
    } catch (error) {
      console.error('Error obteniendo información de usuario:', error);
      return null;
    }
  };

  // Función para obtener recepcionistas (SIGUIENDO PATRÓN USERMANAGEMENT)
  const fetchRecepcionistas = async (page = 1, turno = '', search = '') => {
    try {
      setLoading(true);
      setError(null);

      let url = `${BASE_URL}/recepcionistas/?page=${page}&per_page=10`;
      
      if (turno) {
        url += `&turno=${turno}`;
      }

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      let filteredData = data.recepcionistas || [];
      
      // Filtrar por término de búsqueda localmente
      if (search.trim()) {
        filteredData = filteredData.filter(recep => 
          recep.dni?.toString().includes(search) ||
          recep.nombre?.toLowerCase().includes(search.toLowerCase()) ||
          recep.apellido_paterno?.toLowerCase().includes(search.toLowerCase()) ||
          recep.apellido_materno?.toLowerCase().includes(search.toLowerCase())
        );
      }

      // Enriquecer con información de usuario
      const recepcionistasCompletos = await Promise.all(
        filteredData.map(async (recep) => {
          try {
            if (recep.id_usuario) {
              const userInfo = await fetchUserInfo(recep.id_usuario);
              return {
                ...recep,
                username: userInfo?.username || 'N/A',
                estado_usuario: userInfo?.estado || 'N/A'
              };
            }
            return {
              ...recep,
              username: 'N/A',
              estado_usuario: 'N/A'
            };
          } catch (error) {
            console.warn(`Error obteniendo info de usuario para recepcionista ${recep.id_recepcionista}:`, error);
            return {
              ...recep,
              username: 'N/A',
              estado_usuario: 'N/A'
            };
          }
        })
      );

      // Filtrar solo usuarios activos
      const recepcionistasActivos = recepcionistasCompletos.filter(
        rec => rec.estado_usuario === 'Activo' || rec.estado_usuario === 'N/A'
      );

      // Mapear los datos para que coincidan con la estructura esperada por Table
      const mappedRecepcionistas = recepcionistasActivos.map(recep => ({
        id: recep.id_recepcionista,
        id_usuario: recep.id_usuario,
        dni: recep.dni || 'Sin DNI',
        nombre: recep.nombre || 'Sin nombre',
        apellido_paterno: recep.apellido_paterno || 'Sin apellido',
        apellido_materno: recep.apellido_materno || 'Sin apellido',
        telefono: recep.telefono || 'Sin teléfono',
        email: recep.email || 'Sin email',
        genero: recep.genero,
        turno: recep.turno || 'Sin turno',
        fecha_ingreso: recep.fecha_ingreso,
        username: recep.username
      }));

      setRecepcionistas(mappedRecepcionistas);
      setTotalRecords(data.total || 0);
      setTotalPages(data.total_pages || 1);
      setCurrentPage(page);

    } catch (error) {
      console.error('Error al obtener recepcionistas:', error);
      setError(error.message);
      setRecepcionistas([]);
    } finally {
      setLoading(false);
    }
  };

  // Efectos
  useEffect(() => {
    fetchRecepcionistas();
  }, []);

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      fetchRecepcionistas(1, selectedTurno, searchTerm);
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchTerm, selectedTurno]);

  // Manejadores de eventos
  const handleAdd = () => {
    setModalType('add');
    setSelectedReceptionist(null);
    setFormData({
      dni: '',
      nombre: '',
      apellido_paterno: '',
      apellido_materno: '',
      telefono: '',
      email: '',
      genero: 'F',
      turno: '',
      contraseña: '',
      username: ''
    });
    setFormErrors({});
    setShowModal(true);
  };

  const handleEdit = (receptionist) => {
    setModalType('edit');
    setSelectedReceptionist(receptionist);
    setFormData({
      dni: receptionist.dni === 'Sin DNI' ? '' : receptionist.dni,
      nombre: receptionist.nombre === 'Sin nombre' ? '' : receptionist.nombre,
      apellido_paterno: receptionist.apellido_paterno === 'Sin apellido' ? '' : receptionist.apellido_paterno,
      apellido_materno: receptionist.apellido_materno === 'Sin apellido' ? '' : receptionist.apellido_materno,
      telefono: receptionist.telefono === 'Sin teléfono' ? '' : receptionist.telefono,
      email: receptionist.email === 'Sin email' ? '' : receptionist.email,
      genero: receptionist.genero || 'F',
      turno: receptionist.turno === 'Sin turno' ? '' : receptionist.turno,
      contraseña: '',
      username: receptionist.username === 'N/A' ? '' : receptionist.username
    });
    setFormErrors({});
    setShowModal(true);
  };

  const handleDelete = async (receptionist) => {
    if (!window.confirm(`¿Está seguro de eliminar al recepcionista "${receptionist.nombre}"? Esta acción desactivará su cuenta de usuario.`)) {
      return;
    }

    if (!receptionist.id_usuario) {
      alert('No se puede eliminar: no tiene usuario asociado');
      return;
    }

    setDeleteLoading(true);
    
    const result = await deactivateUser(receptionist.id_usuario);
    if (result.success) {
      alert('Recepcionista eliminado exitosamente (usuario desactivado)');
      fetchRecepcionistas(currentPage, selectedTurno, searchTerm);
    } else {
      alert(`Error al eliminar: ${result.message}`);
    }

    setDeleteLoading(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const errors = validateForm();
    if (Object.keys(errors).length > 0) {
      setFormErrors(errors);
      return;
    }

    setSubmitLoading(true);
    setFormErrors({});

    try {
      if (modalType === 'add') {
        // Crear nuevo recepcionista completo (usuario + perfil)
        const submitData = {
          dni: formData.dni.trim(),
          nombre: formData.nombre.trim(),
          apellido_paterno: formData.apellido_paterno.trim(),
          apellido_materno: formData.apellido_materno.trim(),
          telefono: formData.telefono.trim(),
          email: formData.email.trim(),
          genero: formData.genero,
          turno: formData.turno,
          username: formData.username.trim(),
          contraseña: formData.contraseña.trim()
        };

        const result = await createRecepcionistaCompleto(submitData);
        
        if (result.success) {
          setShowModal(false);
          fetchRecepcionistas(currentPage, selectedTurno, searchTerm);
          alert('Recepcionista creado exitosamente');
        } else {
          alert(`Error: ${result.message}`);
        }
      } else {
        // Actualizar recepcionista existente
        const updateData = {
          dni: formData.dni.trim(),
          nombre: formData.nombre.trim(),
          apellido_paterno: formData.apellido_paterno.trim(),
          apellido_materno: formData.apellido_materno.trim() || null,
          telefono: formData.telefono.trim(),
          email: formData.email.trim(),
          genero: formData.genero,
          turno: formData.turno
        };

        // Actualizar datos del perfil
        const result = await updateRecepcionista(selectedReceptionist.id, updateData);
        
        if (!result.success) {
          throw new Error(result.message);
        }

        let messages = ['Recepcionista actualizado exitosamente'];

        // Si se cambió el username, actualizarlo
        if (formData.username.trim() && formData.username.trim() !== selectedReceptionist.username && selectedReceptionist.id_usuario) {
          const userUpdateResult = await updateUser(selectedReceptionist.id_usuario, {
            username: formData.username.trim()
          });
          if (userUpdateResult.success) {
            messages.push('Username actualizado');
          } else {
            console.warn('No se pudo actualizar username:', userUpdateResult.message);
          }
        }

        // Si se proporcionó una nueva contraseña, cambiarla por separado
        if (formData.contraseña.trim() && selectedReceptionist.id_usuario) {
          const passwordResult = await changePassword(selectedReceptionist.id_usuario, formData.contraseña.trim());
          if (passwordResult.success) {
            messages.push('Contraseña actualizada');
          } else {
            console.warn('No se pudo actualizar contraseña:', passwordResult.message);
          }
        }

        alert(messages.join(', '));
        setShowModal(false);
        fetchRecepcionistas(currentPage, selectedTurno, searchTerm);
      }

    } catch (error) {
      console.error('Error en submit:', error);
      alert(`Error: ${error.message}`);
    } finally {
      setSubmitLoading(false);
    }
  };

  const validateForm = () => {
    const errors = {};
    
    if (!formData.dni.trim()) {
      errors.dni = 'El DNI es requerido';
    } else if (!/^\d{8}$/.test(formData.dni.trim())) {
      errors.dni = 'El DNI debe tener 8 dígitos';
    }
    
    if (!formData.nombre.trim()) {
      errors.nombre = 'El nombre es requerido';
    }
    
    if (!formData.apellido_paterno.trim()) {
      errors.apellido_paterno = 'El apellido paterno es requerido';
    }
    
    if (!formData.telefono.trim()) {
      errors.telefono = 'El teléfono es requerido';
    } else if (!/^\d{9}$/.test(formData.telefono.trim())) {
      errors.telefono = 'El teléfono debe tener 9 dígitos';
    }
    
    if (!formData.email.trim()) {
      errors.email = 'El email es requerido';
    } else if (!/\S+@\S+\.\S+/.test(formData.email.trim())) {
      errors.email = 'El email no tiene un formato válido';
    }

    if (!formData.turno) {
      errors.turno = 'El turno es requerido';
    }
    
    if (modalType === 'add' && !formData.contraseña.trim()) {
      errors.contraseña = 'La contraseña es requerida para nuevos usuarios';
    } else if (formData.contraseña.trim() && formData.contraseña.length < 3) {
      errors.contraseña = 'La contraseña debe tener al menos 3 caracteres';
    }
    
    return errors;
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => {
      const newData = {
        ...prev,
        [name]: value
      };
      
      // Auto-generar username cuando cambie el nombre (solo en modo agregar)
      if (name === 'nombre' && modalType === 'add') {
        newData.username = generateUsername(value);
      }
      
      return newData;
    });
    
    // Limpiar error del campo cuando el usuario empiece a escribir
    if (formErrors[name]) {
      setFormErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages) {
      fetchRecepcionistas(newPage, selectedTurno, searchTerm);
    }
  };

  const clearFilters = () => {
    setSearchTerm('');
    setSelectedTurno('');
    setCurrentPage(1);
    fetchRecepcionistas(1, '', '');
  };

  // Configuración de columnas y acciones
  const columns = [
  { key: 'id', header: 'ID' },
  { key: 'dni', header: 'DNI' },
  { key: 'nombre', header: 'NOMBRE' },
  { 
    key: 'apellidos', 
    header: 'APELLIDOS',
    render: (recep) => `${recep.apellido_paterno} ${recep.apellido_materno}`.trim()
  },
  { key: 'telefono', header: 'TELÉFONO' },
  { key: 'email', header: 'EMAIL' },
  { 
    key: 'genero', 
    header: 'GÉNERO',
    render: (recep) => recep.genero === 'M' ? 'Masculino' : recep.genero === 'F' ? 'Femenino' : 'N/A'
  },
  { key: 'turno', header: 'TURNO' }
];
const handleView = (receptionist) => {
  setModalType('view');
  setSelectedReceptionist(receptionist);
  setShowModal(true);
};

  const actions = [
  { label: '👁️', type: 'view', onClick: handleView },
  { label: '✏️', type: 'edit', onClick: handleEdit },
  { label: '🗑️', type: 'delete', onClick: handleDelete }
];

  if (loading && recepcionistas.length === 0) {
    return (
      
      <div className="receptionist-management">
        <div className="loading-container">
          <p>Cargando recepcionistas...</p>
        </div>
      </div>
    );
  }

  return (
    <>
    <style jsx>{`
      .receptionist-management table th {
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

    <div className="receptionist-management">
      {/* CABECERA PRINCIPAL */}
      <div className="section-header">
        <h2>GESTIÓN DE RECEPCIONISTAS</h2>
        <button onClick={handleAdd} className="btn-add">
          + AÑADIR RECEPCIONISTA
        </button>
      </div>

      {/* CONTENEDOR DE TABLA */}
      <div className="receptionist-table-section">
        {/* FILTROS */}
        <div className="table-header">
          <h3>LISTA DE RECEPCIONISTAS</h3>
          <div className="filters-container">
            <input
              type="text"
              placeholder="🔍 Buscar por DNI, nombre o apellidos..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
            <select 
              value={selectedTurno} 
              onChange={(e) => setSelectedTurno(e.target.value)}
              className="filter-select"
            >
              <option value="">Todos los turnos</option>
              <option value="Mañana">Mañana</option>
              <option value="Tarde">Tarde</option>
              <option value="Noche">Noche</option>
            </select>
            {(searchTerm || selectedTurno) && (
              <button onClick={clearFilters} className="clear-filters-btn">
                LIMPIAR
              </button>
            )}
          </div>
        </div>

        {/* INFO DE ESTADO */}
        <div className="results-info">
          <span>Total: {totalRecords} registros | Página {currentPage} de {totalPages} | Mostrando: {recepcionistas.length} registros</span>
          {deleteLoading && <span style={{color: 'red'}}>Eliminando...</span>}
        </div>

        {/* MENSAJE DE ERROR */}
        {error && (
          <div className="error-message">
            <p>Error: {error}</p>
            <button onClick={() => fetchRecepcionistas()} className="btn-retry">
              Reintentar
            </button>
          </div>
        )}

        {/* TABLA */}
        <Table 
          columns={columns}
          data={recepcionistas}
          actions={actions}
          emptyMessage={
            searchTerm || selectedTurno 
              ? "No se encontraron recepcionistas con los filtros aplicados"
              : "No hay recepcionistas registrados"
          }
        />

        {/* PAGINACIÓN */}
        {totalPages > 1 && (
          <div className="pagination">
            <button 
              className="pagination-btn"
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1}
            >
              ← Anterior
            </button>
            <span className="pagination-info">
              Página {currentPage} de {totalPages}
            </span>
            <button 
              className="pagination-btn"
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
            >
              Siguiente →
            </button>
          </div>
        )}
      </div>

      {/* MODAL */}
      <Modal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        title={
          modalType === 'add'
            ? 'AGREGAR RECEPCIONISTA'
            : modalType === 'edit'
            ? 'EDITAR RECEPCIONISTA'
            : 'DETALLES DEL RECEPCIONISTA'
        }
        size="large"
      >
        {modalType === 'view' ? (
          <div className="receptionist-view">
            <div className="form-section">
              <h3>Información Personal</h3>
              <div className="info-grid">
                <div><strong>ID:</strong> {selectedReceptionist?.id}</div>
                <div><strong>DNI:</strong> {selectedReceptionist?.dni}</div>
                <div><strong>Nombre:</strong> {selectedReceptionist?.nombre}</div>
                <div><strong>Apellido Paterno:</strong> {selectedReceptionist?.apellido_paterno}</div>
                <div><strong>Apellido Materno:</strong> {selectedReceptionist?.apellido_materno}</div>
                <div><strong>Género:</strong> {selectedReceptionist?.genero === 'M' ? 'Masculino' : 'Femenino'}</div>
                <div><strong>Teléfono:</strong> {selectedReceptionist?.telefono}</div>
                <div><strong>Email:</strong> {selectedReceptionist?.email}</div>
                <div><strong>Turno:</strong> {selectedReceptionist?.turno}</div>
                <div><strong>Username:</strong> {selectedReceptionist?.username}</div>
              </div>
            </div>
          </div>
  ) : (
        <form onSubmit={handleSubmit} className="modal-form">
          <div className="form-section">
            <h3>DATOS PERSONALES</h3>
            
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="dni">DNI (*)</label>
                <input
                  type="text"
                  id="dni"
                  name="dni"
                  value={formData.dni}
                  onChange={handleInputChange}
                  placeholder="DNI..."
                  maxLength="8"
                  className={formErrors.dni ? 'error' : ''}
                  disabled={modalType === 'edit'}
                />
                {formErrors.dni && <span className="error-message">{formErrors.dni}</span>}
              </div>
              
              <div className="form-group">
                <label htmlFor="nombre">NOMBRES (*)</label>
                <input
                  type="text"
                  id="nombre"
                  name="nombre"
                  value={formData.nombre}
                  onChange={handleInputChange}
                  placeholder="NOMBRES..."
                  className={formErrors.nombre ? 'error' : ''}
                />
                {formErrors.nombre && <span className="error-message">{formErrors.nombre}</span>}
              </div>
              
              <div className="form-group">
                <label htmlFor="genero">Género (*)</label>
                <select
                  id="genero"
                  name="genero"
                  value={formData.genero}
                  onChange={handleInputChange}
                  className={formErrors.genero ? 'error' : ''}
                >
                  <option value="F">F</option>
                  <option value="M">M</option>
                </select>
                {formErrors.genero && <span className="error-message">{formErrors.genero}</span>}
              </div>
            </div>
            
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="apellido_paterno">APELLIDO PATERNO (*)</label>
                <input
                  type="text"
                  id="apellido_paterno"
                  name="apellido_paterno"
                  value={formData.apellido_paterno}
                  onChange={handleInputChange}
                  placeholder="APELLIDOS..."
                  className={formErrors.apellido_paterno ? 'error' : ''}
                />
                {formErrors.apellido_paterno && <span className="error-message">{formErrors.apellido_paterno}</span>}
              </div>
              
              <div className="form-group">
                <label htmlFor="apellido_materno">APELLIDO MATERNO (*)</label>
                <input
                  type="text"
                  id="apellido_materno"
                  name="apellido_materno"
                  value={formData.apellido_materno}
                  onChange={handleInputChange}
                  placeholder="APELLIDOS..."
                  className={formErrors.apellido_materno ? 'error' : ''}
                />
                {formErrors.apellido_materno && <span className="error-message">{formErrors.apellido_materno}</span>}
              </div>
            </div>
            
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="telefono">TELÉFONO (*)</label>
                <input
                  type="text"
                  id="telefono"
                  name="telefono"
                  value={formData.telefono}
                  onChange={handleInputChange}
                  placeholder="999999999"
                  maxLength="9"
                  className={formErrors.telefono ? 'error' : ''}
                />
                {formErrors.telefono && <span className="error-message">{formErrors.telefono}</span>}
              </div>
              
              <div className="form-group">
                <label htmlFor="email">EMAIL (*)</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  placeholder="EXAMPLE@GMAIL.COM"
                  className={formErrors.email ? 'error' : ''}
                />
                {formErrors.email && <span className="error-message">{formErrors.email}</span>}
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="turno">TURNO (*)</label>
                <select
                  id="turno"
                  name="turno"
                  value={formData.turno}
                  onChange={handleInputChange}
                  className={formErrors.turno ? 'error' : ''}
                >
                  <option value="">Seleccione turno</option>
                  <option value="Mañana">Mañana</option>
                  <option value="Tarde">Tarde</option>
                  <option value="Noche">Noche</option>
                </select>
                {formErrors.turno && <span className="error-message">{formErrors.turno}</span>}
              </div>

              <div className="form-group">
                <label htmlFor="username">USERNAME {modalType === 'add' ? '(Auto-generado)' : '(Editable)'}</label>
                <input
                  type="text"
                  id="username"
                  name="username"
                  value={formData.username}
                  onChange={handleInputChange}
                  placeholder="USERNAME..."
                  className={formErrors.username ? 'error' : ''}
                  disabled={modalType === 'add'} // Solo auto-generado al crear
                />
                {formErrors.username && <span className="error-message">{formErrors.username}</span>}
              </div>
            </div>
            
            <div className="form-row">
              <div className="form-group full-width">
                <label htmlFor="contraseña">
                  CONTRASEÑA {modalType === 'add' ? '(*)' : '(Dejar vacío para mantener actual)'}
                </label>
                <input
                  type="password"
                  id="contraseña"
                  name="contraseña"
                  value={formData.contraseña}
                  onChange={handleInputChange}
                  placeholder="CONTRASEÑA"
                  className={formErrors.contraseña ? 'error' : ''}
                />
                {formErrors.contraseña && <span className="error-message">{formErrors.contraseña}</span>}
              </div>
            </div>
          </div>
          
          <div className="form-actions">
            <button 
              type="button" 
              onClick={() => setShowModal(false)}
              className="btn-cancel"
              disabled={submitLoading}
            >
              CANCELAR
            </button>
            <button 
              type="submit"
              className="btn-submit"
              disabled={submitLoading}
            >
              {submitLoading ? 'PROCESANDO...' : 'GUARDAR'}
            </button>
          </div>
        </form>
       )} 
      </Modal>
    </div>
    </>
  );
};

export default ReceptionistManagement;
/*import React, { useState, useEffect } from 'react';
import Table from '../common/Table';
import Modal from '../common/Modal';

const ReceptionistManagement = () => {
  const [recepcionistas, setRecepcionistas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [modalType, setModalType] = useState('add');
  const [selectedReceptionist, setSelectedReceptionist] = useState(null);
  const [submitLoading, setSubmitLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTurno, setSelectedTurno] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalRecords, setTotalRecords] = useState(0);

  // Estados para el formulario
  const [formData, setFormData] = useState({
    dni: '',
    nombre: '',
    apellido_paterno: '',
    apellido_materno: '',
    telefono: '',
    email: '',
    genero: 'F',
    turno: '',
    contraseña: '',
    username: ''
  });

  const [formErrors, setFormErrors] = useState({});

  // URL base de tu backend
  const BASE_URL = 'https://veterinariaclinicabackend-production.up.railway.app/api/v1';

  // Función para generar username automático
  const generateUsername = (nombre) => {
    if (!nombre.trim()) return '';
    const primerNombre = nombre.trim().split(' ')[0].toLowerCase();
    return `recep_${primerNombre}`;
  };

  // Función para crear usuario base
  const createUser = async (userData) => {
    try {
      const response = await fetch(`${BASE_URL}/usuarios/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || `Error: ${response.status}`);
      }

      const data = await response.json();
      console.log('Usuario creado:', data);
      return { success: true, data };
    } catch (error) {
      console.error('Error creando usuario:', error);
      return { success: false, message: error.message };
    }
  };

  // Función para crear recepcionista (requiere id_usuario)
  const createRecepcionista = async (recepData) => {
    try {
      const response = await fetch(`${BASE_URL}/recepcionistas/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(recepData)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || `Error: ${response.status}`);
      }

      const data = await response.json();
      console.log('Recepcionista creado:', data);
      return { success: true, data };
    } catch (error) {
      console.error('Error creando recepcionista:', error);
      return { success: false, message: error.message };
    }
  };

  // Función para crear recepcionista completo (usuario + perfil)
  const createRecepcionistaCompleto = async (formData) => {
    try {
      // PASO 1: Crear usuario
      console.log('🔸 Paso 1: Creando usuario...');
      const userData = {
        username: formData.username.trim(),
        contraseña: formData.contraseña.trim(),
        tipo_usuario: 'Recepcionista',
        estado: 'Activo'
      };

      const userResult = await createUser(userData);
      if (!userResult.success) {
        throw new Error(`Error creando usuario: ${userResult.message}`);
      }

      const userId = userResult.data.id_usuario;
      console.log('✅ Usuario creado con ID:', userId);

      // PASO 2: Crear recepcionista con el id_usuario
      console.log('🔸 Paso 2: Creando perfil de recepcionista...');
      const recepData = {
        id_usuario: userId, // ← Campo requerido
        dni: formData.dni.trim(),
        nombre: formData.nombre.trim(),
        apellido_paterno: formData.apellido_paterno.trim(),
        apellido_materno: formData.apellido_materno.trim() || null,
        telefono: formData.telefono.trim(),
        email: formData.email.trim(),
        genero: formData.genero,
        turno: formData.turno,
        fecha_ingreso: new Date().toISOString().split('T')[0]
      };

      const recepResult = await createRecepcionista(recepData);
      if (!recepResult.success) {
        // Si falla crear recepcionista, intentar limpiar el usuario creado
        console.warn('⚠️ Fallo crear recepcionista, pero usuario ya fue creado');
        throw new Error(`Error creando recepcionista: ${recepResult.message}`);
      }

      console.log('✅ Recepcionista creado exitosamente');
      return { success: true, data: recepResult.data };

    } catch (error) {
      console.error('❌ Error en proceso completo:', error);
      return { success: false, message: error.message };
    }
  };

  // Función para actualizar recepcionista
  const updateRecepcionista = async (recepId, recepData) => {
    try {
      const response = await fetch(`${BASE_URL}/recepcionistas/${recepId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(recepData)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || `Error: ${response.status}`);
      }

      const data = await response.json();
      console.log('Recepcionista actualizado:', data);
      return { success: true, data };
    } catch (error) {
      console.error('Error actualizando recepcionista:', error);
      return { success: false, message: error.message };
    }
  };

  // Función para actualizar usuario (username)
  const updateUser = async (userId, userData) => {
    try {
      const response = await fetch(`${BASE_URL}/usuarios/${userId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || `Error: ${response.status}`);
      }

      const data = await response.json();
      console.log('Usuario actualizado:', data);
      return { success: true, data };
    } catch (error) {
      console.error('Error actualizando usuario:', error);
      return { success: false, message: error.message };
    }
  };

  // Función para cambiar contraseña (usando endpoint de usuarios)
  const changePassword = async (userId, newPassword) => {
    try {
      const response = await fetch(`${BASE_URL}/usuarios/${userId}/reset-password`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          new_password: newPassword
        })
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || `Error: ${response.status}`);
      }

      const data = await response.json();
      console.log('Contraseña cambiada:', data);
      return { success: true, data };
    } catch (error) {
      console.error('Error cambiando contraseña:', error);
      return { success: false, message: error.message };
    }
  };

  // Función para desactivar usuario (soft delete)
  const deactivateUser = async (userId) => {
    try {
      const response = await fetch(`${BASE_URL}/usuarios/${userId}/deactivate`, {
        method: 'PATCH'
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || `Error: ${response.status}`);
      }

      return { success: true };
    } catch (error) {
      console.error('Error desactivando usuario:', error);
      return { success: false, message: error.message };
    }
  };

  // Función para obtener información de usuario
  const fetchUserInfo = async (userId) => {
    try {
      const response = await fetch(`${BASE_URL}/usuarios/${userId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      const userData = await response.json();
      return userData;
    } catch (error) {
      console.error('Error obteniendo información de usuario:', error);
      return null;
    }
  };

  // Función para obtener recepcionistas (SIGUIENDO PATRÓN USERMANAGEMENT)
  const fetchRecepcionistas = async (page = 1, turno = '', search = '') => {
    try {
      setLoading(true);
      setError(null);

      let url = `${BASE_URL}/recepcionistas/?page=${page}&per_page=10`;
      
      if (turno) {
        url += `&turno=${turno}`;
      }

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      let filteredData = data.recepcionistas || [];
      
      // Filtrar por término de búsqueda localmente
      if (search.trim()) {
        filteredData = filteredData.filter(recep => 
          recep.dni?.toString().includes(search) ||
          recep.nombre?.toLowerCase().includes(search.toLowerCase()) ||
          recep.apellido_paterno?.toLowerCase().includes(search.toLowerCase()) ||
          recep.apellido_materno?.toLowerCase().includes(search.toLowerCase())
        );
      }

      // Enriquecer con información de usuario
      const recepcionistasCompletos = await Promise.all(
        filteredData.map(async (recep) => {
          try {
            if (recep.id_usuario) {
              const userInfo = await fetchUserInfo(recep.id_usuario);
              return {
                ...recep,
                username: userInfo?.username || 'N/A',
                estado_usuario: userInfo?.estado || 'N/A'
              };
            }
            return {
              ...recep,
              username: 'N/A',
              estado_usuario: 'N/A'
            };
          } catch (error) {
            console.warn(`Error obteniendo info de usuario para recepcionista ${recep.id_recepcionista}:`, error);
            return {
              ...recep,
              username: 'N/A',
              estado_usuario: 'N/A'
            };
          }
        })
      );

      // Filtrar solo usuarios activos
      const recepcionistasActivos = recepcionistasCompletos.filter(
        rec => rec.estado_usuario === 'Activo' || rec.estado_usuario === 'N/A'
      );

      // Mapear los datos para que coincidan con la estructura esperada por Table
      const mappedRecepcionistas = recepcionistasActivos.map(recep => ({
        id: recep.id_recepcionista,
        id_usuario: recep.id_usuario,
        dni: recep.dni || 'Sin DNI',
        nombre: recep.nombre || 'Sin nombre',
        apellido_paterno: recep.apellido_paterno || 'Sin apellido',
        apellido_materno: recep.apellido_materno || 'Sin apellido',
        telefono: recep.telefono || 'Sin teléfono',
        email: recep.email || 'Sin email',
        genero: recep.genero,
        turno: recep.turno || 'Sin turno',
        fecha_ingreso: recep.fecha_ingreso,
        username: recep.username
      }));

      setRecepcionistas(mappedRecepcionistas);
      setTotalRecords(data.total || 0);
      setTotalPages(data.total_pages || 1);
      setCurrentPage(page);

    } catch (error) {
      console.error('Error al obtener recepcionistas:', error);
      setError(error.message);
      setRecepcionistas([]);
    } finally {
      setLoading(false);
    }
  };

  // Efectos
  useEffect(() => {
    fetchRecepcionistas();
  }, []);

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      fetchRecepcionistas(1, selectedTurno, searchTerm);
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchTerm, selectedTurno]);

  // Manejadores de eventos
  const handleAdd = () => {
    setModalType('add');
    setSelectedReceptionist(null);
    setFormData({
      dni: '',
      nombre: '',
      apellido_paterno: '',
      apellido_materno: '',
      telefono: '',
      email: '',
      genero: 'F',
      turno: '',
      contraseña: '',
      username: ''
    });
    setFormErrors({});
    setShowModal(true);
  };

  const handleEdit = (receptionist) => {
    setModalType('edit');
    setSelectedReceptionist(receptionist);
    setFormData({
      dni: receptionist.dni === 'Sin DNI' ? '' : receptionist.dni,
      nombre: receptionist.nombre === 'Sin nombre' ? '' : receptionist.nombre,
      apellido_paterno: receptionist.apellido_paterno === 'Sin apellido' ? '' : receptionist.apellido_paterno,
      apellido_materno: receptionist.apellido_materno === 'Sin apellido' ? '' : receptionist.apellido_materno,
      telefono: receptionist.telefono === 'Sin teléfono' ? '' : receptionist.telefono,
      email: receptionist.email === 'Sin email' ? '' : receptionist.email,
      genero: receptionist.genero || 'F',
      turno: receptionist.turno === 'Sin turno' ? '' : receptionist.turno,
      contraseña: '',
      username: receptionist.username === 'N/A' ? '' : receptionist.username
    });
    setFormErrors({});
    setShowModal(true);
  };

  const handleDelete = async (receptionist) => {
    if (!window.confirm(`¿Está seguro de eliminar al recepcionista "${receptionist.nombre}"? Esta acción desactivará su cuenta de usuario.`)) {
      return;
    }

    if (!receptionist.id_usuario) {
      alert('No se puede eliminar: no tiene usuario asociado');
      return;
    }

    setDeleteLoading(true);
    
    const result = await deactivateUser(receptionist.id_usuario);
    if (result.success) {
      alert('Recepcionista eliminado exitosamente (usuario desactivado)');
      fetchRecepcionistas(currentPage, selectedTurno, searchTerm);
    } else {
      alert(`Error al eliminar: ${result.message}`);
    }

    setDeleteLoading(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const errors = validateForm();
    if (Object.keys(errors).length > 0) {
      setFormErrors(errors);
      return;
    }

    setSubmitLoading(true);
    setFormErrors({});

    try {
      if (modalType === 'add') {
        // Crear nuevo recepcionista completo (usuario + perfil)
        const submitData = {
          dni: formData.dni.trim(),
          nombre: formData.nombre.trim(),
          apellido_paterno: formData.apellido_paterno.trim(),
          apellido_materno: formData.apellido_materno.trim(),
          telefono: formData.telefono.trim(),
          email: formData.email.trim(),
          genero: formData.genero,
          turno: formData.turno,
          username: formData.username.trim(),
          contraseña: formData.contraseña.trim()
        };

        const result = await createRecepcionistaCompleto(submitData);
        
        if (result.success) {
          setShowModal(false);
          fetchRecepcionistas(currentPage, selectedTurno, searchTerm);
          alert('Recepcionista creado exitosamente');
        } else {
          alert(`Error: ${result.message}`);
        }
      } else {
        // Actualizar recepcionista existente
        const updateData = {
          dni: formData.dni.trim(),
          nombre: formData.nombre.trim(),
          apellido_paterno: formData.apellido_paterno.trim(),
          apellido_materno: formData.apellido_materno.trim() || null,
          telefono: formData.telefono.trim(),
          email: formData.email.trim(),
          genero: formData.genero,
          turno: formData.turno
        };

        // Actualizar datos del perfil
        const result = await updateRecepcionista(selectedReceptionist.id, updateData);
        
        if (!result.success) {
          throw new Error(result.message);
        }

        let messages = ['Recepcionista actualizado exitosamente'];

        // Si se cambió el username, actualizarlo
        if (formData.username.trim() && formData.username.trim() !== selectedReceptionist.username && selectedReceptionist.id_usuario) {
          const userUpdateResult = await updateUser(selectedReceptionist.id_usuario, {
            username: formData.username.trim()
          });
          if (userUpdateResult.success) {
            messages.push('Username actualizado');
          } else {
            console.warn('No se pudo actualizar username:', userUpdateResult.message);
          }
        }

        // Si se proporcionó una nueva contraseña, cambiarla por separado
        if (formData.contraseña.trim() && selectedReceptionist.id_usuario) {
          const passwordResult = await changePassword(selectedReceptionist.id_usuario, formData.contraseña.trim());
          if (passwordResult.success) {
            messages.push('Contraseña actualizada');
          } else {
            console.warn('No se pudo actualizar contraseña:', passwordResult.message);
          }
        }

        alert(messages.join(', '));
        setShowModal(false);
        fetchRecepcionistas(currentPage, selectedTurno, searchTerm);
      }

    } catch (error) {
      console.error('Error en submit:', error);
      alert(`Error: ${error.message}`);
    } finally {
      setSubmitLoading(false);
    }
  };

  const validateForm = () => {
    const errors = {};
    
    if (!formData.dni.trim()) {
      errors.dni = 'El DNI es requerido';
    } else if (!/^\d{8}$/.test(formData.dni.trim())) {
      errors.dni = 'El DNI debe tener 8 dígitos';
    }
    
    if (!formData.nombre.trim()) {
      errors.nombre = 'El nombre es requerido';
    }
    
    if (!formData.apellido_paterno.trim()) {
      errors.apellido_paterno = 'El apellido paterno es requerido';
    }
    
    if (!formData.telefono.trim()) {
      errors.telefono = 'El teléfono es requerido';
    } else if (!/^\d{9}$/.test(formData.telefono.trim())) {
      errors.telefono = 'El teléfono debe tener 9 dígitos';
    }
    
    if (!formData.email.trim()) {
      errors.email = 'El email es requerido';
    } else if (!/\S+@\S+\.\S+/.test(formData.email.trim())) {
      errors.email = 'El email no tiene un formato válido';
    }

    if (!formData.turno) {
      errors.turno = 'El turno es requerido';
    }
    
    if (modalType === 'add' && !formData.contraseña.trim()) {
      errors.contraseña = 'La contraseña es requerida para nuevos usuarios';
    } else if (formData.contraseña.trim() && formData.contraseña.length < 3) {
      errors.contraseña = 'La contraseña debe tener al menos 3 caracteres';
    }
    
    return errors;
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => {
      const newData = {
        ...prev,
        [name]: value
      };
      
      // Auto-generar username cuando cambie el nombre (solo en modo agregar)
      if (name === 'nombre' && modalType === 'add') {
        newData.username = generateUsername(value);
      }
      
      return newData;
    });
    
    // Limpiar error del campo cuando el usuario empiece a escribir
    if (formErrors[name]) {
      setFormErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages) {
      fetchRecepcionistas(newPage, selectedTurno, searchTerm);
    }
  };

  const clearFilters = () => {
    setSearchTerm('');
    setSelectedTurno('');
    setCurrentPage(1);
    fetchRecepcionistas(1, '', '');
  };

  // Configuración de columnas y acciones
  const columns = [
    { key: 'id', header: 'ID' },
    { key: 'dni', header: 'DNI' },
    { key: 'nombre', header: 'NOMBRE' },
    { 
      key: 'apellidos', 
      header: 'APELLIDOS',
      render: (recep) => `${recep.apellido_paterno} ${recep.apellido_materno}`.trim()
    },
    { key: 'telefono', header: 'TELÉFONO' },
    { key: 'email', header: 'EMAIL' },
    { 
      key: 'genero', 
      header: 'GÉNERO',
      render: (recep) => recep.genero === 'M' ? 'Masculino' : recep.genero === 'F' ? 'Femenino' : 'N/A'
    },
    { key: 'turno', header: 'TURNO' },
    { key: 'username', header: 'USERNAME' },
    { 
      key: 'contraseña', 
      header: 'CONTRASEÑA',
      render: () => '••••••••'
    }
  ];

  const actions = [
    { label: '✏️', type: 'edit', onClick: handleEdit },
    { label: '🗑️', type: 'delete', onClick: handleDelete }
  ];

  if (loading && recepcionistas.length === 0) {
    return (
      <div className="receptionist-management">
        <div className="loading-container">
          <p>Cargando recepcionistas...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="receptionist-management">
      <div className="section-header">
        <div className="search-controls">
          <input
            type="text"
            placeholder="Buscar por DNI, nombre o apellidos..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          
          <select 
            value={selectedTurno} 
            onChange={(e) => setSelectedTurno(e.target.value)}
            className="filter-select"
          >
            <option value="">Todos los turnos</option>
            <option value="Mañana">Mañana</option>
            <option value="Tarde">Tarde</option>
            <option value="Noche">Noche</option>
          </select>

          {(searchTerm || selectedTurno) && (
            <button onClick={clearFilters} className="btn-clear">
              Limpiar
            </button>
          )}
        </div>
        
        <button onClick={handleAdd} className="btn-add">
          AGREGAR
        </button>
      </div>

      <div className="status-info">
        <span>Total: {totalRecords} registros</span>
        <span>Página {currentPage} de {totalPages}</span>
        <span>Mostrando: {recepcionistas.length} registros</span>
        {deleteLoading && <span style={{color: 'red'}}>Eliminando...</span>}
      </div>

      {error && (
        <div className="error-message">
          <p>Error: {error}</p>
          <button onClick={() => fetchRecepcionistas()} className="btn-retry">
            Reintentar
          </button>
        </div>
      )}

      <Table 
        columns={columns}
        data={recepcionistas}
        actions={actions}
        emptyMessage={
          searchTerm || selectedTurno 
            ? "No se encontraron recepcionistas con los filtros aplicados"
            : "No hay recepcionistas registrados"
        }
      />

      {totalPages > 1 && (
        <div className="pagination">
          <button 
            className="pagination-btn"
            onClick={() => handlePageChange(currentPage - 1)}
            disabled={currentPage === 1}
          >
            ← Anterior
          </button>
          
          <span className="pagination-info">
            Página {currentPage} de {totalPages}
          </span>
          
          <button 
            className="pagination-btn"
            onClick={() => handlePageChange(currentPage + 1)}
            disabled={currentPage === totalPages}
          >
            Siguiente →
          </button>
        </div>
      )}

      <Modal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        title={modalType === 'add' ? 'AGREGAR RECEPCIONISTA' : 'EDITAR RECEPCIONISTA'}
        size="large"
      >
        <form onSubmit={handleSubmit} className="modal-form">
          <div className="form-section">
            <h3>DATOS PERSONALES</h3>
            
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="dni">DNI (*)</label>
                <input
                  type="text"
                  id="dni"
                  name="dni"
                  value={formData.dni}
                  onChange={handleInputChange}
                  placeholder="DNI..."
                  maxLength="8"
                  className={formErrors.dni ? 'error' : ''}
                  disabled={modalType === 'edit'}
                />
                {formErrors.dni && <span className="error-message">{formErrors.dni}</span>}
              </div>
              
              <div className="form-group">
                <label htmlFor="nombre">NOMBRES (*)</label>
                <input
                  type="text"
                  id="nombre"
                  name="nombre"
                  value={formData.nombre}
                  onChange={handleInputChange}
                  placeholder="NOMBRES..."
                  className={formErrors.nombre ? 'error' : ''}
                />
                {formErrors.nombre && <span className="error-message">{formErrors.nombre}</span>}
              </div>
              
              <div className="form-group">
                <label htmlFor="genero">Género (*)</label>
                <select
                  id="genero"
                  name="genero"
                  value={formData.genero}
                  onChange={handleInputChange}
                  className={formErrors.genero ? 'error' : ''}
                >
                  <option value="F">F</option>
                  <option value="M">M</option>
                </select>
                {formErrors.genero && <span className="error-message">{formErrors.genero}</span>}
              </div>
            </div>
            
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="apellido_paterno">APELLIDO PATERNO (*)</label>
                <input
                  type="text"
                  id="apellido_paterno"
                  name="apellido_paterno"
                  value={formData.apellido_paterno}
                  onChange={handleInputChange}
                  placeholder="APELLIDOS..."
                  className={formErrors.apellido_paterno ? 'error' : ''}
                />
                {formErrors.apellido_paterno && <span className="error-message">{formErrors.apellido_paterno}</span>}
              </div>
              
              <div className="form-group">
                <label htmlFor="apellido_materno">APELLIDO MATERNO (*)</label>
                <input
                  type="text"
                  id="apellido_materno"
                  name="apellido_materno"
                  value={formData.apellido_materno}
                  onChange={handleInputChange}
                  placeholder="APELLIDOS..."
                  className={formErrors.apellido_materno ? 'error' : ''}
                />
                {formErrors.apellido_materno && <span className="error-message">{formErrors.apellido_materno}</span>}
              </div>
            </div>
            
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="telefono">TELÉFONO (*)</label>
                <input
                  type="text"
                  id="telefono"
                  name="telefono"
                  value={formData.telefono}
                  onChange={handleInputChange}
                  placeholder="999999999"
                  maxLength="9"
                  className={formErrors.telefono ? 'error' : ''}
                />
                {formErrors.telefono && <span className="error-message">{formErrors.telefono}</span>}
              </div>
              
              <div className="form-group">
                <label htmlFor="email">EMAIL (*)</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  placeholder="EXAMPLE@GMAIL.COM"
                  className={formErrors.email ? 'error' : ''}
                />
                {formErrors.email && <span className="error-message">{formErrors.email}</span>}
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="turno">TURNO (*)</label>
                <select
                  id="turno"
                  name="turno"
                  value={formData.turno}
                  onChange={handleInputChange}
                  className={formErrors.turno ? 'error' : ''}
                >
                  <option value="">Seleccione turno</option>
                  <option value="Mañana">Mañana</option>
                  <option value="Tarde">Tarde</option>
                  <option value="Noche">Noche</option>
                </select>
                {formErrors.turno && <span className="error-message">{formErrors.turno}</span>}
              </div>

              <div className="form-group">
                <label htmlFor="username">USERNAME {modalType === 'add' ? '(Auto-generado)' : '(Editable)'}</label>
                <input
                  type="text"
                  id="username"
                  name="username"
                  value={formData.username}
                  onChange={handleInputChange}
                  placeholder="USERNAME..."
                  className={formErrors.username ? 'error' : ''}
                  disabled={modalType === 'add'} // Solo auto-generado al crear
                />
                {formErrors.username && <span className="error-message">{formErrors.username}</span>}
              </div>
            </div>
            
            <div className="form-row">
              <div className="form-group full-width">
                <label htmlFor="contraseña">
                  CONTRASEÑA {modalType === 'add' ? '(*)' : '(Dejar vacío para mantener actual)'}
                </label>
                <input
                  type="password"
                  id="contraseña"
                  name="contraseña"
                  value={formData.contraseña}
                  onChange={handleInputChange}
                  placeholder="CONTRASEÑA"
                  className={formErrors.contraseña ? 'error' : ''}
                />
                {formErrors.contraseña && <span className="error-message">{formErrors.contraseña}</span>}
              </div>
            </div>
          </div>
          
          <div className="form-actions">
            <button 
              type="button" 
              onClick={() => setShowModal(false)}
              className="btn-cancel"
              disabled={submitLoading}
            >
              CANCELAR
            </button>
            <button 
              type="submit"
              className="btn-submit"
              disabled={submitLoading}
            >
              {submitLoading ? 'PROCESANDO...' : 'GUARDAR'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default ReceptionistManagement;*/
