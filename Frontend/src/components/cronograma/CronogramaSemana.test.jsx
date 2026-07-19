// src/components/cronograma/CronogramaSemana.test.jsx
import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import CronogramaSemana from './CronogramaSemana';
import { apiFetch } from '../../api/client';

vi.mock('../../api/client', () => ({ apiFetch: vi.fn() }));
const mockRes = (data, ok = true) =>
  Promise.resolve({ ok, status: ok ? 200 : 500, json: () => Promise.resolve(data) });

const semana = {
  dias: [
    {
      fecha: '2026-07-13',
      dia_semana: 'Lunes',
      veterinarios: [
        { id_veterinario: 1, turno: 'Mañana', veterinario: 'Dr. House', estado: 'Activo', origen: 'recurrente' },
      ],
    },
  ],
};

describe('CronogramaSemana', () => {
  beforeEach(() => vi.clearAllMocks());

  it('muestra el estado de carga al inicio', () => {
    apiFetch.mockReturnValue(mockRes(semana));
    render(<CronogramaSemana />);
    expect(screen.getByText('Cargando...')).toBeInTheDocument();
  });

  it('renderiza la grilla con los datos', async () => {
    apiFetch.mockReturnValue(mockRes(semana));
    render(<CronogramaSemana />);
    await waitFor(() => expect(screen.getByText('Dr. House')).toBeInTheDocument());
    expect(screen.getByText('Lunes')).toBeInTheDocument();
  });

  it('muestra error cuando la API falla', async () => {
    apiFetch.mockReturnValue(mockRes(null, false));
    render(<CronogramaSemana />);
    await waitFor(() =>
      expect(screen.getByText(/No se pudo cargar la semana/)).toBeInTheDocument(),
    );
  });
});
