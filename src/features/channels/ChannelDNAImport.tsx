import { ChangeEvent, useEffect, useState } from 'react';
import { Alert, Button, Card, CardContent, Divider, Stack, TextField, Typography } from '@mui/material';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { ApiRequestError, api, type Channel, type ChannelDNAUpdate } from '../../api/client';

export function ChannelDNAImport({ channel }: { channel: Channel }) {
  const queryClient = useQueryClient();
  const key = ['channel-dna', channel.channel_id];
  const current = useQuery({ queryKey: key, queryFn: () => api.channelDNA(channel.channel_id) });
  const [text, setText] = useState('');
  const [localError, setLocalError] = useState<string | null>(null);
  const [saved, setSaved] = useState<string | null>(null);

  useEffect(() => {
    if (current.data?.dna) setText(JSON.stringify(current.data.dna, null, 2));
  }, [current.data?.artifact_id]);

  const save = useMutation({
    mutationFn: (dna: Record<string, unknown>) => api.saveChannelDNA(channel.channel_id, dna, current.data?.artifact_id ?? null),
    onSuccess: (result) => {
      setLocalError(null);
      setSaved(`Saved immutable revision ${result.artifact_id}.`);
      setText(JSON.stringify(result.dna, null, 2));
      queryClient.setQueryData(key, result);
      void queryClient.invalidateQueries({ queryKey: ['projects'] });
      void queryClient.invalidateQueries({ queryKey: ['project'] });
    },
    onError: (error) => {
      setSaved(null);
      if (error instanceof ApiRequestError && error.body.code === 'CHANNEL_DNA_STALE_REVISION') {
        setLocalError(`This revision is stale. Current revision: ${String(error.body.details.current_artifact_id ?? 'none')}. Reload before saving again.`);
        void current.refetch();
      }
    },
  });

  function submit() {
    setLocalError(null); setSaved(null);
    let parsed: unknown;
    try { parsed = JSON.parse(text); }
    catch (error) { setLocalError(`Invalid JSON: ${error instanceof Error ? error.message : 'parse failed'}`); return; }
    if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) { setLocalError('Channel DNA must be a JSON object.'); return; }
    save.mutate(parsed as ChannelDNAUpdate['dna']);
  }

  async function loadFile(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    setText(await file.text()); setLocalError(null); setSaved(null); event.target.value = '';
  }

  const backendError = save.error instanceof ApiRequestError && save.error.body.code !== 'CHANNEL_DNA_STALE_REVISION'
    ? `${save.error.message}${save.error.body.details.recovery ? ` ${String(save.error.body.details.recovery)}` : ''}`
    : save.error && !(save.error instanceof ApiRequestError) ? String(save.error) : null;

  return <Card variant="outlined"><CardContent><Stack spacing={2}>
    <Typography variant="subtitle1">Channel DNA v2</Typography>
    <Typography variant="body2" color="text.secondary">Paste or upload the complete JSON document. Saving creates a new immutable revision.</Typography>
    <Typography variant="caption" data-testid="dna-revision">Current revision: {current.data?.artifact_id ?? 'none'}</Typography>
    {current.data?.artifact_id && <Stack divider={<Divider flexItem />}>
      <Typography variant="caption">Visual: {current.data.visual_style_hash}</Typography>
      <Typography variant="caption">Performance: {current.data.performance_style_hash}</Typography>
      <Typography variant="caption">Narration: {current.data.narration_identity_hash}</Typography>
    </Stack>}
    <Button component="label" variant="outlined">Upload JSON<input hidden type="file" accept="application/json,.json" onChange={loadFile} /></Button>
    <TextField label="Channel DNA JSON" value={text} onChange={(event) => setText(event.target.value)} multiline minRows={8} inputProps={{ 'data-testid': `dna-json-${channel.channel_id}` }} />
    <Button variant="contained" onClick={submit} disabled={!text.trim() || save.isPending}>Save Channel DNA</Button>
    {current.isError && <Alert severity="error">Could not load current Channel DNA.</Alert>}
    {(localError || backendError) && <Alert severity="error">{localError ?? backendError}</Alert>}
    {saved && <Alert severity="success">{saved}</Alert>}
  </Stack></CardContent></Card>;
}
