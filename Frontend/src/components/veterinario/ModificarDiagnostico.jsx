import React, { useState, useEffect } from 'react';

const ModificarDiagnostico = ({ diagnosticoId, onSave, onCancel }) => {
  const [formData, setFormData] = useState({
    tipoDiagnostico: 'Presuntivo',
    diagnostico: '',
    patologia: '',
    especieAfecta: '',
    esContagioso: false,
    esCronico: false,
    estadoPatologia: '',
    gravedadPatologia: '',
    fechaInicio: '',
    tipoTratamiento: '',
    eficaciaTratamiento: ''
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);

  // Cargar el diagnóstico cuando se pase el id_diagnostico
  useEffect(() => {
    const fetchDiagnosticoInfo = async () => {
      try {
        const response = await fetch(`https://veterinariaclinicabackend-production.up.railway.app/api/v1/consultas/diagnostico/${diagnosticoId}/info`);
        
        if (response.ok) {
          const data = await response.json();
          const diagnostico = data[0];

          setFormData({
            tipoDiagnostico: diagnostico.tipo_diagnostico || 'Presuntivo',
            diagnostico: diagnostico.diagnostico || '',
            patologia: diagnostico.nombre_patologia || '',
            especieAfecta: diagnostico.especie_afecta || '',
            esContagioso: diagnostico.es_contagiosa || false,
            esCronico: diagnostico.es_cronica || false,
            estadoPatologia: diagnostico.estado_patologia || 'Activa',
            gravedadPatologia: diagnostico.gravedad || 'Leve',
            fechaInicio: diagnostico.fecha_inicio_tratamiento || '',
            tipoTratamiento: diagnostico.tipo_tratamiento || 'Medicamento',
            eficaciaTratamiento: diagnostico.eficacia_tratamiento || 'Muy buena'
          });

          setLoading(false);
        } else {
          setError('No se encontró el diagnóstico');
          setLoading(false);
        }
      } catch (err) {
        setError('Error al cargar los datos');
        setLoading(false);
      }
    };

    fetchDiagnosticoInfo();
  }, [diagnosticoId]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validaciones básicas
    if (!formData.diagnostico.trim()) {
      alert('El diagnóstico es obligatorio');
      return;
    }
    
    if (!formData.patologia.trim()) {
      alert('El nombre de la patología es obligatorio');
      return;
    }

    try {
      setSaving(true);
      
      // Mapear los datos del formulario al formato que espera el backend
      const payload = {
        tipo_diagnostico: formData.tipoDiagnostico,
        diagnostico: formData.diagnostico,
        estado_patologia: formData.estadoPatologia,
        nombre_patologia: formData.patologia,
        especie_afecta: formData.especieAfecta,
        es_contagioso: formData.esContagioso,
        es_cronico: formData.esCronico,
        gravedad_patologia: formData.gravedadPatologia,
        fecha_inicio: formData.fechaInicio || null,
        tipo_tratamiento: formData.tipoTratamiento,
        eficacia_tratamiento: formData.eficaciaTratamiento
      };

      console.log('Enviando datos:', payload);

      const response = await fetch(
        `https://veterinariaclinicabackend-production.up.railway.app/api/v1/consultas/diagnostico/${diagnosticoId}/completo`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(payload)
        }
      );

      if (response.ok) {
        const result = await response.json();
        console.log('Diagnóstico actualizado correctamente:', result);
        alert('Diagnóstico actualizado correctamente');
        
        // Llamar a onSave para cerrar modal y refrescar datos
        onSave();
      } else {
        const errorData = await response.json();
        console.error('Error del servidor:', errorData);
        
        // Mostrar errores de validación específicos
        if (errorData.detail && Array.isArray(errorData.detail)) {
          const errorMessages = errorData.detail.map(err => err.msg).join('\n');
          alert(`Errores de validación:\n${errorMessages}`);
        } else {
          alert(`Error al actualizar: ${errorData.detail || 'Error desconocido'}`);
        }
      }
    } catch (error) {
      console.error('Error de red:', error);
      alert('Error de conexión. Por favor, verifica tu conexión a internet.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <p>Cargando datos del diagnóstico...</p>;
  }

  if (error) {
    return (
      <div>
        <p>Error: {error}</p>
        <button onClick={() => window.location.reload()}>Reintentar</button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="modificar-diagnostico">
      <div className="form-section">
        <div className="form-row">
          <div className="form-group">
            <label>TIPO DIAGNÓSTICO</label>
            <select
              name="tipoDiagnostico"
              value={formData.tipoDiagnostico}
              onChange={handleChange}
              required
            >
              <option value="Presuntivo">Presuntivo</option>
              <option value="Confirmado">Confirmado</option>
            </select>
          </div>
          
          <div className="form-group">
            <label>DIAGNÓSTICO *</label>
            <input
              type="text"
              name="diagnostico"
              value={formData.diagnostico}
              onChange={handleChange}
              required
              minLength={5}
              placeholder="Mínimo 5 caracteres"
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>N. PATOLOGÍA *</label>
            <input
              type="text"
              name="patologia"
              value={formData.patologia}
              onChange={handleChange}
              required
              minLength={3}
              placeholder="Mínimo 3 caracteres"
            />
          </div>
          
          <div className="form-group">
            <label>ESPECIE AFECTA</label>
            <select
              name="especieAfecta"
              value={formData.especieAfecta}
              onChange={handleChange}
            >
              <option value="">Seleccionar...</option>
              <option value="Perro">Perro</option>
              <option value="Gato">Gato</option>
              <option value="Ambas">Ambas</option>
            </select>
          </div>
          
          <div className="form-group checkbox-group">
            <label>
              <input
                type="checkbox"
                name="esContagioso"
                checked={formData.esContagioso}
                onChange={handleChange}
              />
              ES CONTAGIOSO?
            </label>
            <label>
              <input
                type="checkbox"
                name="esCronico"
                checked={formData.esCronico}
                onChange={handleChange}
              />
              ES CRÓNICO?
            </label>
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>ESTADO PATOLOGÍA</label>
            <select
              name="estadoPatologia"
              value={formData.estadoPatologia}
              onChange={handleChange}
            >
              <option value="Activa">Activa</option>
              <option value="Controlada">Controlada</option>
              <option value="Curada">Curada</option>
              <option value="En seguimiento">En seguimiento</option>
            </select>
          </div>
          
          <div className="form-group">
            <label>GRAVEDAD PATOLOGÍA</label>
            <select
              name="gravedadPatologia"
              value={formData.gravedadPatologia}
              onChange={handleChange}
            >
              <option value="Leve">Leve</option>
              <option value="Moderada">Moderada</option>
              <option value="Severa">Severa</option>
            </select>
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>FECHA INICIO</label>
            <input
              type="date"
              name="fechaInicio"
              value={formData.fechaInicio}
              onChange={handleChange}
            />
          </div>
          
          <div className="form-group">
            <label>TIPO TRATAMIENTO</label>
            <select
              name="tipoTratamiento"
              value={formData.tipoTratamiento}
              onChange={handleChange}
            >
              <option value="Medicamentoso">Medicamentoso</option>
              <option value="Quirurgico">Quirúrgico</option>
              <option value="Terapia">Terapia</option>
              <option value="Preventivo">Preventivo</option>
            </select>
          </div>

          
          <div className="form-group">
            <label>EFICACIA TRATAMIENTO</label>
            <select
              name="eficaciaTratamiento"
              value={formData.eficaciaTratamiento}
              onChange={handleChange}
            >
              <option value="Muy buena">Muy buena</option>
              <option value="Buena">Buena</option>
              <option value="Regular">Regular</option>
              <option value="Mala">Mala</option>
            </select>
          </div>
        </div>
      </div>

      <div className="form-actions">
        <button 
          type="button" 
          onClick={onCancel} 
          className="btn-cancel"
          disabled={saving}
        >
          Cancelar
        </button>
        <button 
          type="submit" 
          className="btn-submit"
          disabled={saving}
        >
          {saving ? 'Guardando...' : 'Guardar Cambios'}
        </button>
      </div>
    </form>
  );
};

export default ModificarDiagnostico;