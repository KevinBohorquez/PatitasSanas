import React, { useState, useEffect } from 'react';
import { apiFetch } from '../../api/client';
import Table from '../common/Table';
import Modal from '../ui/Modal/Modal';
import './ListadoMascotas.css';
import HistorialClinicoModal from './HistorialClinico'; // Este archivo puede reutilizarse como base para mostrar información del historial
import Loader from '../ui/Loader/Loader';

const ListadoMascotas = () => {
  const [mascotas, setMascotas] = useState([]);
  const [filtros, setFiltros] = useState({
    especie: '',
    genero: '',
    busqueda: ''
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false); // Estado para manejar la visibilidad del modal
  const [selectedMascota, setSelectedMascota] = useState(null); // Guardar la mascota seleccionada

  // Función para cargar las mascotas desde el endpoint
  const fetchMascotas = async () => {
    try {
      setLoading(true);
      // Un único endpoint enriquecido (especie, raza, próxima cita y última atención
      // resueltas con JOINs en el servidor) reemplaza el patrón N+1 anterior de
      // 1 + N*3 peticiones (/info, /proxima-cita y /ultima-atencion por mascota).
      const response = await apiFetch(
        '/mascotas/enriquecidas?page=1&per_page=20'
      );
      if (!response.ok) {
        throw new Error('Error al cargar las mascotas');
      }
      const data = await response.json();

      const mappedMascotas = data.mascotas.map((mascota) => {
        // Formatear la fecha de última atención
        const ultimaAtencionFecha = mascota.ultima_atencion
          ? new Date(mascota.ultima_atencion).toLocaleDateString('es-PE') // Día/Mes/Año
          : '--';

        return {
          id: mascota.id_mascota,  // Guardamos el ID de la mascota para uso futuro
          nombre: mascota.nombre || '--',
          genero: mascota.sexo || '--',  // 'sexo' es equivalente a 'genero' en la tabla
          color: mascota.color || '--',
          especie: mascota.especie || '--',
          raza: mascota.raza || '--',
          proximaCita: mascota.proxima_cita || '--',
          ultimaAtencion: ultimaAtencionFecha,  // Última atención con formato de fecha
        };
      });

      setMascotas(mappedMascotas);
    } catch (err) {
      console.error(err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMascotas();
  }, []);

  const handleFiltroChange = (e) => {
    setFiltros({
      ...filtros,
      [e.target.name]: e.target.value
    });
  };

  const handleHistorialClick = (id) => {
    // Buscar la mascota seleccionada
    const mascotaSeleccionada = mascotas.find((mascota) => mascota.id === id);
    setSelectedMascota(mascotaSeleccionada); // Asignar la mascota seleccionada
    setIsModalOpen(true); // Abre el modal
  };

  const handleCloseModal = () => {
    setIsModalOpen(false); // Cierra el modal
    setSelectedMascota(null); // Limpiar la mascota seleccionada
  };

  const mascotasFiltradas = mascotas.filter((mascota) => {
    return (
      (filtros.especie === '' || mascota.especie?.toLowerCase().includes(filtros.especie.toLowerCase())) &&
      (filtros.genero === '' || mascota.genero === filtros.genero) &&
      (filtros.busqueda === '' || mascota.nombre.toLowerCase().includes(filtros.busqueda.toLowerCase()))
    );
  });

  const columns = [
    { key: 'nombre', header: 'NOMBRE' },
    { key: 'especie', header: 'ESPECIE' },
    { key: 'raza', header: 'RAZA' },
    { key: 'genero', header: 'GÉNERO' },
    { key: 'color', header: 'COLOR' },
    { key: 'proximaCita', header: 'PRÓXIMA CITA' },
    { key: 'ultimaAtencion', header: 'ÚLTIMA ATENCIÓN' },
    { key: 'historial', header: 'HISTORIAL CLÍNICO' }
  ];

  const dataWithHistorial = mascotasFiltradas.map((mascota) => ({
    ...mascota,
    historial: (
      <button 
        onClick={() => handleHistorialClick(mascota.id)}
        className="btn btn-primary"
      >
        Ver Historial Clínico
      </button>
    )
  }));

  if (loading) {
    return <Loader message="Cargando mascotas" />;
  }

  if (error) {
    return (
      <div>
        <p>Error: {error}</p>
        <button onClick={fetchMascotas}>Reintentar</button>
      </div>
    );
  }

  return (
    <div className="listado-mascotas container">
      <div className="section-header">
        <h2>Listado de Mascotas</h2>
        
        <div className="filters-row">
          <input
            type="text"
            name="busqueda"
            placeholder="Buscar mascota..."
            value={filtros.busqueda}
            onChange={handleFiltroChange}
            className="search-input"
          />
          
          <select
            name="especie"
            value={filtros.especie}
            onChange={handleFiltroChange}
            className="filter-select"
          >
            <option value="">Todas las especies</option>
            <option value="perro">Perro</option>
            <option value="gato">Gato</option>
          </select>
          
          <select
            name="genero"
            value={filtros.genero}
            onChange={handleFiltroChange}
            className="filter-select"
          >
            <option value="">Todos los géneros</option>
            <option value="Macho">Macho</option>
            <option value="Hembra">Hembra</option>
          </select>
        </div>
      </div>

      <Table 
        columns={columns}
        data={dataWithHistorial}
        emptyMessage="No se encontraron mascotas"
      />

      {/* Modal para mostrar el historial clínico */}
      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title="Historial Clínico de la Mascota"
        size="large"
      >
        <HistorialClinicoModal
          isOpen={isModalOpen}
          mascotaId={selectedMascota?.id}  // Le pasamos la ID de la mascota
          onClose={handleCloseModal}
        />
       </Modal>
    </div>
  );
};

export default ListadoMascotas;
