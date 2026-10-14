import type { components } from './generated';

type Schemas = components['schemas'];
export type ApiError = Schemas['ErrorEnvelope'];
export type Channel = Schemas['ChannelResponse'];
export type Project = Schemas['ProjectResponse'];
export type Stage = Schemas['StageResponse'];
export type Job = Schemas['JobResponse'];
export type ChannelDNAUpdate = Schemas['ChannelDNAUpdate'];
export type ChannelDNA = Schemas['ChannelDNAResponse'];
type ChannelPage = Schemas['PageResponse_ChannelResponse_'];
type ProjectPage = Schemas['PageResponse_ProjectResponse_'];
type JobPage = Schemas['PageResponse_JobResponse_'];
const base = import.meta.env.DEV && import.meta.env.VITE_API_BASE_URL ? import.meta.env.VITE_API_BASE_URL : '/api/v1';

export class ApiRequestError extends Error {
  constructor(public status: number, public body: ApiError['error']) { super(`${body.code}: ${body.message}`); }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try { response = await fetch(path.startsWith('http') ? path : `${base}${path}`, { ...init, headers: { 'Content-Type': 'application/json', ...init?.headers } }); }
  catch { throw new Error('Could not reach the local backend. Start the API and retry.'); }
  const payload = await response.json() as { data?: T; error?: ApiError['error'] };
  if (!response.ok || !payload.data) {
    if (payload.error) throw new ApiRequestError(response.status, payload.error);
    throw new Error(`Request failed (${response.status}).`);
  }
  return payload.data;
}

export const api = {
  channels: () => request<ChannelPage>('/channels'),
  createChannel: (input: Schemas['ChannelCreate']) => request<Channel>('/channels', { method: 'POST', body: JSON.stringify(input) }),
  channelDNA: (id: string) => request<ChannelDNA>(`/channels/${encodeURIComponent(id)}/dna`),
  saveChannelDNA: (id: string, dna: ChannelDNAUpdate['dna'], expected: string | null) => {
    const input: ChannelDNAUpdate = { dna, expected_current_artifact_id: expected };
    return request<ChannelDNA>(`/channels/${encodeURIComponent(id)}/dna`, { method: 'PUT', body: JSON.stringify(input) });
  },
  projects: () => request<ProjectPage>('/projects'),
  createProject: (input: Schemas['ProjectCreate']) => request<Project>('/projects', { method: 'POST', body: JSON.stringify(input) }),
  project: (id: string) => request<Project>(`/projects/${encodeURIComponent(id)}`),
  jobs: () => request<JobPage>('/jobs'),
  health: () => request<Schemas['HealthResponse']>(new URL('/health', window.location.origin).toString()),
};
