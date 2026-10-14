import { AppBar, Box, Button, Container, Toolbar, Typography } from '@mui/material';
import { NavLink, Outlet } from 'react-router-dom';

const links = [['Channels', '/channels'], ['Projects', '/projects'], ['Jobs', '/jobs'], ['Settings', '/settings']] as const;

export function AppShell() {
  return <Box minHeight="100vh" bgcolor="#111318" color="#f4f4f5">
    <AppBar position="static" color="transparent" elevation={0} sx={{ borderBottom: '1px solid #30323a' }}>
      <Toolbar sx={{ gap: 1, flexWrap: 'wrap' }}>
        <Typography variant="h6" sx={{ fontWeight: 700, mr: 3 }}>Framecraft Studio</Typography>
        {links.map(([label, to]) => <Button key={to} component={NavLink} to={to} color="inherit" sx={{ '&.active': { color: '#8ab4f8' } }}>{label}</Button>)}
      </Toolbar>
    </AppBar>
    <Container maxWidth="lg" sx={{ py: 4 }}><Outlet /></Container>
  </Box>;
}
