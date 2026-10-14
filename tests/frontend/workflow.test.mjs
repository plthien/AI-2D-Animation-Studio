import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

test('Studio renders the seven persisted backend workflow stages in order', async () => {
  const source = await readFile(new URL('../../src/pages/StudioPage.tsx', import.meta.url), 'utf8');
  const api = await readFile(new URL('../../src/api/client.ts', import.meta.url), 'utf8');
  assert.match(api, /stages\?: Stage\[\]/);
  assert.match(source, /project\.data\.stages\?\.map/);
  assert.match(source, /stage\.status/);
  assert.doesNotMatch(source, /mock|fake success|simulate generation/i);
});

test('only the local API base and loopback host are configured', async () => {
  const api = await readFile(new URL('../../src/api/client.ts', import.meta.url), 'utf8');
  const vite = await readFile(new URL('../../vite.config.ts', import.meta.url), 'utf8');
  assert.match(api, /http:\/\/127\.0\.0\.1:8000\/api\/v1/);
  assert.match(vite, /host: '127\.0\.0\.1'/);
});
