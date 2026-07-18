import React, { useState, useEffect } from 'react';
import { apiFetch } from '../../api/client';

const API_BASE_URL = '';

const KPICards = () => {
  const [kpiData, setKpiData] = useState({
    totalCitas: 0,
    ingresosEstimados: 0,
    tasaAsistencia: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchKpiData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [tasaResponse, ingresosResponse] = await Promise.all([
        apiFetch(`${API_BASE_URL}/dashboard/tasa-asistencia`, {
          method: 'GET',
          headers: { 'Accept': 'application/json' },
        }),
        apiFetch(`${API_BASE_URL}/dashboard/ingresos-por-servicio`, {
          method: 'GET',
          headers: { 'Accept': 'application/json' },
        }),
      ]);

      let totalCitas = 0;
      let tasaAsistencia = 0;

      if (tasaResponse.ok) {
        const tasaData = await tasaResponse.json();
        const programadas = tasaData.Programada || 0;
        const canceladas = tasaData.Cancelada || 0;
        const atendidas = tasaData.Atendida || 0;
        totalCitas = programadas + canceladas + atendidas;
        tasaAsistencia = tasaData.tasa_asistencia || 0;
      }

      let ingresosEstimados = 0;
      if (ingresosResponse.ok) {
        const ingresosData = await ingresosResponse.json();
        if (Array.isArray(ingresosData)) {
          ingresosEstimados = ingresosData.reduce(
            (sum, item) => sum + (item.ingreso_estimado || 0),
            0
          );
        }
      }

      setKpiData({ totalCitas, ingresosEstimados, tasaAsistencia });
    } catch (err) {
      console.error('Error al cargar KPIs:', err);
      setError('Error al cargar indicadores. Inténtalo de nuevo.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchKpiData();
  }, []);

  const formatCurrency = (value) =>
    value.toLocaleString('es-PE', { style: 'currency', currency: 'PEN', minimumFractionDigits: 2 });

  const cards = [
    {
      title: 'Total de Citas',
      value: loading ? '...' : kpiData.totalCitas.toString().padStart(2, '0'),
      icon: 'https://i.ibb.co/qYHnQGk9/cita1-Comprimido.png',
      color: 'blue',
    },
    {
      title: 'Ingresos Estimados',
      value: loading ? '...' : formatCurrency(kpiData.ingresosEstimados),
      icon: 'https://i.ibb.co/mVjXndWF/Cliente1-Comprimido.png',
      color: 'green',
    },
    {
      title: 'Tasa de Asistencia',
      value: loading ? '...' : `${kpiData.tasaAsistencia.toFixed(1)}%`,
      icon: 'https://i.ibb.co/S7tyCF7B/Recepcionista1-Comprimido.png',
      color: 'purple',
    },
  ];

  return (
    <div className="kpi-cards-section">
      {error && (
        <div className="error-message">
          <p>{error}</p>
          <button onClick={fetchKpiData} className="retry-button">
            Reintentar
          </button>
        </div>
      )}

      <div className="stats-grid">
        {cards.map((card, index) => (
          <div key={index} className={`stat-card stat-${card.color}`}>
            <div className="stat-content two-columns">
              <div className="left-column">
                <h3 className="stat-title">{card.title}</h3>
                <div className="stat-value">{card.value}</div>
              </div>
              <div className="right-column">
                <div className="stat-icon-container">
                  <img
                    src={card.icon}
                    alt={card.title}
                    className="stat-icon"
                    onError={(e) => { e.target.style.display = 'none'; }}
                  />
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="dashboard-footer">
        <p>Última actualización: {new Date().toLocaleString('es-PE', {
          timeZone: 'America/Lima',
          day: '2-digit',
          month: '2-digit',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
        })}</p>
      </div>
    </div>
  );
};

export default KPICards;
