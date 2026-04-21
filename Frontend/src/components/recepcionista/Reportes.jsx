// components/recepcionista/Reportes.jsx
import React, { useState, useEffect } from 'react';
import './Reportes.css';

const Reportes = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [serviciosPopulares, setServiciosPopulares] = useState([]);
  const [mascotasPorSexo, setMascotasPorSexo] = useState({});
  const [clientesPorGenero, setClientesPorGenero] = useState({});
  const [razasPopulares, setRazasPopulares] = useState([]);

  const BASE_URL = 'https://veterinariaclinicabackend-production.up.railway.app/api/v1';

  useEffect(() => {
    fetchAllReports();
  }, []);

  const fetchAllReports = async () => {
    setLoading(true);
    setError(null);

    try {
      await Promise.all([
        fetchServiciosPopulares(),
        fetchMascotasPorSexo(),
        fetchClientesPorGenero(),
        fetchRazasPopulares()
      ]);
    } catch (err) {
      console.error('Error al cargar reportes:', err);
      setError('Error al cargar los reportes. Intente nuevamente.');
    } finally {
      setLoading(false);
    }
  };

  const fetchServiciosPopulares = async () => {
    try {
      const response = await fetch(`${BASE_URL}/catalogos/servicios/populares/top`, {
        method: 'GET',
        mode: 'cors',
        headers: {
          'Accept': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setServiciosPopulares(data || []);
      } else {
        console.error('Error al cargar servicios populares:', response.statusText);
      }
    } catch (error) {
      console.error('Error en servicios populares:', error);
    }
  };

  const fetchMascotasPorSexo = async () => {
    try {
      const response = await fetch(`${BASE_URL}/mascotas/stats/por-sexo`, {
        method: 'GET',
        mode: 'cors',
        headers: {
          'Accept': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setMascotasPorSexo(data);
      } else {
        console.error('Error al cargar estadísticas por sexo:', response.statusText);
      }
    } catch (error) {
      console.error('Error en mascotas por sexo:', error);
    }
  };

  const fetchClientesPorGenero = async () => {
    try {
      const response = await fetch(`${BASE_URL}/clientes/stats/genero`, {
        method: 'GET',
        mode: 'cors',
        headers: {
          'Accept': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setClientesPorGenero(data);
      } else {
        console.error('Error al cargar estadísticas de género:', response.statusText);
      }
    } catch (error) {
      console.error('Error en clientes por género:', error);
    }
  };

  const fetchRazasPopulares = async () => {
    try {
      const response = await fetch(`${BASE_URL}/catalogos/razas/populares/top?limit=5`, {
        method: 'GET',
        mode: 'cors',
        headers: {
          'Accept': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setRazasPopulares(data || []);
      } else {
        console.error('Error al cargar razas populares:', response.statusText);
      }
    } catch (error) {
      console.error('Error en razas populares:', error);
    }
  };

  const getMaxValue = (data, key) => {
    if (!data || data.length === 0) return 100;
    return Math.max(...data.map(item => item[key] || 0));
  };

  const getBarHeight = (value, maxValue) => {
    if (!value || !maxValue) return 10;
    return Math.max((value / maxValue) * 100, 10);
  };

  const renderServiciosPopulares = () => {
    if (!serviciosPopulares || serviciosPopulares.length === 0) {
      return <div className="no-data">No hay datos de servicios disponibles</div>;
    }

    const maxSolicitudes = getMaxValue(serviciosPopulares, 'total_solicitudes');

    return (
      <div className="chart-container">
        <div className="bar-chart">
          {serviciosPopulares.slice(0, 6).map((servicio, index) => (
            <div key={index} className="bar-item">
              <div className="bar-info">
                <span className="bar-value">{servicio.total_solicitudes}</span>
              </div>
              <div 
                className="bar servicios-bar" 
                style={{
                  height: `${getBarHeight(servicio.total_solicitudes, maxSolicitudes)}%`,
                  backgroundColor: `hsl(${200 + index * 30}, 70%, 60%)`
                }}
                title={`${servicio.nombre_servicio}: ${servicio.total_solicitudes} solicitudes`}
              ></div>
              <label className="bar-label">
                {servicio.nombre_servicio?.length > 12 
                  ? servicio.nombre_servicio.substring(0, 12) + '...' 
                  : servicio.nombre_servicio}
              </label>
            </div>
          ))}
        </div>
        <div className="chart-summary">
          <p>Total de servicios registrados: {serviciosPopulares.length}</p>
        </div>
      </div>
    );
  };

  const renderMascotasPorSexo = () => {
    if (!mascotasPorSexo.estadisticas_por_sexo) {
      return <div className="no-data">No hay datos de mascotas por sexo</div>;
    }

    const { machos, hembras } = mascotasPorSexo.estadisticas_por_sexo;
    const total = mascotasPorSexo.total || (machos + hembras);
    const maxValue = Math.max(machos, hembras);

    const porcentajeMachos = total > 0 ? ((machos / total) * 100).toFixed(1) : 0;
    const porcentajeHembras = total > 0 ? ((hembras / total) * 100).toFixed(1) : 0;

    return (
      <div className="chart-container">
        <div className="bar-chart sexo-chart">
          <div className="bar-item">
            <div className="bar-info">
              <span className="bar-value">{machos}</span>
              <span className="bar-percentage">({porcentajeMachos}%)</span>
            </div>
            <div 
              className="bar sexo-bar macho-bar" 
              style={{
                height: `${getBarHeight(machos, maxValue)}%`,
                backgroundColor: '#4A90E2'
              }}
              title={`Machos: ${machos} (${porcentajeMachos}%)`}
            ></div>
            <label className="bar-label">Machos</label>
          </div>
          
          <div className="bar-item">
            <div className="bar-info">
              <span className="bar-value">{hembras}</span>
              <span className="bar-percentage">({porcentajeHembras}%)</span>
            </div>
            <div 
              className="bar sexo-bar hembra-bar" 
              style={{
                height: `${getBarHeight(hembras, maxValue)}%`,
                backgroundColor: '#E24A90'
              }}
              title={`Hembras: ${hembras} (${porcentajeHembras}%)`}
            ></div>
            <label className="bar-label">Hembras</label>
          </div>
        </div>
        <div className="chart-summary">
          <p>Total de mascotas registradas: {total}</p>
        </div>
      </div>
    );
  };

  const renderClientesPorGenero = () => {
    if (!clientesPorGenero.estadisticas || !clientesPorGenero.porcentajes) {
      return <div className="no-data">No hay datos de clientes por género</div>;
    }

    const { F: femenino, M: masculino, total } = clientesPorGenero.estadisticas;
    const { femenino: porcentajeFemenino, masculino: porcentajeMasculino } = clientesPorGenero.porcentajes;
    const maxValue = Math.max(femenino, masculino);

    return (
      <div className="chart-container">
        <div className="bar-chart genero-chart">
          <div className="bar-item">
            <div className="bar-info">
              <span className="bar-value">{femenino}</span>
              <span className="bar-percentage">({porcentajeFemenino}%)</span>
            </div>
            <div 
              className="bar genero-bar femenino-bar" 
              style={{
                height: `${getBarHeight(femenino, maxValue)}%`,
                backgroundColor: '#9B59B6'
              }}
              title={`Femenino: ${femenino} (${porcentajeFemenino}%)`}
            ></div>
            <label className="bar-label">Femenino</label>
          </div>
          
          <div className="bar-item">
            <div className="bar-info">
              <span className="bar-value">{masculino}</span>
              <span className="bar-percentage">({porcentajeMasculino}%)</span>
            </div>
            <div 
              className="bar genero-bar masculino-bar" 
              style={{
                height: `${getBarHeight(masculino, maxValue)}%`,
                backgroundColor: '#2ECC71'
              }}
              title={`Masculino: ${masculino} (${porcentajeMasculino}%)`}
            ></div>
            <label className="bar-label">Masculino</label>
          </div>
        </div>
        <div className="chart-summary">
          <p>Total de clientes registrados: {total}</p>
        </div>
      </div>
    );
  };

  const renderRazasPopulares = () => {
    if (!razasPopulares || razasPopulares.length === 0) {
      return <div className="no-data">No hay datos de razas disponibles</div>;
    }

    const maxMascotas = getMaxValue(razasPopulares, 'total_mascotas');

    return (
      <div className="chart-container">
        <div className="bar-chart">
          {razasPopulares.slice(0, 5).map((raza, index) => (
            <div key={index} className="bar-item">
              <div className="bar-info">
                <span className="bar-value">{raza.total_mascotas}</span>
              </div>
              <div 
                className="bar razas-bar" 
                style={{
                  height: `${getBarHeight(raza.total_mascotas, maxMascotas)}%`,
                  backgroundColor: `hsl(${120 + index * 45}, 65%, 55%)`
                }}
                title={`${raza.nombre_raza}: ${raza.total_mascotas} mascotas`}
              ></div>
              <label className="bar-label">
                {raza.nombre_raza?.length > 10 
                  ? raza.nombre_raza.substring(0, 10) + '...' 
                  : raza.nombre_raza}
              </label>
            </div>
          ))}
        </div>
        <div className="chart-summary">
          <p>Top 5 razas más populares</p>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="reportes">
        <div className="section-header">
          <h2>Reportes Estadísticos</h2>
        </div>
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Cargando reportes estadísticos...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="reportes">
        <div className="section-header">
          <h2>Reportes Estadísticos</h2>
        </div>
        <div className="error-container">
          <div className="error-message">
            <p>{error}</p>
            <button onClick={fetchAllReports} className="retry-button">
              Intentar nuevamente
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="reportes">
      <div className="section-header">
        <h2>Reportes Estadísticos</h2>
        <button onClick={fetchAllReports} className="btn-refresh" disabled={loading}>
          🔄 Actualizar Datos
        </button>
      </div>

      <div className="reportes-content">
        <div className="reportes-section">
          <div className="section-title">
            <h3>📊 SERVICIOS MÁS SOLICITADOS</h3>
            <span className="section-subtitle">Ranking de servicios por popularidad</span>
          </div>
          {renderServiciosPopulares()}
        </div>

        <div className="reportes-section">
          <div className="section-title">
            <h3>🐕 MASCOTAS POR SEXO</h3>
            <span className="section-subtitle">Distribución demográfica de mascotas</span>
          </div>
          {renderMascotasPorSexo()}
        </div>

        <div className="reportes-section">
          <div className="section-title">
            <h3>👥 CLIENTES POR GÉNERO</h3>
            <span className="section-subtitle">Distribución demográfica de clientes</span>
          </div>
          {renderClientesPorGenero()}
        </div>

        <div className="reportes-section">
          <div className="section-title">
            <h3>🏆 RAZAS MÁS POPULARES</h3>
            <span className="section-subtitle">Top 5 razas con más mascotas registradas</span>
          </div>
          {renderRazasPopulares()}
        </div>
      </div>

      <div className="reportes-footer">
        <div className="update-info">
          <p>📅 Última actualización: {new Date().toLocaleString('es-PE', {
            timeZone: 'America/Lima',
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
          })}</p>
        </div>
        <div className="system-info">
          <p>🏥 Sistema de Reportes - Veterinaria Colitas Felices</p>
        </div>
      </div>
    </div>
  );
};

export default Reportes;