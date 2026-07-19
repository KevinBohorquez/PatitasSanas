// src/components/admin/ServicesBarChart.test.jsx
import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import ServicesBarChart from './ServicesBarChart';
import { apiFetch } from '../../api/client';

vi.mock('../../api/client', () => ({ apiFetch: vi.fn() }));
vi.mock('react-chartjs-2', () => ({
  Bar: ({ data }) => (
    <div data-testid="chart" data-labels={data.labels.join('|')}>
      {data.datasets[0].data.join(',')}
    </div>
  ),
}));

const mockRes = (data, ok = true) =>
  Promise.resolve({ ok, status: ok ? 200 : 500, json: () => Promise.resolve(data) });

describe('ServicesBarChart', () => {
  beforeEach(() => vi.clearAllMocks());

  it('carga los servicios y arma labels + valores del gráfico', async () => {
    apiFetch.mockReturnValue(mockRes([
      { nombre_servicio: 'Vacunación', total_solicitudes: 10 },
      { nombre_servicio: 'Baño', total_solicitudes: 4 },
    ]));
    render(<ServicesBarChart />);

    await waitFor(() => expect(screen.getByTestId('chart')).toHaveTextContent('10,4'));
    expect(screen.getByTestId('chart')).toHaveAttribute('data-labels', 'Vacunación|Baño');
  });
});
