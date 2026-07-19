// components/ui/EmptyState/EmptyState.jsx
// Estado vacío con la mascota de PatitasSanas (gatito durmiendo).
// Uso:  <EmptyState title="Sin solicitudes" message="No hay solicitudes pendientes." />
import emptyCat from '../../../assets/mascots/empty.webp';
import './EmptyState.css';

export default function EmptyState({
  title = 'Nada por aquí',
  message,
  action,
  size = 150,
  className = '',
}) {
  return (
    <div className={`ps-empty ${className}`.trim()} role="status">
      <img className="ps-empty__mascot" src={emptyCat} alt="" style={{ width: size }} />
      <h3 className="ps-empty__title">{title}</h3>
      {message && <p className="ps-empty__message">{message}</p>}
      {action && <div className="ps-empty__action">{action}</div>}
    </div>
  );
}
