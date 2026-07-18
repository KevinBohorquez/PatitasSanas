import React, { useState, useEffect } from 'react';
import { apiFetch } from '../../api/client';
import { useToast } from '../../context/ToastContext';
import Loader from '../common/Loader/Loader';
import { formatApiError } from '../../utils/apiError';

const AtenderCita = ({ cita, onComplete, onCancel }) => {
  const [formData, setFormData] = useState({
    resultado: '',
    fechaRealizacion: new Date().toISOString().split('T')[0],
    archivoAdjunto: null,
    interpretacion: ''
  });
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const toast = useToast();

  // Cargar resultado de servicio si existe
  const fetchResultadoServicio = async (citaId) => {
    try {
      
      const response = await apiFetch(
        `/consultas/resultado_servicio/${citaId}`
      );
      
      if (!response.ok) {
        if (response.status === 404) {
          setFormData({
            resultado: '',
            interpretacion: '',
            archivoAdjunto: null,
            fechaRealizacion: new Date().toISOString().split('T')[0]
          });
          return;
        }
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Error HTTP ${response.status}`);
      }
      
      const data = await response.json();
      
      setFormData({
        resultado: data.resultado || '',
        interpretacion: data.interpretacion || '',
        archivoAdjunto: data.archivo_adjunto ? data.archivo_adjunto.split('/').pop() : null,
        fechaRealizacion: data.fecha_realizacion ? 
          new Date(data.fecha_realizacion).toISOString().split('T')[0] : 
          new Date().toISOString().split('T')[0]
      });
    } catch (err) {
      console.error('Error al cargar resultado:', err);
      setError(`Error al cargar: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    
    if (cita && cita.id) {
      fetchResultadoServicio(cita.id);
    } else {
      console.error('Cita inválida:', cita);
      setError('No se recibió una cita válida');
      setLoading(false);
    }
  }, [cita]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0] || null;
    // SC-020 / F27: conservar el File real para subirlo a Drive al guardar.
    setFormData({
      ...formData,
      archivoAdjunto: file ? file.name : null,
      archivoAdjuntoFile: file
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!cita || !cita.id) {
      setError('No se puede guardar: ID de cita no válido');
      return;
    }

    if (!formData.resultado.trim()) {
      setError('El resultado es requerido');
      return;
    }

    if (!formData.fechaRealizacion) {
      setError('La fecha de realización es requerida');
      return;
    }
    
    try {
      setLoading(true);
      setError(null);

      // SC-020 / F27: si se seleccionó un archivo, subirlo a Google Drive y usar el
      // enlace devuelto como archivo_adjunto (antes solo se guardaba el nombre).
      let archivoLink = formData.archivoAdjunto || null;
      if (formData.archivoAdjuntoFile) {
        const fd = new FormData();
        fd.append('archivo', formData.archivoAdjuntoFile);
        const upRes = await apiFetch(
          `/consultas/resultado_servicio/${cita.id}/adjunto`,
          { method: 'POST', body: fd }
        );
        if (!upRes.ok) {
          const upErr = await upRes.json().catch(() => null);
          throw new Error((upErr && upErr.detail) || 'No se pudo subir el archivo adjunto a Drive');
        }
        const upData = await upRes.json();
        archivoLink = upData.archivo_adjunto;
      }

      const updatedData = {
        id_cita: cita.id,
        id_veterinario: cita.id_veterinario || 4, // fallback
        resultado: formData.resultado.trim(),
        interpretacion: formData.interpretacion.trim() || null,
        archivo_adjunto: archivoLink,
        fecha_realizacion: `${formData.fechaRealizacion}T00:00:00`
      };

      const response = await apiFetch(
        `/consultas/resultado_servicio/${cita.id}`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(updatedData)
        }
      );

      if (!response.ok) {
        const errorBody = await response.json().catch(() => null);
        throw new Error(formatApiError(errorBody, 'No se pudo guardar el resultado de la cita'));
      }

      await response.json();

      toast.success('Cita atendida exitosamente', { title: 'Cita guardada' });
      onComplete();
      
    } catch (err) {
      console.error('Error al guardar:', err);
      setError(err.message || 'Error desconocido al guardar');
    } finally {
      setLoading(false);
    }
  };

  if (!cita) {
    return <div className="error-message">No se recibió información de la cita</div>;
  }

  if (loading && !error) {
    return <Loader message="Cargando información del resultado" />;
  }

  return (
    <div className="atender-cita-container">
      {error && (
        <div className="error-container">
          <p className="error-message">⚠️ {error}</p>
          <button 
            onClick={() => {
              setError(null);
              setLoading(true);
              fetchResultadoServicio(cita.id);
            }}
            className="btn-retry"
          >
            Reintentar
          </button>
        </div>
      )}

      <form onSubmit={handleSubmit} className="atender-cita">
        <div className="form-section">
          <h3>Datos de la Cita</h3>
          
          <div className="cita-info">
            <p><strong>ID Cita:</strong> {cita.id}</p>
            <p><strong>Mascota:</strong> {cita.mascota}</p>
            <p><strong>Servicio:</strong> {cita.servicio}</p>
            <p><strong>Fecha:</strong> {cita.fecha}</p>
            <p><strong>Hora:</strong> {cita.hora}</p>
          </div>

          <div className="form-group">
            <label>RESULTADO *</label>
            <textarea
              name="resultado"
              value={formData.resultado}
              onChange={handleChange}
              placeholder="Resultado de la consulta"
              rows="4"
              required
              disabled={loading}
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Fecha realización *</label>
              <input
                type="date"
                name="fechaRealizacion"
                value={formData.fechaRealizacion}
                onChange={handleChange}
                required
                disabled={loading}
              />
            </div>
          </div>

          <div className="form-group">
            <label>INTERPRETACIÓN</label>
            <textarea
              name="interpretacion"
              value={formData.interpretacion}
              onChange={handleChange}
              placeholder="Interpretación del resultado (opcional)"
              rows="3"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label>ARCHIVO ADJUNTO</label>
            <input
              type="file"
              name="archivoAdjunto"
              onChange={handleFileChange}
              accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
              disabled={loading}
            />
            <small>
              {formData.archivoAdjunto ? 
                `📎 Archivo: ${formData.archivoAdjunto}` : 
                'No hay archivo adjunto'
              }
            </small>
          </div>
        </div>

        <div className="form-actions">
          <button 
            type="button" 
            onClick={onCancel} 
            className="btn-cancel"
            disabled={loading}
          >
            Cancelar
          </button>
          <button 
            type="submit" 
            className="btn-submit" 
            disabled={loading || !formData.resultado.trim()}
          >
            {loading ? 'Guardando...' : 'Finalizar Atención'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default AtenderCita;
