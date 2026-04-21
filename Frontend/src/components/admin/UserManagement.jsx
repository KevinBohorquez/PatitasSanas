import React, { useState, useEffect } from 'react';
import Table from '../common/Table';
import Modal from '../common/Modal';
import './UserManagement.css';

const UserManagement = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [modalType, setModalType] = useState('add');
  const [selectedUser, setSelectedUser] = useState(null);
  const [submitLoading, setSubmitLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedGenero, setSelectedGenero] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalRecords, setTotalRecords] = useState(0);

  const [formData, setFormData] = useState({
    dni: '',
    nombre: '',
    apellido_paterno: '',
    apellido_materno: '',
    telefono: '',
    email: '',
    genero: 'M',
    contraseña: '',
    username: ''
  });

  const [formErrors, setFormErrors] = useState({});

  const BASE_URL = 'https://veterinariaclinicabackend-production.up.railway.app/api/v1';

  const generateUsername = (nombre) => {
    if (!nombre.trim()) return '';
    const primerNombre = nombre.trim().split(' ')[0].toLowerCase();
    return `admin_${primerNombre}`;
  };

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

  const createAdministrador = async (adminData) => {
    try {
      const response = await fetch(`${BASE_URL}/administradores/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(adminData)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || `Error: ${response.status}`);
      }

      const data = await response.json();
      console.log('Administrador creado:', data);
      return { success: true, data };
    } catch (error) {
      console.error('Error creando administrador:', error);
      return { success: false, message: error.message };
    }
  };

  const updateAdministrador = async (adminId, adminData) => {
    try {
      const response = await fetch(`${BASE_URL}/administradores/${adminId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(adminData)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || `Error: ${response.status}`);
      }

      const data = await response.json();
      console.log('Administrador actualizado:', data);
      return { success: true, data };
    } catch (error) {
      console.error('Error actualizando administrador:', error);
      return { success: false, message: error.message };
    }
  };

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
      return { success: true, data };
    } catch (error) {
      console.error('Error actualizando usuario:', error);
      return { success: false, message: error.message };
    }
  };

  const changePassword = async (adminId, newPassword) => {
    try {
      const response = await fetch(`${BASE_URL}/administradores/${adminId}/change-password`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          admin_id: adminId,
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

  const deleteAdministrador = async (adminId) => {
    try {
      const response = await fetch(`${BASE_URL}/administradores/${adminId}?permanent=false`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || `Error: ${response.status}`);
      }

      return { success: true };
    } catch (error) {
      console.error('Error eliminando administrador:', error);
      return { success: false, message: error.message };
    }
  };

  const fetchAdministradores = async (page = 1, genero = '', search = '') => {
    try {
      setLoading(true);
      setError(null);

      let url = `${BASE_URL}/administradores/?page=${page}&per_page=10&activos_solo=true`;
      
      if (genero) {
        url += `&genero=${genero}`;
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
      
      let filteredData = data.administradores || [];
      
      if (search.trim()) {
        filteredData = filteredData.filter(admin => 
          admin.dni?.toString().includes(search) ||
          admin.nombre?.toLowerCase().includes(search.toLowerCase()) ||
          admin.apellido_paterno?.toLowerCase().includes(search.toLowerCase()) ||
          admin.apellido_materno?.toLowerCase().includes(search.toLowerCase())
        );
      }

      // ✅ CORREGIDO: Enriquecer con información de usuario (como en VetManagement)
      const administradoresCompletos = await Promise.all(
        filteredData.map(async (admin) => {
          try {
            if (admin.id_usuario) {
              const userInfo = await fetchUserInfo(admin.id_usuario);
              return {
                ...admin,
                username: userInfo?.username || 'N/A',
                id_usuario: admin.id_usuario
              };
            }
            return {
              ...admin,
              username: 'N/A',
              id_usuario: null
            };
          } catch (error) {
            console.warn(`Error obteniendo info de usuario para admin ${admin.id_administrador}:`, error);
            return {
              ...admin,
              username: 'N/A',
              id_usuario: null
            };
          }
        })
      );

      const mappedUsers = administradoresCompletos.map(admin => ({
        id: admin.id_administrador,
        id_usuario: admin.id_usuario,
        dni: admin.dni || 'Sin DNI',
        nombre: admin.nombre || 'Sin nombre',
        apellido_paterno: admin.apellido_paterno || 'Sin apellido',
        apellido_materno: admin.apellido_materno || 'Sin apellido',
        telefono: admin.telefono || 'Sin teléfono',
        email: admin.email || 'Sin email',
        genero: admin.genero,
        username: admin.username // ✅ AGREGADO: incluir username en el mapeo
      }));

      mappedUsers.sort((a, b) => a.id - b.id);
      setUsers(mappedUsers);
      setTotalRecords(data.total || 0);
      setTotalPages(data.total_pages || 1);
      setCurrentPage(page);

    } catch (error) {
      console.error('Error al obtener administradores:', error);
      setError(error.message);
      setUsers([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAdministradores();
  }, []);

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      fetchAdministradores(1, selectedGenero, searchTerm);
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchTerm, selectedGenero]);

  const handleAdd = () => {
    setModalType('add');
    setSelectedUser(null);
    setFormData({
      dni: '',
      nombre: '',
      apellido_paterno: '',
      apellido_materno: '',
      telefono: '',
      email: '',
      genero: 'M',
      contraseña: '',
      username: ''
    });
    setFormErrors({});
    setShowModal(true);
  };

  const handleView = (user) => {
    setModalType('view');
    setSelectedUser(user);
    setShowModal(true);
  };

  const handleEdit = (user) => {
    setModalType('edit');
    setSelectedUser(user);
    setFormData({
      dni: user.dni === 'Sin DNI' ? '' : user.dni,
      nombre: user.nombre === 'Sin nombre' ? '' : user.nombre,
      apellido_paterno: user.apellido_paterno === 'Sin apellido' ? '' : user.apellido_paterno,
      apellido_materno: user.apellido_materno === 'Sin apellido' ? '' : user.apellido_materno,
      telefono: user.telefono === 'Sin teléfono' ? '' : user.telefono,
      email: user.email === 'Sin email' ? '' : user.email,
      genero: user.genero || 'M',
      contraseña: '',
      username: user.username || '' // ✅ CORREGIDO: cargar username en edición
    });
    setFormErrors({});
    setShowModal(true);
  };

  const handleDelete = async (user) => {
    if (!window.confirm(`¿Está seguro de eliminar PERMANENTEMENTE el administrador "${user.nombre}"? Esta acción no se puede deshacer.`)) {
      return;
    }

    setDeleteLoading(true);
    
    const result = await deleteAdministrador(user.id);
    if (result.success) {
      alert('Administrador eliminado permanentemente');
      fetchAdministradores(currentPage, selectedGenero, searchTerm);
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
        if (!formData.nombre.trim()) {
          alert('El nombre es obligatorio');
          return;
        }

        if (!formData.dni.trim() || !/^\d{8}$/.test(formData.dni.trim())) {
          alert('El DNI debe tener 8 dígitos');
          return;
        }

        if (!formData.email.trim() || !/\S+@\S+\.\S+/.test(formData.email.trim())) {
          alert('El email no tiene un formato válido');
          return;
        }

        if (!formData.contraseña.trim() || formData.contraseña.length < 3) {
          alert('La contraseña debe tener al menos 3 caracteres');
          return;
        }

        const submitData = {
          dni: formData.dni.trim(),
          nombre: formData.nombre.trim(),
          apellido_paterno: formData.apellido_paterno.trim(),
          apellido_materno: formData.apellido_materno.trim() || null,
          telefono: formData.telefono.trim(),
          email: formData.email.trim(),
          genero: formData.genero,
          contraseña: formData.contraseña.trim(),
          username: generateUsername(formData.nombre),
          fecha_ingreso: new Date().toISOString().split('T')[0]
        };

        const result = await createAdministrador(submitData);
        
        if (result.success) {
          setShowModal(false);
          fetchAdministradores(currentPage, selectedGenero, searchTerm);
          alert('Administrador creado exitosamente');
        } else {
          alert(`Error: ${result.message}`);
        }
      } else {
        const updateData = {
          dni: formData.dni.trim(),
          nombre: formData.nombre.trim(),
          apellido_paterno: formData.apellido_paterno.trim(),
          apellido_materno: formData.apellido_materno.trim() || null,
          telefono: formData.telefono.trim(),
          email: formData.email.trim(),
          genero: formData.genero
        };

        const result = await updateAdministrador(selectedUser.id, updateData);
        
        if (!result.success) {
          throw new Error(result.message);
        }

        let messages = ['Administrador actualizado exitosamente'];

        if (formData.username.trim() && formData.username.trim() !== selectedUser.username && selectedUser.id_usuario) {
          const userUpdateResult = await updateUser(selectedUser.id_usuario, {
            username: formData.username.trim()
          });
          if (userUpdateResult.success) {
            messages.push('Username actualizado');
          } else {
            console.warn('No se pudo actualizar username:', userUpdateResult.message);
          }
        }

        if (formData.contraseña.trim()) {
          const passwordResult = await changePassword(selectedUser.id, formData.contraseña.trim());
          if (!passwordResult.success) {
            throw new Error(passwordResult.message);
          }
          messages.push('Contraseña actualizada');
        }

        alert(messages.join(', '));
        setShowModal(false);
        fetchAdministradores(currentPage, selectedGenero, searchTerm);
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
      
      if (name === 'nombre' && modalType === 'add') {
        newData.username = generateUsername(value);
      }
      
      return newData;
    });
    
    if (formErrors[name]) {
      setFormErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages) {
      fetchAdministradores(newPage, selectedGenero, searchTerm);
    }
  };

  const clearFilters = () => {
    setSearchTerm('');
    setSelectedGenero('');
    setCurrentPage(1);
    fetchAdministradores(1, '', '');
  };

  const columns = [
    { key: 'id', header: 'ID' },
    { key: 'dni', header: 'DNI' },
    { key: 'nombre', header: 'NOMBRE' },
    { 
      key: 'apellidos', 
      header: 'APELLIDOS',
      render: (user) => `${user.apellido_paterno} ${user.apellido_materno}`.trim()
    },
    { key: 'telefono', header: 'TELÉFONO' },
    { key: 'email', header: 'EMAIL' },
    { 
      key: 'genero', 
      header: 'GÉNERO',
      render: (user) => user.genero === 'M' ? 'Masculino' : user.genero === 'F' ? 'Femenino' : 'N/A'
    }
  ];

  const actions = [
    { label: '👁️', type: 'view', onClick: handleView },
    { label: '✏️', type: 'edit', onClick: handleEdit },
    { label: '🗑️', type: 'delete', onClick: handleDelete }
  ];

  const filteredUsers = users;

  if (loading && users.length === 0) {
    return (
      <div className="users-management">
        <div className="loading-container">
          <p>Cargando administradores...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="users-management">
      {/* ✅ AGREGADO: Estilos CSS para el header colorido */}
      <style jsx>{`
        .users-management table th {
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

      <div className="section-header">
        <h2>GESTIÓN DE ADMINISTRADORES</h2>
        <button onClick={handleAdd} className="btn-add">
          + AÑADIR ADMINISTRADOR
        </button>
      </div>

      <div className="users-table-section">
        <div className="table-header">
          <h3>LISTA DE ADMINISTRADORES</h3>
          
          <div className="filters-container">
            <input
              type="text"
              placeholder="🔍 Buscar por DNI, nombre o apellidos..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
            
            <select 
              value={selectedGenero} 
              onChange={(e) => setSelectedGenero(e.target.value)}
              className="filter-select"
            >
              <option value="">Todos los géneros</option>
              <option value="M">Masculino</option>
              <option value="F">Femenino</option>
            </select>

            {(searchTerm || selectedGenero) && (
              <button onClick={clearFilters} className="clear-filters-btn">
                LIMPIAR
              </button>
            )}
          </div>
        </div>

        <div className="results-info">
          <span>Total: {totalRecords} registros | Página {currentPage} de {totalPages} | Mostrando: {users.length} registros</span>
          {deleteLoading && <span style={{color: 'red'}}>Eliminando...</span>}
        </div>

        {error && (
          <div className="error-message">
            <p>Error: {error}</p>
            <button onClick={() => fetchAdministradores()} className="btn-retry">
              Reintentar
            </button>
          </div>
        )}

        <Table 
          columns={columns}
          data={filteredUsers}
          actions={actions}
          emptyMessage={
            searchTerm || selectedGenero 
              ? "No se encontraron administradores con los filtros aplicados"
              : "No hay administradores registrados"
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
      </div>

      <Modal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        title={
          modalType === 'add' ? 'AGREGAR ADMINISTRADOR' : 
          modalType === 'edit' ? 'EDITAR ADMINISTRADOR' : 
          'DETALLES DEL ADMINISTRADOR'
        }
        size="large"
      >
        {modalType === 'view' ? (
          <div className="user-view">
            <div className="form-section">
              <h3>Información Personal</h3>
              <div className="info-grid">
                <div><strong>ID:</strong> {selectedUser?.id}</div>
                <div><strong>DNI:</strong> {selectedUser?.dni}</div>
                <div><strong>Nombre:</strong> {selectedUser?.nombre}</div>
                <div><strong>Apellido Paterno:</strong> {selectedUser?.apellido_paterno}</div>
                <div><strong>Apellido Materno:</strong> {selectedUser?.apellido_materno}</div>
                <div><strong>Género:</strong> {selectedUser?.genero === 'M' ? 'Masculino' : 'Femenino'}</div>
                <div><strong>Teléfono:</strong> {selectedUser?.telefono}</div>
                <div><strong>Username:</strong> {selectedUser?.username}</div> {/* ✅ AGREGADO: mostrar username en vista */}
                <div><strong>Email:</strong> {selectedUser?.email}</div>
              </div>
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="user-form">
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
                    <option value="M">M</option>
                    <option value="F">F</option>
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
                  <label htmlFor="username">
                    USERNAME {modalType === 'add' ? '(autogenerado)' : '(editable)'}
                  </label>
                  <input
                    type="text"
                    id="username"
                    name="username"
                    value={formData.username}
                    onChange={handleInputChange}
                    readOnly={modalType === 'add'}
                    style={modalType === 'add' ? { backgroundColor: '#f8f9fa', cursor: 'not-allowed' } : {}}
                    placeholder={modalType === 'add' ? "Se genera automáticamente" : "Ingrese username"}
                  />
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
  );
};

export default UserManagement;

/*import React, { useState, useEffect } from 'react';
import Table from '../common/Table';
import Modal from '../common/Modal';

const UserManagement = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [modalType, setModalType] = useState('add');
  const [selectedUser, setSelectedUser] = useState(null);
  const [submitLoading, setSubmitLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedGenero, setSelectedGenero] = useState('');
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
    genero: 'M',
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
    return `admin_${primerNombre}`;
  };

  // Función para crear administrador
  const createAdministrador = async (adminData) => {
    try {
      const response = await fetch(`${BASE_URL}/administradores/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(adminData)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || `Error: ${response.status}`);
      }

      const data = await response.json();
      console.log('Administrador creado:', data);
      return { success: true, data };
    } catch (error) {
      console.error('Error creando administrador:', error);
      return { success: false, message: error.message };
    }
  };

  // Función para actualizar administrador
  const updateAdministrador = async (adminId, adminData) => {
    try {
      const response = await fetch(`${BASE_URL}/administradores/${adminId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(adminData)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || `Error: ${response.status}`);
      }

      const data = await response.json();
      console.log('Administrador actualizado:', data);
      return { success: true, data };
    } catch (error) {
      console.error('Error actualizando administrador:', error);
      return { success: false, message: error.message };
    }
  };

  // Función para cambiar contraseña
  const changePassword = async (adminId, newPassword) => {
    try {
      const response = await fetch(`${BASE_URL}/administradores/${adminId}/change-password`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          admin_id: adminId,
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

  // Función para eliminar administrador
  const deleteAdministrador = async (adminId) => {
    try {
      const response = await fetch(`${BASE_URL}/administradores/${adminId}?permanent=false`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || `Error: ${response.status}`);
      }

      return { success: true };
    } catch (error) {
      console.error('Error eliminando administrador:', error);
      return { success: false, message: error.message };
    }
  };

  // Función para obtener administradores
  const fetchAdministradores = async (page = 1, genero = '', search = '') => {
    try {
      setLoading(true);
      setError(null);

      // Agregar filtro para solo obtener administradores activos
      let url = `${BASE_URL}/administradores/?page=${page}&per_page=10&activos_solo=true`;
      
      if (genero) {
        url += `&genero=${genero}`;
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
      
      let filteredData = data.administradores || [];
      
      // Filtrar por término de búsqueda localmente
      if (search.trim()) {
        filteredData = filteredData.filter(admin => 
          admin.dni?.toString().includes(search) ||
          admin.nombre?.toLowerCase().includes(search.toLowerCase()) ||
          admin.apellido_paterno?.toLowerCase().includes(search.toLowerCase()) ||
          admin.apellido_materno?.toLowerCase().includes(search.toLowerCase())
        );
      }

      // Mapear los datos para que coincidan con la estructura esperada por Table
      const mappedUsers = filteredData.map(admin => ({
        id: admin.id_administrador,
        dni: admin.dni || 'Sin DNI',
        nombre: admin.nombre || 'Sin nombre',
        apellido_paterno: admin.apellido_paterno || 'Sin apellido',
        apellido_materno: admin.apellido_materno || 'Sin apellido',
        telefono: admin.telefono || 'Sin teléfono',
        email: admin.email || 'Sin email',
        genero: admin.genero
      }));

      
      mappedUsers.sort((a, b) => a.id - b.id);
      setUsers(mappedUsers);
      setTotalRecords(data.total || 0);
      setTotalPages(data.total_pages || 1);
      setCurrentPage(page);

    } catch (error) {
      console.error('Error al obtener administradores:', error);
      setError(error.message);
      setUsers([]);
    } finally {
      setLoading(false);
    }
  };

  // Efectos
  useEffect(() => {
    fetchAdministradores();
  }, []);

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      fetchAdministradores(1, selectedGenero, searchTerm);
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchTerm, selectedGenero]);

  // Manejadores de eventos
  const handleAdd = () => {
    setModalType('add');
    setSelectedUser(null);
    setFormData({
      dni: '',
      nombre: '',
      apellido_paterno: '',
      apellido_materno: '',
      telefono: '',
      email: '',
      genero: 'M',
      contraseña: '',
      username: ''
    });
    setFormErrors({});
    setShowModal(true);
  };

  const handleEdit = (user) => {
    setModalType('edit');
    setSelectedUser(user);
    setFormData({
      dni: user.dni === 'Sin DNI' ? '' : user.dni,
      nombre: user.nombre === 'Sin nombre' ? '' : user.nombre,
      apellido_paterno: user.apellido_paterno === 'Sin apellido' ? '' : user.apellido_paterno,
      apellido_materno: user.apellido_materno === 'Sin apellido' ? '' : user.apellido_materno,
      telefono: user.telefono === 'Sin teléfono' ? '' : user.telefono,
      email: user.email === 'Sin email' ? '' : user.email,
      genero: user.genero || 'M',
      contraseña: '',
      username: ''
    });
    setFormErrors({});
    setShowModal(true);
  };

  const handleDelete = async (user) => {
    if (!window.confirm(`¿Está seguro de eliminar PERMANENTEMENTE el administrador "${user.nombre}"? Esta acción no se puede deshacer.`)) {
      return;
    }

    setDeleteLoading(true);
    
    const result = await deleteAdministrador(user.id);
    if (result.success) {
      alert('Administrador eliminado permanentemente');
      fetchAdministradores(currentPage, selectedGenero, searchTerm);
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
        // Validaciones básicas
        if (!formData.nombre.trim()) {
          alert('El nombre es obligatorio');
          return;
        }

        if (!formData.dni.trim() || !/^\d{8}$/.test(formData.dni.trim())) {
          alert('El DNI debe tener 8 dígitos');
          return;
        }

        if (!formData.email.trim() || !/\S+@\S+\.\S+/.test(formData.email.trim())) {
          alert('El email no tiene un formato válido');
          return;
        }

        if (!formData.contraseña.trim() || formData.contraseña.length < 3) {
          alert('La contraseña debe tener al menos 3 caracteres');
          return;
        }

        // Crear nuevo administrador
        const submitData = {
          dni: formData.dni.trim(),
          nombre: formData.nombre.trim(),
          apellido_paterno: formData.apellido_paterno.trim(),
          apellido_materno: formData.apellido_materno.trim() || null,
          telefono: formData.telefono.trim(),
          email: formData.email.trim(),
          genero: formData.genero,
          contraseña: formData.contraseña.trim(),
          username: generateUsername(formData.nombre),
          fecha_ingreso: new Date().toISOString().split('T')[0]
        };

        const result = await createAdministrador(submitData);
        
        if (result.success) {
          setShowModal(false);
          fetchAdministradores(currentPage, selectedGenero, searchTerm);
          alert('Administrador creado exitosamente');
        } else {
          alert(`Error: ${result.message}`);
        }
      } else {
        // Actualizar administrador existente
        const updateData = {
          dni: formData.dni.trim(),
          nombre: formData.nombre.trim(),
          apellido_paterno: formData.apellido_paterno.trim(),
          apellido_materno: formData.apellido_materno.trim() || null,
          telefono: formData.telefono.trim(),
          email: formData.email.trim(),
          genero: formData.genero
        };

        // Actualizar datos del perfil
        const result = await updateAdministrador(selectedUser.id, updateData);
        
        if (!result.success) {
          throw new Error(result.message);
        }

        // Si se proporcionó una nueva contraseña, cambiarla por separado
        if (formData.contraseña.trim()) {
          const passwordResult = await changePassword(selectedUser.id, formData.contraseña.trim());
          if (!passwordResult.success) {
            throw new Error(passwordResult.message);
          }
          alert('Administrador y contraseña actualizados exitosamente');
        } else {
          alert('Administrador actualizado exitosamente');
        }

        setShowModal(false);
        fetchAdministradores(currentPage, selectedGenero, searchTerm);
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
      fetchAdministradores(newPage, selectedGenero, searchTerm);
    }
  };

  const clearFilters = () => {
    setSearchTerm('');
    setSelectedGenero('');
    setCurrentPage(1);
    fetchAdministradores(1, '', '');
  };

  // Configuración de columnas y acciones
  const columns = [
    { key: 'id', header: 'ID' },
    { key: 'dni', header: 'DNI' },
    { key: 'nombre', header: 'NOMBRE' },
    { 
      key: 'apellidos', 
      header: 'APELLIDOS',
      render: (user) => `${user.apellido_paterno} ${user.apellido_materno}`.trim()
    },
    { key: 'telefono', header: 'TELÉFONO' },
    { key: 'email', header: 'EMAIL' },
    { 
      key: 'genero', 
      header: 'GÉNERO',
      render: (user) => user.genero === 'M' ? 'Masculino' : user.genero === 'F' ? 'Femenino' : 'N/A'
    }
  ];

  const actions = [
    { label: '✏️', type: 'edit', onClick: handleEdit },
    { label: '🗑️', type: 'delete', onClick: handleDelete }
  ];

  const filteredUsers = users;

  if (loading && users.length === 0) {
    return (
      <div className="user-management">
        <div className="loading-container">
          <p>Cargando administradores...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="user-management">
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
            value={selectedGenero} 
            onChange={(e) => setSelectedGenero(e.target.value)}
            className="filter-select"
          >
            <option value="">Todos los géneros</option>
            <option value="M">Masculino</option>
            <option value="F">Femenino</option>
          </select>

          {(searchTerm || selectedGenero) && (
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
        <span>Mostrando: {users.length} registros</span>
        {deleteLoading && <span style={{color: 'red'}}>Eliminando...</span>}
      </div>

      {error && (
        <div className="error-message">
          <p>Error: {error}</p>
          <button onClick={() => fetchAdministradores()} className="btn-retry">
            Reintentar
          </button>
        </div>
      )}

      <Table 
        columns={columns}
        data={filteredUsers}
        actions={actions}
        emptyMessage={
          searchTerm || selectedGenero 
            ? "No se encontraron administradores con los filtros aplicados"
            : "No hay administradores registrados"
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
        title={modalType === 'add' ? 'AGREGAR' : 'EDITAR ADMINISTRADOR'}
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
                  <option value="M">M</option>
                  <option value="F">F</option>
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

export default UserManagement; */