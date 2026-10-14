import { expect, test } from '@playwright/test';
import { readFile } from 'node:fs/promises';
import path from 'node:path';

const stageLabels = [
  'Idea → Script → Shot Plan',
  'Asset Resolver',
  'G-Labs Image Generation',
  'Native Auto-Rig',
  'AI Animation Director',
  'Motion Planner + Spine Preview',
  'Shot Render → Voice → MP4',
];

async function dnaFor(channelId: string) {
  const dna = JSON.parse(await readFile(path.join(process.cwd(), 'contracts/examples/channel_dna.json'), 'utf8'));
  dna.channel_id = channelId;
  dna.channel = { name: 'Browser Channel', language: 'en', niche: 'cartoon comedy', audience: 'general' };
  return dna as Record<string, unknown>;
}

test('P0 browser workflow provisions immutable DNA and persists readiness', async ({ page, request }) => {
  await page.goto('/channels');
  await expect(page.getByRole('heading', { name: 'Channels' })).toBeVisible();
  await page.getByLabel('Name').fill('Browser Channel');
  await page.getByLabel('Language').fill('en');
  await page.getByLabel('Niche').fill('cartoon comedy');
  await page.getByLabel('Audience').fill('general');
  await page.getByRole('button', { name: 'Create channel' }).click();
  await expect(page.getByRole('heading', { name: 'Browser Channel' })).toBeVisible();
  const channelId = (await page.locator('text=/chn_[0-9a-f]{32}/').first().textContent())!.trim();

  await page.getByRole('link', { name: 'Projects' }).click();
  await page.getByLabel('Channel').click();
  await page.getByRole('option', { name: 'Browser Channel' }).click();
  await page.getByLabel('Project name').fill('Browser Project');
  await page.getByLabel('Description').fill('P0 browser acceptance');
  await page.getByRole('button', { name: 'Create project' }).click();
  await page.getByRole('link', { name: 'Browser Project' }).click();

  const stageCards = page.locator('.MuiCard-root').filter({ has: page.locator('.MuiChip-root') });
  await expect(stageCards).toHaveCount(7);
  for (let index = 0; index < stageLabels.length; index += 1) {
    await expect(stageCards.nth(index)).toContainText(stageLabels[index]);
    await expect(stageCards.nth(index)).toContainText('blocked');
  }
  await expect(page.getByRole('button', { name: /generate|rig|render|author/i })).toHaveCount(0);

  await page.getByRole('link', { name: 'Channels' }).click();
  const editor = page.getByLabel('Channel DNA JSON');
  await editor.fill('{ invalid');
  await page.getByRole('button', { name: 'Save Channel DNA' }).click();
  await expect(page.getByText(/Invalid JSON:/)).toBeVisible();

  const invalidSchema = await dnaFor(channelId);
  delete invalidSchema.visual_identity;
  await editor.fill(JSON.stringify(invalidSchema));
  await page.getByRole('button', { name: 'Save Channel DNA' }).click();
  await expect(page.getByText(/CHANNEL_DNA_INVALID:.*Correct the field/i)).toBeVisible();

  const dna = await dnaFor(channelId);
  await editor.fill(JSON.stringify(dna));
  await page.getByRole('button', { name: 'Save Channel DNA' }).click();
  await expect(page.getByText(/Saved immutable revision art_/)).toBeVisible();
  const firstRevision = (await page.getByTestId('dna-revision').textContent())!.replace('Current revision: ', '');

  await page.getByRole('link', { name: 'Projects' }).click();
  await page.getByRole('link', { name: 'Browser Project' }).click();
  await expect(stageCards.nth(0)).toContainText('ready');
  for (let index = 1; index < stageLabels.length; index += 1) await expect(stageCards.nth(index)).toContainText('blocked');
  await page.reload();
  await expect(stageCards.nth(0)).toContainText('ready');
  await expect(stageCards).toHaveCount(7);
  await page.screenshot({ path: 'workspace/e2e-evidence/p0-studio-ready.png', fullPage: true });

  await page.getByRole('link', { name: 'Channels' }).click();
  await expect(page.getByTestId('dna-revision')).toContainText(firstRevision);
  const externalDna = await dnaFor(channelId);
  (externalDna.animation_identity as Record<string, unknown>).motion_energy = 'high';
  const external = await request.put(`/api/v1/channels/${channelId}/dna`, { data: { dna: externalDna, expected_current_artifact_id: firstRevision } });
  expect(external.status()).toBe(200);
  await editor.fill(JSON.stringify(dna));
  await page.getByRole('button', { name: 'Save Channel DNA' }).click();
  await expect(page.getByText(/This revision is stale.*Reload before saving again/i)).toBeVisible();
});
