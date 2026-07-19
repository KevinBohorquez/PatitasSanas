// src/test/setup.js
// Configuración global de los tests de componentes:
// registra los matchers de jest-dom (toBeInTheDocument, etc.) y limpia el DOM
// entre tests.
import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';

afterEach(() => {
  cleanup();
});
