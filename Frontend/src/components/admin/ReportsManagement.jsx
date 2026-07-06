import React, { useState, useEffect } from 'react';
import './ReportsManagement.css';
import { toast } from '../../utils/toast';

const ReportsManagement = () => {
  const [loadingCitas, setLoadingCitas] = useState(false);
  const [loadingHistorial, setLoadingHistorial] = useState(false);
  const [mascotas, setMascotas] = useState([]);
  
  // Filtros
  const [fechaInicio, setFechaInicio] = useState('');
  const [fechaFin, setFechaFin] = useState('');
  const [selectedMascotaId, setSelectedMascotaId] = useState('');

  // URL base de la API
  const API_BASE_URL = '/api/v1';

  // Obtener lista de mascotas
  useEffect(() => {
    const fetchMascotas = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/mascotas/?per_page=100`);
        if (response.ok) {
          const data = await response.json();
          setMascotas(data.mascotas || []);
        }
      } catch (error) {
        console.error('Error fetching mascotas:', error);
      }
    };
    fetchMascotas();
  }, []);

  const downloadCitasPDF = async () => {
    if (fechaInicio && fechaFin && fechaInicio > fechaFin) {
      toast.warning('La fecha de inicio no puede ser posterior a la fecha de fin.');
      return;
    }

    try {
      setLoadingCitas(true);
      
      let queryUrl = `${API_BASE_URL}/reportes/citas/pdf`;
      const queryParams = [];
      if (fechaInicio) queryParams.push(`fecha_inicio=${fechaInicio}`);
      if (fechaFin) queryParams.push(`fecha_fin=${fechaFin}`);
      
      if (queryParams.length > 0) {
        queryUrl += `?${queryParams.join('&')}`;
      }
      
      const response = await fetch(queryUrl);
      
      if (!response.ok) {
        let errorMessage = 'Error al descargar el PDF';
        try {
          const errorData = await response.json();
          if (errorData?.detail) {
            errorMessage = typeof errorData.detail === 'string'
              ? errorData.detail
              : 'Error al descargar el PDF';
          }
        } catch {
          // Respuesta sin cuerpo JSON
        }
        throw new Error(errorMessage);
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Reporte_Citas_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Error:', error);
      toast.error(error.message || 'Hubo un error al generar el reporte de citas.');
    } finally {
      setLoadingCitas(false);
    }
  };

  const downloadHistorialPDF = async () => {
    if (!selectedMascotaId) {
      toast.warning('Por favor selecciona una mascota primero.');
      return;
    }
    
    try {
      setLoadingHistorial(true);
      const response = await fetch(`${API_BASE_URL}/reportes/historial/${selectedMascotaId}/pdf`);
      
      if (!response.ok) throw new Error('Error al descargar el PDF');
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Historial_Clinico_Mascota_${selectedMascotaId}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Error:', error);
      toast.error('Hubo un error al generar el historial clínico.');
    } finally {
      setLoadingHistorial(false);
    }
  };

  return (
    <div className="reports-management">
      <div className="section-header">
        <h2>Gestión de Reportes</h2>
      </div>

      <div className="reports-grid">
        {/* Tarjeta de Reporte de Citas */}
        <div className="report-card">
          <div className="report-icon">📅</div>
          <h3>Citas Diarias</h3>
          <p>Descarga un reporte consolidado con todas las citas médicas programadas para un rango de fechas.</p>
          
          <div className="report-filters">
            <div className="filter-group">
              <label>Fecha Inicio:</label>
              <input 
                type="date" 
                value={fechaInicio} 
                onChange={(e) => setFechaInicio(e.target.value)} 
                className="report-input"
              />
            </div>
            <div className="filter-group">
              <label>Fecha Fin:</label>
              <input 
                type="date" 
                value={fechaFin} 
                onChange={(e) => setFechaFin(e.target.value)} 
                className="report-input"
              />
            </div>
          </div>

          <button 
            className="btn-download-pdf" 
            onClick={downloadCitasPDF}
            disabled={loadingCitas}
          >
            {loadingCitas ? '⏳ Generando PDF...' : '📄 Descargar Reporte PDF'}
          </button>
        </div>

        {/* Tarjeta de Historial Clínico */}
        <div className="report-card">
          <div className="report-icon">🏥</div>
          <h3>Historial Clínico</h3>
          <p>Genera la ficha médica completa seleccionando una mascota de la base de datos.</p>
          
          <div className="report-filters">
            <div className="filter-group">
              <label>Seleccionar Mascota:</label>
              <select 
                value={selectedMascotaId} 
                onChange={(e) => setSelectedMascotaId(e.target.value)}
                className="report-input"
              >
                <option value="">-- Elige una mascota --</option>
                {mascotas.map(m => (
                  <option key={m.id_mascota} value={m.id_mascota}>
                    {m.nombre} (Dueño: {m.cliente ? m.cliente.nombre : 'Sin dueño'})
                  </option>
                ))}
              </select>
            </div>
          </div>

          <button 
            className="btn-download-pdf" 
            onClick={downloadHistorialPDF}
            disabled={loadingHistorial || !selectedMascotaId}
          >
            {loadingHistorial ? '⏳ Generando PDF...' : '📄 Descargar Historial PDF'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ReportsManagement;
