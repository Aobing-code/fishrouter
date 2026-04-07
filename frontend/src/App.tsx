import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation, Link } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { Activity, Server, Settings, LayoutDashboard } from 'lucide-react';
import './index.css';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Backends from './pages/Backends';
import Configuration from './pages/Configuration';
import SettingsPage from './pages/Settings';

const Layout: React.FC<{ children: React.ReactNode; onLogout: () => void }> = ({ children, onLogout }) => {
  const location = useLocation();
  const navItems = [
    { path: '/', label: '监控', icon: <Activity size={20} /> },
    { path: '/backends', label: '后端', icon: <Server size={20} /> },
    { path: '/config', label: '配置', icon: <Settings size={20} /> },
    { path: '/settings', label: '设置', icon: <LayoutDashboard size={20} /> },
  ];

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-border/40 bg-bg-secondary/60 backdrop-blur-md sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-primary to-accent-secondary flex items-center justify-center text-xl font-bold shadow-lg group-hover:shadow-accent-glow/30 transition-shadow">F</div>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-accent-primary to-accent-secondary bg-clip-text text-transparent">FishRouter</h1>
              <p className="text-xs text-text-muted">AI模型智能路由</p>
            </div>
          </Link>
          <nav className="flex items-center gap-2">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <Link key={item.path} to={item.path} className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${isActive ? 'bg-accent-primary/15 text-accent-primary border border-accent-primary/30' : 'text-text-secondary hover:text-accent-primary hover:bg-bg-tertiary/50'}`}>
                  {item.icon} {item.label}
                </Link>
              );
            })}
          </nav>
          <button onClick={onLogout} className="btn-secondary">退出</button>
        </div>
      </header>
      <main className="flex-1">{children}</main>
    </div>
  );
};

const App: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkSession();
  }, []);

  const checkSession = async () => {
    try {
      const res = await fetch('/api/session/check', { credentials: 'include' });
      const data = await res.json();
      if (data.authenticated) setIsAuthenticated(true);
    } catch (e) {
      console.error('Session check failed:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = () => setIsAuthenticated(true);
  const handleLogout = async () => {
    try { await fetch('/api/logout', { method: 'POST', credentials: 'include' }); } catch (e) {}
    setIsAuthenticated(false);
  };

  if (loading) return <div className="min-h-screen flex items-center justify-center bg-bg-primary text-accent-primary">加载中...</div>;

  return (
    <BrowserRouter>
      <AnimatePresence mode="wait">
        <Routes>
          <Route path="/login" element={isAuthenticated ? <Navigate to="/" replace /> : <Login onLogin={handleLogin} />} />
          <Route path="/" element={<Layout onLogout={handleLogout}><Dashboard /></Layout>} />
          <Route path="/backends" element={<Layout onLogout={handleLogout}><Backends /></Layout>} />
          <Route path="/config" element={<Layout onLogout={handleLogout}><Configuration /></Layout>} />
          <Route path="/settings" element={<Layout onLogout={handleLogout}><SettingsPage /></Layout>} />
        </Routes>
      </AnimatePresence>
    </BrowserRouter>
  );
};

export default App;
