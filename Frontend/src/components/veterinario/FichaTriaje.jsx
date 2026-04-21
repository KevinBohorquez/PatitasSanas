// components/veterinario/FichaTriaje.jsx
import React, { useState, useEffect } from 'react';


const FichaTriaje = ({ solicitud, onComplete, onCancel }) => {
  const [formData, setFormData] = useState({
    peso: '',
    latidosPm: '',
    frecuenciaResp: '',
    temperatura: '',
    talla: '',
    tiempoCapilar: '',
    colorMucosas: '',
    frecuenciaPulso: '',
    deshidratacion: '',
    condicionCorporal: 'Select',
    clasificacionUrgencia: 'Select'
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [triageData, setTriageData] = useState(null);

  // Función para cargar datos de triaje existente
  const fetchTriageData = async () => {
    if (!solicitud?.id) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      // Usando el ID de la solicitud como triaje_id
      // Si tienes una relación diferente, ajusta según tu modelo de datos
      const response = await fetch(`https://veterinariaclinicabackend-production.up.railway.app/api/v1/triaje/consulta/${solicitud.id}`);
      
      if (response.ok) {
        const data = await response.json();
        setTriageData(data);
        
        // Mapear los datos de la API al formulario
        setFormData({
          peso: data.peso_mascota?.toString() || '',
          latidosPm: data.latido_por_minuto?.toString() || '',
          frecuenciaResp: data.frecuencia_respiratoria_rpm?.toString() || '',
          temperatura: data.temperatura?.toString() || '',
          talla: data.talla?.toString() || '',
          tiempoCapilar: data.tiempo_capilar || '',
          colorMucosas: data.color_mucosas || '',
          frecuenciaPulso: data.frecuencia_pulso?.toString() || '',
          deshidratacion: data.porce_deshidratacion?.toString() || '',
          condicionCorporal: data.condicion_corporal || 'Select',
          clasificacionUrgencia: mapearClasificacionUrgencia(data.clasificacion_urgencia) || 'Select'
        });
      } else if (response.status === 404) {
        // No existe triaje aún, mantener formulario vacío
        console.log('No existe triaje para esta solicitud, creando nuevo');
      } else {
        throw new Error('Error al cargar datos de triaje');
      }
    } catch (error) {
      console.error('Error al cargar triaje:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  // Función para mapear clasificación de urgencia de la API al formulario
  const mapearClasificacionUrgencia = (clasificacionAPI) => {
    const mapeo = {
      'No urgente': 'Baja',
      'Poco urgente': 'Media',
      'Urgente': 'Alta',
      'Muy urgente': 'Crítica'
    };
    return mapeo[clasificacionAPI] || clasificacionAPI;
  };

  // Función para mapear clasificación de urgencia del formulario a la API
  const mapearClasificacionUrgenciaParaAPI = (clasificacionForm) => {
    const mapeo = {
      'Baja': 'No urgente',
      'Media': 'Poco urgente',
      'Alta': 'Urgente',
      'Crítica': 'Muy urgente'
    };
    return mapeo[clasificacionForm] || clasificacionForm;
  };

  // Cargar datos al montar el componente
  useEffect(() => {
    fetchTriageData();
  }, [solicitud]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      // Preparar datos para enviar a la API
      const triageDataToSend = {
        id_solicitud: solicitud.id, // SIEMPRE incluir id_solicitud
        id_veterinario: 1, // Aquí deberías obtener el ID del veterinario logueado
        peso_mascota: parseFloat(formData.peso) || 0,
        latido_por_minuto: parseInt(formData.latidosPm) || 0,
        talla: parseFloat(formData.talla) || 0,
        tiempo_capilar: formData.tiempoCapilar || "",
        color_mucosas: formData.colorMucosas || "",
        frecuencia_pulso: parseInt(formData.frecuenciaPulso) || 0,
        porce_deshidratacion: parseFloat(formData.deshidratacion) || 0,
        frecuencia_respiratoria_rpm: parseInt(formData.frecuenciaResp) || 0,
        temperatura: parseFloat(formData.temperatura) || 0,
        clasificacion_urgencia: mapearClasificacionUrgenciaParaAPI(formData.clasificacionUrgencia),
        condicion_corporal: formData.condicionCorporal
      };

      console.log('Datos a enviar:', triageDataToSend);
      console.log('¿Existe triaje?', !!triageData);
      if (triageData) {
        console.log('ID del triaje:', triageData.id_triaje);
      }

      let response;
      
      if (triageData) {
        // Actualizar triaje existente
        console.log('Actualizando triaje existente...');
        response = await fetch(`https://veterinariaclinicabackend-production.up.railway.app/api/v1/triaje/triaje/${triageData.id_triaje}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(triageDataToSend)
        });
      } else {
        // Crear nuevo triaje
        console.log('Creando nuevo triaje...');
        response = await fetch('https://veterinariaclinicabackend-production.up.railway.app/api/v1/triaje/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(triageDataToSend)
        });
      }

      console.log('Status de respuesta:', response.status);
      
      if (!response.ok) {
        const errorData = await response.text();
        console.error('Error del servidor:', errorData);
        throw new Error(`Error ${response.status}: ${errorData}`);
      }

      const result = await response.json();
      console.log('Triaje guardado exitosamente:', result);
      onComplete();
    } catch (error) {
      console.error('Error completo:', error);
      alert(`Error al guardar los datos del triaje: ${error.message}`);
    }
  };

  if (loading) {
    return (
      <div className="ficha-triaje">
        <div className="loading-message">
          <p>Cargando datos del triaje...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="ficha-triaje">
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
    <form onSubmit={handleSubmit} className="ficha-triaje">
      <div className="form-section">
        <h3>Datos del Triaje</h3>
        {triageData && (
          <div className="info-banner">
            <p>ℹ️ Editando triaje existente del {new Date(triageData.fecha_hora_triaje).toLocaleString()}</p>
          </div>
        )}
        
        <div className="form-row">
          <div className="form-group">
            <label>PESO</label>
            <input
              type="number"
              step="0.1"
              name="peso"
              value={formData.peso}
              onChange={handleChange}
              placeholder="Kg"
              required
            />
          </div>
          
          <div className="form-group">
            <label>LATIDOS P/M</label>
            <input
              type="number"
              name="latidosPm"
              value={formData.latidosPm}
              onChange={handleChange}
              placeholder="latidos por minuto"
              required
            />
          </div>
          
          <div className="form-group">
            <label>FRECUENCIA RESP</label>
            <input
              type="number"
              name="frecuenciaResp"
              value={formData.frecuenciaResp}
              onChange={handleChange}
              placeholder="resp por minuto"
              required
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>TEMPERATURA</label>
            <input
              type="number"
              step="0.1"
              name="temperatura"
              value={formData.temperatura}
              onChange={handleChange}
              placeholder="°C"
              required
            />
          </div>
          
          <div className="form-group">
            <label>TALLA</label>
            <input
              type="number"
              step="0.1"
              name="talla"
              value={formData.talla}
              onChange={handleChange}
              placeholder="cm"
            />
          </div>
          
          <div className="form-group">
            <label>TIEMPO CAPILAR</label>
            <input
              type="text"
              name="tiempoCapilar"
              value={formData.tiempoCapilar}
              onChange={handleChange}
              placeholder="ej: 2 segundos"
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>COLOR MUCOSAS</label>
            <input
              type="text"
              name="colorMucosas"
              value={formData.colorMucosas}
              onChange={handleChange}
            />
          </div>
          
          <div className="form-group">
            <label>FRECUENCIA PULSO</label>
            <input
              type="number"
              name="frecuenciaPulso"
              value={formData.frecuenciaPulso}
              onChange={handleChange}
              placeholder="pulsos por minuto"
            />
          </div>
          
          <div className="form-group">
            <label>% DESHIDRATACIÓN</label>
            <input
              type="number"
              step="0.1"
              name="deshidratacion"
              value={formData.deshidratacion}
              onChange={handleChange}
              placeholder="0.0"
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>CONDICIÓN CORPORAL</label>
            <select
              name="condicionCorporal"
              value={formData.condicionCorporal}
              onChange={handleChange}
              required
            >
              <option value="Select">Select</option>
              <option value="Muy delgado">Muy delgado</option>
              <option value="Delgado">Delgado</option>
              <option value="Ideal">Ideal</option>
              <option value="Sobrepeso">Sobrepeso</option>
              <option value="Obeso">Obeso</option>
            </select>
          </div>
          
          <div className="form-group">
            <label>CLASIFICACIÓN URGENCIA</label>
            <select
              name="clasificacionUrgencia"
              value={formData.clasificacionUrgencia}
              onChange={handleChange}
              required
            >
              <option value="Select">Select</option>
              <option value="Baja">Baja</option>
              <option value="Media">Media</option>
              <option value="Alta">Alta</option>
              <option value="Crítica">Crítica</option>
            </select>
          </div>
        </div>
      </div>

      <div className="form-actions">
        <button type="button" onClick={onCancel} className="btn-cancel">
          Cancelar
        </button>
        <button type="submit" className="btn-submit">
          {triageData ? 'Actualizar y Continuar' : 'Guardar y Continuar a Consulta'}
        </button>
      </div>
    </form>
  );
};

export default FichaTriaje;