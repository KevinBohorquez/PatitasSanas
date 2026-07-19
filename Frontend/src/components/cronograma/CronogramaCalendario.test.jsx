// src/components/cronograma/CronogramaCalendario.test.jsx
import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import CronogramaCalendario from './CronogramaCalendario';
import { apiFetch } from '../../api/client';

vi.mock('../../api/client', () => ({ apiFetch: vi.fn() }));
const mockRes = (data, ok = true) =>
  Promise.resolve({ ok, status: ok ? 200 : 500, json: () => Promise.resolve(data) });

const mesData = {
  dias: [
    { fecha: '2026-07-01', total: 3 },
    { fecha: '2026-07-02', total: 0 },
  ],
};

describe('CronogramaCalendario', () => {
  beforeEach(() => vi.clearAllMocks());

  it('muestra el estado de carga al inicio', () => {
    apiFetch.mockReturnValue(mockRes(mesData));
    render(<CronogramaCalendario />);
    expect(screen.getByText('Cargando...')).toBeInTheDocument();
  });

  it('renderiza la grilla del mes con los datos', async () => {
    apiFetch.mockReturnValue(mockRes(mesData));
    const { container } = render(<CronogramaCalendario />);
    await waitFor(() =>
      expect(container.querySelector('.cro-cal-grid')).toBeInTheDocument(),
    );
    expect(container.querySelector('.cro-cal-badge')?.textContent).toContain('3');
  });

  it('muestra error cuando la API falla', async () => {
    apiFetch.mockReturnValue(mockRes(null, false));
    render(<CronogramaCalendario />);
    await waitFor(() =>
      expect(screen.getByText(/No se pudo cargar el mes/)).toBeInTheDocument(),
    );
  });
});
