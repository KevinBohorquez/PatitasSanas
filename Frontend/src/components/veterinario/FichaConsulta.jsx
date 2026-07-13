// components/veterinario/FichaConsulta.jsx
import React, { useState, useEffect } from 'react';
import Modal from '../common/Modal';
import ModificarDiagnostico from './ModificarDiagnostico';
import ModificarServicio from './ModificarServicio';
import { useAuth } from '../../context/AuthContext';
import { toast } from '../../utils/toast';
import { formatApiError } from '../../utils/apiError';
import Loader from '../common/Loader/Loader';


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
      const response = await fetch(`/api/v1/triaje/consulta/${solicitud.id}`);
      
      if (response.ok) {
        const triageResult = await response.json();
        setTriageData(triageResult);
        
        const consulta = await fetchConsultaData(triageResult.id_triaje);
        // SC-041 / F22: los diagnósticos se piden por id_consulta, no por id_triaje.
        await fetchDiagnosticos(consulta?.id_consulta);
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
      // SC-040 / F21: obtener la consulta del triaje directamente. Antes se traía
      // la primera página de /consultas/ (20 por página) y se filtraba en memoria,
      // lo que fallaba al superar 20 consultas si la del triaje no estaba en esa página.
      const response = await fetch(`/api/v1/consultas/triaje/${idTriaje}`);

      if (response.ok) {
        // El endpoint devuelve la consulta del triaje, o null si aún no existe.
        const consultaEncontrada = await response.json();

        if (consultaEncontrada) {
          setConsultaData(consultaEncontrada);

          setFormData({
            motivoConsulta: consultaEncontrada.motivo_consulta || '',
            diagnosticoPreliminar: consultaEncontrada.diagnostico_preliminar || '',
            sintomasObservados: consultaEncontrada.sintomas_observados || '',
            observaciones: consultaEncontrada.observaciones || '',
            condicionGeneral: consultaEncontrada.condicion_general || 'Select',
            tipoConsulta: consultaEncontrada.tipo_consulta || '',
            esSeguimiento: consultaEncontrada.es_seguimiento || false
          });
        }

        // SC-041 / F22: exponer la consulta cargada para usar su id_consulta.
        return consultaEncontrada;
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
  const fetchDiagnosticos = async (idConsulta) => {
    // SC-041 / F22: el endpoint filtra por id_consulta. Antes se le pasaba id_triaje,
    // que coincidía por casualidad porque id_consulta == id_triaje en los datos
    // actuales (el trigger los crea en lockstep); si divergen, se mostrarían mal.
    if (!idConsulta) {
      setDiagnosticos([]);
      return;
    }
    try {
      const response = await fetch(`/api/v1/consultas/diagnosticos/${idConsulta}`);
      
      if (response.ok) {
        const diagnosticosData = await response.json();
        setDiagnosticos(diagnosticosData);
      } else {
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
          `/api/v1/veterinarios/veterinario/usuario/${user.id}/disposicionLibre`,
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
      } catch (error) {
        console.error('Error al actualizar disposición:', error);
        toast.error(`Error al actualizar disposición del veterinario: ${error.message}`);
      }
    };


  const handleSubmit = async (e) => {
      e.preventDefault();

      if (!formData.motivoConsulta.trim()) {
        toast.warning('El motivo de la consulta es obligatorio');
        return;
      }
      if (!formData.tipoConsulta.trim()) {
        toast.warning('El tipo de consulta es obligatorio');
        return;
      }
      if (formData.condicionGeneral === 'Select') {
        toast.warning('Debe seleccionar una condición general');
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


      try {
        let response;

        if (consultaData) {
          // Si existe, ACTUALIZAR
          const url = `/api/v1/consultas/${consultaData.id_consulta}`;
          response = await fetch(url, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
          });
        } else {
          toast.warning('La creación de nuevas consultas aún no está implementada.');
          return;
        }

        if (!response.ok) {
          const errorBody = await response.json().catch(() => null);
          throw new Error(formatApiError(errorBody, 'No se pudo guardar la consulta'));
        }

        const result = await response.json();

        // 🚀 Aquí actualizas la disposición:
        await actualizarDisposicion();

        toast.success('Consulta actualizada correctamente.');
        // SC-056 / F41: pasar el id_consulta para que el contenedor pueda
        // finalizar la atención (persistir "Completada" y liberar al vet).
        onComplete(consultaData?.id_consulta);

      } catch (error) {
        console.error('Error al guardar consulta:', error);
        toast.error(error.message || 'No se pudo guardar la consulta');
      }
    };


  const handleModificarDiagnostico = (id) => {
    setDiagnosticoId(id);
    setShowModificarDiagnostico(true);
  };

  // Función para añadir diagnóstico
  const handleAñadirDiagnostico = async () => {
    if (!consultaData?.id_consulta) {
      toast.warning('No hay una consulta activa para añadir diagnóstico');
      return;
    }

    try {
      
      const response = await fetch(
        `/api/v1/consultas/diagnostico/${consultaData.id_consulta}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        const errorBody = await response.json().catch(() => null);
        throw new Error(formatApiError(errorBody, 'No se pudo añadir el diagnóstico'));
      }

      const result = await response.json();

      toast.success(`Diagnóstico añadido correctamente. ID: ${result.id}`);
      
      if (consultaData?.id_consulta) {
        await fetchDiagnosticos(consultaData.id_consulta);
      }

    } catch (error) {
      console.error('Error al añadir diagnóstico:', error);
      toast.error(error.message || 'No se pudo añadir el diagnóstico');
    }
  };

  // Función para añadir servicio - CORREGIDA
  const handleAñadirServicio = () => {
    if (!consultaData?.id_consulta) {
      toast.warning('No hay consulta activa para añadir servicio');
      return;
    }

    setShowModificarServicio(true);
  };

  useEffect(() => {
    fetchTriageData();
  }, [solicitud]);

  if (loading) {
    return (
      <div className="ficha-consulta">
        <div className="loading-message">
          <Loader message="Cargando datos de la consulta" />
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
            if (consultaData?.id_consulta) {
              await fetchDiagnosticos(consultaData.id_consulta);
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
            toast.success('Servicio creado correctamente');
          }}
          onCancel={() => setShowModificarServicio(false)}
        />
      </Modal>
    </>
  );
};

export default FichaConsulta;