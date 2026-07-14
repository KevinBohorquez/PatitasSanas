import React, { useState } from 'react';
import EmptyState from './EmptyState/EmptyState';
import '../../styles/Dashboard.css';

const Table = ({ columns, data, actions, emptyMessage = "No hay datos disponibles", mobileTitle }) => {
  // En móvil cada fila se muestra como una tarjeta tipo acordeón: la primera
  // celda es la cabecera y, al tocarla, se despliegan el resto de campos.
  const [expandedRows, setExpandedRows] = useState({});
  const toggleRow = (index) => {
    setExpandedRows((prev) => ({ ...prev, [index]: !prev[index] }));
  };

  return (
    <div className="table-container">
      <table className="data-table">
        <thead>
          <tr>
            {columns.map((column, index) => (
              <th key={index}>{column.header}</th>
            ))}
            {actions && <th>ACCIONES</th>}
          </tr>
        </thead>
        <tbody>
          {data.length === 0 ? (
            <tr>
              <td colSpan={columns.length + (actions ? 1 : 0)} className="empty-message">
                <EmptyState title={emptyMessage} size={130} />
              </td>
            </tr>
          ) : (
            data.map((row, rowIndex) => (
              <tr key={rowIndex} className={expandedRows[rowIndex] ? 'expanded' : ''}>
                {columns.map((column, colIndex) => (
                  <td
                    key={colIndex}
                    data-label={column.header}
                    className={colIndex === 0 ? `card-header-cell${mobileTitle ? ' has-mobile-title' : ''}` : ''}
                    onClick={colIndex === 0 ? () => toggleRow(rowIndex) : undefined}
                  >
                    {colIndex === 0 && mobileTitle ? (
                      <>
                        <span className="cell-desktop-value">
                          {column.render ? column.render(row) : row[column.key]}
                        </span>
                        <span className="cell-mobile-title">{mobileTitle(row)}</span>
                      </>
                    ) : (
                      column.render ? column.render(row) : row[column.key]
                    )}
                  </td>
                ))}
                {actions && (
                  <td data-label="Acciones">
                    <div className="action-buttons">
                      {actions.map((action, actionIndex) => {
                        const label = typeof action.label === 'function' ? action.label(row) : action.label;
                        const type = typeof action.type === 'function' ? action.type(row) : action.type;
                        const title = typeof action.title === 'function' ? action.title(row) : action.title;
                        return (
                          <button
                            key={actionIndex}
                            className={`action-btn ${type}`}
                            title={title}
                            onClick={() => action.onClick(row)}
                          >
                            {label}
                          </button>
                        );
                      })}
                    </div>
                  </td>
                )}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};

export default Table;
