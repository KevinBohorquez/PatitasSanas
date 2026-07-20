import React, { useState, useEffect } from 'react';
import { apiFetch } from '../../api/client';
import Table from '../common/Table';
import Modal from '../ui/Modal/Modal';
import AtenderCita from './AtenderCita';
import { useAuth } from "../../context/AuthContext";
import { toast } from '../../utils/toast';
import Loader from '../ui/Loader/Loader';

const CitasProgramadas = () => {
  const { user } = useAuth();
  const [citas, setCitas] = useState([]);
  const [selectedCita, setSelectedCita] = useState(null);
  const [showAtender, setShowAtender] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [vista, setVista] = useState('programadas'); // 'programadas' | 'atendidas'

  const fetchCitas = async () => {
    try {
      setLoading(true);

      // SC-016 / F4: listar por Cita.id_veterinario (incluye las citas creadas
      // por el recepcionista, que antes no aparecían por depender de Resultado_servicio).
      const url = vista === 'atendidas'
        ? `/veterinarios/resultados-citas/${user.id}`
        : `/veterinarios/citas-programadas/${user.id}`;
      const response = await apiFetch(url);
      if (!response.ok) {
        throw new Error('Error al cargar citas');
      }
      const data = await response.json();

      // Los endpoints ya devuelven mascota, servicio y veterinario resueltos por
      // JOIN, así que se elimina el N+1 (antes 3 fetch por cita:
      // citaMascota/citaServicio/citaVeterinario).
      const citasConDatos = data.map((item) => {
        const cita = item.cita || {};
        const fechaObj = new Date(cita.fecha_hora_programada);

        return {
          id: cita.id_cita,
          id_cita: cita.id_cita, // 👈 ESTE CAMPO
          mascota: item.nombre_mascota || 'Mascota no encontrada',
          servicio: item.nombre_servicio || 'Servicio no encontrado',
          veterinario: item.nombre_veterinario || 'Veterinario no encontrado',
          fecha: fechaObj.toLocaleDateString(),
          hora: fechaObj.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          estado: cita.estado_cita
        };
      });

      setCitas(citasConDatos);
    } catch (err) {
      console.error(err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user?.id) {
      fetchCitas();
    }
  }, [user, vista]);

  const handleAtender = (cita) => {
    if (cita?.id) {
      setSelectedCita(cita);
      setShowAtender(true);
    } else {
      toast.warning('No se puede atender la cita seleccionada.');
    }
  };

  const handleAtenderComplete = () => {
    setShowAtender(false);
    setCitas((prev) =>
      prev.map((c) =>
        c.id === selectedCita.id ? { ...c, estado: 'Atendida' } : c
      )
    );
    setSelectedCita(null);
  };

  const columns = [
    { key: 'mascota', header: 'MASCOTA' },
    { key: 'servicio', header: 'SERVICIO' },
    { key: 'veterinario', header: 'VETERINARIO' },
    { key: 'fecha', header: 'FECHA' },
    { key: 'hora', header: 'HORA' },
    {
      key: 'estado',
      header: 'ESTADO',
      render: (row) => (
        <span className={`status-badge status-${row.estado.toLowerCase()}`}>
          {row.estado}
        </span>
      )
    }
  ];

  const actions = [
    {
      label: 'Atender',
      type: 'primary',
      onClick: handleAtender
    }
  ];

  if (loading) {
    return <Loader message="Cargando citas" />;
  }

  if (error) {
    return (
      <div>
        <p>Error: {error}</p>
        <button onClick={fetchCitas}>Reintentar</button>
      </div>
    );
  }

  return (
    <div className="citas-programadas">
      <div className="section-header" style={{ display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap' }}>
        <h2>{vista === 'atendidas' ? 'Citas Atendidas' : 'Citas Programadas'}</h2>
        <select value={vista} onChange={(e) => setVista(e.target.value)} style={{ padding: 8, borderRadius: 6, border: '1px solid #ccc' }}>
          <option value="programadas">Programadas (por atender)</option>
          <option value="atendidas">Atendidas</option>
        </select>
      </div>

      <Table
        columns={columns}
        data={citas}
        actions={vista === 'programadas' ? actions : null}
        emptyMessage={vista === 'atendidas' ? 'No hay citas atendidas' : 'No hay citas programadas'}
      />

      <Modal
        isOpen={showAtender}
        onClose={() => setShowAtender(false)}
        title="Atender Cita"
        size="large"
      >
        <AtenderCita
          cita={selectedCita}
          onComplete={handleAtenderComplete}
          onCancel={() => setShowAtender(false)}
        />
      </Modal>
    </div>
  );
};

export default CitasProgramadas;
