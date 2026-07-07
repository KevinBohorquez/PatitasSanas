// components/common/Toast/Toast.jsx
// Notificación individual: ícono, título/mensaje, botón de cierre, barra de progreso,
// animación de entrada/salida, auto-cierre con pausa al pasar el mouse.
import { useEffect, useRef, useState, useCallback } from 'react';
import successIcon from '../../../assets/toast/success.webp';
import errorIcon from '../../../assets/toast/error.webp';
import warningIcon from '../../../assets/toast/warning.webp';
import infoIcon from '../../../assets/toast/info.webp';

// Mascotas de PatitasSanas como ícono según el tipo.
const ICONS = {
  success: successIcon,
  error: errorIcon,
  warning: warningIcon,
  info: infoIcon,
};

const DEFAULT_TITLES = {
  success: 'Éxito',
  error: 'Error',
  warning: 'Advertencia',
  info: 'Información',
};

export default function Toast({ id, type = 'info', title, message, duration = 4000, onDismiss }) {
  const [leaving, setLeaving] = useState(false);
  const timerRef = useRef(null);
  const remainingRef = useRef(duration);
  const startRef = useRef(0);

  const close = useCallback(() => setLeaving(true), []);

  const startTimer = useCallback(() => {
    if (duration <= 0) return;
    startRef.current = Date.now();
    clearTimeout(timerRef.current);
    timerRef.current = setTimeout(close, remainingRef.current);
  }, [duration, close]);

  const pauseTimer = useCallback(() => {
    if (duration <= 0) return;
    clearTimeout(timerRef.current);
    remainingRef.current -= Date.now() - startRef.current;
  }, [duration]);

  useEffect(() => {
    startTimer();
    return () => clearTimeout(timerRef.current);
  }, [startTimer]);

  // Al terminar la animación de salida, se remueve del estado.
  const handleAnimationEnd = (e) => {
    if (leaving && e.animationName === 'toast-out') {
      onDismiss(id);
    }
  };

  const isUrgent = type === 'error' || type === 'warning';

  return (
    <div
      className={`toast toast--${type} ${leaving ? 'toast--leaving' : 'toast--entering'}`}
      role={isUrgent ? 'alert' : 'status'}
      aria-live={type === 'error' ? 'assertive' : 'polite'}
      onMouseEnter={pauseTimer}
      onMouseLeave={startTimer}
      onAnimationEnd={handleAnimationEnd}
    >
      <img className="toast__icon" src={ICONS[type] || ICONS.info} alt="" aria-hidden="true" width="44" height="44" />

      <div className="toast__content">
        <p className="toast__title">{title || DEFAULT_TITLES[type]}</p>
        {message && <p className="toast__message">{message}</p>}
      </div>

      <button type="button" className="toast__close" onClick={close} aria-label="Cerrar notificación">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor"
             strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M18 6 6 18M6 6l12 12" />
        </svg>
      </button>

      {duration > 0 && (
        <span className="toast__progress" style={{ animationDuration: `${duration}ms` }} />
      )}
    </div>
  );
}
