import { mkdir, rm } from 'node:fs/promises';
import path from 'node:path';

const workspace = path.resolve(process.cwd(), 'workspace');
const state = path.resolve(workspace, 'e2e-state');
const evidence = path.resolve(workspace, 'e2e-evidence');
if (path.dirname(state) !== workspace || path.dirname(evidence) !== workspace) throw new Error('E2E paths escaped workspace');
await rm(state, { recursive: true, force: true });
await rm(evidence, { recursive: true, force: true });
await mkdir(evidence, { recursive: true });
