// src/components/veterinario/HistorialClinico.test.jsx
import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import HistorialClinicoModal from './HistorialClinico';
import { apiFetch } from '../../api/client';

vi.mock('../../api/client', () => ({ apiFetch: vi.fn() }));
const mockRes = (data, ok = true) =>
  Promise.resolve({ ok, status: ok ? 200 : 500, json: () => Promise.resolve(data) });

describe('HistorialClinicoModal', () => {
  beforeEach(() => vi.clearAllMocks());

  it('no renderiza nada si isOpen=false', () => {
    apiFetch.mockReturnValue(mockRes([]));
    const { container } = render(<HistorialClinicoModal isOpen={false} mascotaId={1} />);
    expect(container.firstChild).toBeNull();
  });

  it('muestra el estado de carga al inicio', () => {
    apiFetch.mockReturnValue(mockRes([]));
    render(<HistorialClinicoModal isOpen mascotaId={1} />);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('renderiza los datos de la consulta', async () => {
    apiFetch.mockReturnValue(mockRes([{ tipo_consulta: 'General', motivo_consulta: 'Fiebre' }]));
    render(<HistorialClinicoModal isOpen mascotaId={1} />);
    await waitFor(() => expect(screen.getByDisplayValue('Fiebre')).toBeInTheDocument());
    expect(screen.getByDisplayValue('General')).toBeInTheDocument();
  });

  it('muestra estado vacío cuando no hay consultas', async () => {
    apiFetch.mockReturnValue(mockRes([]));
    render(<HistorialClinicoModal isOpen mascotaId={1} />);
    await waitFor(() => expect(screen.getByText(/Sin consultas/)).toBeInTheDocument());
  });

  it('muestra error cuando la API falla', async () => {
    apiFetch.mockReturnValue(mockRes(null, false));
    render(<HistorialClinicoModal isOpen mascotaId={1} />);
    await waitFor(() =>
      expect(screen.getByText(/Error al cargar el historial clínico/)).toBeInTheDocument(),
    );
  });
});
