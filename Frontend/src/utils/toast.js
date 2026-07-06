// utils/toast.js
// Puente singleton para disparar notificaciones toast desde cualquier lugar
// (componentes, handlers, funciones utilitarias) sin necesitar el hook useToast().
// El <ToastProvider> registra su API real al montarse (ver ToastContext.jsx).

let _api = null;

/** Lo llama internamente el ToastProvider para registrar su API. */
export function _bindToast(api) {
  _api = api;
}

function call(method, ...args) {
  if (_api && typeof _api[method] === 'function') {
    return _api[method](...args);
  }
  // Fallback defensivo: si el provider aún no montó, no rompemos el flujo.
  if (typeof console !== 'undefined') {
    console.warn('[toast] ToastProvider no está montado todavía:', method, args[0]);
  }
  return null;
}

export const toast = {
  success: (message, options) => call('success', message, options),
  error:   (message, options) => call('error', message, options),
  warning: (message, options) => call('warning', message, options),
  info:    (message, options) => call('info', message, options),
  show:    (options) => call('show', options),
  dismiss: (id) => call('dismiss', id),
};

export default toast;
