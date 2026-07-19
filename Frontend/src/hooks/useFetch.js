// src/hooks/useFetch.js
// Hook reutilizable para la carga de un recurso vía la capa api/ (apiFetch).
// Encapsula el patrón repetido de loading / error / data + recarga.
//
// Uso:
//   const { data, loading, error, refetch } = useFetch(`/veterinarios/dashboard/${id}`, {
//     deps: [id],
//     enabled: !!id,
//     transform: (json) => json.items,      // opcional
//     errorMessage: 'No se pudo cargar',     // opcional (mensaje fijo)
//   });
//
// Devuelve el dato ya parseado (json). Lanza el manejo de error a `error` como
// string. `refetch` re-ejecuta la carga; `setData` permite ajustes locales.
import { useState, useEffect, useCallback } from 'react';
import { apiFetch } from '../api/client';

export function useFetch(path, options = {}) {
  const {
    deps = [],
    enabled = true,
    transform,
    errorMessage,
    init,
    onSuccess,
  } = options;

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(enabled);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    if (!enabled) return;
    setLoading(true);
    setError(null);
    try {
      const res = await apiFetch(path, init);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      const result = transform ? transform(json) : json;
      setData(result);
      if (onSuccess) onSuccess(result);
    } catch (err) {
      setError(errorMessage || err.message || 'Error al cargar los datos');
    } finally {
      setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => {
    load();
  }, [load]);

  return { data, loading, error, refetch: load, setData, setError };
}

export default useFetch;
