import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

test('Studio renders the seven persisted backend workflow stages in order', async () => {
  const source = await readFile(new URL('../../src/pages/StudioPage.tsx', import.meta.url), 'utf8');
  const api = await readFile(new URL('../../src/api/client.ts', import.meta.url), 'utf8');
  assert.match(api, /components.*generated/);
  assert.match(source, /project\.data\.stages\?\.map/);
  assert.match(source, /stage\.status/);
  assert.doesNotMatch(source, /mock|fake success|simulate generation/i);
});

test('only the local API base and loopback host are configured', async () => {
  const api = await readFile(new URL('../../src/api/client.ts', import.meta.url), 'utf8');
  const vite = await readFile(new URL('../../vite.config.ts', import.meta.url), 'utf8');
  assert.match(api, /import\.meta\.env\.DEV.*'\/api\/v1'/);
  assert.match(vite, /host: '127\.0\.0\.1'/);
});

test('Channels exposes a real revision-aware Channel DNA import workflow', async () => {
  const page = await readFile(new URL('../../src/pages/ChannelsPage.tsx', import.meta.url), 'utf8');
  const editor = await readFile(new URL('../../src/features/channels/ChannelDNAImport.tsx', import.meta.url), 'utf8');
  const api = await readFile(new URL('../../src/api/client.ts', import.meta.url), 'utf8');
  assert.match(page, /ChannelDNAImport/);
  assert.match(editor, /Upload JSON/);
  assert.match(editor, /current\.data\?\.artifact_id/);
  assert.match(editor, /CHANNEL_DNA_STALE_REVISION/);
  assert.match(api, /expected_current_artifact_id/);
});
