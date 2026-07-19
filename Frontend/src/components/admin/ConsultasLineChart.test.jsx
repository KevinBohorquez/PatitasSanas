// src/components/admin/ConsultasLineChart.test.jsx
import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import ConsultasLineChart from './ConsultasLineChart';
import { apiFetch } from '../../api/client';

vi.mock('../../api/client', () => ({ apiFetch: vi.fn() }));

const mockRes = (data, ok = true) =>
  Promise.resolve({ ok, status: ok ? 200 : 500, json: () => Promise.resolve(data) });

describe('ConsultasLineChart', () => {
  beforeEach(() => vi.clearAllMocks());

  it('muestra el estado de carga al inicio', () => {
    apiFetch.mockReturnValue(mockRes([{ mes: 'Enero', total_consultas: 5 }]));
    render(<ConsultasLineChart />);
    expect(screen.getByRole('status')).toBeInTheDocument();
    expect(screen.getByText('📈 Evolución de Consultas')).toBeInTheDocument();
  });

  it('renderiza el gráfico (svg) cuando hay datos', async () => {
    apiFetch.mockReturnValue(mockRes([
      { mes: 'Enero', total_consultas: 5 },
      { mes: 'Febrero', total_consultas: 8 },
    ]));
    const { container } = render(<ConsultasLineChart />);

    await waitFor(() => expect(container.querySelector('svg')).toBeInTheDocument());
    // total = 13 en el KPI
    expect(screen.getByText('13')).toBeInTheDocument();
    expect(apiFetch).toHaveBeenCalled();
  });

  it('muestra estado vacío cuando no hay consultas', async () => {
    apiFetch.mockReturnValue(mockRes([]));
    render(<ConsultasLineChart />);

    await waitFor(() =>
      expect(screen.getByText(/Sin consultas registradas/)).toBeInTheDocument(),
    );
  });

  it('muestra error y botón Reintentar cuando la API falla', async () => {
    apiFetch.mockReturnValue(mockRes(null, false));
    render(<ConsultasLineChart />);

    await waitFor(() => expect(screen.getByText('Reintentar')).toBeInTheDocument());
  });
});
