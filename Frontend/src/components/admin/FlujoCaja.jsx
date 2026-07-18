import React, { useState, useEffect } from 'react';
import { apiFetch } from '../../api/client';
import './FlujoCaja.css';
import Loader from '../common/Loader/Loader';

const API_BASE_URL = '/movimientos-financieros';

const FlujoCaja = () => {
  const [movimientos, setMovimientos] = useState([]);
  const [resumen, setResumen] = useState({ total_ingresos: 0, total_egresos: 0, saldo_neto: 0 });
  const [filtro, setFiltro] = useState('todos');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    tipo: 'Egreso',
    categoria: 'Operativo',
    monto: '',
    concepto: '',
    fecha: new Date().toISOString().split('T')[0]
  });
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState(null);

  const fetchMovimientos = async (tipo = null) => {
    try {
      setLoading(true);
      setError(null);
      let url = `${API_BASE_URL}/`;
      if (tipo && tipo !== 'todos') {
        url += `?tipo=${tipo}`;
      }
      const response = await apiFetch(url);
      if (!response.ok) throw new Error('Error al cargar movimientos');
      const data = await response.json();
      setMovimientos(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchResumen = async () => {
    try {
      const response = await apiFetch(`${API_BASE_URL}/resumen`);
      if (!response.ok) throw new Error('Error al cargar resumen');
      const data = await response.json();
      setResumen(data);
    } catch (err) {
      console.error('Error fetching resumen:', err);
    }
  };

  useEffect(() => {
    fetchMovimientos();
    fetchResumen();
  }, []);

  useEffect(() => {
    fetchMovimientos(filtro);
  }, [filtro]);

  const handleFiltroChange = (nuevoFiltro) => {
    setFiltro(nuevoFiltro);
  };

  const formatMonto = (monto) => {
    return parseFloat(monto).toLocaleString('es-PE', {
      style: 'currency',
      currency: 'PEN',
      minimumFractionDigits: 2
    });
  };

  const formatFecha = (fechaStr) => {
    return new Date(fechaStr).toLocaleString('es-PE', {
      timeZone: 'America/Lima',
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const openModal = (tipo = 'Egreso') => {
    setFormData({
      tipo,
      categoria: tipo === 'Ingreso' ? 'Servicio' : 'Operativo',
      monto: '',
      concepto: '',
      fecha: new Date().toISOString().split('T')[0]
    });
    setFormError(null);
    setShowModal(true);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError(null);

    const montoNum = parseFloat(formData.monto);
    if (!montoNum || montoNum <= 0) {
      setFormError('El monto debe ser mayor a 0');
      return;
    }
    if (!formData.concepto || formData.concepto.trim().length < 3) {
      setFormError('El concepto debe tener al menos 3 caracteres');
      return;
    }

    const payload = {
      tipo: formData.tipo,
      categoria: formData.categoria,
      monto: montoNum,
      concepto: formData.concepto.trim(),
      fecha_movimiento: new Date(formData.fecha).toISOString()
    };

    setSubmitting(true);
    try {
      const response = await apiFetch(`${API_BASE_URL}/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Error al registrar movimiento');
      }
      setShowModal(false);
      fetchMovimientos(filtro);
      fetchResumen();
    } catch (err) {
      setFormError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="flujo-caja">
      <div className="section-header">
        <h2>Flujo de Caja</h2>
        <div className="header-actions">
          <button className="btn-registrar" onClick={() => openModal('Ingreso')}>
            + Registrar Ingreso
          </button>
          <button className="btn-registrar egreso" onClick={() => openModal('Egreso')}>
            + Registrar Gasto
          </button>
        </div>
      </div>

      {error && (
        <div className="error-message">
          <p>Error: {error}</p>
          <button onClick={() => fetchMovimientos(filtro)} className="btn-retry">Reintentar</button>
        </div>
      )}

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
          <h3>Saldo Neto</h3>
          <p className="monto">{formatMonto(resumen.saldo_neto)}</p>
        </div>
      </div>

      <div className="filtros">
        <button
          className={`filtro-btn ${filtro === 'todos' ? 'active' : ''}`}
          onClick={() => handleFiltroChange('todos')}
        >
          Todos
        </button>
        <button
          className={`filtro-btn ${filtro === 'Ingreso' ? 'active' : ''}`}
          onClick={() => handleFiltroChange('Ingreso')}
        >
          Ingresos
        </button>
        <button
          className={`filtro-btn ${filtro === 'Egreso' ? 'active' : ''}`}
          onClick={() => handleFiltroChange('Egreso')}
        >
          Egresos
        </button>
      </div>

      {loading ? (
        <Loader message="Cargando movimientos" />
      ) : (
        <div className="tabla-container">
          <table className="tabla-movimientos">
            <thead>
              <tr>
                <th>ID</th>
                <th>Tipo</th>
                <th>Categoría</th>
                <th>Monto</th>
                <th>Concepto</th>
                <th>Fecha</th>
                <th>Cita</th>
              </tr>
            </thead>
            <tbody>
              {movimientos.length === 0 ? (
                <tr>
                  <td colSpan="7" className="empty-message">No hay movimientos registrados</td>
                </tr>
              ) : (
                movimientos.map((m) => (
                  <tr key={m.id_movimiento} className={`fila-${m.tipo.toLowerCase()}`}>
                    <td>{m.id_movimiento}</td>
                    <td>
                      <span className={`tipo-badge tipo-${m.tipo.toLowerCase()}`}>
                        {m.tipo}
                      </span>
                    </td>
                    <td>{m.categoria}</td>
                    <td className="monto-cell">{formatMonto(m.monto)}</td>
                    <td className="concepto-cell" title={m.concepto}>{m.concepto}</td>
                    <td>{formatFecha(m.fecha_movimiento)}</td>
                    <td>{m.id_cita || '-'}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-container" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Registrar {formData.tipo === 'Ingreso' ? 'Ingreso' : 'Gasto'}</h3>
              <button className="modal-close" onClick={() => setShowModal(false)}>&times;</button>
            </div>
            <form onSubmit={handleSubmit} className="modal-form">
              {formError && <div className="form-error">{formError}</div>}

              <div className="form-group">
                <label>Tipo</label>
                <select name="tipo" value={formData.tipo} onChange={handleInputChange}>
                  <option value="Ingreso">Ingreso</option>
                  <option value="Egreso">Egreso</option>
                </select>
              </div>

              <div className="form-group">
                <label>Categoría</label>
                <select name="categoria" value={formData.categoria} onChange={handleInputChange}>
                  {formData.tipo === 'Ingreso' ? (
                    <option value="Servicio">Servicio</option>
                  ) : (
                    <>
                      <option value="Operativo">Operativo</option>
                      <option value="Nomina">Nómina</option>
                    </>
                  )}
                </select>
              </div>

              <div className="form-group">
                <label>Monto (S/)</label>
                <input
                  type="number"
                  name="monto"
                  step="0.01"
                  min="0.01"
                  placeholder="0.00"
                  value={formData.monto}
                  onChange={handleInputChange}
                  required
                />
              </div>

              <div className="form-group">
                <label>Concepto</label>
                <input
                  type="text"
                  name="concepto"
                  placeholder="Describe el movimiento"
                  value={formData.concepto}
                  onChange={handleInputChange}
                  required
                />
              </div>

              <div className="form-group">
                <label>Fecha</label>
                <input
                  type="date"
                  name="fecha"
                  value={formData.fecha}
                  onChange={handleInputChange}
                  required
                />
              </div>

              <div className="modal-actions">
                <button type="button" className="btn-cancelar" onClick={() => setShowModal(false)}>
                  Cancelar
                </button>
                <button type="submit" className="btn-guardar" disabled={submitting}>
                  {submitting ? 'Guardando...' : 'Guardar'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default FlujoCaja;
