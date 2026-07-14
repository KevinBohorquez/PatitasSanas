import React, { useState, useRef } from 'react';
import '../../styles/Dashboard.css';

// Iconos SVG usados SOLO en el menú móvil (en escritorio se mantiene el emoji).
// Se mapean por el id de cada opción; si un id no tiene SVG, se usa el emoji.
const svgProps = {
  viewBox: '0 0 24 24',
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 1.9,
  strokeLinecap: 'round',
  strokeLinejoin: 'round',
};

const navSvgIcons = {
  inicio: (
    <svg {...svgProps}><path d="M3 10.5 12 3l9 7.5" /><path d="M5 9.5V21h14V9.5" /><path d="M9.5 21v-6h5v6" /></svg>
  ),
  clientes: (
    <svg {...svgProps}><circle cx="9" cy="8" r="3.2" /><path d="M3.5 19a5.5 5.5 0 0 1 11 0" /><path d="M16 6.2a3.2 3.2 0 0 1 0 6" /><path d="M17 14.3a5.5 5.5 0 0 1 3.5 4.7" /></svg>
  ),
  usuarios: (
    <svg {...svgProps}><circle cx="12" cy="8" r="3.5" /><path d="M5 20a7 7 0 0 1 14 0" /></svg>
  ),
  mascotas: (
    <svg viewBox="0 0 24 24" fill="currentColor" stroke="none"><ellipse cx="6" cy="11" rx="1.7" ry="2.1" /><ellipse cx="10" cy="7.5" rx="1.7" ry="2.1" /><ellipse cx="14" cy="7.5" rx="1.7" ry="2.1" /><ellipse cx="18" cy="11" rx="1.7" ry="2.1" /><path d="M12 12.5c-2.6 0-4.7 2.1-4.7 4.4 0 1.6 1.3 2.6 2.8 2.6.8 0 1.3-.4 1.9-.4s1.1.4 1.9.4c1.5 0 2.8-1 2.8-2.6 0-2.3-2.1-4.4-4.7-4.4z" /></svg>
  ),
  solicitudes: (
    <svg {...svgProps}><rect x="5" y="4" width="14" height="17" rx="2" /><path d="M9 4V3.5A1.5 1.5 0 0 1 10.5 2h3A1.5 1.5 0 0 1 15 3.5V4" /><path d="M8.5 10h7M8.5 14h7M8.5 18h4" /></svg>
  ),
  citas: (
    <svg {...svgProps}><rect x="3.5" y="5" width="17" height="16" rx="2" /><path d="M8 3v4M16 3v4M3.5 10h17" /><path d="M9 15.5l2 2 4-4" /></svg>
  ),
  cronograma: (
    <svg {...svgProps}><rect x="3.5" y="3.5" width="7" height="7" rx="1.3" /><rect x="13.5" y="3.5" width="7" height="7" rx="1.3" /><rect x="3.5" y="13.5" width="7" height="7" rx="1.3" /><rect x="13.5" y="13.5" width="7" height="7" rx="1.3" /></svg>
  ),
  veterinarios: (
    <svg {...svgProps}><path d="M6 3v5a4.5 4.5 0 0 0 9 0V3" /><path d="M6 3H4.3M15 3h1.7" /><path d="M10.5 15.5a5 5 0 0 0 5 5 3.8 3.8 0 0 0 3.8-3.8v-1.4" /><circle cx="19.3" cy="12.5" r="2" /></svg>
  ),
  recepcionistas: (
    <svg {...svgProps}><path d="M4.5 13v-1a7.5 7.5 0 0 1 15 0v1" /><rect x="2.5" y="12.5" width="4" height="6" rx="2" /><rect x="17.5" y="12.5" width="4" height="6" rx="2" /><path d="M19.5 18.5a4 4 0 0 1-4 3.5h-2.5" /></svg>
  ),
  servicios: (
    <svg {...svgProps}><rect x="3" y="7.5" width="18" height="12.5" rx="2" /><path d="M8.5 7.5v-1A2 2 0 0 1 10.5 4.5h3a2 2 0 0 1 2 2v1" /><path d="M12 11v5M9.5 13.5h5" /></svg>
  ),
  reportes: (
    <svg {...svgProps}><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z" /><path d="M14 3v5h5" /><path d="M9 13h6M9 16.5h4" /></svg>
  ),
  analytics: (
    <svg {...svgProps}><path d="M4 3v17h17" /><rect x="7.5" y="12" width="2.8" height="5.5" rx="0.5" /><rect x="12.5" y="8.5" width="2.8" height="9" rx="0.5" /><rect x="17.5" y="5" width="2.8" height="12.5" rx="0.5" /></svg>
  ),
  flujocaja: (
    <svg {...svgProps}><rect x="2.5" y="6.5" width="19" height="11" rx="2" /><circle cx="12" cy="12" r="2.4" /><path d="M6 12h.01M18 12h.01" /></svg>
  ),
  balance: (
    <svg {...svgProps}><path d="M3 17l6-6 4 4 8-8" /><path d="M15 7h6v6" /></svg>
  ),
};

