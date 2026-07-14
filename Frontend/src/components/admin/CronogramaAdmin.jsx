import React, { useState } from 'react';
import '../cronograma/Cronograma.css';
import CronogramaManagement from './CronogramaManagement';
import { CONFIG_VET, CONFIG_RECEP } from '../cronograma/cronogramaConfig';

// Vista del admin: dos secciones de cronograma (veterinarios y recepcionistas),
// cada una con sus pestañas Día/Semana/Calendario. Exclusiva del administrador.
const CronogramaAdmin = () => {
  const [rol, setRol] = useState('vet');

  return (
    <div>
      <div className="cro-tabs" style={{ marginBottom: 4 }}>
        <button className={`cro-tab ${rol === 'vet' ? 'active' : ''}`} onClick={() => setRol('vet')}>
          👨‍⚕️ Veterinarios
        </button>
        <button className={`cro-tab ${rol === 'recep' ? 'active' : ''}`} onClick={() => setRol('recep')}>
          👩‍💼 Recepcionistas
        </button>
      </div>

      {rol === 'vet'
        ? <CronogramaManagement config={CONFIG_VET} />
        : <CronogramaManagement config={CONFIG_RECEP} />}
    </div>
  );
};

export default CronogramaAdmin;
