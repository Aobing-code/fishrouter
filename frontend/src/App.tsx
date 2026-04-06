import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import './index.css';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Backends from './pages/Backends';
import Configuration from './pages/Configuration';
import Settings from './pages/Settings';

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
      if (data.authenticated) {
        setIsAuthenticated(true);
      }
    } catch (e) {
      console.error('Session check failed:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = (_token: string) => {
    setIsAuthenticated(true);
  };

  const handleLogout = async () => {
    try {
      await fetch('/api/logout', { method: 'POST', credentials: 'include' });
    } catch (e) {}
    setIsAuthenticated(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-bg-primary">
        <div className="text-accent-primary text-lg">加载中...</div>
      </div>
    );
  }

  return (
    <BrowserRouter>
      <AnimatePresence mode="wait">
        <Routes>
          <Route
            path="/login"
            element={
              isAuthenticated ? (
                <Navigate to="/" replace />
              ) : (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <Login onLogin={handleLogin} />
                </motion.div>
              )
            }
          />
          <Route
            path="/"
            element={
              isAuthenticated ? (
                <Dashboard onLogout={handleLogout} />
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
          <Route
            path="/backends"
            element={
              isAuthenticated ? <Backends /> : <Navigate to="/login" replace />
            }
          />
          <Route
            path="/config"
            element={
              isAuthenticated ? <Configuration /> : <Navigate to="/login" replace />
            }
          />
          <Route
            path="/settings"
            element={
              isAuthenticated ? <Settings /> : <Navigate to="/login" replace />
            }
          />
        </Routes>
      </AnimatePresence>
    </BrowserRouter>
  );
};

export default App;
