import { Alert } from '@mui/material';

export function ErrorNotice({ error }: { error: unknown }) {
  if (!error) return null;
  return <Alert severity="error">{error instanceof Error ? error.message : 'The request failed.'}</Alert>;
}
