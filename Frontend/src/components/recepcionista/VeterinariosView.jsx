import React, { useState, useEffect } from 'react';
import Table from '../common/Table';
import './VeterinariosView.css';

const VeterinariosView = () => {
  const [veterinarios, setVeterinarios] = useState([]);
  const [filteredVeterinarios, setFilteredVeterinarios] = useState([]);
  const [especialidades, setEspecialidades] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Estados para filtros
  const [searchTerm, setSearchTerm] = useState('');
  const [especialidadFilter, setEspecialidadFilter] = useState('todos');

  const BASE_URL = 'https://veterinariaclinicabackend-production.up.railway.app/api/v1';

  // Cargar datos
  useEffect(() => {
    fetchVeterinarios();
    fetchEspecialidades();
  }, []);

  // Aplicar filtros
  useEffect(() => {
    applyFilters();
  }, [veterinarios, searchTerm, especialidadFilter]);

  const applyFilters = () => {
    let filtered = [...veterinarios];

    // Filtro por DNI o nombre completo
    if (searchTerm.trim()) {
      const term = searchTerm.toLowerCase().trim();
      filtered = filtered.filter(veterinario => {
        const nombreCompleto = `${veterinario.nombre} ${veterinario.apellido_paterno} ${veterinario.apellido_materno || ''}`.toLowerCase();
        const dni = veterinario.dni?.toLowerCase() || '';
        
        return nombreCompleto.includes(term) || dni.includes(term);
      });
    }

    // Filtro por especialidad
    if (especialidadFilter !== 'todos') {
      filtered = filtered.filter(veterinario => {
        const especialidad = especialidades.find(e => e.id_especialidad === veterinario.id_especialidad);
        return especialidad?.descripcion.toLowerCase() === especialidadFilter.toLowerCase();
      });
    }

    setFilteredVeterinarios(filtered);
  };

  // Obtener todos los veterinarios
  const fetchVeterinarios = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${BASE_URL}/veterinarios/`, {
        method: 'GET',
        mode: 'cors',
        headers: {
          'Accept': 'application/json',
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setVeterinarios(data.veterinarios || data || []);
      } else {
        const errorData = await response.json().catch(() => ({}));
        console.error('Error al cargar veterinarios:', response.status, errorData);
        
        if (response.status === 404) {
          setVeterinarios([]);
        } else {
          alert(`Error al cargar los veterinarios: ${errorData.detail || response.statusText}`);
        }
      }
    } catch (error) {
      console.error('Error de conexión:', error);
      alert('Error de conexión al cargar veterinarios. Verifique su conexión a internet.');
      setVeterinarios([]);
    } finally {
      setLoading(false);
    }
  };

  // Obtener todas las especialidades
  const fetchEspecialidades = async () => {
    try {
      const response = await fetch(`${BASE_URL}/catalogos/especialidades/`, {
        method: 'GET',
        mode: 'cors',
        headers: {
          'Accept': 'application/json',
        },
      });
      if (response.ok) {
        const data = await response.json();
        setEspecialidades(data || []);
      } else {
        console.error('Error al cargar especialidades:', response.status);
        setEspecialidades([]);
      }
    } catch (error) {
      console.error('Error al cargar especialidades:', error);
      setEspecialidades([]);
    }
  };

  // Función de disponibilidad
  const getDisponibilidad = (veterinario) => {
    return veterinario.disposicion;
  };

  const clearFilters = () => {
    setSearchTerm('');
    setEspecialidadFilter('todos');
  };

  const columns = [
    { 
      key: 'numero', 
      header: 'N°',
      render: (veterinario, index) => {
        // Calcular el índice basado en la lista filtrada
        const filteredIndex = filteredVeterinarios.findIndex(v => v.id_veterinario === veterinario.id_veterinario);
        return String(filteredIndex + 1);
      }
    },
    { key: 'dni', header: 'DNI', render: (veterinario) => veterinario.dni || 'Sin DNI' },
    { key: 'codigo_CMVP', header: 'CMVP', render: (veterinario) => veterinario.codigo_CMVP || 'Sin código' },
    { key: 'nombre', header: 'Nombre', render: (veterinario) => veterinario.nombre || 'Sin nombre' },
    { 
      key: 'apellidos', 
      header: 'Apellidos',
      render: (veterinario) => {
        const apellidos = `${veterinario.apellido_paterno || ''} ${veterinario.apellido_materno || ''}`.trim();
        return apellidos || 'Sin apellidos';
      }
    },
    { 
      key: 'especialidad', 
      header: 'Especialidad',
      render: (veterinario) => {
        const especialidad = especialidades.find(e => e.id_especialidad === veterinario.id_especialidad);
        return especialidad?.descripcion || 'Sin especialidad';
      }
    },
    { 
      key: 'turno', 
      header: 'Turno',
      render: (veterinario) => {
        const turno = veterinario.turno;
        if (!turno) return 'No asignado';
        
        // Capitalizar primera letra
        return turno.charAt(0).toUpperCase() + turno.slice(1).toLowerCase();
      }
    },
    { 
      key: 'disponibilidad', 
      header: 'Disponibilidad',
      render: (veterinario) => {
        const disponibilidad = getDisponibilidad(veterinario);
        let className = '';
        let displayText = disponibilidad;
        
        // Normalizar el texto
        const disponibilidadLower = disponibilidad.toLowerCase();
        
        if (disponibilidadLower.includes('libre')) {
          className = 'status-libre';
          displayText = 'LIBRE';
        } else if (disponibilidadLower.includes('ocupado') || disponibilidadLower.includes('ocupada')) {
          className = 'status-ocupado';
          displayText = 'OCUPADO';
        } else if (disponibilidadLower.includes('fuera')) {
          className = 'status-fuera-turno';
          displayText = 'FUERA DE TURNO';
        } else {
          className = 'status-libre';
          displayText = displayText.toUpperCase();
        }
        
        return (
          <span className={`status-badge ${className}`}>
            {displayText}
          </span>
        );
      }
    }
  ];

  if (loading && veterinarios.length === 0) {
    return (
      <div className="loading-container">
        <p>Cargando veterinarios...</p>
      </div>
    );
  }

  return (
    <div className="veterinarios-view">
      <div className="section-header">
        <h2>SECCIÓN VETERINARIOS 👨‍⚕️</h2>
      </div>

      <div className="veterinarios-table-section">
        <div className="table-header">
          <h3>REGISTROS DE VETERINARIOS</h3>
          <div className="filters-container">
            <div className="search-container">
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Buscar por DNI o nombre..."
                className="search-input"
              />
              <button className="search-btn">
                <img src="https://i.ibb.co/3mvthkJT/Icono-Buscar-Comprimida.png" alt="search" className="search-icon" />
              </button>
            </div>
            <div className="filter-container">
              <select 
                value={especialidadFilter} 
                onChange={(e) => setEspecialidadFilter(e.target.value)}
                className="filter-select"
              >
                <option value="todos">Todas las especialidades</option>
                {especialidades.map(especialidad => (
                  <option key={especialidad.id_especialidad} value={especialidad.descripcion}>
                    {especialidad.descripcion}
                  </option>
                ))}
              </select>
            </div>
            {(searchTerm || especialidadFilter !== 'todos') && (
              <button onClick={clearFilters} className="clear-filters-btn">
                Limpiar filtros
              </button>
            )}
          </div>
        </div>

        {(searchTerm || especialidadFilter !== 'todos') && (
          <div className="results-info">
            <span>
              {filteredVeterinarios.length} de {veterinarios.length} veterinarios 
              {searchTerm && ` que coinciden con "${searchTerm}"`}
              {especialidadFilter !== 'todos' && ` (filtrado por ${especialidadFilter})`}
            </span>
          </div>
        )}

        <Table 
          columns={columns}
          data={filteredVeterinarios}
          emptyMessage="No hay veterinarios registrados"
        />
      </div>
    </div>
  );
};

export default VeterinariosView;
/*import React, { useState } from 'react';
import Table from '../common/Table';

const VeterinariosView = () => {
  const [veterinarios, setVeterinarios] = useState([
    { 
      id: 'C54H67B', 
      dni: '74343', 
      nombre: 'Julio', 
      apellidos: 'Morales Garcia',
      especialidad: 'Radiografia',
      estado: 'LIBRE'
    },
    { 
      id: 'STU562P1', 
      dni: '64331', 
      nombre: 'Maria', 
      apellidos: 'Paz Solano',
      especialidad: 'Traumatologia',
      estado: 'OCUPADO'
    }
  ]);

  const [filtros, setFiltros] = useState({
    busqueda: '',
    especialidad: ''
  });

  const handleFiltroChange = (e) => {
    setFiltros({
      ...filtros,
      [e.target.name]: e.target.value
    });
  };

  const veterinariosFiltrados = veterinarios.filter(vet => {
    return (
      (filtros.busqueda === '' || vet.nombre.toLowerCase().includes(filtros.busqueda.toLowerCase())) &&
      (filtros.especialidad === '' || vet.especialidad.toLowerCase().includes(filtros.especialidad.toLowerCase()))
    );
  });

  const columns = [
    { key: 'id', header: 'N°' },
    { key: 'dni', header: 'DNI' },
    { key: 'id', header: 'CODIGO CMP' },
    { key: 'nombre', header: 'Nombre' },
    { key: 'apellidos', header: 'Apellidos' },
    { key: 'especialidad', header: 'Especialidad' },
    { 
      key: 'estado', 
      header: 'Estado',
      render: (row) => (
        <span className={`status-badge ${row.estado === 'LIBRE' ? 'status-libre' : 'status-ocupado'}`}>
          {row.estado}
        </span>
      )
    }
  ];

  return (
    <div className="veterinarios-view">
      <div className="section-header">
        <h2>Veterinarios</h2>
        <div className="filters-row">
          <input
            type="text"
            name="busqueda"
            placeholder="Buscar veterinario..."
            value={filtros.busqueda}
            onChange={handleFiltroChange}
            className="search-input"
          />
          <select
            name="especialidad"
            value={filtros.especialidad}
            onChange={handleFiltroChange}
          >
            <option value="">Todas las especialidades</option>
            <option value="radiografia">Radiografía</option>
            <option value="traumatologia">Traumatología</option>
            <option value="cirugia">Cirugía</option>
          </select>
        </div>
      </div>

      <div className="veterinarios-table-section">
        <h3>REGISTRO DE VETERINARIOS</h3>
        <Table 
          columns={columns}
          data={veterinariosFiltrados}
          emptyMessage="No hay veterinarios registrados"
        />
      </div>
    </div>
  );
};

export default VeterinariosView;*/