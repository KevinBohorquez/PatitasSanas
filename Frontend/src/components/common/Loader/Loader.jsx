// components/common/Loader/Loader.jsx
// Indicador de carga con la mascota de PatitasSanas (perrito corriendo animado).
//
// Uso:
//   {loading && <Loader message="Cargando solicitudes" />}
//   <Loader overlay />                 // pantalla completa (backdrop)
//   <Loader size={80} message="" />    // solo la mascota, más pequeña
import loadingDog from '../../../assets/mascots/loading.webp';
import './Loader.css';

export default function Loader({
  message = 'Cargando',
  size = 120,
  overlay = false,
  className = '',
}) {
  const body = (
    <div className={`ps-loader ${className}`.trim()} role="status" aria-live="polite">
      <div className="ps-loader__stage">
        <img className="ps-loader__mascot" src={loadingDog} alt="" style={{ width: size }} />
        <span className="ps-loader__shadow" />
      </div>
      {message && (
        <p className="ps-loader__text">
          {message}
          <span className="ps-loader__dots" aria-hidden="true"><i>.</i><i>.</i><i>.</i></span>
        </p>
      )}
      <span className="ps-loader__sr">Cargando, por favor espere</span>
    </div>
  );

  return overlay ? <div className="ps-loader-overlay">{body}</div> : body;
}
