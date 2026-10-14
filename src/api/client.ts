export type ApiError = { error: { code: string; message: string; retryable: boolean; details: Record<string, unknown> } };
export type Channel = { channel_id: string; name: string; language: string; niche: string; audience: string; created_at: string; updated_at: string };
export type Project = { project_id: string; channel_id: string; name: string; description: string; status: string; created_at: string; updated_at: string; stages?: Stage[] };
export type Stage = { stage_key: string; label: string; status: 'blocked' | 'ready' | 'draft' | 'approved' | 'stale' | 'running' | 'failed'; artifact_id: string | null; blocked_reason: string | null };
export type Job = { job_id: string; operation_id: string | null; project_id: string; kind: string; status: string; progress: number; heartbeat_at: string | null; created_at: string; updated_at: string };
export type Page<T> = { items: T[]; total: number; page: number; page_size: number };
const base = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api/v1';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try { response = await fetch(path.startsWith('http') ? path : `${base}${path}`, { ...init, headers: { 'Content-Type': 'application/json', ...init?.headers } }); }
  catch { throw new Error('Could not reach the local backend. Start the API and retry.'); }
  const payload = await response.json() as { data?: T; error?: ApiError['error'] };
  if (!response.ok || !payload.data) throw new Error(payload.error ? `${payload.error.code}: ${payload.error.message}` : `Request failed (${response.status}).`);
  return payload.data;
}

export const api = {
  channels: () => request<Page<Channel>>('/channels'),
  createChannel: (input: Pick<Channel, 'name' | 'language' | 'niche' | 'audience'>) => request<Channel>('/channels', { method: 'POST', body: JSON.stringify(input) }),
  projects: () => request<Page<Project>>('/projects'),
  createProject: (input: { channel_id: string; name: string; description: string }) => request<Project>('/projects', { method: 'POST', body: JSON.stringify(input) }),
  project: (id: string) => request<Project>(`/projects/${encodeURIComponent(id)}`),
  jobs: () => request<Page<Job>>('/jobs'),
  health: () => request<{ status: string; schema_version: string }>('http://127.0.0.1:8000/health'),
};
