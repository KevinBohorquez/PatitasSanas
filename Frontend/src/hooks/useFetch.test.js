// src/hooks/useFetch.test.js
import { renderHook, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { useFetch } from './useFetch';
import { apiFetch } from '../api/client';

vi.mock('../api/client', () => ({ apiFetch: vi.fn() }));

const mockRes = (data, ok = true) =>
  Promise.resolve({ ok, status: ok ? 200 : 500, json: () => Promise.resolve(data) });

describe('useFetch', () => {
  beforeEach(() => vi.clearAllMocks());

  it('empieza cargando y entrega los datos al resolver', async () => {
    apiFetch.mockReturnValue(mockRes({ a: 1 }));
    const { result } = renderHook(() => useFetch('/x'));

    expect(result.current.loading).toBe(true);
    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.data).toEqual({ a: 1 });
    expect(result.current.error).toBeNull();
    expect(apiFetch).toHaveBeenCalledWith('/x', undefined);
  });

  it('aplica transform al resultado', async () => {
    apiFetch.mockReturnValue(mockRes({ items: [1, 2, 3] }));
    const { result } = renderHook(() => useFetch('/x', { transform: (j) => j.items }));

    await waitFor(() => expect(result.current.data).toEqual([1, 2, 3]));
  });

  it('setea error cuando la respuesta no es ok y no toca data', async () => {
    apiFetch.mockReturnValue(mockRes(null, false));
    const { result } = renderHook(() => useFetch('/x'));

    await waitFor(() => expect(result.current.error).toBeTruthy());
    expect(result.current.data).toBeNull();
    expect(result.current.loading).toBe(false);
  });

  it('usa errorMessage fijo cuando se provee', async () => {
    apiFetch.mockReturnValue(mockRes(null, false));
    const { result } = renderHook(() =>
      useFetch('/x', { errorMessage: 'No se pudo cargar' }),
    );

    await waitFor(() => expect(result.current.error).toBe('No se pudo cargar'));
  });

  it('no dispara la carga si enabled=false', async () => {
    const { result } = renderHook(() => useFetch('/x', { enabled: false }));

    expect(apiFetch).not.toHaveBeenCalled();
    expect(result.current.loading).toBe(false);
    expect(result.current.data).toBeNull();
  });
});
