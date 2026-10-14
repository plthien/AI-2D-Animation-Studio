import { useState } from 'react';
import { Alert, Button, Card, CardContent, FormControl, InputLabel, MenuItem, Select, Stack, TextField, Typography } from '@mui/material';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { api } from '../api/client';
import { ErrorNotice } from '../components/Notice';

export function ProjectsPage() {
  const client = useQueryClient();
  const channels = useQuery({ queryKey: ['channels'], queryFn: api.channels });
  const projects = useQuery({ queryKey: ['projects'], queryFn: api.projects });
  const [channelId, setChannelId] = useState(''); const [name, setName] = useState(''); const [description, setDescription] = useState('');
  const create = useMutation({ mutationFn: api.createProject, onSuccess: () => { setName(''); setDescription(''); void client.invalidateQueries({ queryKey: ['projects'] }); } });
  return <Stack spacing={3}>
    <Typography variant="h4">Projects</Typography>
    <Card><CardContent><Stack component="form" spacing={2} onSubmit={(e) => { e.preventDefault(); create.mutate({ channel_id: channelId, name, description }); }}>
      <Typography variant="h6">Create a project</Typography>
      <FormControl required><InputLabel id="channel-label">Channel</InputLabel><Select labelId="channel-label" label="Channel" value={channelId} onChange={(e) => setChannelId(String(e.target.value))}>{channels.data?.items.map((channel) => <MenuItem key={channel.channel_id} value={channel.channel_id}>{channel.name}</MenuItem>)}</Select></FormControl>
      <TextField label="Project name" value={name} onChange={(e) => setName(e.target.value)} required />
      <TextField label="Description" value={description} onChange={(e) => setDescription(e.target.value)} multiline />
      <Button type="submit" variant="contained" disabled={!channelId || create.isPending}>Create project</Button>
    </Stack></CardContent></Card>
    <ErrorNotice error={channels.error || projects.error || create.error} />
    {(channels.isLoading || projects.isLoading) && <Alert severity="info">Loading channels and projects…</Alert>}
    {channels.data?.items.length === 0 && <Alert severity="info">Create a channel before creating a project.</Alert>}
    {projects.data?.items.length === 0 && <Alert severity="info">No projects yet.</Alert>}
    {projects.data?.items.map((project) => <Card key={project.project_id}><CardContent><Typography variant="h6"><Link to={`/studio/${project.project_id}`}>{project.name}</Link></Typography><Typography color="text.secondary">{project.description || 'No description'} · {project.status}</Typography></CardContent></Card>)}
  </Stack>;
}
