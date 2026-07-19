import React, { useState } from 'react';
import { apiFetch } from '../../api/client';
import './BalanceFinanciero.css';

const API_BASE_URL = '/movimientos-financieros';

const BalanceFinanciero = () => {
  const [fechaDesde, setFechaDesde] = useState('');
  const [fechaHasta, setFechaHasta] = useState('');
  const [resumen, setResumen] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [consultado, setConsultado] = useState(false);

  const fetchBalance = async () => {
    if (!fechaDesde || !fechaHasta) {
      setError('Selecciona ambas fechas para consultar el balance');
      return;
    }
    if (new Date(fechaDesde) > new Date(fechaHasta)) {
      setError('La fecha desde no puede ser mayor que la fecha hasta');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const url = `${API_BASE_URL}/resumen?fecha_desde=${fechaDesde}&fecha_hasta=${fechaHasta}`;
      const response = await apiFetch(url);
      if (!response.ok) throw new Error('Error al obtener el balance');
      const data = await response.json();
      setResumen(data);
      setConsultado(true);
    } catch (err) {
      setError(err.message);
      setConsultado(false);
    } finally {
      setLoading(false);
    }
  };

  const formatMonto = (monto) => {
    return parseFloat(monto).toLocaleString('es-PE', {
      style: 'currency',
      currency: 'PEN',
      minimumFractionDigits: 2
    });
  };

  const getPorcentaje = (monto, total) => {
    if (!total || total === 0) return '0.0';
    return ((monto / total) * 100).toFixed(1);
  };

  const presetPeriodo = (dias) => {
    const hoy = new Date();
    const desde = new Date();
    desde.setDate(hoy.getDate() - dias);
    setFechaDesde(desde.toISOString().split('T')[0]);
    setFechaHasta(hoy.toISOString().split('T')[0]);
  };

  return (
    <div className="balance-financiero">
      <div className="section-header">
        <h2>Balance Financiero</h2>
      </div>

      <div className="periodo-selector">
        <div className="fecha-group">
          <label>Desde</label>
          <input
            type="date"
            value={fechaDesde}
            onChange={(e) => setFechaDesde(e.target.value)}
          />
        </div>
        <div className="fecha-group">
          <label>Hasta</label>
          <input
            type="date"
            value={fechaHasta}
            onChange={(e) => setFechaHasta(e.target.value)}
          />
        </div>
        <div className="preset-buttons">
          <button onClick={() => presetPeriodo(7)}>7 días</button>
          <button onClick={() => presetPeriodo(30)}>30 días</button>
          <button onClick={() => presetPeriodo(90)}>90 días</button>
          <button onClick={() => presetPeriodo(365)}>1 año</button>
        </div>
        <button className="btn-consultar" onClick={fetchBalance} disabled={loading}>
          {loading ? 'Consultando...' : 'Consultar'}
        </button>
      </div>

      {error && (
        <div className="error-message">
          <p>Error: {error}</p>
        </div>
      )}

      {consultado && resumen && (
        <>
          <div className="resumen-cards">
            <div className="resumen-card ingreso">
              <h3>Total Ingresos</h3>
              <p className="monto">{formatMonto(resumen.total_ingresos)}</p>
            </div>
            <div className="resumen-card egreso">
              <h3>Total Egresos</h3>
              <p className="monto">{formatMonto(resumen.total_egresos)}</p>
            </div>
            <div className={`resumen-card ${resumen.saldo_neto >= 0 ? 'saldo-positivo' : 'saldo-negativo'}`}>
              <h3>Ganancia Neta</h3>
              <p className="monto">{formatMonto(resumen.saldo_neto)}</p>
            </div>
          </div>

          <div className="desglose-section">
            <h3>Desglose de Ingresos</h3>
            {Object.keys(resumen.desglose_ingresos).length === 0 ? (
              <p className="empty-text">No hay ingresos en este período</p>
            ) : (
              <div className="tabla-container">
                <table className="tabla-desglose">
                  <thead>
                    <tr>
                      <th>Categoría</th>
                      <th>Monto</th>
                      <th>% del Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(resumen.desglose_ingresos).map(([cat, monto]) => (
                      <tr key={cat} className="fila-ingreso">
                        <td>{cat}</td>
                        <td className="monto-cell">{formatMonto(monto)}</td>
                        <td>
                          <div className="porcentaje-bar">
                            <div
                              className="porcentaje-fill ingreso"
                              style={{ width: `${getPorcentaje(monto, resumen.total_ingresos)}%` }}
                            ></div>
                            <span>{getPorcentaje(monto, resumen.total_ingresos)}%</span>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          <div className="desglose-section">
            <h3>Desglose de Egresos</h3>
            {Object.keys(resumen.desglose_egresos).length === 0 ? (
              <p className="empty-text">No hay egresos en este período</p>
            ) : (
              <div className="tabla-container">
                <table className="tabla-desglose">
                  <thead>
                    <tr>
                      <th>Categoría</th>
                      <th>Monto</th>
                      <th>% del Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(resumen.desglose_egresos).map(([cat, monto]) => (
                      <tr key={cat} className="fila-egreso">
                        <td>{cat}</td>
                        <td className="monto-cell">{formatMonto(monto)}</td>
                        <td>
                          <div className="porcentaje-bar">
                            <div
                              className="porcentaje-fill egreso"
                              style={{ width: `${getPorcentaje(monto, resumen.total_egresos)}%` }}
                            ></div>
                            <span>{getPorcentaje(monto, resumen.total_egresos)}%</span>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}

      {!consultado && !loading && (
        <div className="placeholder">
          <p>Selecciona un período y haz clic en "Consultar" para ver el balance financiero</p>
        </div>
      )}
    </div>
  );
};

export default BalanceFinanciero;
