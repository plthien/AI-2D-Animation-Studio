import { Alert, Card, CardContent, Stack, Typography } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import { ErrorNotice } from '../components/Notice';

export function JobsPage() {
  const jobs = useQuery({ queryKey: ['jobs'], queryFn: api.jobs, refetchInterval: (query) => query.state.data?.items.some((job) => ['queued', 'running'].includes(job.status)) ? 3000 : false });
  return <Stack spacing={2}><Typography variant="h4">Jobs</Typography><ErrorNotice error={jobs.error} />{jobs.isLoading && <Alert severity="info">Loading jobs…</Alert>}{jobs.data?.items.length === 0 && <Alert severity="info">There are no jobs yet.</Alert>}{jobs.data?.items.map((job) => <Card key={job.job_id}><CardContent><Typography variant="h6">{job.kind}</Typography><Typography>{job.status} · {job.progress}% · project {job.project_id}</Typography></CardContent></Card>)}</Stack>;
}
