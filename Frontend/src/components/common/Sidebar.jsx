import React, { useState, useRef } from 'react';
import '../../styles/Dashboard.css';

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
          <div className="mobile-nav-top">
            <span className="mobile-nav-title">Menú</span>
            <button
              type="button"
              className="mobile-nav-close"
              aria-label="Cerrar menú"
              onClick={() => setMobileOpen(false)}
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round">
                <line x1="6" y1="6" x2="18" y2="18" />
                <line x1="18" y1="6" x2="6" y2="18" />
              </svg>
            </button>
          </div>

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
                    <span className="mobile-nav-card-icon">{item.icon}</span>
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
