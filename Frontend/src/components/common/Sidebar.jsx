import React from 'react';
import '../../styles/Dashboard.css';

const Sidebar = ({ items = [], activeItem, onItemClick }) => {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="logo">
          <span className="logo-text">Veterinaria</span>
          <span className="logo-subtext">COLITAS FELICES</span>
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
  );
};

export default Sidebar;