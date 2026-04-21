// src/components/admin/VetManagement.jsx - MEJORADO CON VISTA Y DISEÑO CONSISTENTE
import React, { useState, useEffect } from 'react';
import Table from '../common/Table';
import Modal from '../common/Modal';
import './VetManagement.css';

const VetManagement = () => {
  const [veterinarios, setVeterinarios] = useState([]);
  const [especialidades, setEspecialidades] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [modalType, setModalType] = useState('add');
  const [selectedVet, setSelectedVet] = useState(null);
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
    genero: 'M',
    turno: '',
    codigo_cmvp: '',
    id_especialidad: '',
    fecha_nacimiento: '',
    contraseña: '',
    username: ''
  });

  const [formErrors, setFormErrors] = useState({});

  // URL base de tu backend
  const BASE_URL = 'https://veterinariaclinicabackend-production.up.railway.app/api/v1';

  // Función para determinar el tipo de veterinario según la especialidad
  const getTipoVeterinario = (idEspecialidad) => {
    if (!idEspecialidad) return 'Medico General';
    
    // Buscar la especialidad en el array
    const especialidad = especialidades.find(e => e.id_especialidad === parseInt(idEspecialidad));
    
    // Si la especialidad es "Medicina General" o similar, es médico general
    if (especialidad && (
      especialidad.descripcion.toLowerCase().includes('general') || 
      especialidad.descripcion.toLowerCase().includes('medicina general')
    )) {
      return 'Medico General';
    }
    
    // Cualquier otra especialidad es especializado
    return 'Especializado';
  };
  
  const generateUsername = (nombre) => {
    if (!nombre.trim()) return '';
    const primerNombre = nombre.trim().split(' ')[0].toLowerCase();
    return `vet_${primerNombre}`;
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

  // Función para crear veterinario (requiere id_usuario)
  const createVeterinario = async (vetData) => {
    try {
      const response = await fetch(`${BASE_URL}/veterinarios/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(vetData)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || `Error: ${response.status}`);
      }

      const data = await response.json();
      console.log('Veterinario creado:', data);
      return { success: true, data };
    } catch (error) {
      console.error('Error creando veterinario:', error);
      return { success: false, message: error.message };
    }
  };

  // Función para crear veterinario completo (usuario + perfil)
  const createVeterinarioCompleto = async (formData) => {
    try {
      // PASO 1: Crear usuario
      console.log('🔸 Paso 1: Creando usuario...');
      const userData = {
        username: formData.username.trim(),
        contraseña: formData.contraseña.trim(),
        tipo_usuario: 'Veterinario',
        estado: 'Activo'
      };

      const userResult = await createUser(userData);
      if (!userResult.success) {
        throw new Error(`Error creando usuario: ${userResult.message}`);
      }

      const userId = userResult.data.id_usuario;
      console.log('✅ Usuario creado con ID:', userId);

      // PASO 2: Crear veterinario con el id_usuario
      console.log('🔸 Paso 2: Creando perfil de veterinario...');
      
      // ⚠️ IMPORTANTE: Usar fecha actual para fecha_ingreso
      const fechaIngreso = new Date().toISOString().split('T')[0];
      
      const vetData = {
        id_usuario: userId, // Campo requerido
        dni: formData.dni.trim(),
        nombre: formData.nombre.trim(),
        apellido_paterno: formData.apellido_paterno.trim(),
        apellido_materno: formData.apellido_materno.trim() || null,
        telefono: formData.telefono.trim(),
        email: formData.email.trim(),
        genero: formData.genero,
        turno: formData.turno,
        codigo_CMVP: formData.codigo_cmvp.trim(), // ← CORREGIDO: Backend espera 'codigo_CMVP'
        fecha_nacimiento: formData.fecha_nacimiento,
        fecha_ingreso: fechaIngreso, // ← AGREGADO: Campo requerido
        disposicion: 'Libre'
      };

      // Ajustar tipo_veterinario según la especialidad seleccionada
      const tipoVeterinario = getTipoVeterinario(formData.id_especialidad);
      vetData.tipo_veterinario = tipoVeterinario;
      vetData.id_especialidad = parseInt(formData.id_especialidad) || 1; // Default a 1 si no se selecciona

      const vetResult = await createVeterinario(vetData);
      if (!vetResult.success) {
        console.warn('⚠️ Fallo crear veterinario, pero usuario ya fue creado');
        throw new Error(`Error creando veterinario: ${vetResult.message}`);
      }

      console.log('✅ Veterinario creado exitosamente');
      return { success: true, data: vetResult.data };

    } catch (error) {
      console.error('❌ Error en proceso completo:', error);
      return { success: false, message: error.message };
    }
  };

  // Función para actualizar veterinario
  const updateVeterinario = async (vetId, vetData) => {
    try {
      const response = await fetch(`${BASE_URL}/veterinarios/${vetId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(vetData)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || `Error: ${response.status}`);
      }

      const data = await response.json();
      console.log('Veterinario actualizado:', data);
      return { success: true, data };
    } catch (error) {
      console.error('Error actualizando veterinario:', error);
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

  // Función para obtener especialidades
  const fetchEspecialidades = async () => {
    try {
      const response = await fetch(`${BASE_URL}/catalogos/especialidades/`, {
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
      console.log('✅ Especialidades obtenidas:', data);
      setEspecialidades(data || []);
    } catch (error) {
      console.error('Error obteniendo especialidades:', error);
      setEspecialidades([]);
    }
  };

  // Función para obtener veterinarios (CORREGIDA PARA CMVP)
  const fetchVeterinarios = async (page = 1, turno = '', search = '') => {
    try {
      setLoading(true);
      setError(null);

      let url = `${BASE_URL}/veterinarios/?page=${page}&per_page=10`;
      
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
      
      let filteredData = data.veterinarios || [];
      
      // Filtrar por término de búsqueda localmente
      if (search.trim()) {
        filteredData = filteredData.filter(vet => 
          vet.dni?.toString().includes(search) ||
          vet.nombre?.toLowerCase().includes(search.toLowerCase()) ||
          vet.apellido_paterno?.toLowerCase().includes(search.toLowerCase()) ||
          vet.apellido_materno?.toLowerCase().includes(search.toLowerCase()) ||
          vet.codigo_CMVP?.toLowerCase().includes(search.toLowerCase())
        );
      }

      // Enriquecer con información de usuario
      const veterinariosCompletos = await Promise.all(
        filteredData.map(async (vet) => {
          try {
            if (vet.id_usuario) {
              const userInfo = await fetchUserInfo(vet.id_usuario);
              return {
                ...vet,
                username: userInfo?.username || 'N/A',
                estado_usuario: userInfo?.estado || 'N/A'
              };
            }
            return {
              ...vet,
              username: 'N/A',
              estado_usuario: 'N/A'
            };
          } catch (error) {
            console.warn(`Error obteniendo info de usuario para veterinario ${vet.id_veterinario}:`, error);
            return {
              ...vet,
              username: 'N/A',
              estado_usuario: 'N/A'
            };
          }
        })
      );

      // Filtrar solo usuarios activos
      const veterinariosActivos = veterinariosCompletos.filter(
        vet => vet.estado_usuario === 'Activo' || vet.estado_usuario === 'N/A'
      );

      // Mapear los datos para que coincidan con la estructura esperada por Table
      const mappedVeterinarios = veterinariosActivos.map(vet => ({
        id: vet.id_veterinario,
        id_usuario: vet.id_usuario,
        dni: vet.dni || 'Sin DNI',
        nombre: vet.nombre || 'Sin nombre',
        apellido_paterno: vet.apellido_paterno || 'Sin apellido',
        apellido_materno: vet.apellido_materno || 'Sin apellido',
        telefono: vet.telefono || 'Sin teléfono',
        email: vet.email || 'Sin email',
        genero: vet.genero,
        turno: vet.turno || 'Sin turno',
        codigo_cmvp: vet.codigo_CMVP || 'Sin código',
        fecha_nacimiento: vet.fecha_nacimiento,
        id_especialidad: vet.id_especialidad,
        disposicion: vet.disposicion || 'Libre',
        username: vet.username,
        tipo_veterinario: vet.tipo_veterinario || 'General'
      }));

      setVeterinarios(mappedVeterinarios);
      setTotalRecords(data.total || 0);
      setTotalPages(data.total_pages || 1);
      setCurrentPage(page);

    } catch (error) {
      console.error('Error al obtener veterinarios:', error);
      setError(error.message);
      setVeterinarios([]);
    } finally {
      setLoading(false);
    }
  };

  // Función para obtener nombre de especialidad
  const getNombreEspecialidad = (idEspecialidad) => {
    if (!idEspecialidad) return '-';
    const especialidad = especialidades.find(e => e.id_especialidad === idEspecialidad);
    return especialidad ? especialidad.descripcion : '-';
  };

  // Efectos
  useEffect(() => {
    fetchEspecialidades();
    fetchVeterinarios();
  }, []);

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      fetchVeterinarios(1, selectedTurno, searchTerm);
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchTerm, selectedTurno]);

  // Manejadores de eventos
  const handleAdd = () => {
    setModalType('add');
    setSelectedVet(null);
    setFormData({
      dni: '',
      nombre: '',
      apellido_paterno: '',
      apellido_materno: '',
      telefono: '',
      email: '',
      genero: 'M',
      turno: '',
      codigo_cmvp: '',
      id_especialidad: '',
      fecha_nacimiento: '',
      contraseña: '',
      username: ''
    });
    setFormErrors({});
    setShowModal(true);
  };

  // ✅ AGREGADO: handleView para mostrar información completa
  const handleView = (vet) => {
    setModalType('view');
    setSelectedVet(vet);
    setShowModal(true);
  };

  const handleEdit = (vet) => {
    setModalType('edit');
    setSelectedVet(vet);
    setFormData({
      dni: vet.dni === 'Sin DNI' ? '' : vet.dni,
      nombre: vet.nombre === 'Sin nombre' ? '' : vet.nombre,
      apellido_paterno: vet.apellido_paterno === 'Sin apellido' ? '' : vet.apellido_paterno,
      apellido_materno: vet.apellido_materno === 'Sin apellido' ? '' : vet.apellido_materno,
      telefono: vet.telefono === 'Sin teléfono' ? '' : vet.telefono,
      email: vet.email === 'Sin email' ? '' : vet.email,
      genero: vet.genero || 'M',
      turno: vet.turno === 'Sin turno' ? '' : vet.turno,
      codigo_cmvp: vet.codigo_cmvp === 'Sin código' ? '' : vet.codigo_cmvp,
      id_especialidad: vet.id_especialidad || '',
      fecha_nacimiento: vet.fecha_nacimiento || '',
      contraseña: '',
      username: vet.username === 'N/A' ? '' : vet.username
    });
    setFormErrors({});
    setShowModal(true);
  };

  const handleDelete = async (vet) => {
    if (!window.confirm(`¿Está seguro de eliminar al veterinario "${vet.nombre}"? Esta acción desactivará su cuenta de usuario.`)) {
      return;
    }

    if (!vet.id_usuario) {
      alert('No se puede eliminar: no tiene usuario asociado');
      return;
    }

    setDeleteLoading(true);
    
    const result = await deactivateUser(vet.id_usuario);
    if (result.success) {
      alert('Veterinario eliminado exitosamente (usuario desactivado)');
      fetchVeterinarios(currentPage, selectedTurno, searchTerm);
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
        // Crear nuevo veterinario completo (usuario + perfil)
        const submitData = {
          dni: formData.dni.trim(),
          nombre: formData.nombre.trim(),
          apellido_paterno: formData.apellido_paterno.trim(),
          apellido_materno: formData.apellido_materno.trim(),
          telefono: formData.telefono.trim(),
          email: formData.email.trim(),
          genero: formData.genero,
          turno: formData.turno,
          codigo_cmvp: formData.codigo_cmvp.trim(),
          id_especialidad: formData.id_especialidad,
          fecha_nacimiento: formData.fecha_nacimiento,
          username: formData.username.trim(),
          contraseña: formData.contraseña.trim()
        };

        const result = await createVeterinarioCompleto(submitData);
        
        if (result.success) {
          setShowModal(false);
          fetchVeterinarios(currentPage, selectedTurno, searchTerm);
          alert('Veterinario creado exitosamente');
        } else {
          alert(`Error: ${result.message}`);
        }
      } else {
        // Actualizar veterinario existente
        const updateData = {
          dni: formData.dni.trim(),
          nombre: formData.nombre.trim(),
          apellido_paterno: formData.apellido_paterno.trim(),
          apellido_materno: formData.apellido_materno.trim() || null,
          telefono: formData.telefono.trim(),
          email: formData.email.trim(),
          genero: formData.genero,
          turno: formData.turno,
          codigo_CMVP: formData.codigo_cmvp.trim(),
          fecha_nacimiento: formData.fecha_nacimiento
        };

        // Manejar especialidad y tipo según la especialidad seleccionada
        const tipoVeterinario = getTipoVeterinario(formData.id_especialidad);
        updateData.tipo_veterinario = tipoVeterinario;
        updateData.id_especialidad = parseInt(formData.id_especialidad) || null;

        // Actualizar datos del perfil
        const result = await updateVeterinario(selectedVet.id, updateData);
        
        if (!result.success) {
          throw new Error(result.message);
        }

        let messages = ['Veterinario actualizado exitosamente'];

        // Si se cambió el username, actualizarlo
        if (formData.username.trim() && formData.username.trim() !== selectedVet.username && selectedVet.id_usuario) {
          const userUpdateResult = await updateUser(selectedVet.id_usuario, {
            username: formData.username.trim()
          });
          if (userUpdateResult.success) {
            messages.push('Username actualizado');
          } else {
            console.warn('No se pudo actualizar username:', userUpdateResult.message);
          }
        }

        // Si se proporcionó una nueva contraseña, cambiarla por separado
        if (formData.contraseña.trim() && selectedVet.id_usuario) {
          const passwordResult = await changePassword(selectedVet.id_usuario, formData.contraseña.trim());
          if (passwordResult.success) {
            messages.push('Contraseña actualizada');
          } else {
            console.warn('No se pudo actualizar contraseña:', passwordResult.message);
          }
        }

        alert(messages.join(', '));
        setShowModal(false);
        fetchVeterinarios(currentPage, selectedTurno, searchTerm);
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

    if (!formData.codigo_cmvp.trim()) {
      errors.codigo_cmvp = 'El código CMVP es requerido';
    }

    if (!formData.fecha_nacimiento) {
      errors.fecha_nacimiento = 'La fecha de nacimiento es requerida';
    }

    if (!formData.id_especialidad) {
      errors.id_especialidad = 'Debe seleccionar una especialidad';
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
      fetchVeterinarios(newPage, selectedTurno, searchTerm);
    }
  };

  const clearFilters = () => {
    setSearchTerm('');
    setSelectedTurno('');
    setCurrentPage(1);
    fetchVeterinarios(1, '', '');
  };

  // ✅ MEJORADO: Columnas optimizadas sin CMVP y fecha de nacimiento
  const columns = [
    { key: 'id', header: 'ID' },
    { key: 'dni', header: 'DNI' },
    { 
      key: 'nombre', 
      header: 'NOMBRE',
      render: (vet) => `${vet.nombre} ${vet.apellido_paterno} ${vet.apellido_materno}`.trim()
    },
    { key: 'telefono', header: 'TELÉFONO' },
    { key: 'email', header: 'EMAIL' },
    { 
      key: 'genero', 
      header: 'GÉNERO',
      render: (vet) => vet.genero === 'M' ? 'Masculino' : vet.genero === 'F' ? 'Femenino' : 'N/A'
    },
    { 
      key: 'turno', 
      header: 'TURNO',
      render: (vet) => {
        const turno = vet.turno || 'Sin turno';
        return turno === 'Mañana' ? 'Mañana' : turno === 'Tarde' ? 'Tarde' : turno === 'Noche' ? 'Noche' : turno;
      }
    },
    { 
      key: 'especialidad', 
      header: 'ESPECIALIDAD',
      render: (vet) => getNombreEspecialidad(vet.id_especialidad)
    }
  ];

  // ✅ MEJORADO: Acciones con ojo para vista
  const actions = [
    { label: '👁️', type: 'view', onClick: handleView },
    { label: '✏️', type: 'edit', onClick: handleEdit },
    { label: '🗑️', type: 'delete', onClick: handleDelete }
  ];

  if (loading && veterinarios.length === 0) {
    return (
      <div className="vet-management">
        <div className="loading-container">
          <p>Cargando veterinarios...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="vet-management">
      {/* ✅ AGREGADO: Estilos CSS para el header colorido consistente */}
      <style jsx>{`
        .vet-management table th {
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
        <h2>GESTIÓN DE VETERINARIOS</h2>
        <button onClick={handleAdd} className="btn-add">
          + AÑADIR VETERINARIO
        </button>
      </div>

      <div className="vet-table-section">
        <div className="table-header">
          <h3>LISTA DE VETERINARIOS</h3>
          
          <div className="filters-container">
            <input
              type="text"
              placeholder="🔍 Buscar por DNI, nombre o código CMVP..."
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

        <div className="results-info">
          <span>Total: {totalRecords} registros | Página {currentPage} de {totalPages} | Mostrando: {veterinarios.length} registros</span>
          {deleteLoading && <span style={{color: 'red'}}>Eliminando...</span>}
        </div>

        {error && (
          <div className="error-message">
            <p>Error: {error}</p>
            <button onClick={() => fetchVeterinarios()} className="btn-retry">
              Reintentar
            </button>
          </div>
        )}

        <Table 
          columns={columns}
          data={veterinarios}
          actions={actions}
          emptyMessage={
            searchTerm || selectedTurno 
              ? "No se encontraron veterinarios con los filtros aplicados"
              : "No hay veterinarios registrados"
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
          modalType === 'add' ? 'AGREGAR VETERINARIO' : 
          modalType === 'edit' ? 'EDITAR VETERINARIO' : 
          'DETALLES DEL VETERINARIO'
        }
        size="large"
      >
        {modalType === 'view' ? (
          // ✅ AGREGADO: Vista completa del veterinario
          <div className="vet-view">
            <div className="form-section">
              <h3>INFORMACIÓN PERSONAL</h3>
              <div className="info-grid">
                <div><strong>ID:</strong> {selectedVet?.id}</div>
                <div><strong>DNI:</strong> {selectedVet?.dni}</div>
                <div><strong>Nombre:</strong> {selectedVet?.nombre}</div>
                <div><strong>Apellido Paterno:</strong> {selectedVet?.apellido_paterno}</div>
                <div><strong>Apellido Materno:</strong> {selectedVet?.apellido_materno}</div>
                <div><strong>Género:</strong> {selectedVet?.genero === 'M' ? 'Masculino' : 'Femenino'}</div>
                <div><strong>Fecha de Nacimiento:</strong> {selectedVet?.fecha_nacimiento || 'N/A'}</div>
              </div>
            </div>

            <div className="form-section">
              <h3>INFORMACIÓN DE CONTACTO</h3>
              <div className="info-grid">
                <div><strong>Teléfono:</strong> {selectedVet?.telefono}</div>
                <div><strong>Email:</strong> {selectedVet?.email}</div>
              </div>
            </div>

            <div className="form-section">
              <h3>INFORMACIÓN PROFESIONAL</h3>
              <div className="info-grid">
                <div><strong>Código CMVP:</strong> {selectedVet?.codigo_cmvp}</div>
                <div><strong>Turno:</strong> {selectedVet?.turno}</div>
                <div><strong>Especialidad:</strong> {getNombreEspecialidad(selectedVet?.id_especialidad)}</div>
                <div><strong>Tipo:</strong> {selectedVet?.tipo_veterinario || 'General'}</div>
                <div><strong>Disposición:</strong> {selectedVet?.disposicion}</div>
                <div><strong>Username:</strong> {selectedVet?.username}</div>
              </div>
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="vet-form">
            <div className="form-section">
              <h3>DATOS PERSONALES</h3>
              
              {/* Primera fila: DNI, Código CMVP, Género */}
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
                  <label htmlFor="codigo_cmvp">CÓDIGO CMVP (*)</label>
                  <input
                    type="text"
                    id="codigo_cmvp"
                    name="codigo_cmvp"
                    value={formData.codigo_cmvp}
                    onChange={handleInputChange}
                    placeholder="CMVP..."
                    className={formErrors.codigo_cmvp ? 'error' : ''}
                  />
                  {formErrors.codigo_cmvp && <span className="error-message">{formErrors.codigo_cmvp}</span>}
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
                    <option value="M">Masculino</option>
                    <option value="F">Femenino</option>
                  </select>
                  {formErrors.genero && <span className="error-message">{formErrors.genero}</span>}
                </div>
              </div>

              {/* Segunda fila: Nombres y Apellidos */}
              <div className="form-row">
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
              
              {/* Tercera fila: Teléfono, Email, Fecha de Nacimiento */}
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

                <div className="form-group">
                  <label htmlFor="fecha_nacimiento">F. DE NACIMIENTO (*)</label>
                  <input
                    type="date"
                    id="fecha_nacimiento"
                    name="fecha_nacimiento"
                    value={formData.fecha_nacimiento}
                    onChange={handleInputChange}
                    className={formErrors.fecha_nacimiento ? 'error' : ''}
                  />
                  {formErrors.fecha_nacimiento && <span className="error-message">{formErrors.fecha_nacimiento}</span>}
                </div>
              </div>

              {/* Cuarta fila: Turno, Especialidad */}
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
                    <option value="Mañana">MAÑANA</option>
                    <option value="Tarde">TARDE</option>
                    <option value="Noche">NOCHE</option>
                  </select>
                  {formErrors.turno && <span className="error-message">{formErrors.turno}</span>}
                </div>

                <div className="form-group">
                  <label htmlFor="id_especialidad">ESPECIALIDAD (*)</label>
                  <select
                    id="id_especialidad"
                    name="id_especialidad"
                    value={formData.id_especialidad}
                    onChange={handleInputChange}
                    className={formErrors.id_especialidad ? 'error' : ''}
                  >
                    <option value="">Seleccione especialidad</option>
                    {especialidades.map(esp => (
                      <option key={esp.id_especialidad} value={esp.id_especialidad}>
                        {esp.descripcion.toUpperCase()}
                      </option>
                    ))}
                  </select>
                  {formErrors.id_especialidad && <span className="error-message">{formErrors.id_especialidad}</span>}
                </div>
              </div>

              {/* Quinta fila: Username */}
              <div className="form-row">
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
              
              {/* Sexta fila: Contraseña */}
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

export default VetManagement;
/*
// src/components/admin/VetManagement.jsx - CÓDIGO COMPLETO CORREGIDO CMVP Y ESPACIADO
import React, { useState, useEffect } from 'react';
import Table from '../common/Table';
import Modal from '../common/Modal';

const VetManagement = () => {
  const [veterinarios, setVeterinarios] = useState([]);
  const [especialidades, setEspecialidades] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [modalType, setModalType] = useState('add');
  const [selectedVet, setSelectedVet] = useState(null);
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
    genero: 'M',
    turno: '',
    codigo_cmvp: '',
    id_especialidad: '',
    fecha_nacimiento: '',
    contraseña: '',
    username: ''
  });

  const [formErrors, setFormErrors] = useState({});

  // URL base de tu backend
  const BASE_URL = 'https://veterinariaclinicabackend-production.up.railway.app/api/v1';

  // Función para determinar el tipo de veterinario según la especialidad
  const getTipoVeterinario = (idEspecialidad) => {
    if (!idEspecialidad) return 'Medico General';
    
    // Buscar la especialidad en el array
    const especialidad = especialidades.find(e => e.id_especialidad === parseInt(idEspecialidad));
    
    // Si la especialidad es "Medicina General" o similar, es médico general
    if (especialidad && (
      especialidad.descripcion.toLowerCase().includes('general') || 
      especialidad.descripcion.toLowerCase().includes('medicina general')
    )) {
      return 'Medico General';
    }
    
    // Cualquier otra especialidad es especializado
    return 'Especializado';
  };
  const generateUsername = (nombre) => {
    if (!nombre.trim()) return '';
    const primerNombre = nombre.trim().split(' ')[0].toLowerCase();
    return `vet_${primerNombre}`;
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

  // Función para crear veterinario (requiere id_usuario)
  const createVeterinario = async (vetData) => {
    try {
      const response = await fetch(`${BASE_URL}/veterinarios/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(vetData)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || `Error: ${response.status}`);
      }

      const data = await response.json();
      console.log('Veterinario creado:', data);
      return { success: true, data };
    } catch (error) {
      console.error('Error creando veterinario:', error);
      return { success: false, message: error.message };
    }
  };

  // Función para crear veterinario completo (usuario + perfil)
  const createVeterinarioCompleto = async (formData) => {
    try {
      // PASO 1: Crear usuario
      console.log('🔸 Paso 1: Creando usuario...');
      const userData = {
        username: formData.username.trim(),
        contraseña: formData.contraseña.trim(),
        tipo_usuario: 'Veterinario',
        estado: 'Activo'
      };

      const userResult = await createUser(userData);
      if (!userResult.success) {
        throw new Error(`Error creando usuario: ${userResult.message}`);
      }

      const userId = userResult.data.id_usuario;
      console.log('✅ Usuario creado con ID:', userId);

      // PASO 2: Crear veterinario con el id_usuario
      console.log('🔸 Paso 2: Creando perfil de veterinario...');
      
      // ⚠️ IMPORTANTE: Usar fecha actual para fecha_ingreso
      const fechaIngreso = new Date().toISOString().split('T')[0];
      
      const vetData = {
        id_usuario: userId, // Campo requerido
        dni: formData.dni.trim(),
        nombre: formData.nombre.trim(),
        apellido_paterno: formData.apellido_paterno.trim(),
        apellido_materno: formData.apellido_materno.trim() || null,
        telefono: formData.telefono.trim(),
        email: formData.email.trim(),
        genero: formData.genero,
        turno: formData.turno,
        codigo_CMVP: formData.codigo_cmvp.trim(), // ← CORREGIDO: Backend espera 'codigo_CMVP'
        fecha_nacimiento: formData.fecha_nacimiento,
        fecha_ingreso: fechaIngreso, // ← AGREGADO: Campo requerido
        disposicion: 'Libre'
      };

      // Ajustar tipo_veterinario según la especialidad seleccionada
      const tipoVeterinario = getTipoVeterinario(formData.id_especialidad);
      vetData.tipo_veterinario = tipoVeterinario;
      vetData.id_especialidad = parseInt(formData.id_especialidad) || 1; // Default a 1 si no se selecciona

      const vetResult = await createVeterinario(vetData);
      if (!vetResult.success) {
        console.warn('⚠️ Fallo crear veterinario, pero usuario ya fue creado');
        throw new Error(`Error creando veterinario: ${vetResult.message}`);
      }

      console.log('✅ Veterinario creado exitosamente');
      return { success: true, data: vetResult.data };

    } catch (error) {
      console.error('❌ Error en proceso completo:', error);
      return { success: false, message: error.message };
    }
  };

  // Función para actualizar veterinario
  const updateVeterinario = async (vetId, vetData) => {
    try {
      const response = await fetch(`${BASE_URL}/veterinarios/${vetId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(vetData)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || `Error: ${response.status}`);
      }

      const data = await response.json();
      console.log('Veterinario actualizado:', data);
      return { success: true, data };
    } catch (error) {
      console.error('Error actualizando veterinario:', error);
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

  // Función para obtener especialidades
  const fetchEspecialidades = async () => {
    try {
      const response = await fetch(`${BASE_URL}/catalogos/especialidades/`, {
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
      console.log('✅ Especialidades obtenidas:', data);
      setEspecialidades(data || []);
    } catch (error) {
      console.error('Error obteniendo especialidades:', error);
      setEspecialidades([]);
    }
  };

  // Función para obtener veterinarios (CORREGIDA PARA CMVP)
  const fetchVeterinarios = async (page = 1, turno = '', search = '') => {
    try {
      setLoading(true);
      setError(null);

      let url = `${BASE_URL}/veterinarios/?page=${page}&per_page=10`;
      
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
      
      let filteredData = data.veterinarios || [];
      
      // 🔍 DEBUG: Verificar estructura de datos recibidos
      console.log('✅ Datos de veterinarios obtenidos:', data);
      console.log('📋 Primer veterinario completo:', filteredData[0]);
      console.log('🔧 Campos disponibles:', filteredData[0] ? Object.keys(filteredData[0]) : 'No hay datos');
      
      // Filtrar por término de búsqueda localmente
      if (search.trim()) {
        filteredData = filteredData.filter(vet => 
          vet.dni?.toString().includes(search) ||
          vet.nombre?.toLowerCase().includes(search.toLowerCase()) ||
          vet.apellido_paterno?.toLowerCase().includes(search.toLowerCase()) ||
          vet.apellido_materno?.toLowerCase().includes(search.toLowerCase()) ||
          vet.codigo_CMVP?.toLowerCase().includes(search.toLowerCase()) // ← CORREGIDO: Backend devuelve 'codigo_CMVP'
        );
      }

      // Enriquecer con información de usuario
      const veterinariosCompletos = await Promise.all(
        filteredData.map(async (vet) => {
          try {
            if (vet.id_usuario) {
              const userInfo = await fetchUserInfo(vet.id_usuario);
              return {
                ...vet,
                username: userInfo?.username || 'N/A',
                estado_usuario: userInfo?.estado || 'N/A'
              };
            }
            return {
              ...vet,
              username: 'N/A',
              estado_usuario: 'N/A'
            };
          } catch (error) {
            console.warn(`Error obteniendo info de usuario para veterinario ${vet.id_veterinario}:`, error);
            return {
              ...vet,
              username: 'N/A',
              estado_usuario: 'N/A'
            };
          }
        })
      );

      // Filtrar solo usuarios activos
      const veterinariosActivos = veterinariosCompletos.filter(
        vet => vet.estado_usuario === 'Activo' || vet.estado_usuario === 'N/A'
      );

      // Mapear los datos para que coincidan con la estructura esperada por Table
      const mappedVeterinarios = veterinariosActivos.map(vet => ({
        id: vet.id_veterinario,
        id_usuario: vet.id_usuario,
        dni: vet.dni || 'Sin DNI',
        nombre: vet.nombre || 'Sin nombre',
        apellido_paterno: vet.apellido_paterno || 'Sin apellido',
        apellido_materno: vet.apellido_materno || 'Sin apellido',
        telefono: vet.telefono || 'Sin teléfono',
        email: vet.email || 'Sin email',
        genero: vet.genero,
        turno: vet.turno || 'Sin turno',
        codigo_cmvp: vet.codigo_CMVP || 'Sin código', // ← CORREGIDO: Mapear desde 'codigo_CMVP' del backend
        fecha_nacimiento: vet.fecha_nacimiento,
        id_especialidad: vet.id_especialidad,
        disposicion: vet.disposicion || 'Libre',
        username: vet.username,
        tipo_veterinario: vet.tipo_veterinario || 'General'
      }));

      console.log('📊 Veterinarios mapeados (primer elemento):', mappedVeterinarios[0]);

      setVeterinarios(mappedVeterinarios);
      setTotalRecords(data.total || 0);
      setTotalPages(data.total_pages || 1);
      setCurrentPage(page);

    } catch (error) {
      console.error('Error al obtener veterinarios:', error);
      setError(error.message);
      setVeterinarios([]);
    } finally {
      setLoading(false);
    }
  };

  // Función para obtener nombre de especialidad
  const getNombreEspecialidad = (idEspecialidad) => {
    if (!idEspecialidad) return '-';
    const especialidad = especialidades.find(e => e.id_especialidad === idEspecialidad);
    return especialidad ? especialidad.descripcion : '-';
  };

  // Efectos
  useEffect(() => {
    fetchEspecialidades();
    fetchVeterinarios();
  }, []);

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      fetchVeterinarios(1, selectedTurno, searchTerm);
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchTerm, selectedTurno]);

  // Manejadores de eventos
  const handleAdd = () => {
    setModalType('add');
    setSelectedVet(null);
    setFormData({
      dni: '',
      nombre: '',
      apellido_paterno: '',
      apellido_materno: '',
      telefono: '',
      email: '',
      genero: 'M',
      turno: '',
      codigo_cmvp: '',
      id_especialidad: '',
      fecha_nacimiento: '',
      contraseña: '',
      username: ''
    });
    setFormErrors({});
    setShowModal(true);
  };

  const handleEdit = (vet) => {
    setModalType('edit');
    setSelectedVet(vet);
    setFormData({
      dni: vet.dni === 'Sin DNI' ? '' : vet.dni,
      nombre: vet.nombre === 'Sin nombre' ? '' : vet.nombre,
      apellido_paterno: vet.apellido_paterno === 'Sin apellido' ? '' : vet.apellido_paterno,
      apellido_materno: vet.apellido_materno === 'Sin apellido' ? '' : vet.apellido_materno,
      telefono: vet.telefono === 'Sin teléfono' ? '' : vet.telefono,
      email: vet.email === 'Sin email' ? '' : vet.email,
      genero: vet.genero || 'M',
      turno: vet.turno === 'Sin turno' ? '' : vet.turno,
      codigo_cmvp: vet.codigo_cmvp === 'Sin código' ? '' : vet.codigo_cmvp,
      id_especialidad: vet.id_especialidad || '',
      fecha_nacimiento: vet.fecha_nacimiento || '',
      contraseña: '',
      username: vet.username === 'N/A' ? '' : vet.username
    });
    setFormErrors({});
    setShowModal(true);
  };

  const handleDelete = async (vet) => {
    if (!window.confirm(`¿Está seguro de eliminar al veterinario "${vet.nombre}"? Esta acción desactivará su cuenta de usuario.`)) {
      return;
    }

    if (!vet.id_usuario) {
      alert('No se puede eliminar: no tiene usuario asociado');
      return;
    }

    setDeleteLoading(true);
    
    const result = await deactivateUser(vet.id_usuario);
    if (result.success) {
      alert('Veterinario eliminado exitosamente (usuario desactivado)');
      fetchVeterinarios(currentPage, selectedTurno, searchTerm);
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
        // Crear nuevo veterinario completo (usuario + perfil)
        const submitData = {
          dni: formData.dni.trim(),
          nombre: formData.nombre.trim(),
          apellido_paterno: formData.apellido_paterno.trim(),
          apellido_materno: formData.apellido_materno.trim(),
          telefono: formData.telefono.trim(),
          email: formData.email.trim(),
          genero: formData.genero,
          turno: formData.turno,
          codigo_cmvp: formData.codigo_cmvp.trim(),
          id_especialidad: formData.id_especialidad,
          fecha_nacimiento: formData.fecha_nacimiento,
          username: formData.username.trim(),
          contraseña: formData.contraseña.trim()
        };

        const result = await createVeterinarioCompleto(submitData);
        
        if (result.success) {
          setShowModal(false);
          fetchVeterinarios(currentPage, selectedTurno, searchTerm);
          alert('Veterinario creado exitosamente');
        } else {
          alert(`Error: ${result.message}`);
        }
      } else {
        // Actualizar veterinario existente
        const updateData = {
          dni: formData.dni.trim(),
          nombre: formData.nombre.trim(),
          apellido_paterno: formData.apellido_paterno.trim(),
          apellido_materno: formData.apellido_materno.trim() || null,
          telefono: formData.telefono.trim(),
          email: formData.email.trim(),
          genero: formData.genero,
          turno: formData.turno,
          codigo_CMVP: formData.codigo_cmvp.trim(), // ← CORREGIDO: Backend espera 'codigo_CMVP'
          fecha_nacimiento: formData.fecha_nacimiento
        };

        // Manejar especialidad y tipo según la especialidad seleccionada
        const tipoVeterinario = getTipoVeterinario(formData.id_especialidad);
        updateData.tipo_veterinario = tipoVeterinario;
        updateData.id_especialidad = parseInt(formData.id_especialidad) || null;

        // Actualizar datos del perfil
        const result = await updateVeterinario(selectedVet.id, updateData);
        
        if (!result.success) {
          throw new Error(result.message);
        }

        let messages = ['Veterinario actualizado exitosamente'];

        // Si se cambió el username, actualizarlo
        if (formData.username.trim() && formData.username.trim() !== selectedVet.username && selectedVet.id_usuario) {
          const userUpdateResult = await updateUser(selectedVet.id_usuario, {
            username: formData.username.trim()
          });
          if (userUpdateResult.success) {
            messages.push('Username actualizado');
          } else {
            console.warn('No se pudo actualizar username:', userUpdateResult.message);
          }
        }

        // Si se proporcionó una nueva contraseña, cambiarla por separado
        if (formData.contraseña.trim() && selectedVet.id_usuario) {
          const passwordResult = await changePassword(selectedVet.id_usuario, formData.contraseña.trim());
          if (passwordResult.success) {
            messages.push('Contraseña actualizada');
          } else {
            console.warn('No se pudo actualizar contraseña:', passwordResult.message);
          }
        }

        alert(messages.join(', '));
        setShowModal(false);
        fetchVeterinarios(currentPage, selectedTurno, searchTerm);
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

    if (!formData.codigo_cmvp.trim()) {
      errors.codigo_cmvp = 'El código CMVP es requerido';
    }

    if (!formData.fecha_nacimiento) {
      errors.fecha_nacimiento = 'La fecha de nacimiento es requerida';
    }

    if (!formData.id_especialidad) {
      errors.id_especialidad = 'Debe seleccionar una especialidad';
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
      fetchVeterinarios(newPage, selectedTurno, searchTerm);
    }
  };

  const clearFilters = () => {
    setSearchTerm('');
    setSelectedTurno('');
    setCurrentPage(1);
    fetchVeterinarios(1, '', '');
  };

  // Configuración de columnas y acciones - OPTIMIZADA CON ANCHO ID CORREGIDO
  const columns = [
    { 
      key: 'id', 
      header: 'ID',
      style: { width: '40px', fontSize: '12px' } // ← REDUCIDO: de 50px a 40px
    },
    { 
      key: 'dni', 
      header: 'DNI',
      style: { width: '80px', fontSize: '12px' }
    },
    { 
      key: 'nombre', 
      header: 'NOMBRE',
      render: (vet) => {
        const nombreCompleto = `${vet.nombre} ${vet.apellido_paterno} ${vet.apellido_materno}`.trim();
        return nombreCompleto.length > 20 ? nombreCompleto.substring(0, 20) + '...' : nombreCompleto;
      },
      style: { width: '140px', fontSize: '12px' }
    },
    { 
      key: 'codigo_cmvp', 
      header: 'CMVP',
      style: { width: '80px', fontSize: '12px' }
    },
    { 
      key: 'telefono', 
      header: 'TELÉFONO',
      style: { width: '90px', fontSize: '12px' }
    },
    { 
      key: 'email', 
      header: 'EMAIL',
      render: (vet) => {
        const email = vet.email || 'Sin email';
        return email.length > 15 ? email.substring(0, 15) + '...' : email;
      },
      style: { width: '120px', fontSize: '12px' }
    },
    { 
      key: 'genero', 
      header: 'GÉNERO',
      render: (vet) => vet.genero === 'M' ? 'M' : vet.genero === 'F' ? 'F' : 'N/A',
      style: { width: '60px', fontSize: '12px' }
    },
    { 
      key: 'turno', 
      header: 'TURNO',
      render: (vet) => {
        const turno = vet.turno || 'Sin turno';
        return turno === 'Mañana' ? 'MAÑ' : turno === 'Tarde' ? 'TAR' : turno === 'Noche' ? 'NOC' : turno;
      },
      style: { width: '60px', fontSize: '12px' }
    },
    { 
      key: 'especialidad', 
      header: 'ESPECIALIDAD',
      render: (vet) => {
        const especialidad = getNombreEspecialidad(vet.id_especialidad);
        return especialidad.length > 12 ? especialidad.substring(0, 12) + '...' : especialidad;
      },
      style: { width: '100px', fontSize: '12px' }
    },
    { 
      key: 'disposicion', 
      header: 'DISPOSICIÓN',
      render: (vet) => {
        const disp = vet.disposicion || 'Libre';
        return disp === 'Libre' ? 'LIB' : disp === 'Ocupado' ? 'OCU' : disp;
      },
      style: { width: '80px', fontSize: '12px' }
    },
    { 
      key: 'fecha_nacimiento', 
      header: 'F. NACIMIENTO',
      render: (vet) => {
        if (vet.fecha_nacimiento) {
          const fecha = new Date(vet.fecha_nacimiento);
          return fecha.toLocaleDateString('es-PE', { 
            day: '2-digit', 
            month: '2-digit', 
            year: '2-digit' 
          });
        }
        return 'N/A';
      },
      style: { width: '90px', fontSize: '12px' }
    }
  ];

  const actions = [
    { 
      label: '✏️', 
      type: 'edit', 
      onClick: handleEdit,
      style: { fontSize: '16px', cursor: 'pointer', color: '#28a745' }
    },
    { 
      label: '🗑️', 
      type: 'delete', 
      onClick: handleDelete,
      style: { fontSize: '16px', cursor: 'pointer', color: '#dc3545' }
    }
  ];

  if (loading && veterinarios.length === 0) {
    return (
      <div className="vet-management">
        <div className="loading-container">
          <p>Cargando veterinarios...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="vet-management">
      <style jsx>{`
        .vet-management table {
          font-size: 12px;
          width: 100%;
          table-layout: fixed;
        }
        .vet-management table th,
        .vet-management table td {
          padding: 8px 4px;
          text-align: center;
          vertical-align: middle;
          word-wrap: break-word;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
        .vet-management table th {
          background: #68c1da !important;
          color: white !important;
          font-weight: 600;
          font-size: 11px;
          text-transform: uppercase;
          letter-spacing: 0.3px;
        }
        .vet-management .search-input {
          width: 350px;
          font-size: 14px;
        }
        .vet-management .status-info {
          font-size: 13px;
          margin: 10px 0;
        }
        .vet-management .pagination {
          margin-top: 15px;
        }
      `}</style>

      <div className="section-header">
        <div className="search-controls">
          <input
            type="text"
            placeholder="Buscar por DNI, nombre o código CMVP..."
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
        <span>Mostrando: {veterinarios.length} registros</span>
        {deleteLoading && <span style={{color: 'red'}}>Eliminando...</span>}
      </div>

      {error && (
        <div className="error-message">
          <p>Error: {error}</p>
          <button onClick={() => fetchVeterinarios()} className="btn-retry">
            Reintentar
          </button>
        </div>
      )}

      <Table 
        columns={columns}
        data={veterinarios}
        actions={actions}
        emptyMessage={
          searchTerm || selectedTurno 
            ? "No se encontraron veterinarios con los filtros aplicados"
            : "No hay veterinarios registrados"
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
        title={modalType === 'add' ? 'AGREGAR VETERINARIO' : 'EDITAR VETERINARIO'}
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
                <label htmlFor="codigo_cmvp">CÓDIGO CMVP (*)</label>
                <input
                  type="text"
                  id="codigo_cmvp"
                  name="codigo_cmvp"
                  value={formData.codigo_cmvp}
                  onChange={handleInputChange}
                  placeholder="CMVP..."
                  className={formErrors.codigo_cmvp ? 'error' : ''}
                />
                {formErrors.codigo_cmvp && <span className="error-message">{formErrors.codigo_cmvp}</span>}
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
                  <option value="M">Masculino</option>
                  <option value="F">Femenino</option>
                </select>
                {formErrors.genero && <span className="error-message">{formErrors.genero}</span>}
              </div>
            </div>

            <div className="form-row">
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

              <div className="form-group">
                <label htmlFor="fecha_nacimiento">F. DE NACIMIENTO (*)</label>
                <input
                  type="date"
                  id="fecha_nacimiento"
                  name="fecha_nacimiento"
                  value={formData.fecha_nacimiento}
                  onChange={handleInputChange}
                  className={formErrors.fecha_nacimiento ? 'error' : ''}
                />
                {formErrors.fecha_nacimiento && <span className="error-message">{formErrors.fecha_nacimiento}</span>}
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
                  <option value="Mañana">MAÑANA</option>
                  <option value="Tarde">TARDE</option>
                  <option value="Noche">NOCHE</option>
                </select>
                {formErrors.turno && <span className="error-message">{formErrors.turno}</span>}
              </div>

              <div className="form-group">
                <label htmlFor="id_especialidad">ESPECIALIDAD (*)</label>
                <select
                  id="id_especialidad"
                  name="id_especialidad"
                  value={formData.id_especialidad}
                  onChange={handleInputChange}
                  className={formErrors.id_especialidad ? 'error' : ''}
                >
                  <option value="">Seleccione especialidad</option>
                  {especialidades.map(esp => (
                    <option key={esp.id_especialidad} value={esp.id_especialidad}>
                      {esp.descripcion.toUpperCase()}
                    </option>
                  ))}
                </select>
                {formErrors.id_especialidad && <span className="error-message">{formErrors.id_especialidad}</span>}
              </div>
            </div>

            <div className="form-row">
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

export default VetManagement; */