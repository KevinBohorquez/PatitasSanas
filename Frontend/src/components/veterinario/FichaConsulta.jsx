// components/veterinario/FichaConsulta.jsx
import React, { useState, useEffect } from 'react';
import Modal from '../common/Modal';
import ModificarDiagnostico from './ModificarDiagnostico';
import ModificarServicio from './ModificarServicio';
import { useAuth } from '../../context/AuthContext';


const FichaConsulta = ({ solicitud, onComplete, onCancel }) => {
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    motivoConsulta: '',
    diagnosticoPreliminar: '',
    sintomasObservados: '',
    observaciones: '',
    condicionGeneral: 'Select',
    tipoConsulta: '',
    esSeguimiento: false
  });

  const [showModificarDiagnostico, setShowModificarDiagnostico] = useState(false);
  const [showModificarServicio, setShowModificarServicio] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [consultaData, setConsultaData] = useState(null);
  const [triageData, setTriageData] = useState(null);
  const [diagnosticos, setDiagnosticos] = useState([]);
  const [diagnosticoId, setDiagnosticoId] = useState(null);

  // Cargar datos de triaje
  const fetchTriageData = async () => {
    if (!solicitud?.id) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const response = await fetch(`https://veterinariaclinicabackend-production.up.railway.app/api/v1/triaje/consulta/${solicitud.id}`);
      
      if (response.ok) {
        const triageResult = await response.json();
        setTriageData(triageResult);
        console.log('Triaje cargado para consulta:', triageResult);
        
        await fetchConsultaData(triageResult.id_triaje);
        await fetchDiagnosticos(triageResult.id_triaje);
      } else {
        throw new Error('Error al cargar datos de triaje');
      }
    } catch (error) {
      console.error('Error al cargar triaje:', error);
      setError(error.message);
      setLoading(false);
    }
  };

  // Cargar datos de consulta
  const fetchConsultaData = async (idTriaje) => {
    try {
      const response = await fetch('https://veterinariaclinicabackend-production.up.railway.app/api/v1/consultas/');
      
      if (response.ok) {
        const data = await response.json();
        const consultaEncontrada = data.consultas.find(
          consulta => consulta.id_triaje === idTriaje
        );
        
        if (consultaEncontrada) {
          setConsultaData(consultaEncontrada);
          console.log('Consulta encontrada:', consultaEncontrada);
          
          setFormData({
            motivoConsulta: consultaEncontrada.motivo_consulta || '',
            diagnosticoPreliminar: consultaEncontrada.diagnostico_preliminar || '',
            sintomasObservados: consultaEncontrada.sintomas_observados || '',
            observaciones: consultaEncontrada.observaciones || '',
            condicionGeneral: consultaEncontrada.condicion_general || 'Select',
            tipoConsulta: consultaEncontrada.tipo_consulta || '',
            esSeguimiento: consultaEncontrada.es_seguimiento || false
          });
        } else {
          console.log('No existe consulta para este triaje, creando nueva');
        }
      } else {
        throw new Error('Error al cargar datos de consulta');
      }
    } catch (error) {
      console.error('Error al cargar consulta:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  // Cargar los diagnósticos de la consulta
  const fetchDiagnosticos = async (idTriaje) => {
    try {
      const response = await fetch(`https://veterinariaclinicabackend-production.up.railway.app/api/v1/consultas/diagnosticos/${idTriaje}`);
      
      if (response.ok) {
        const diagnosticosData = await response.json();
        setDiagnosticos(diagnosticosData);
        console.log('Diagnósticos cargados:', diagnosticosData);
      } else {
        console.log('No se encontraron diagnósticos para esta consulta');
        setDiagnosticos([]);
      }
    } catch (error) {
      console.error('Error al cargar diagnósticos:', error);
      setError(error.message);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
  };
  
  const actualizarDisposicion = async () => {
      try {
        const response = await fetch(
          `https://veterinariaclinicabackend-production.up.railway.app/api/v1/veterinarios/veterinario/usuario/${user.id}/disposicionLibre`,
          {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json'
            }
          }
        );

        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`Error ${response.status}: ${errorText}`);
        }

        const result = await response.json();
        console.log('Disposición actualizada:', result);
      } catch (error) {
        console.error('Error al actualizar disposición:', error);
        alert(`Error al actualizar disposición del veterinario: ${error.message}`);
      }
    };


  const handleSubmit = async (e) => {
      e.preventDefault();

      if (!formData.motivoConsulta.trim()) {
        alert('El motivo de la consulta es obligatorio');
        return;
      }
      if (!formData.tipoConsulta.trim()) {
        alert('El tipo de consulta es obligatorio');
        return;
      }
      if (formData.condicionGeneral === 'Select') {
        alert('Debe seleccionar una condición general');
        return;
      }

      const payload = {
        tipo_consulta: formData.tipoConsulta,
        motivo_consulta: formData.motivoConsulta,
        sintomas_observados: formData.sintomasObservados,
        diagnostico_preliminar: formData.diagnosticoPreliminar,
        observaciones: formData.observaciones,
        condicion_general: formData.condicionGeneral,
        es_seguimiento: formData.esSeguimiento
      };

      console.log('Datos de consulta preparados para enviar:', payload);

      try {
        let response;

        if (consultaData) {
          // Si existe, ACTUALIZAR
          const url = `https://veterinariaclinicabackend-production.up.railway.app/api/v1/consultas/${consultaData.id_consulta}`;
          response = await fetch(url, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
          });
        } else {
          alert('La creación de nuevas consultas aún no está implementada.');
          return;
        }

        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`Error ${response.status}: ${errorText}`);
        }

        const result = await response.json();
        console.log('Consulta actualizada correctamente:', result);

        // 🚀 Aquí actualizas la disposición:
        await actualizarDisposicion();

        alert('Consulta actualizada correctamente.');
        onComplete();

      } catch (error) {
        console.error('Error al guardar consulta:', error);
        alert(`Error al guardar la consulta: ${error.message}`);
      }
    };


  const handleModificarDiagnostico = (id) => {
    setDiagnosticoId(id);
    setShowModificarDiagnostico(true);
  };

  // Función para añadir diagnóstico
  const handleAñadirDiagnostico = async () => {
    if (!consultaData?.id_consulta) {
      alert('No hay una consulta activa para añadir diagnóstico');
      return;
    }

    try {
      console.log('Añadiendo diagnóstico para consulta:', consultaData.id_consulta);
      
      const response = await fetch(
        `https://veterinariaclinicabackend-production.up.railway.app/api/v1/consultas/diagnostico/${consultaData.id_consulta}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Error ${response.status}: ${errorText}`);
      }

      const result = await response.json();
      console.log('Diagnóstico añadido exitosamente:', result);
      
      alert(`Diagnóstico añadido correctamente. ID: ${result.id}`);
      
      if (triageData?.id_triaje) {
        await fetchDiagnosticos(triageData.id_triaje);
      }
      
    } catch (error) {
      console.error('Error al añadir diagnóstico:', error);
      alert(`Error al añadir diagnóstico: ${error.message}`);
    }
  };

  // Función para añadir servicio - CORREGIDA
  const handleAñadirServicio = () => {
    if (!consultaData?.id_consulta) {
      alert('No hay consulta activa para añadir servicio');
      return;
    }

    console.log('Abriendo modal de servicio para consulta ID:', consultaData.id_consulta);
    setShowModificarServicio(true);
  };

  useEffect(() => {
    fetchTriageData();
  }, [solicitud]);

  if (loading) {
    return (
      <div className="ficha-consulta">
        <div className="loading-message">
          <p>Cargando datos de la consulta...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="ficha-consulta">
        <div className="error-message">
          <p>Error: {error}</p>
          <button onClick={() => fetchTriageData()} className="btn-retry">
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  return (
    <>
      <form onSubmit={handleSubmit} className="ficha-consulta">
        <div className="form-section">
          <h3>Datos de la consulta</h3>
          {consultaData && (
            <div className="info-banner">
              <p>ℹ️ Editando consulta existente del {new Date(consultaData.fecha_consulta).toLocaleString()}</p>
            </div>
          )}

          {/* Campos del formulario */}
          <div className="form-row">
            <div className="form-group">
              <label>TIPO DE CONSULTA *</label>
              <input
                type="text"
                name="tipoConsulta"
                value={formData.tipoConsulta}
                onChange={handleChange}
                placeholder="ej: Consulta general, Consulta de seguimiento"
                required
              />
            </div>

            <div className="form-group">
              <label>ES SEGUIMIENTO</label>
              <input
                type="checkbox"
                name="esSeguimiento"
                checked={formData.esSeguimiento}
                onChange={handleChange}
              />
            </div>
          </div>

          <div className="form-group full-width">
            <label>MOTIVO DE LA CONSULTA *</label>
            <textarea
              name="motivoConsulta"
              value={formData.motivoConsulta}
              onChange={handleChange}
              rows="3"
              required
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>DIAGNÓSTICO PRELIMINAR</label>
              <input
                type="text"
                name="diagnosticoPreliminar"
                value={formData.diagnosticoPreliminar}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label>SÍNTOMAS OBSERVADOS</label>
              <input
                type="text"
                name="sintomasObservados"
                value={formData.sintomasObservados}
                onChange={handleChange}
              />
            </div>
          </div>

          <div className="form-group full-width">
            <label>OBSERVACIONES</label>
            <textarea
              name="observaciones"
              value={formData.observaciones}
              onChange={handleChange}
              rows="3"
            />
          </div>

          <div className="form-group">
            <label>CONDICIÓN GENERAL *</label>
            <select
              name="condicionGeneral"
              value={formData.condicionGeneral}
              onChange={handleChange}
              required
            >
              <option value="Select">Select</option>
              <option value="Excelente">Excelente</option>
              <option value="Buena">Buena</option>
              <option value="Regular">Regular</option>
              <option value="Mala">Mala</option>
              <option value="Critica">Crítica</option>
            </select>
          </div>

          {/* Tabla de diagnósticos */}
          {diagnosticos.length > 0 && (
            <div className="consulta-list">
              <h4>Diagnósticos</h4>
              <table>
                <thead>
                  <tr>
                    <th>Diagnóstico</th>
                    <th>Tipo</th>
                    <th>Fecha</th>
                    <th>Acción</th>
                  </tr>
                </thead>
                <tbody>
                  {diagnosticos.map((diagnostico) => (
                    <tr key={diagnostico.id_diagnostico}>
                      <td>{diagnostico.diagnostico || ''}</td>
                      <td>{diagnostico.tipo_diagnostico || ''}</td>
                      <td>{diagnostico.fecha_diagnostico ? new Date(diagnostico.fecha_diagnostico).toLocaleString() : ''}</td>
                      <td>
                        <button type="button" onClick={() => handleModificarDiagnostico(diagnostico.id_diagnostico)}>
                          Modificar Diagnóstico
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="form-actions">
          <button 
            type="button" 
            onClick={handleAñadirDiagnostico}
            className="btn-secondary"
          >
            Añadir Diagnóstico
          </button>
          <button 
            type="button" 
            onClick={handleAñadirServicio}
            className="btn-secondary"
          >
            Añadir Servicio
          </button>
          <button type="submit" className="btn-submit">
            {consultaData ? 'Actualizar Consulta' : 'Guardar Consulta'}
          </button>
          <button type="button" onClick={onCancel} className="btn-cancel">
            Cancelar
          </button>
        </div>
      </form>

      <Modal
        isOpen={showModificarDiagnostico}
        onClose={() => setShowModificarDiagnostico(false)}
        title="Modificar Diagnóstico"
        size="large"
      >
        <ModificarDiagnostico 
          diagnosticoId={diagnosticoId}
          onSave={async () => {
            setShowModificarDiagnostico(false);
            if (triageData?.id_triaje) {
              await fetchDiagnosticos(triageData.id_triaje);
            }
          }}
          onCancel={() => setShowModificarDiagnostico(false)}
        />
      </Modal>

      <Modal
        isOpen={showModificarServicio}
        onClose={() => setShowModificarServicio(false)}
        title="Añadir Servicio"
        size="large"
      >
        <ModificarServicio 
          consultaId={consultaData?.id_consulta}
          onSave={async () => {
            setShowModificarServicio(false);
            alert('Servicio creado correctamente');
          }}
          onCancel={() => setShowModificarServicio(false)}
        />
      </Modal>
    </>
  );
};

export default FichaConsulta;