const Sidebar = ({ items = [], activeItem, onItemClick }) => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState(0);
  const pagesRef = useRef(null);

  const openMenu = () => {
    setCurrentPage(0);
    setMobileOpen(true);
  };

  const handleSelect = (id) => {
    onItemClick(id);
    setMobileOpen(false);
  };

  const handlePagesScroll = () => {
    const el = pagesRef.current;
    if (!el || el.clientWidth === 0) return;
    setCurrentPage(Math.round(el.scrollLeft / el.clientWidth));
  };

  // Agrupar las opciones en páginas de 4 (rejilla 2x2) para el menú móvil.
  const pages = [];
  for (let i = 0; i < items.length; i += 4) {
    pages.push(items.slice(i, i + 4));
  }

  return (
    <>
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="logo">
            <span className="logo-text">Veterinaria</span>
            <span className="logo-subtext">PATITAS SANAS</span>
            <img src="https://i.ibb.co/rG8YQzjQ/Logo-Veterinaria-Sin-Letras-Recorte.png" alt="Logo Veterinaria" className="logo-image" />
          </div>
        </div>

        <nav className="sidebar-nav">
          <ul className="nav-list">
            {items.map((item) => (
              <li key={item.id} className="nav-item">
                <button
                  className={`nav-link ${activeItem === item.id ? 'active' : ''}`}
                  onClick={() => onItemClick(item.id)}
                >
                  <span className="nav-icon">{item.icon}</span>
                  <span className="nav-label">{item.label}</span>
                </button>
              </li>
            ))}
          </ul>
        </nav>
      </aside>

      {/* Botón hamburguesa flotante (solo móvil) */}
      <button
        type="button"
        className="mobile-nav-fab"
        aria-label="Abrir menú de navegación"
        aria-expanded={mobileOpen}
        onClick={openMenu}
      >
        <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
          <line x1="3" y1="6" x2="21" y2="6" />
          <line x1="3" y1="12" x2="21" y2="12" />
          <line x1="3" y1="18" x2="21" y2="18" />
        </svg>
      </button>

      {/* Overlay del menú móvil: opciones en rejilla 2x2 deslizable */}
      <div
        className={`mobile-nav-overlay ${mobileOpen ? 'open' : ''}`}
        onClick={() => setMobileOpen(false)}
      >
        <div className="mobile-nav-panel" onClick={(e) => e.stopPropagation()}>
          <div className="mobile-nav-pages" ref={pagesRef} onScroll={handlePagesScroll}>
            {pages.map((page, pi) => (
              <div className="mobile-nav-page" key={pi}>
                {page.map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    className={`mobile-nav-card ${activeItem === item.id ? 'active' : ''}`}
                    onClick={() => handleSelect(item.id)}
                  >
                    <span className="mobile-nav-card-icon">{navSvgIcons[item.id] || item.icon}</span>
                    <span className="mobile-nav-card-label">{item.label}</span>
                  </button>
                ))}
              </div>
            ))}
          </div>

          {pages.length > 1 && (
            <div className="mobile-nav-dots">
              {pages.map((_, di) => (
                <span key={di} className={`mobile-nav-dot ${currentPage === di ? 'active' : ''}`} />
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default Sidebar;
