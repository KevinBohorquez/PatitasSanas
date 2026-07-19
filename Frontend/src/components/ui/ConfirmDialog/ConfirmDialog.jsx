// components/ui/ConfirmDialog/ConfirmDialog.jsx
// Diálogo de confirmación con mascota de PatitasSanas. Reemplaza a window.confirm().
import { useEffect, useRef } from 'react';
import confirmCat from '../../../assets/mascots/confirm.webp';
import deleteDog from '../../../assets/mascots/delete.webp';
import './ConfirmDialog.css';

export default function ConfirmDialog({
  title,
  message,
  variant = 'default',            // 'default' | 'danger'
  confirmText,
  cancelText = 'Cancelar',
  onConfirm,
  onCancel,
}) {
  const confirmBtnRef = useRef(null);
  const isDanger = variant === 'danger';
  const mascot = isDanger ? deleteDog : confirmCat;
  const heading = title || (isDanger ? '¿Eliminar?' : '¿Estás seguro?');
  const okText = confirmText || (isDanger ? 'Sí, eliminar' : 'Confirmar');

  // Foco inicial + atajos de teclado (Esc cancela, Enter confirma).
  useEffect(() => {
    confirmBtnRef.current?.focus();
    const onKey = (e) => {
      if (e.key === 'Escape') onCancel();
      else if (e.key === 'Enter') onConfirm();
    };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [onConfirm, onCancel]);

  return (
    <div className="ps-confirm-backdrop" onMouseDown={onCancel}>
      <div
        className={`ps-confirm ps-confirm--${variant}`}
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="ps-confirm-title"
        aria-describedby="ps-confirm-msg"
        onMouseDown={(e) => e.stopPropagation()}
      >
        <img className="ps-confirm__mascot" src={mascot} alt="" width="120" height="120" />
        <h3 className="ps-confirm__title" id="ps-confirm-title">{heading}</h3>
        {message && <p className="ps-confirm__message" id="ps-confirm-msg">{message}</p>}
        <div className="ps-confirm__actions">
          <button type="button" className="ps-confirm__btn ps-confirm__btn--cancel" onClick={onCancel}>
            {cancelText}
          </button>
          <button
            type="button"
            ref={confirmBtnRef}
            className={`ps-confirm__btn ps-confirm__btn--ok ${isDanger ? 'is-danger' : ''}`}
            onClick={onConfirm}
          >
            {okText}
          </button>
        </div>
      </div>
    </div>
  );
}
