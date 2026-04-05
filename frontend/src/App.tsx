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

  useEffect(() => {
    // Check if user has valid session
    const token = localStorage.getItem('fishrouter_session');
    if (token) {
      // TODO: verify token with API
      setIsAuthenticated(true);
    }
  }, []);

  const handleLogin = (token: string) => {
    localStorage.setItem('fishrouter_session', token);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('fishrouter_session');
    setIsAuthenticated(false);
  };

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
