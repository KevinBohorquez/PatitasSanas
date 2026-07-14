import React, { useState, useEffect } from 'react';
import './HistorialClinico.css';
import Loader from '../common/Loader/Loader';
import EmptyState from '../common/EmptyState/EmptyState';

const HistorialClinicoModal = ({ isOpen, mascotaId, onClose }) => {
  const [consultas, setConsultas] = useState([]); // Historial detallado por consulta
  const [selectedIndex, setSelectedIndex] = useState(0); // Consulta seleccionada en el panel
  const [showDiagnostico, setShowDiagnostico] = useState(false); // Modal de diagnóstico completo
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Cargar el historial clínico detallado (una entrada por consulta, con edad/peso/observaciones
  // y sus diagnósticos con patología).
  const fetchHistorialDetallado = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(
        `/api/v1/consultas/historialDetallado/${mascotaId}?limit=50`
      );
      if (!response.ok) {
        throw new Error('Error al cargar el historial clínico');
      }
      const data = await response.json();
      setConsultas(data);
      setSelectedIndex(0); // Por defecto se muestra la consulta más reciente
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (mascotaId) {
      fetchHistorialDetallado();
    }
  }, [mascotaId]);

  if (!isOpen) return null;

  const formatFecha = (valor) => (valor ? new Date(valor).toLocaleString() : '--');

  const formatEdad = (meses) => {
    if (meses === null || meses === undefined) return '--';
    const anios = Math.floor(meses / 12);
    const resto = meses % 12;
    if (anios > 0) return `${anios} año(s) ${resto} mes(es)`;
    return `${resto} mes(es)`;
  };

  const formatBool = (valor) => {
    if (valor === null || valor === undefined) return '--';
    return valor ? 'Sí' : 'No';
  };

  const consultaSel = consultas[selectedIndex] || null;

  return (
    <div className="form-section">
      <h2>Historial Clínico de la Mascota</h2>

      {loading && <Loader message="Cargando historial clínico" />}
      {error && <p>Error: {error}</p>}

      {!loading && !error && consultas.length === 0 && (
        <EmptyState title="Sin consultas" message="No se encontraron consultas para esta mascota." size={120} />
      )}

      {/* Panel de la consulta seleccionada */}
      {consultaSel && (
        <div className="form-container">
          <div className="form-group">
            <label>Fecha de la Consulta:</label>
            <input type="text" value={formatFecha(consultaSel.fecha_consulta)} disabled />
          </div>

          <div className="form-group">
            <label>Tipo de Consulta:</label>
            <input type="text" value={consultaSel.tipo_consulta || '--'} disabled />
          </div>

          <div className="form-group">
            <label>Motivo de Consulta:</label>
            <input type="text" value={consultaSel.motivo_consulta || '--'} disabled />
          </div>

          <div className="form-group">
            <label>Síntomas Observados:</label>
            <input type="text" value={consultaSel.sintomas_observados || '--'} disabled />
          </div>

          <div className="form-group">
            <label>Condición General:</label>
            <input type="text" value={consultaSel.condicion_general || '--'} disabled />
          </div>

          <div className="form-group">
            <label>Edad en Meses:</label>
            <input type="text" value={formatEdad(consultaSel.edad_meses)} disabled />
          </div>

          <div className="form-group">
            <label>Peso en el Momento:</label>
            <input type="text" value={consultaSel.peso_momento ?? '--'} disabled />
          </div>

          <div className="form-group">
            <label>Veterinario Responsable:</label>
            <input type="text" value={consultaSel.veterinario || '--'} disabled />
          </div>

          <div className="form-group">
            <label>Diagnóstico Preliminar:</label>
            <input type="text" value={consultaSel.diagnostico_preliminar || '--'} disabled />
          </div>

          <div className="form-group">
            <label>Observaciones:</label>
            <input
              type="text"
              value={consultaSel.observaciones || consultaSel.observaciones_historial || '--'}
              disabled
            />
          </div>

          <div className="form-group historial-diagnostico-action">
            <button
              type="button"
              className="btn-diagnostico"
              disabled={!consultaSel.diagnosticos || consultaSel.diagnosticos.length === 0}
              onClick={() => setShowDiagnostico(true)}
            >
              {consultaSel.diagnosticos && consultaSel.diagnosticos.length > 0
                ? `Ver diagnóstico completo (${consultaSel.diagnosticos.length})`
                : 'Sin diagnóstico registrado'}
            </button>
          </div>
        </div>
      )}

      {/* Lista de consultas: al hacer click se actualiza el panel superior */}
      {consultas.length > 0 && (
        <div className="consulta-list">
          <h3>Consultas Realizadas</h3>
          <table>
            <thead>
              <tr>
                <th>Fecha de Consulta</th>
                <th>Tipo de Consulta</th>
                <th>Motivo de Consulta</th>
                <th>Diagnósticos</th>
              </tr>
            </thead>
            <tbody>
              {consultas.map((consulta, index) => (
                <tr
                  key={consulta.id_consulta}
                  className={index === selectedIndex ? 'consulta-row-active' : ''}
                  onClick={() => setSelectedIndex(index)}
                >
                  <td>{formatFecha(consulta.fecha_consulta)}</td>
                  <td>{consulta.tipo_consulta}</td>
                  <td>{consulta.motivo_consulta}</td>
                  <td>{consulta.diagnosticos ? consulta.diagnosticos.length : 0}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Modal con el detalle completo de los diagnósticos de la consulta seleccionada */}
      {showDiagnostico && consultaSel && (
        <div className="diagnostico-overlay" onClick={() => setShowDiagnostico(false)}>
          <div className="diagnostico-modal" onClick={(e) => e.stopPropagation()}>
            <h3>Diagnóstico(s) de la consulta</h3>
            {consultaSel.diagnosticos.map((d) => (
              <div key={d.id_diagnostico} className="diagnostico-card">
                <p><strong>Diagnóstico:</strong> {d.diagnostico || '--'}</p>
                <p><strong>Tipo:</strong> {d.tipo_diagnostico || '--'}</p>
                <p><strong>Estado de la patología:</strong> {d.estado_patologia || '--'}</p>
                <p><strong>Fecha:</strong> {formatFecha(d.fecha_diagnostico)}</p>
                {d.patologia ? (
                  <div className="diagnostico-patologia">
                    <p><strong>Patología:</strong> {d.patologia.nombre || '--'}</p>
                    <p><strong>Gravedad:</strong> {d.patologia.gravedad || '--'}</p>
                    <p><strong>Especie afectada:</strong> {d.patologia.especie_afecta || '--'}</p>
                    <p><strong>¿Contagiosa?:</strong> {formatBool(d.patologia.es_contagiosa)}</p>
                    <p><strong>¿Crónica?:</strong> {formatBool(d.patologia.es_cronica)}</p>
                  </div>
                ) : (
                  <p><em>Sin patología asociada</em></p>
                )}
              </div>
            ))}
            <button onClick={() => setShowDiagnostico(false)} className="btn-close">Cerrar detalle</button>
          </div>
        </div>
      )}

      <button onClick={onClose} className="btn-close">Cerrar</button>
    </div>
  );
};

export default HistorialClinicoModal;
