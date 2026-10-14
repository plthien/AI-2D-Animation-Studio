import { Alert, Card, CardContent, Chip, Stack, Typography } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { useParams } from 'react-router-dom';
import { api } from '../api/client';
import { ErrorNotice } from '../components/Notice';

export function StudioPage() {
  const { projectId = '' } = useParams();
  const project = useQuery({ queryKey: ['project', projectId], queryFn: () => api.project(projectId), enabled: Boolean(projectId) });
  return <Stack spacing={3}><Typography variant="h4">Studio</Typography><ErrorNotice error={project.error} />
    {project.isLoading && <Alert severity="info">Loading project status…</Alert>}
    {project.data && <><Typography variant="h5">{project.data.name}</Typography><Typography color="text.secondary">Live workflow status from the local backend</Typography>
      {project.data.stages?.map((stage, index) => <Card key={stage.stage_key}><CardContent sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 2 }}>
        <Stack direction="row" spacing={2} alignItems="center"><Typography color="text.secondary">{String(index + 1).padStart(2, '0')}</Typography><Stack><Typography variant="h6">{stage.label}</Typography><Typography variant="body2" color="text.secondary">{stage.blocked_reason ?? stage.artifact_id ?? 'No published artifact yet'}</Typography></Stack></Stack>
        <Chip label={stage.status} color={stage.status === 'ready' || stage.status === 'approved' ? 'success' : 'default'} />
      </CardContent></Card>)}
      <Alert severity="info">Later workflow stages are blocked until their phase is implemented and its required inputs are approved.</Alert>
    </>}
  </Stack>;
}
