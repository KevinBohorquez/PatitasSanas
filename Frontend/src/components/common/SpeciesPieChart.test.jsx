// src/components/common/SpeciesPieChart.test.jsx
import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import SpeciesPieChart from './SpeciesPieChart';
import { apiFetch } from '../../api/client';

vi.mock('../../api/client', () => ({ apiFetch: vi.fn() }));
vi.mock('react-chartjs-2', () => ({
  Doughnut: ({ data }) => <div data-testid="chart">{data.datasets[0].data.join(',')}</div>,
}));

const mockRes = (data, ok = true) =>
  Promise.resolve({ ok, status: ok ? 200 : 500, json: () => Promise.resolve(data) });

describe('SpeciesPieChart', () => {
  beforeEach(() => vi.clearAllMocks());

  it('carga las especies y arma la data del gráfico', async () => {
    apiFetch.mockReturnValue(mockRes([
      { especie: 'Perro', total: 3 },
      { especie: 'Gato', total: 1 },
    ]));
    render(<SpeciesPieChart />);

    await waitFor(() => expect(screen.getByTestId('chart')).toHaveTextContent('3,1'));
    expect(screen.getByText(/Perros — 75%/)).toBeInTheDocument();
  });
});
