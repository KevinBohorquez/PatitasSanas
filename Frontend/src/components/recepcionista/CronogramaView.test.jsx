// src/components/recepcionista/CronogramaView.test.jsx
import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import CronogramaView from './CronogramaView';
import { apiFetch } from '../../api/client';

vi.mock('../../api/client', () => ({ apiFetch: vi.fn() }));
const mockRes = (data, ok = true) =>
  Promise.resolve({ ok, status: ok ? 200 : 500, json: () => Promise.resolve(data) });

const dia = {
  dia_semana: 'Lunes',
  total: 1,
  veterinarios: [
    { id_veterinario: 1, turno: 'Mañana', veterinario: 'Dr. House', especialidad: 'Cirugía', estado: 'Activo', origen: 'recurrente' },
  ],
};

describe('CronogramaView', () => {
  beforeEach(() => vi.clearAllMocks());

  it('muestra el estado de carga al inicio', () => {
    apiFetch.mockReturnValue(mockRes(dia));
    render(<CronogramaView />);
    expect(screen.getByText('Cargando...')).toBeInTheDocument();
  });

  it('renderiza la tabla del día con los datos', async () => {
    apiFetch.mockReturnValue(mockRes(dia));
    render(<CronogramaView />);
    await waitFor(() => expect(screen.getByText('Dr. House')).toBeInTheDocument());
    expect(screen.getByText(/veterinario\(s\) en turno/)).toBeInTheDocument();
  });

  it('muestra error cuando la API falla', async () => {
    apiFetch.mockReturnValue(mockRes(null, false));
    render(<CronogramaView />);
    await waitFor(() =>
      expect(screen.getByText(/No se pudo cargar el cronograma/)).toBeInTheDocument(),
    );
  });
});
