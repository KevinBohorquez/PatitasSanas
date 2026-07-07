// context/ToastContext.jsx
// Sistema de notificaciones "Toast" propio, sin dependencias externas.
// Uso:
//   const toast = useToast();
//   toast.success('Cita guardada');
//   toast.error('Error al guardar el historial', { title: 'Ups' });
//   toast.warning('Faltan datos en el triaje');
//   toast.info('Sincronizando...', { duration: 6000 });
//   toast.show({ type: 'success', title: 'Bienvenido', message: 'Sesión iniciada' });
import { createContext, useContext, useState, useCallback, useMemo, useEffect } from 'react';
import { createPortal } from 'react-dom';
import Toast from '../components/common/Toast/Toast';
import { _bindToast } from '../utils/toast';
import '../components/common/Toast/Toast.css';

const ToastContext = createContext(null);

let idSeq = 0;

export function ToastProvider({
  children,
  position = 'top-right',        // top-right | top-left | bottom-right | bottom-left | top-center | bottom-center
  defaultDuration = 4000,        // ms (usar 0 para que no se auto-cierre)
}) {
  const [toasts, setToasts] = useState([]);

  const dismiss = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const show = useCallback((input) => {
    const opts = typeof input === 'string' ? { message: input } : (input || {});
    const id = ++idSeq;
    const toast = {
      id,
      type: opts.type || 'info',
      title: opts.title,
      message: opts.message || '',
      duration: opts.duration ?? defaultDuration,
    };
    setToasts((prev) => [...prev, toast]);
    return id;
  }, [defaultDuration]);

  const api = useMemo(() => {
    const withType = (type) => (message, options = {}) => show({ type, message, ...options });
    return {
      show,
      dismiss,
      success: withType('success'),
      error: withType('error'),
      warning: withType('warning'),
      info: withType('info'),
    };
  }, [show, dismiss]);

  // Expone la API al puente singleton (utils/toast.js) para usar toast.* sin el hook.
  useEffect(() => {
    _bindToast(api);
  }, [api]);

  return (
    <ToastContext.Provider value={api}>
      {children}
      {createPortal(
        <div className={`toast-viewport toast-viewport--${position}`} role="region" aria-label="Notificaciones">
          {toasts.map((t) => (
            <Toast key={t.id} {...t} onDismiss={dismiss} />
          ))}
        </div>,
        document.body
      )}
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) {
    throw new Error('useToast() debe usarse dentro de <ToastProvider>');
  }
  return ctx;
}

export default ToastContext;
