import { useState } from 'react';
import { Alert, Button, Card, CardContent, Stack, TextField, Typography } from '@mui/material';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/client';
import { ErrorNotice } from '../components/Notice';
import { ChannelDNAImport } from '../features/channels/ChannelDNAImport';

export function ChannelsPage() {
  const client = useQueryClient();
  const channels = useQuery({ queryKey: ['channels'], queryFn: api.channels });
  const [name, setName] = useState('');
  const [language, setLanguage] = useState('en');
  const [niche, setNiche] = useState('');
  const [audience, setAudience] = useState('general');
  const create = useMutation({ mutationFn: api.createChannel, onSuccess: () => { setName(''); setNiche(''); void client.invalidateQueries({ queryKey: ['channels'] }); } });
  return <Stack spacing={3}>
    <Typography variant="h4">Channels</Typography>
    <Card><CardContent><Stack component="form" spacing={2} onSubmit={(event) => { event.preventDefault(); create.mutate({ name, language, niche, audience }); }}>
      <Typography variant="h6">Create a channel</Typography>
      <TextField label="Name" value={name} onChange={(e) => setName(e.target.value)} required />
      <TextField label="Language" value={language} onChange={(e) => setLanguage(e.target.value)} required />
      <TextField label="Niche" value={niche} onChange={(e) => setNiche(e.target.value)} required />
      <TextField label="Audience" value={audience} onChange={(e) => setAudience(e.target.value)} required />
      <Button type="submit" variant="contained" disabled={create.isPending}>Create channel</Button>
    </Stack></CardContent></Card>
    <ErrorNotice error={channels.error || create.error} />
    {channels.isLoading && <Alert severity="info">Loading channels…</Alert>}
    {channels.data?.items.length === 0 && <Alert severity="info">No channels yet. Create one to get started.</Alert>}
    {channels.data?.items.map((channel) => <Stack key={channel.channel_id} spacing={1}><Card><CardContent><Typography variant="h6">{channel.name}</Typography><Typography color="text.secondary">{channel.niche} · {channel.language} · {channel.audience}</Typography><Typography variant="caption">{channel.channel_id}</Typography></CardContent></Card><ChannelDNAImport channel={channel} /></Stack>)}
  </Stack>;
}
