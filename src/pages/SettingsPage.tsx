import { Alert, Stack, Typography } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import { ErrorNotice } from '../components/Notice';

export function SettingsPage() {
  const health = useQuery({ queryKey: ['health'], queryFn: api.health, retry: false });
  return <Stack spacing={2}><Typography variant="h4">Settings</Typography><Typography>Local application connection and fixed render settings.</Typography><ErrorNotice error={health.error} />{health.data && <Alert severity="success">Backend {health.data.status} · schema {health.data.schema_version}</Alert>}<Alert severity="info">Rendering is fixed at 1280 × 720 and 24 FPS. No production rendering controls are enabled in P0.</Alert></Stack>;
}
