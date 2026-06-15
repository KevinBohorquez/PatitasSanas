import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { describe, expect, it } from 'vitest';

const currentDir = path.dirname(fileURLToPath(import.meta.url));
const frontendRoot = path.resolve(currentDir, '..');

function getSourceFiles(directory) {
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const entryPath = path.join(directory, entry.name);

    if (entry.isDirectory()) {
      return getSourceFiles(entryPath);
    }

    return /\.(js|jsx|ts|tsx)$/.test(entry.name) ? [entryPath] : [];
  });
}

describe('deployment configuration', () => {
  it('does not hardcode the local backend URL in source files', () => {
    const forbiddenBackendUrl = ['http://', 'localhost', ':8000'].join('');
    const filesWithLocalBackend = getSourceFiles(currentDir).filter((filePath) => {
      return fs.readFileSync(filePath, 'utf8').includes(forbiddenBackendUrl);
    });

    expect(filesWithLocalBackend).toEqual([]);
  });

  it('rewrites API requests to the Railway backend in Vercel', () => {
    const vercelConfig = JSON.parse(
      fs.readFileSync(path.join(frontendRoot, 'vercel.json'), 'utf8'),
    );

    expect(vercelConfig.rewrites).toContainEqual({
      source: '/api/(.*)',
      destination: 'https://patitassanas-production.up.railway.app/api/$1',
    });
    expect(vercelConfig.rewrites).toContainEqual({
      source: '/(.*)',
      destination: '/index.html',
    });
  });
});
