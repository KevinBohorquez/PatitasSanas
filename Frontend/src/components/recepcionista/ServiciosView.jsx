import React, { useState, useEffect } from 'react';
import Table from '../common/Table';
import './ServiciosView.css';

const ServiciosView = () => {
  const [servicios, setServicios] = useState([]);
  const [filteredServicios, setFilteredServicios] = useState([]);
  const [tiposServicio, setTiposServicio] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Estados para filtros
  const [searchTerm, setSearchTerm] = useState('');
  const [tipoFilter, setTipoFilter] = useState('todos');

  const BASE_URL = 'https://veterinariaclinicabackend-production.up.railway.app/api/v1';

  // Cargar datos
  useEffect(() => {
    fetchServicios();
    fetchTiposServicio();
  }, []);

  // Aplicar filtros 
  useEffect(() => {
    applyFilters();
  }, [servicios, searchTerm, tipoFilter]);

  const applyFilters = () => {
    let filtered = [...servicios];

    // Filtro por nombre del servicio
    if (searchTerm.trim()) {
      const term = searchTerm.toLowerCase().trim();
      filtered = filtered.filter(servicio => {
        const nombreServicio = servicio.nombre_servicio?.toLowerCase() || '';
        return nombreServicio.includes(term);
      });
    }

    // Filtro por tipo de servicio
    if (tipoFilter !== 'todos') {
      filtered = filtered.filter(servicio => {
        const tipoServicio = tiposServicio.find(t => t.id_tipo_servicio === servicio.id_tipo_servicio);
        return tipoServicio?.descripcion.toLowerCase() === tipoFilter.toLowerCase();
      });
    }

    setFilteredServicios(filtered);
  };

  // Obtener todos los servicios
  const fetchServicios = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${BASE_URL}/catalogos/servicios/`, {
        method: 'GET',
        mode: 'cors',
        headers: {
          'Accept': 'application/json',
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        // Servicios activos
        const serviciosActivos = (data.servicios || data || []).filter(servicio => servicio.activo !== false);
        setServicios(serviciosActivos);
      } else {
        const errorData = await response.json().catch(() => ({}));
        console.error('Error al cargar servicios:', response.status, errorData);
        
        if (response.status === 404) {
          setServicios([]);
        } else {
          alert(`Error al cargar los servicios: ${errorData.detail || response.statusText}`);
        }
      }
    } catch (error) {
      console.error('Error de conexión:', error);
      alert('Error de conexión al cargar servicios. Verifique su conexión a internet.');
      setServicios([]);
    } finally {
      setLoading(false);
    }
  };

  // Obtener todos los tipos de servicio
  const fetchTiposServicio = async () => {
    try {
      const response = await fetch(`${BASE_URL}/catalogos/tipos-servicio/`, {
        method: 'GET',
        mode: 'cors',
        headers: {
          'Accept': 'application/json',
        },
      });
      if (response.ok) {
        const data = await response.json();
        setTiposServicio(data.tipos_servicio || data || []);
      } else {
        console.error('Error al cargar tipos de servicio:', response.status);
        setTiposServicio([]);
      }
    } catch (error) {
      console.error('Error al cargar tipos de servicio:', error);
      setTiposServicio([]);
    }
  };

  const clearFilters = () => {
    setSearchTerm('');
    setTipoFilter('todos');
  };

  const columns = [
    { 
      key: 'numero', 
      header: 'N°',
      render: (servicio, index) => {
        // Calcular el índice basado en la lista filtrada
        const filteredIndex = filteredServicios.findIndex(s => s.id_servicio === servicio.id_servicio);
        return String(filteredIndex + 1);
      }
    },
    { 
      key: 'nombre_servicio', 
      header: 'Servicio',
      render: (servicio) => servicio.nombre_servicio || 'Sin nombre'
    },
    { 
      key: 'tipo', 
      header: 'Tipo',
      render: (servicio) => {
        const tipoServicio = tiposServicio.find(t => t.id_tipo_servicio === servicio.id_tipo_servicio);
        return tipoServicio?.descripcion || 'Sin tipo';
      }
    },
    { 
      key: 'precio', 
      header: 'Precio',
      render: (servicio) => {
        const precio = parseFloat(servicio.precio || 0);
        return (
          <div className="precio-container">
            <span className="precio-badge">
              S/ {precio.toFixed(2)}
            </span>
          </div>
        );
      }
    }
  ];

  if (loading && servicios.length === 0) {
    return (
      <div className="loading-container">
        <p>Cargando servicios...</p>
      </div>
    );
  }

  return (
    <div className="servicios-view">
      <div className="section-header">
        <h2>SECCIÓN SERVICIOS 🗂️</h2>
      </div>

      <div className="servicios-table-section">
        <div className="table-header">
          <h3>SERVICIOS DISPONIBLES</h3>
          <div className="filters-container">
            <div className="search-container">
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Buscar servicio..."
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
                <option value="todos">Tipo de servicio</option>
                {tiposServicio.map(tipo => (
                  <option key={tipo.id_tipo_servicio} value={tipo.descripcion}>
                    {tipo.descripcion}
                  </option>
                ))}
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
              {filteredServicios.length} de {servicios.length} servicios 
              {searchTerm && ` que coinciden con "${searchTerm}"`}
              {tipoFilter !== 'todos' && ` (filtrado por ${tipoFilter})`}
            </span>
          </div>
        )}

        <Table 
          columns={columns}
          data={filteredServicios}
          emptyMessage="No hay servicios disponibles"
        />
      </div>
    </div>
  );
};

export default ServiciosView;