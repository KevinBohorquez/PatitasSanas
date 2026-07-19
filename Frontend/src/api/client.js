// src/api/client.js
// Cliente HTTP central de la aplicación.
//
// Antepone la base de la API a la ruta recibida y delega en `fetch`, devolviendo
// el mismo objeto Response. Así los componentes centralizan la URL base (un solo
// lugar que cambiar) sin alterar el manejo de respuestas/errores que ya tienen.
//
// Uso:
//   const res = await apiFetch(`/mascotas/${id}`);
//   if (res.ok) { const data = await res.json(); ... }
//
// La base se resuelve contra el proxy de Vite (/api -> backend). Ver vite.config.js.
export const API_BASE = '/api/v1';

export function apiFetch(path, options) {
  const p = String(path ?? '');
  if (/^https?:\/\//i.test(p)) {
    return fetch(p, options);
  }
  const url = `${API_BASE}${p.startsWith('/') ? '' : '/'}${p}`;
  return fetch(url, options);
}

export default apiFetch;
