import React, { useState, useEffect } from 'react';
import './HistorialClinico.css';

const HistorialClinicoModal = ({ isOpen, mascotaId, onClose }) => {
  const [historial, setHistorial] = useState(null); // Guardar el historial clínico
  const [consultas, setConsultas] = useState([]); // Guardar las consultas
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Función para cargar el historial clínico de la mascota con mascotaId
  const fetchHistorialClinico = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        `https://veterinariaclinicabackend-production.up.railway.app/api/v1/consultas/historial/${mascotaId}`
      );
      if (!response.ok) {
        throw new Error('Error al cargar el historial clínico');
      }
      const data = await response.json();
      if (data.length > 0) {
        setHistorial(data[0]); // Usamos el primer objeto del array
      } else {
        setHistorial(null); // Si no hay datos, dejamos historial en null
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Función para cargar las consultas de la mascota
  const fetchConsultas = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        `https://veterinariaclinicabackend-production.up.railway.app/api/v1/consultas/historialConsultas/${mascotaId}?limit=50`
      );
      if (!response.ok) {
        throw new Error('Error al cargar las consultas');
      }
      const data = await response.json();

      if (data.length > 0) {
        setConsultas(data); // Asignamos las consultas al estado
      } else {
        setConsultas([]); // Si no hay consultas, asignamos un array vacío
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (mascotaId) {
      fetchHistorialClinico(); // Cargar el historial clínico al recibir mascotaId
      fetchConsultas(); // Cargar las consultas relacionadas a la mascota
    }
  }, [mascotaId]);

  if (!isOpen) return null; // Si el modal no está abierto, no renderizamos nada

  return (
    <div className="form-section">
      <h2>Historial Clínico de la Mascota</h2>

      {loading && <p>Cargando historial clínico y consultas...</p>}
      {error && <p>Error: {error}</p>}

      {/* Mostrar historial clínico si existe */}
      {historial ? (
        <div className="form-container">
          <div className="form-group">
            <label>Fecha del Evento:</label>
            <input type="text" value={historial.fecha_evento || '--'} disabled />
          </div>

          <div className="form-group">
            <label>Tipo de Evento:</label>
            <input type="text" value={historial.tipo_evento || '--'} disabled />
          </div>

          <div className="form-group">
            <label>Edad en Meses:</label>
            <input type="text" value={historial.edad_meses || '--'} disabled />
          </div>

          <div className="form-group">
            <label>Descripción del Evento:</label>
            <input type="text" value={historial.descripcion_evento || '--'} disabled />
          </div>

          <div className="form-group">
            <label>Peso en el Momento:</label>
            <input type="text" value={historial.peso_momento || '--'} disabled />
          </div>

          <div className="form-group">
            <label>Observaciones:</label>
            <input type="text" value={historial.observaciones || '--'} disabled />
          </div>
        </div>
      ) : (
        <p>No se encontraron datos para el historial clínico.</p>
      )}

      {/* Mostrar lista de consultas si existen */}
      {consultas.length > 0 ? (
        <div className="consulta-list">
          <h3>Consultas Realizadas</h3>
          <table>
            <thead>
              <tr>
                <th>Fecha de Consulta</th>
                <th>Tipo de Consulta</th>
                <th>Motivo de Consulta</th>
                <th>Diagnóstico Preliminar</th>
                <th>Observaciones</th>
              </tr>
            </thead>
            <tbody>
              {consultas.map((consulta) => (
                <tr key={consulta.id_consulta}>
                  <td>{new Date(consulta.fecha_consulta).toLocaleString()}</td>
                  <td>{consulta.tipo_consulta}</td>
                  <td>{consulta.motivo_consulta}</td>
                  <td>{consulta.diagnostico_preliminar}</td>
                  <td>{consulta.observaciones}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p>No se encontraron consultas para esta mascota.</p>
      )}

      <button onClick={onClose} className="btn-close">Cerrar</button>
    </div>
  );
};

export default HistorialClinicoModal;
