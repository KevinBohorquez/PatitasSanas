// utils/confirm.js
// Puente singleton para diálogos de confirmación con promesa, sin necesitar el hook.
// Uso:
//   import { confirm } from '../../utils/confirm';
//   if (await confirm({ variant: 'danger', message: '¿Eliminar al cliente?' })) { ... }
//
// El <ConfirmProvider> registra su handler real al montarse.

let _open = null;

export function _bindConfirm(fn) {
  _open = fn;
}

/**
 * Abre el diálogo de confirmación. Devuelve una promesa que resuelve
 * `true` (confirmar) o `false` (cancelar).
 * @param {string|object} options - mensaje, o { title, message, variant, confirmText, cancelText }
 */
export function confirm(options = {}) {
  const opts = typeof options === 'string' ? { message: options } : options;
  if (_open) {
    return _open(opts);
  }
  // Fallback defensivo si el provider aún no montó.
  return Promise.resolve(window.confirm(opts.message || '¿Está seguro?'));
}

export default confirm;
