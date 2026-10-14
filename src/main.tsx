import React from 'react';
import ReactDOM from 'react-dom/client';
import { CssBaseline, ThemeProvider, createTheme } from '@mui/material';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { AppShell } from './layout/AppShell';
import { ChannelsPage } from './pages/ChannelsPage';
import { JobsPage } from './pages/JobsPage';
import { ProjectsPage } from './pages/ProjectsPage';
import { SettingsPage } from './pages/SettingsPage';
import { StudioPage } from './pages/StudioPage';

const queryClient = new QueryClient({ defaultOptions: { queries: { retry: 1, staleTime: 10_000 } } });
const theme = createTheme({ palette: { mode: 'dark', primary: { main: '#8ab4f8' }, background: { default: '#111318', paper: '#1b1d24' } }, typography: { fontFamily: 'Inter, Segoe UI, sans-serif' } });

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode><ThemeProvider theme={theme}><CssBaseline /><QueryClientProvider client={queryClient}><BrowserRouter><Routes><Route element={<AppShell />}><Route index element={<Navigate to="/channels" replace />} /><Route path="channels" element={<ChannelsPage />} /><Route path="projects" element={<ProjectsPage />} /><Route path="studio/:projectId" element={<StudioPage />} /><Route path="jobs" element={<JobsPage />} /><Route path="settings" element={<SettingsPage />} /><Route path="*" element={<Navigate to="/channels" replace />} /></Route></Routes></BrowserRouter></QueryClientProvider></ThemeProvider></React.StrictMode>,
);
