import React, { useState } from 'react';
import './ReportsManagement.css';

const ReportsManagement = () => {
  const [loadingCitas, setLoadingCitas] = useState(false);
  const [loadingHistorial, setLoadingHistorial] = useState(false);
  
  // URL base de la API
  const API_BASE_URL = 'http://localhost:8000/api/v1';

  const downloadCitasPDF = async () => {
    try {
      setLoadingCitas(true);
      const response = await fetch(`${API_BASE_URL}/reportes/citas/pdf`);
      
      if (!response.ok) throw new Error('Error al descargar el PDF');
      
      // Convertir la respuesta a Blob y forzar la descarga
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
      alert('Hubo un error al generar el reporte de citas.');
    } finally {
      setLoadingCitas(false);
    }
  };

  const downloadHistorialPDF = async (mascotaId = 1) => {
    try {
      setLoadingHistorial(true);
      // Por ahora pasamos un ID hardcodeado para la demo
      const response = await fetch(`${API_BASE_URL}/reportes/historial/${mascotaId}/pdf`);
      
      if (!response.ok) throw new Error('Error al descargar el PDF');
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Historial_Clinico_Mascota_${mascotaId}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Error:', error);
      alert('Hubo un error al generar el historial clínico.');
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
          <p>Descarga un reporte consolidado con todas las citas médicas programadas para el día de hoy.</p>
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
          <p>Genera la ficha médica completa de una mascota incluyendo todas sus consultas y diagnósticos.</p>
          <button 
            className="btn-download-pdf" 
            onClick={() => downloadHistorialPDF(1)}
            disabled={loadingHistorial}
          >
            {loadingHistorial ? '⏳ Generando PDF...' : '📄 Descargar Historial PDF'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ReportsManagement;
