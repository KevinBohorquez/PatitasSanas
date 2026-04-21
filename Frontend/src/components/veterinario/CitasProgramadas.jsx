import React, { useState, useEffect } from 'react';
import Table from '../common/Table';
import Modal from '../common/Modal';
import AtenderCita from './AtenderCita';
import { useAuth } from "../../context/AuthContext";

const CitasProgramadas = () => {
  const { user } = useAuth();
  const [citas, setCitas] = useState([]);
  const [selectedCita, setSelectedCita] = useState(null);
  const [showAtender, setShowAtender] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchCitas = async () => {
    try {
      setLoading(true);

      // ✅ Aquí llamas a tu endpoint nuevo
      const response = await fetch(
        `https://veterinariaclinicabackend-production.up.railway.app/api/v1/veterinarios/resultados-citas/${user.id}`
      );
      if (!response.ok) {
        throw new Error('Error al cargar citas');
      }
      const data = await response.json();

      // ✅ Para cada resultado, pedir info adicional de la cita
      const citasConDatos = await Promise.all(
        data.map(async (item) => {
          const cita = item.cita || {};
          const fechaObj = new Date(cita.fecha_hora_programada);

          // Fetch mascota
          const mascotaRes = await fetch(
            `https://veterinariaclinicabackend-production.up.railway.app/api/v1/consultas/citaMascota/${cita.id_cita}`
          );
          const mascotaData = await mascotaRes.json();

          // Fetch servicio
          const servicioRes = await fetch(
            `https://veterinariaclinicabackend-production.up.railway.app/api/v1/consultas/citaServicio/${cita.id_cita}`
          );
          const servicioData = await servicioRes.json();

          // Fetch veterinario
          const veterinarioRes = await fetch(
            `https://veterinariaclinicabackend-production.up.railway.app/api/v1/consultas/citaVeterinario/${cita.id_cita}`
          );
          const veterinarioData = await veterinarioRes.json();

          return {
            id: cita.id_cita,
            id_cita: cita.id_cita, // 👈 ESTE CAMPO
            mascota: mascotaData.nombre_mascota || 'Mascota no encontrada',
            servicio: servicioData.nombre_servicio || 'Servicio no encontrado',
            veterinario: veterinarioData.veterinario || 'Veterinario no encontrado',
            fecha: fechaObj.toLocaleDateString(),
            hora: fechaObj.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            estado: cita.estado_cita
          };
        })
      );

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
  }, [user]);

  const handleAtender = (cita) => {
    if (cita?.id) {
      setSelectedCita(cita);
      setShowAtender(true);
    } else {
      alert('No se puede atender la cita seleccionada.');
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
    return <p>Cargando citas...</p>;
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
      <div className="section-header">
        <h2>Citas Programadas</h2>
      </div>

      <Table
        columns={columns}
        data={citas}
        actions={actions}
        emptyMessage="No hay citas programadas"
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
