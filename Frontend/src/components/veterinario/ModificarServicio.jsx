import React, { useState, useEffect } from 'react';

const ModificarServicio = ({ consultaId, onSave, onCancel }) => {
  const [formData, setFormData] = useState({
    idVeterinario: '',
    idServicio: '',
    prioridad: 'Normal',
    comentarioOpcional: '',
    fechaHoraProgramada: '',
    requiereAyuno: false,
    observaciones: ''
  });

  const [loading, setLoading] = useState(false); 
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);
  const [veterinarios, setVeterinarios] = useState([]);
  const [servicios, setServicios] = useState([]);

  // Cargar veterinarios desde la API
  useEffect(() => {
    const fetchVeterinarios = async () => {
      try {
        const response = await fetch('https://veterinariaclinicabackend-production.up.railway.app/api/v1/veterinarios/?page=1&per_page=20');
        
        if (response.ok) {
          const veterinariosData = await response.json();
          setVeterinarios(veterinariosData.veterinarios);
        } else {
          setError('Error al cargar los veterinarios');
        }
      } catch (error) {
        setError('Error al cargar los veterinarios');
        console.error(error);
      }
    };

    const fetchServicios = async () => {
      try {
        const response = await fetch('https://veterinariaclinicabackend-production.up.railway.app/api/v1/catalogos/servicios/?activos_solo=true');
        
        if (response.ok) {
          const serviciosData = await response.json();
          setServicios(serviciosData);
        } else {
          setError('Error al cargar los servicios');
        }
      } catch (error) {
        setError('Error al cargar los servicios');
        console.error(error);
      }
    };

    fetchVeterinarios();
    fetchServicios();
  }, []);

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
    if (!formData.idVeterinario) {
      alert('Debe seleccionar un veterinario');
      return;
    }

    if (!formData.idServicio) {
      alert('Debe seleccionar un servicio');
      return;
    }

    if (!formData.fechaHoraProgramada) {
      alert('Debe seleccionar una fecha y hora programada');
      return;
    }

    // Validar que consultaId existe y es válido
    if (!consultaId) {
      alert('Error: No se ha proporcionado un ID de consulta válido');
      return;
    }

    try {
      setSaving(true);

      // Mapear los datos del formulario al formato que espera el backend
      const payload = {
        id_veterinario: parseInt(formData.idVeterinario),
        id_servicio: parseInt(formData.idServicio),
        prioridad: formData.prioridad,
        comentario_opcional: formData.comentarioOpcional || null,
        fecha_hora_programada: new Date(formData.fechaHoraProgramada).toISOString(),
        requiere_ayuno: formData.requiereAyuno,
        observaciones: formData.observaciones || null
      };

      console.log('Enviando datos del servicio:', payload);
      console.log('Consulta ID:', consultaId);

      // Usar el consultaId correctamente en la URL
      const response = await fetch(
        `https://veterinariaclinicabackend-production.up.railway.app/api/v1/servicio_solicitado/consultas/${consultaId}/servicio-cita`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload)
        }
      );

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Error ${response.status}: ${errorText}`);
      }

      const result = await response.json();
      console.log('Servicio solicitado y cita creados correctamente:', result);
      
      alert('Servicio creado correctamente');
      onSave();
    } catch (error) {
      console.error('Error al crear servicio:', error);
      alert(`Error al crear el servicio: ${error.message}`);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <p>Cargando datos del servicio...</p>;
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
    <form onSubmit={handleSubmit} className="modificar-servicio">
      <div className="form-section">
        <div className="form-row">
          <div className="form-group">
            <label>VETERINARIO *</label>
            <select
              name="idVeterinario"
              value={formData.idVeterinario}
              onChange={handleChange}
              required
            >
              <option value="">Seleccionar veterinario...</option>
              {veterinarios.map((vet) => (
                <option key={vet.id_veterinario} value={vet.id_veterinario}>
                  Dr. {vet.nombre} {vet.apellido_paterno} - {vet.tipo_veterinario}
                </option>
              ))}
            </select>
          </div>
          
          <div className="form-group">
            <label>SERVICIO *</label>
            <select
              name="idServicio"
              value={formData.idServicio}
              onChange={handleChange}
              required
            >
              <option value="">Seleccionar servicio...</option>
              {servicios.map((servicio) => (
                <option key={servicio.id_servicio} value={servicio.id_servicio}>
                  {servicio.nombre_servicio} - S/. {servicio.precio}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>PRIORIDAD</label>
            <select
              name="prioridad"
              value={formData.prioridad}
              onChange={handleChange}
            >
              <option value="Urgente">Urgente</option>
              <option value="Normal">Normal</option>
              <option value="Programable">Programable</option>
            </select>
          </div>
          
          <div className="form-group">
            <label>FECHA Y HORA PROGRAMADA *</label>
            <input
              type="datetime-local"
              name="fechaHoraProgramada"
              value={formData.fechaHoraProgramada}
              onChange={handleChange}
              required
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group checkbox-group">
            <label>
              <input
                type="checkbox"
                name="requiereAyuno"
                checked={formData.requiereAyuno}
                onChange={handleChange}
              />
              REQUIERE AYUNO
            </label>
          </div>
        </div>

        <div className="form-group full-width">
          <label>COMENTARIO OPCIONAL</label>
          <textarea
            name="comentarioOpcional"
            value={formData.comentarioOpcional}
            onChange={handleChange}
            rows="3"
            placeholder="Instrucciones especiales o comentarios adicionales..."
          />
        </div>

        <div className="form-group full-width">
          <label>OBSERVACIONES</label>
          <textarea
            name="observaciones"
            value={formData.observaciones}
            onChange={handleChange}
            rows="3"
            placeholder="Observaciones generales del servicio..."
          />
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

export default ModificarServicio;