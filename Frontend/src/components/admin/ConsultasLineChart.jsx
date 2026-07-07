// src/components/admin/ConsultasLineChart.jsx
import React, { useState, useEffect } from 'react';
import Loader from '../common/Loader/Loader';

const API_BASE_URL = '/api/v1';

// ─── Datos de fallback para cuando la API no tiene registros aún ──────────────
const MESES_LABELS = [
  'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
  'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic',
];

const MESES_COMPLETOS = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
];

// ─── Helpers SVG ──────────────────────────────────────────────────────────────
const W = 640;   // ancho del viewBox
const H = 260;   // alto del viewBox
const PAD = { top: 24, right: 24, bottom: 48, left: 44 };

const chartW = W - PAD.left - PAD.right;
const chartH = H - PAD.top  - PAD.bottom;

function buildPoints(data) {
  const max = Math.max(...data.map(d => d.total_consultas), 1);
  return data.map((d, i) => {
    const x = PAD.left + (i / (data.length - 1 || 1)) * chartW;
    const y = PAD.top  + chartH - (d.total_consultas / max) * chartH;
    return { x, y, ...d };
  });
}

function polyline(pts) {
  return pts.map(p => `${p.x},${p.y}`).join(' ');
}

function areaPath(pts) {
  if (!pts.length) return '';
  const top  = pts.map(p => `${p.x},${p.y}`).join(' L ');
  const last = pts[pts.length - 1];
  const first = pts[0];
  return `M ${first.x},${first.y} L ${top} L ${last.x},${PAD.top + chartH} L ${first.x},${PAD.top + chartH} Z`;
}

