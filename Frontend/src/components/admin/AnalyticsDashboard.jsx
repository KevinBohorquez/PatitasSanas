import React, { useState, useEffect } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell
} from 'recharts';
import '../../styles/AnalyticsDashboard.css';
import ServicesBarChart from './ServicesBarChart';
import SpeciesPieChart from '../common/SpeciesPieChart';
import KPICards from '../common/KPICards';

const API_BASE = '/api/v1';

const PIE_COLORS_GENERO = ['#4f86c6', '#e67e22'];
const PIE_COLORS_SEXO = ['#27ae60', '#e74c3c'];
const BAR_COLORS = ['#4f86c6', '#27ae60', '#e67e22', '#e74c3c', '#9b59b6'];

// ── Gráfico: condición de consultas ───────────────────────────────────────────
const ConsultasCondicionChart = ({ data }) => {
  const chartData = [
    { name: 'Excelente', value: data.excelente },
    { name: 'Buena', value: data.buena },
    { name: 'Regular', value: data.regular },
    { name: 'Mala', value: data.mala },
    { name: 'Crítica', value: data.critica },
  ];
  return (
    <div className="analytics-card">
      <h3 className="analytics-card-title">Condición de Consultas</h3>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
          <XAxis dataKey="name" tick={{ fontSize: 12 }} />
          <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
          <Tooltip />
          <Bar dataKey="value" name="Consultas" radius={[4, 4, 0, 0]}>
            {chartData.map((_, i) => (
              <Cell key={i} fill={BAR_COLORS[i % BAR_COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

// ── Gráfico: clientes por género ──────────────────────────────────────────────
const ClientesGeneroChart = ({ data }) => {
  const chartData = [
    { name: 'Masculino', value: data.estadisticas.M },
    { name: 'Femenino', value: data.estadisticas.F },
  ];
  return (
    <div className="analytics-card">
      <h3 className="analytics-card-title">Clientes por Género</h3>
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            outerRadius={80}
            dataKey="value"
            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
            labelLine={false}
          >
            {chartData.map((_, i) => (
              <Cell key={i} fill={PIE_COLORS_GENERO[i]} />
            ))}
          </Pie>
          <Tooltip formatter={(v) => [`${v} clientes`]} />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

// ── Gráfico: mascotas por sexo ────────────────────────────────────────────────
const MascotasSexoChart = ({ data }) => {
  const chartData = [
    { name: 'Machos', value: data.estadisticas_por_sexo.machos },
    { name: 'Hembras', value: data.estadisticas_por_sexo.hembras },
  ];
  return (
    <div className="analytics-card">
      <h3 className="analytics-card-title">Mascotas por Sexo</h3>
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            outerRadius={80}
            dataKey="value"
            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
            labelLine={false}
          >
            {chartData.map((_, i) => (
              <Cell key={i} fill={PIE_COLORS_SEXO[i]} />
            ))}
          </Pie>
          <Tooltip formatter={(v) => [`${v} mascotas`]} />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

// ── Gráfico: diagnósticos frecuentes ─────────────────────────────────────────
const DiagnosticosChart = ({ data }) => {
  const chartData = data.map(d => ({
    name: d.patologia,
    value: d.total_diagnosticos,
  }));
  return (
    <div className="analytics-card">
      <h3 className="analytics-card-title">Diagnósticos Frecuentes</h3>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart
          layout="vertical"
          data={chartData}
          margin={{ top: 5, right: 30, left: 10, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
          <XAxis type="number" allowDecimals={false} tick={{ fontSize: 12 }} />
          <YAxis dataKey="name" type="category" width={150} tick={{ fontSize: 11 }} />
          <Tooltip />
          <Bar dataKey="value" name="Casos" fill="#9b59b6" radius={[0, 4, 4, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

// ── Gráfico: razas más populares ─────────────────────────────────────────────
const RazasChart = ({ data }) => {
  const chartData = data
    .filter(r => r.total_mascotas > 0)
    .sort((a, b) => b.total_mascotas - a.total_mascotas)
    .slice(0, 8)
    .map(r => ({ name: r.nombre_raza, value: r.total_mascotas }));

  return (
    <div className="analytics-card analytics-card--wide">
      <h3 className="analytics-card-title">Razas más Populares</h3>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 40 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
          <XAxis dataKey="name" tick={{ fontSize: 11, angle: -30, textAnchor: 'end' }} interval={0} />
          <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
          <Tooltip />
          <Bar dataKey="value" name="Mascotas" fill="#1abc9c" radius={[4, 4, 0, 0]}>
            {chartData.map((_, i) => (
              <Cell key={i} fill={BAR_COLORS[i % BAR_COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

// ── Componente contenedor principal ───────────────────────────────────────────
const AnalyticsDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [data, setData] = useState({
    consultas: null,
    clientesGenero: null,
    mascotasSexo: null,
    razas: null,
  });

  // Estado para los KPIs extraídos de tus endpoints
  const [kpiData, setKpiData] = useState({
    totalCitas: 0,
    tasaAsistencia: 0,
    ingresosEstimados: 0,
    citasPorEstado: { Pendiente: 0, Atendida: 0, Cancelada: 0 }
  });

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [
        consultasRes,
        clientesRes,
        mascotasRes,
        razasRes,
        tasaAsistenciaRes,
        statsGeneralesRes
      ] = await Promise.all([
        fetch(`${API_BASE}/consultas/estadisticas/resumen`),
        fetch(`${API_BASE}/clientes/stats/genero`),
        fetch(`${API_BASE}/mascotas/stats/por-sexo`),
        fetch(`${API_BASE}/catalogos/razas/estadisticas/mascotas`),
        fetch(`${API_BASE}/dashboard/tasa-asistencia`),
        fetch(`${API_BASE}/dashboard/stats-generales`)
      ]);

      setData({
        consultas: consultasRes.ok ? await consultasRes.json() : null,
        clientesGenero: clientesRes.ok ? await clientesRes.json() : null,
        mascotasSexo: mascotasRes.ok ? await mascotasRes.json() : null,
        razas: razasRes.ok ? await razasRes.json() : null,
      });

      // Procesamos las respuestas de los KPIs
      const tasaData = tasaAsistenciaRes.ok ? await tasaAsistenciaRes.json() : null;
      const statsData = statsGeneralesRes.ok ? await statsGeneralesRes.json() : null;

      setKpiData({
        totalCitas: statsData?.total_citas ?? 0,
        tasaAsistencia: tasaData?.tasa_asistencia ?? 0,
        ingresosEstimados: statsData?.ingresos_estimados ?? 0,
        citasPorEstado: statsData?.citas_por_estado ?? { Pendiente: 0, Atendida: 0, Cancelada: 0 }
      });

    } catch {
      setError('No se pudieron cargar los datos. Verifica la conexión con el servidor.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  if (loading) {
    return (
      <div className="analytics-state">
        <div className="analytics-spinner" />
        <p>Cargando analíticas…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="analytics-state analytics-state--error">
        <p>{error}</p>
        <button className="analytics-retry" onClick={fetchData}>Reintentar</button>
      </div>
    );
  }

  const totalConsultas = data.consultas?.periodo?.total_consultas ?? 0;
  const totalClientes = data.clientesGenero?.estadisticas?.total ?? 0;
  const totalMascotas = data.mascotasSexo?.total ?? 0;

  // Formateamos los datos para inyectarlos en el componente KPICards
  const kpisToRender = [
    { title: "Total Citas", value: kpiData.totalCitas, icon: "calendar" },
    { title: "Tasa de Asistencia", value: `${typeof kpiData.tasaAsistencia === 'number' ? kpiData.tasaAsistencia.toFixed(1) : kpiData.tasaAsistencia}%`, icon: "check-circle" },
    { title: "Ingresos Estimados", value: `S/ ${typeof kpiData.ingresosEstimados === 'number' ? kpiData.ingresosEstimados.toFixed(2) : kpiData.ingresosEstimados}`, icon: "dollar-sign" },
    {
      title: "Estado de Citas",
      value: `Atendidas: ${kpiData.citasPorEstado.Atendida || kpiData.citasPorEstado.Atendido || 0}`,
      icon: "activity"
    }
  ];

  return (
    <div className="analytics-dashboard">
      <div className="analytics-header">
        <h2 className="analytics-title">Analíticas y Estadísticas</h2>
        <button className="analytics-refresh" onClick={fetchData} title="Actualizar datos">
          🔄 Actualizar
        </button>
      </div>

      {/* Renderizado de los KPIs conectados al backend */}
      <div style={{ marginBottom: '20px' }}>
        <KPICards kpis={kpisToRender} />
      </div>

      {/* Tarjetas resumen */}
      <div className="analytics-summary">
        <div className="analytics-summary-card">
          <span className="analytics-summary-icon">🏥</span>
          <div>
            <p className="analytics-summary-label">Total Consultas</p>
            <p className="analytics-summary-value">{totalConsultas}</p>
          </div>
        </div>
        <div className="analytics-summary-card">
          <span className="analytics-summary-icon">👥</span>
          <div>
            <p className="analytics-summary-label">Total Clientes</p>
            <p className="analytics-summary-value">{totalClientes}</p>
          </div>
        </div>
        <div className="analytics-summary-card">
          <span className="analytics-summary-icon">🐾</span>
          <div>
            <p className="analytics-summary-label">Total Mascotas</p>
            <p className="analytics-summary-value">{totalMascotas}</p>
          </div>
        </div>
      </div>

      {/* Gráficos */}
      <div className="analytics-grid">
        {data.consultas && (
          <ConsultasCondicionChart data={data.consultas.estadisticas_condicion} />
        )}
        {data.clientesGenero && (
          <ClientesGeneroChart data={data.clientesGenero} />
        )}
        {data.mascotasSexo && (
          <MascotasSexoChart data={data.mascotasSexo} />
        )}
        {data.consultas?.diagnosticos_frecuentes?.length > 0 && (
          <DiagnosticosChart data={data.consultas.diagnosticos_frecuentes} />
        )}
        {data.razas && (
          <RazasChart data={data.razas} />
        )}
        <ServicesBarChart />
        <SpeciesPieChart />
      </div>
    </div>
  );
};

export default AnalyticsDashboard;
