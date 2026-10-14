import { spawn, spawnSync } from 'node:child_process';
import path from 'node:path';
import process from 'node:process';

const root = process.cwd();
const python = path.join(root, '.venv', 'Scripts', 'python.exe');
const server = spawn(python, ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '18080'], {
  cwd: root,
  env: {
    ...process.env,
    DATABASE_URL: 'sqlite:///./workspace/e2e-state/app.sqlite',
    ARTIFACT_ROOT: './workspace/e2e-state/artifacts',
    HOST: '127.0.0.1',
    PORT: '18080',
  },
  stdio: 'inherit',
});

function stopServer() {
  if (!server.pid) return;
  if (process.platform === 'win32') {
    server.kill('SIGKILL');
    if (server.exitCode === null) spawnSync('taskkill.exe', ['/pid', String(server.pid), '/t', '/f'], { stdio: 'ignore' });
  } else server.kill('SIGTERM');
}

for (const signal of ['SIGINT', 'SIGTERM']) process.once(signal, () => { stopServer(); process.exit(1); });

try {
  let ready = false;
  for (let attempt = 0; attempt < 120; attempt += 1) {
    if (server.exitCode !== null) throw new Error(`E2E server exited early (${server.exitCode}).`);
    try {
      const response = await fetch('http://127.0.0.1:18080/health');
      if (response.ok) { ready = true; break; }
    } catch { /* server is still starting */ }
    await new Promise((resolve) => setTimeout(resolve, 250));
  }
  if (!ready) throw new Error('E2E server did not become healthy within 30 seconds.');
  const cli = path.join(root, 'node_modules', '@playwright', 'test', 'cli.js');
  const result = spawnSync(process.execPath, [cli, 'test'], { cwd: root, env: process.env, stdio: 'inherit' });
  process.exitCode = result.status ?? 1;
} finally {
  stopServer();
}