// ─── Componente ───────────────────────────────────────────────────────────────
const ConsultasLineChart = () => {
  const currentYear = new Date().getFullYear();

  const [año, setAño] = useState(currentYear);
  const [rawData, setRawData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(null);
  const [tooltip, setTooltip] = useState(null); // { x, y, mes, total }

  // ── fetch ──────────────────────────────────────────────────────────────────
  const fetchData = async (targetYear) => {
    setLoading(true);
    setError(null);
    try {
      // El endpoint del dashboard_crud: GET /api/v1/reportes/consultas-por-mes?año=XXXX
      // Si ese endpoint no existe aún, se prueba con el dashboard genérico
      const res = await fetch(
        `${API_BASE_URL}/reportes/consultas-por-mes?año=${targetYear}`,
        { headers: { 'Content-Type': 'application/json' } }
      );

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();

      // Normalizar: la API devuelve [{ mes: "Enero", total_consultas: 5 }, ...]
      // Completamos los 12 meses aunque no todos tengan datos
      const mapa = {};
      json.forEach(item => { mapa[item.mes] = item.total_consultas; });

      const completo = MESES_COMPLETOS.map(mes => ({
        mes,
        total_consultas: mapa[mes] ?? 0,
      }));
      setRawData(completo);
    } catch (err) {
      // Si la API falla, mostramos mensaje pero no datos inventados
      setError('No se pudo cargar los datos. Verifica que el servidor esté activo.');
      setRawData([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(año); }, [año]);

  // ── Derivados ──────────────────────────────────────────────────────────────
  const points  = rawData.length > 1 ? buildPoints(rawData) : [];
  const maxVal  = Math.max(...rawData.map(d => d.total_consultas), 1);
  const total   = rawData.reduce((s, d) => s + d.total_consultas, 0);
  const promedio = rawData.length ? (total / rawData.length).toFixed(1) : '0';
  const pico    = rawData.reduce((a, b) => (b.total_consultas > a.total_consultas ? b : a), { mes: '—', total_consultas: 0 });

  // Líneas de grilla Y (4 niveles)
  const gridLines = [0.25, 0.5, 0.75, 1].map(f => ({
    y: PAD.top + chartH - f * chartH,
    label: Math.round(f * maxVal),
  }));

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <div style={styles.card}>

      {/* ── Encabezado ─────────────────────────────────────────────── */}
      <div style={styles.header}>
        <div>
          <h3 style={styles.title}>📈 Evolución de Consultas</h3>
          <p style={styles.subtitle}>Total de consultas atendidas por mes</p>
        </div>
        <div style={styles.controls}>
          <button
            style={styles.yearBtn}
            onClick={() => setAño(a => a - 1)}
            title="Año anterior"
          >‹</button>
          <span style={styles.yearLabel}>{año}</span>
          <button
            style={{ ...styles.yearBtn, opacity: año >= currentYear ? 0.35 : 1 }}
            onClick={() => setAño(a => Math.min(a + 1, currentYear))}
            disabled={año >= currentYear}
            title="Año siguiente"
          >›</button>
        </div>
      </div>

      {/* ── KPIs rápidos ────────────────────────────────────────────── */}
      <div style={styles.kpiRow}>
        <div style={styles.kpi}>
          <span style={styles.kpiValue}>{total}</span>
          <span style={styles.kpiLabel}>Total {año}</span>
        </div>
        <div style={styles.kpiDivider} />
        <div style={styles.kpi}>
          <span style={styles.kpiValue}>{promedio}</span>
          <span style={styles.kpiLabel}>Promedio / mes</span>
        </div>
        <div style={styles.kpiDivider} />
        <div style={styles.kpi}>
          <span style={styles.kpiValue}>{pico.mes !== '—' ? pico.mes.slice(0,3) : '—'}</span>
          <span style={styles.kpiLabel}>Mes pico ({pico.total_consultas})</span>
        </div>
      </div>

      {/* ── Estado: cargando / error / sin datos ────────────────────── */}
      {loading && (
        <div style={styles.estado}>
          <span style={styles.spinner}>⏳</span>
          <Loader message="Cargando datos" />
        </div>
      )}

      {!loading && error && (
        <div style={{ ...styles.estado, ...styles.estadoError }}>
          <p style={styles.estadoTexto}>{error}</p>
          <button style={styles.retryBtn} onClick={() => fetchData(año)}>
            Reintentar
          </button>
        </div>
      )}

      {!loading && !error && total === 0 && (
        <div style={styles.estado}>
          <span style={{ fontSize: '2rem' }}>🐾</span>
          <p style={styles.estadoTexto}>
            Sin consultas registradas en {año}.
          </p>
        </div>
      )}

      {/* ── Gráfico SVG ─────────────────────────────────────────────── */}
      {!loading && !error && total > 0 && (
        <div style={styles.svgWrap}>
          <svg
            viewBox={`0 0 ${W} ${H}`}
            style={styles.svg}
            role="img"
            aria-label={`Gráfico de consultas por mes del año ${año}`}
            onMouseLeave={() => setTooltip(null)}
          >
            <defs>
              {/* Gradiente del área */}
              <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%"   stopColor="#6366f1" stopOpacity="0.25" />
                <stop offset="100%" stopColor="#6366f1" stopOpacity="0.02" />
              </linearGradient>
              {/* Filtro de sombra suave para puntos */}
              <filter id="glow">
                <feGaussianBlur stdDeviation="2" result="blur" />
                <feMerge>
                  <feMergeNode in="blur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
            </defs>

            {/* Líneas de grilla horizontales */}
            {gridLines.map(({ y, label }) => (
              <g key={y}>
                <line
                  x1={PAD.left} y1={y}
                  x2={PAD.left + chartW} y2={y}
                  stroke="#e2e8f0" strokeWidth="1" strokeDasharray="4 3"
                />
                <text x={PAD.left - 6} y={y + 4} style={styles.axisLabel} textAnchor="end">
                  {label}
                </text>
              </g>
            ))}

            {/* Eje X: etiquetas de meses */}
            {points.map((p, i) => (
              <text
                key={i}
                x={p.x} y={PAD.top + chartH + 18}
                style={styles.axisLabel}
                textAnchor="middle"
              >
                {MESES_LABELS[i]}
              </text>
            ))}

            {/* Área rellena */}
            <path d={areaPath(points)} fill="url(#areaGrad)" />

            {/* Línea principal */}
            <polyline
              points={polyline(points)}
              fill="none"
              stroke="#6366f1"
              strokeWidth="2.5"
              strokeLinejoin="round"
              strokeLinecap="round"
            />

            {/* Puntos interactivos */}
            {points.map((p, i) => (
              <g
                key={i}
                style={{ cursor: 'pointer' }}
                onMouseEnter={() =>
                  setTooltip({ x: p.x, y: p.y, mes: p.mes, total: p.total_consultas })
                }
              >
                {/* Área de hit invisible más grande */}
                <circle cx={p.x} cy={p.y} r={10} fill="transparent" />
                {/* Punto visible */}
                <circle
                  cx={p.x} cy={p.y} r={4.5}
                  fill={p.total_consultas === pico.total_consultas ? '#4f46e5' : '#ffffff'}
                  stroke="#6366f1"
                  strokeWidth="2.5"
                  filter={p.total_consultas === pico.total_consultas ? 'url(#glow)' : undefined}
                />
              </g>
            ))}

            {/* Tooltip */}
            {tooltip && (() => {
              const tipW = 110, tipH = 48;
              const tipX = Math.min(tooltip.x - tipW / 2, W - tipW - 4);
              const tipY = tooltip.y - tipH - 12;
              return (
                <g pointerEvents="none">
                  <rect
                    x={tipX} y={tipY}
                    width={tipW} height={tipH}
                    rx={8} ry={8}
                    fill="#1e293b"
                    opacity="0.92"
                  />
                  <text x={tipX + tipW / 2} y={tipY + 17} style={styles.tipMes} textAnchor="middle">
                    {tooltip.mes}
                  </text>
                  <text x={tipX + tipW / 2} y={tipY + 36} style={styles.tipVal} textAnchor="middle">
                    {tooltip.total} consulta{tooltip.total !== 1 ? 's' : ''}
                  </text>
                </g>
              );
            })()}
          </svg>
        </div>
      )}

      {/* ── Footer ─────────────────────────────────────────────────── */}
      <p style={styles.footer}>
        Actualizado: {new Date().toLocaleString('es-PE', {
          timeZone: 'America/Lima', day: '2-digit', month: '2-digit',
          year: 'numeric', hour: '2-digit', minute: '2-digit',
        })}
      </p>
    </div>
  );
};

// ─── Estilos en objeto (sin CSS externo para portabilidad) ────────────────────
const styles = {
  card: {
    background: '#ffffff',
    borderRadius: '15px',
    padding: '1.5rem',
    boxShadow: '0 4px 15px rgba(0,0,0,0.08)',
    border: '1px solid #f1f5f9',
    fontFamily: '"Inter", sans-serif',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: '1rem',
  },
  title: {
    fontSize: '1.1rem',
    fontWeight: 700,
    color: '#1e293b',
    margin: 0,
    letterSpacing: '-0.025em',
  },
  subtitle: {
    fontSize: '0.8rem',
    color: '#64748b',
    margin: '0.25rem 0 0',
  },
  controls: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.4rem',
  },
  yearBtn: {
    background: '#f1f5f9',
    border: '1px solid #e2e8f0',
    borderRadius: '6px',
    width: '28px',
    height: '28px',
    cursor: 'pointer',
    fontSize: '1rem',
    color: '#475569',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    lineHeight: 1,
    transition: 'background 0.2s',
  },
  yearLabel: {
    fontSize: '0.95rem',
    fontWeight: 700,
    color: '#1e293b',
    minWidth: '3rem',
    textAlign: 'center',
  },
  kpiRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '1rem',
    padding: '0.75rem 1rem',
    background: '#f8fafc',
    borderRadius: '10px',
    marginBottom: '1.25rem',
  },
  kpi: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    flex: 1,
  },
  kpiValue: {
    fontSize: '1.4rem',
    fontWeight: 800,
    color: '#6366f1',
    letterSpacing: '-0.05em',
    lineHeight: 1,
  },
  kpiLabel: {
    fontSize: '0.7rem',
    color: '#94a3b8',
    marginTop: '0.2rem',
    textAlign: 'center',
  },
  kpiDivider: {
    width: '1px',
    height: '36px',
    background: '#e2e8f0',
  },
  svgWrap: {
    width: '100%',
    overflow: 'hidden',
  },
  svg: {
    width: '100%',
    height: 'auto',
    display: 'block',
  },
  axisLabel: {
    fontSize: '11px',
    fill: '#94a3b8',
    fontFamily: '"Inter", sans-serif',
  },
  tipMes: {
    fontSize: '11px',
    fill: '#94a3b8',
    fontFamily: '"Inter", sans-serif',
    fontWeight: 500,
  },
  tipVal: {
    fontSize: '13px',
    fill: '#ffffff',
    fontFamily: '"Inter", sans-serif',
    fontWeight: 700,
  },
  estado: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '2.5rem 1rem',
    gap: '0.5rem',
  },
  estadoError: {
    background: '#fef2f2',
    borderRadius: '10px',
    border: '1px solid #fecaca',
  },
  estadoTexto: {
    color: '#64748b',
    fontSize: '0.875rem',
    margin: 0,
    textAlign: 'center',
  },
  spinner: {
    fontSize: '1.75rem',
    animation: 'pulse 1.5s ease-in-out infinite',
  },
  retryBtn: {
    marginTop: '0.5rem',
    background: '#dc2626',
    color: '#fff',
    border: 'none',
    borderRadius: '8px',
    padding: '0.5rem 1.25rem',
    fontWeight: 600,
    cursor: 'pointer',
    fontSize: '0.85rem',
  },
  footer: {
    textAlign: 'center',
    color: '#94a3b8',
    fontSize: '0.75rem',
    margin: '1rem 0 0',
    borderTop: '1px solid #f1f5f9',
    paddingTop: '0.75rem',
  },
};

export default ConsultasLineChart;
