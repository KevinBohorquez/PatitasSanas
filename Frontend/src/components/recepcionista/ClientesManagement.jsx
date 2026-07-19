import React, { useState, useEffect } from 'react';
import { apiFetch } from '../../api/client';
import Table from '../common/Table';
import Modal from '../ui/Modal/Modal';
import './ClientesManagement.css';
import { toast } from '../../utils/toast';
import { formatApiError } from '../../utils/apiError';
import Loader from '../ui/Loader/Loader';
import { confirm } from '../../utils/confirm';

const ClientesManagement = () => {
  const [clientes, setClientes] = useState([]);
  const [filteredClientes, setFilteredClientes] = useState([]);
  const [currentPage, setCurrentPage] = useState(1); // SC-019 / F25: paginación client-side
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [modalType, setModalType] = useState('add');
  const [selectedCliente, setSelectedCliente] = useState(null);
  const [mascotas, setMascotas] = useState([]);

  // Estados para filtros
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('todos');

  // Estados para validaciones
  const [validationErrors, setValidationErrors] = useState({});

  const [formData, setFormData] = useState({
    dni: '',
    nombre: '',
    apellido_paterno: '',
    apellido_materno: '',
    telefono: '',
    email: '',
    genero: 'F',
    direccion: '',
    estado: 'Activo'
  });

  const BASE_URL = '';

  // Cargar clientes
  useEffect(() => {
    fetchClientes();
  }, []);

  // Aplicar filtros cuando cambien los clientes
  useEffect(() => {
    applyFilters();
  }, [clientes, searchTerm, statusFilter]);

  // Función para aplicar filtros
  const applyFilters = () => {
    let filtered = [...clientes];

    // Filtro por DNI o nombre completo
    if (searchTerm.trim()) {
      const term = searchTerm.toLowerCase().trim();
      filtered = filtered.filter(cliente => {
        const nombreCompleto = `${cliente.nombre} ${cliente.apellido_paterno} ${cliente.apellido_materno || ''}`.toLowerCase();
        const dni = cliente.dni?.toLowerCase() || '';

        return nombreCompleto.includes(term) || dni.includes(term);
      });
    }

    // Filtro por estado
    if (statusFilter !== 'todos') {
      const estadoFiltro = statusFilter === 'activos' ? 'Activo' : 'Inactivo';
      filtered = filtered.filter(cliente => cliente.estado === estadoFiltro);
    }

    setFilteredClientes(filtered);
    setCurrentPage(1); // SC-019: al cambiar el filtro/búsqueda, volver a la primera página
  };

  // Función para validar campos en tiempo real
  const validateField = (field, value) => {
    const errors = { ...validationErrors };

    switch (field) {
      case 'dni':
        if (value && (!/^\d{8}$/.test(value))) {
          errors.dni = 'El DNI debe contener exactamente 8 números';
        } else {
          delete errors.dni;
        }
        break;

      case 'nombre':
        if (value && !/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(value)) {
          errors.nombre = 'El nombre solo puede contener letras y espacios';
        } else {
          delete errors.nombre;
        }
        break;

      case 'apellido_paterno':
        if (value && !/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(value)) {
          errors.apellido_paterno = 'El apellido solo puede contener letras y espacios';
        } else {
          delete errors.apellido_paterno;
        }
        break;

      case 'apellido_materno':
        if (value && !/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(value)) {
          errors.apellido_materno = 'El apellido solo puede contener letras y espacios';
        } else {
          delete errors.apellido_materno;
        }
        break;

      case 'telefono':
        if (value && (!/^\d{9}$/.test(value) || !value.startsWith('9'))) {
          errors.telefono = 'El teléfono debe tener 9 números y empezar con 9';
        } else {
          delete errors.telefono;
        }
        break;

      case 'email':
        if (value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
          errors.email = 'Ingrese un email válido';
        } else {
          delete errors.email;
        }
        break;

      default:
        break;
    }

    setValidationErrors(errors);
  };

  // Función para manejar cambios en los inputs con validación
  const handleInputChange = (field, value) => {
    // Filtros específicos para ciertos campos
    let filteredValue = value;

    if (field === 'dni' || field === 'telefono') {
      // Solo permitir números
      filteredValue = value.replace(/\D/g, '');
      // Limitar longitud
      if (field === 'dni') {
        filteredValue = filteredValue.slice(0, 8);
      } else if (field === 'telefono') {
        filteredValue = filteredValue.slice(0, 9);
      }
    } else if (field === 'nombre' || field === 'apellido_paterno' || field === 'apellido_materno') {
      // Solo permitir letras, espacios y acentos
      filteredValue = value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]/g, '');
    }

    setFormData({ ...formData, [field]: filteredValue });
    validateField(field, filteredValue);
  };

  // Obtener todos los clientes
  const fetchClientes = async () => {
    setLoading(true);
    try {
      // SC-019 / F25: pedir hasta el máximo del backend para no truncar el listado
      // a la primera página (se pagina en el cliente sobre los resultados filtrados).
      const response = await apiFetch(`${BASE_URL}/clientes/?per_page=100`, {
        method: 'GET',
        mode: 'cors',
        headers: {
          'Accept': 'application/json',
        },
      });
      if (response.ok) {
        const data = await response.json();
        setClientes(data.clientes || data);
      } else {
        console.error('Error al cargar clientes:', response.statusText);
        toast.error('Error al cargar los clientes');
      }
    } catch (error) {
      console.error('Error:', error);
      toast.error('Error de conexión al cargar clientes');
    } finally {
      setLoading(false);
    }
  };

  // Obtener mascotas de un cliente
  const fetchMascotasCliente = async (clienteId) => {
    try {
      const response = await apiFetch(`${BASE_URL}/catalogos/cliente-mascota/cliente/${clienteId}`, {
        method: 'GET',
        mode: 'cors',
        headers: {
          'Accept': 'application/json',
        },
      });
      if (response.ok) {
        const data = await response.json();
        setMascotas(data.mascotas || []);
      } else {
        setMascotas([]);
      }
    } catch (error) {
      console.error('Error al cargar mascotas:', error);
      setMascotas([]);
    }
  };

  const handleAdd = () => {
    setModalType('add');
    setFormData({
      dni: '',
      nombre: '',
      apellido_paterno: '',
      apellido_materno: '',
      telefono: '',
      email: '',
      genero: 'F',
      direccion: '',
      estado: 'Activo'
    });
    setValidationErrors({});
    setMascotas([]);
    setShowModal(true);
  };

  //Editar información del cliente
  const handleEdit = async (cliente) => {
    setModalType('edit');
    setSelectedCliente(cliente);
    setFormData({
      dni: cliente.dni || '',
      nombre: cliente.nombre || '',
      apellido_paterno: cliente.apellido_paterno || '',
      apellido_materno: cliente.apellido_materno || '',
      telefono: cliente.telefono || '',
      email: cliente.email || '',
      genero: cliente.genero || 'F',
      direccion: cliente.direccion || '',
      estado: cliente.estado || 'Activo'
    });
    setValidationErrors({});
    setMascotas([]);
    setShowModal(true);
  };

  //Ver información de cliente
  const handleView = async (cliente) => {
    setModalType('view');
    setSelectedCliente(cliente);
    await fetchMascotasCliente(cliente.id_cliente);
    setShowModal(true);
  };

  //Eliminar cliente Modificando solo su estado
  const handleDelete = async (cliente) => {
    if ((await confirm({ variant: 'danger', message: `¿Está seguro de eliminar al cliente ${cliente.nombre} ${cliente.apellido_paterno}?` }))) {
      setLoading(true);
      try {
        const response = await apiFetch(`${BASE_URL}/clientes/${cliente.id_cliente}`, {
          method: 'DELETE',
          mode: 'cors',
          headers: {
            'Accept': 'application/json',
          },
        });

        if (response.ok) {
          toast.success('Cliente eliminado exitosamente');
          fetchClientes(); // Recargar la lista
        } else {
          const errorData = await response.json();
          toast.error(formatApiError(errorData, 'No se pudo eliminar el cliente'));
        }
      } catch (error) {
        console.error('Error:', error);
        toast.error('Error de conexión al eliminar cliente');
      } finally {
        setLoading(false);
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    // Validaciones básicas
    if (!formData.dni || !formData.nombre || !formData.apellido_paterno || !formData.apellido_materno ||
      !formData.telefono || !formData.email || !formData.direccion) {
      toast.warning('Por favor, complete todos los campos requeridos, incluyendo el Apellido Materno.');
      setLoading(false);
      return;
    }

    // Verificar si hay errores de validación
    if (Object.keys(validationErrors).length > 0) {
      toast.error('Por favor, corrija los errores en el formulario antes de continuar');
      setLoading(false);
      return;
    }

    try {
      const clienteData = {
        dni: formData.dni,
        nombre: formData.nombre,
        apellido_paterno: formData.apellido_paterno,
        apellido_materno: formData.apellido_materno,
        telefono: formData.telefono,
        email: formData.email,
        genero: formData.genero,
        direccion: formData.direccion,
        estado: formData.estado
      };

      let response;

      if (modalType === 'add') {
        response = await apiFetch(`${BASE_URL}/clientes/`, {
          method: 'POST',
          mode: 'cors',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          body: JSON.stringify(clienteData),
        });
      } else if (modalType === 'edit') {
        response = await apiFetch(`${BASE_URL}/clientes/${selectedCliente.id_cliente}`, {
          method: 'PUT',
          mode: 'cors',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          body: JSON.stringify(clienteData),
        });
      }

      if (response.ok) {
        toast.success(modalType === 'add' ? 'Cliente agregado exitosamente' : 'Cliente actualizado exitosamente');
        setShowModal(false);
        fetchClientes(); // Recargar la lista
      } else {
        const errorData = await response.json().catch(() => null);
        toast.error(formatApiError(errorData, 'No se pudo guardar el cliente'));
      }
    } catch (error) {
      console.error('Error:', error);
      toast.error('Error de conexión al guardar cliente');
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
    { key: 'dni', header: 'DNI' },
    { key: 'nombre', header: 'NOMBRES' },
    { key: 'apellido_paterno', header: 'A. PATE' },
    { key: 'apellido_materno', header: 'A. MATERN' },
    {
      key: 'estado',
      header: 'ESTADO',
      render: (row) => (
        <span className={`status-badge ${row.estado === 'Activo' ? 'status-active' : 'status-inactive'}`}>
          {row.estado}
        </span>
      )
    }
  ];

  const actions = [
    { label: <img src="https://i.ibb.co/8nRGkFKS/Icono-Editar-Comprimida.png" alt="Editar" className="action-icon" />, type: 'edit', onClick: handleEdit },
    { label: <img src="https://i.ibb.co/1YfTT2c1/Icono-Ver-Comprimida.png" alt="Ver" className="action-icon" />, type: 'view', onClick: handleView },
    { label: <img src="https://i.ibb.co/LdbzttTC/Icono-Eliminar-Comprimida.png" alt="Eliminar" className="action-icon" />, type: 'delete', onClick: handleDelete }
  ];

  if (loading && clientes.length === 0) {
    return <Loader message="Cargando clientes" />;
  }

  // SC-019 / F25: paginación client-side sobre los resultados filtrados.
  const ITEMS_POR_PAGINA = 10;
  const totalPaginas = Math.max(1, Math.ceil(filteredClientes.length / ITEMS_POR_PAGINA));
  const clientesPagina = filteredClientes.slice(
    (currentPage - 1) * ITEMS_POR_PAGINA,
    currentPage * ITEMS_POR_PAGINA
  );

  return (
    <div className="clientes-management">
      <div className="section-header">
        <h2>SECCIÓN CLIENTES 🙋‍♂️</h2>
        <button onClick={handleAdd} className="btn-add" disabled={loading}>
          + Añadir Cliente
        </button>
      </div>

      <div className="clients-table-section">
        <div className="table-header">
          <h3>Clientes registrados en la base de datos</h3>

          {/* Filtros de búsqueda */}
          <div className="filters-container">
            <div className="search-container">
              <input
                type="text"
                placeholder="Buscar por nombre o DNI..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="search-input"
              />
              <button className="search-btn">
                <img src="https://i.ibb.co/3mvthkJT/Icono-Buscar-Comprimida.png" alt="Buscar" className="search-icon" />
              </button>
            </div>

            <div className="filter-container">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="filter-select"
              >
                <option value="todos">Filtrar por</option>
                <option value="todos">Todos</option>
                <option value="activos">Activos</option>
                <option value="inactivos">Inactivos</option>
              </select>
            </div>

            {(searchTerm || statusFilter !== 'todos') && (
              <button onClick={clearFilters} className="clear-filters-btn">
                Limpiar filtros
              </button>
            )}
          </div>
        </div>

        <div className="results-info">
          <span>
            Mostrando {filteredClientes.length} de {clientes.length} clientes
            {searchTerm && ` - Búsqueda: "${searchTerm}"`}
            {statusFilter !== 'todos' && ` - Estado: ${statusFilter}`}
          </span>
        </div>

        <Table
          columns={columns}
          data={clientesPagina}
          actions={actions}
          mobileTitle={(cliente) => (
            <>
              <span className="card-hd-main">{`${cliente.nombre || ''} ${cliente.apellido_paterno || ''}`.trim() || 'Sin nombre'}</span>
              <span className="card-hd-side">{cliente.dni || 'Sin DNI'}</span>
            </>
          )}
          emptyMessage={
            searchTerm || statusFilter !== 'todos'
              ? "No se encontraron clientes con los filtros aplicados"
              : "No hay clientes registrados"
          }
        />

        {totalPaginas > 1 && (
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
            <span>Página {currentPage} de {totalPaginas}</span>
            <button
              className="btn btn-secondary"
              onClick={() => setCurrentPage((p) => Math.min(totalPaginas, p + 1))}
              disabled={currentPage === totalPaginas}
            >
              Siguiente
            </button>
          </div>
        )}
      </div>

      <Modal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        title={modalType === 'add' ? 'Nuevo cliente' : modalType === 'edit' ? 'Editar cliente' : 'Ver cliente'}
        size="large"
      >
        {modalType === 'view' ? (
          <div className="cliente-view">
            <div className="form-section">
              <h3>DATOS PERSONALES</h3>
              <div className="info-grid">
                <div><strong>DNI:</strong> {selectedCliente?.dni}</div>
                <div><strong>Nombres:</strong> {selectedCliente?.nombre}</div>
                <div><strong>Apellido Paterno:</strong> {selectedCliente?.apellido_paterno}</div>
                <div><strong>Apellido Materno:</strong> {selectedCliente?.apellido_materno}</div>
                <div><strong>Género:</strong> {selectedCliente?.genero === 'F' ? 'Femenino' : 'Masculino'}</div>
                <div><strong>Estado:</strong> {selectedCliente?.estado}</div>
              </div>

              <h3>DATOS DE CONTACTO</h3>
              <div className="info-grid">
                <div><strong>Teléfono:</strong> {selectedCliente?.telefono || '-'}</div>
                <div><strong>Email:</strong> {selectedCliente?.email || '-'}</div>
                <div><strong>Dirección:</strong> {selectedCliente?.direccion || '-'}</div>
              </div>

              <h3>MASCOTAS REGISTRADAS</h3>
              <div className="mascotas-table">
                <table>
                  <thead>
                    <tr>
                      <th>NOMBRE</th>
                      <th>ESPECIE</th>
                      <th>RAZA</th>
                      <th>COLOR</th>
                      <th>EDAD</th>
                    </tr>
                  </thead>
                  <tbody>
                    {mascotas.length > 0 ? (
                      mascotas.map((mascota, index) => (
                        <tr key={index}>
                          <td>{mascota.nombre}</td>
                          <td>{mascota.sexo}</td>
                          <td>{mascota.raza}</td>
                          <td>{mascota.color}</td>
                          <td>{mascota.edad_anios} años, {mascota.edad_meses} meses</td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan="5">No hay mascotas registradas</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="cliente-form">
            <div className="form-section">
              <h3>DATOS PERSONALES</h3>
              <div className="form-row">
                <div className="form-group">
                  <label>DNI (*)</label>
                  <input
                    type="text"
                    value={formData.dni}
                    onChange={(e) => handleInputChange('dni', e.target.value)}
                    className={validationErrors.dni ? 'error' : ''}
                    required
                    maxLength="8"
                    disabled={modalType === 'edit'}
                  />
                  {validationErrors.dni && (
                    <span className="error-message">{validationErrors.dni}</span>
                  )}
                </div>
                <div className="form-group">
                  <label>GÉNERO (*)</label>
                  <select
                    value={formData.genero}
                    onChange={(e) => setFormData({ ...formData, genero: e.target.value })}
                    required
                  >
                    <option value="F">Femenino</option>
                    <option value="M">Masculino</option>
                  </select>
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>NOMBRES (*)</label>
                  <input
                    type="text"
                    value={formData.nombre}
                    onChange={(e) => handleInputChange('nombre', e.target.value)}
                    className={validationErrors.nombre ? 'error' : ''}
                    required
                  />
                  {validationErrors.nombre && (
                    <span className="error-message">{validationErrors.nombre}</span>
                  )}
                </div>
                <div className="form-group">
                  <label>APELLIDO PATERNO (*)</label>
                  <input
                    type="text"
                    value={formData.apellido_paterno}
                    onChange={(e) => handleInputChange('apellido_paterno', e.target.value)}
                    className={validationErrors.apellido_paterno ? 'error' : ''}
                    required
                  />
                  {validationErrors.apellido_paterno && (
                    <span className="error-message">{validationErrors.apellido_paterno}</span>
                  )}
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>APELLIDO MATERNO (*)</label>
                  <input
                    type="text"
                    value={formData.apellido_materno}
                    onChange={(e) => handleInputChange('apellido_materno', e.target.value)}
                    className={validationErrors.apellido_materno ? 'error' : ''}
                    required
                  />
                  {validationErrors.apellido_materno && (
                    <span className="error-message">{validationErrors.apellido_materno}</span>
                  )}
                </div>
                <div className="form-group">
                  <label>ESTADO (*)</label>
                  <select
                    value={formData.estado}
                    onChange={(e) => setFormData({ ...formData, estado: e.target.value })}
                    required
                  >
                    <option value="Activo">Activo</option>
                    <option value="Inactivo">Inactivo</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="form-section">
              <h3>DATOS DE CONTACTO</h3>
              <div className="form-row">
                <div className="form-group">
                  <label>TELÉFONO (*)</label>
                  <input
                    type="tel"
                    value={formData.telefono}
                    onChange={(e) => handleInputChange('telefono', e.target.value)}
                    className={validationErrors.telefono ? 'error' : ''}
                    required
                    maxLength="9"
                  />
                  {validationErrors.telefono && (
                    <span className="error-message">{validationErrors.telefono}</span>
                  )}
                </div>
                <div className="form-group">
                  <label>EMAIL (*)</label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => handleInputChange('email', e.target.value)}
                    className={validationErrors.email ? 'error' : ''}
                    required
                  />
                  {validationErrors.email && (
                    <span className="error-message">{validationErrors.email}</span>
                  )}
                </div>
              </div>

              <div className="form-group full-width">
                <label>DIRECCIÓN (*)</label>
                <input
                  type="text"
                  value={formData.direccion}
                  onChange={(e) => setFormData({ ...formData, direccion: e.target.value })}
                  required
                />
              </div>
            </div>

            <div className="form-actions">
              <button type="button" onClick={() => setShowModal(false)} className="btn-cancel" disabled={loading}>
                CANCELAR
              </button>
              <button type="submit" className="btn-submit" disabled={loading}>
                {loading ? 'PROCESANDO...' : 'FINALIZAR REGISTRO'}
              </button>
            </div>
          </form>
        )}
      </Modal>
    </div>
  );
};

export default ClientesManagement;
