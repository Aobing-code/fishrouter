import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Fish } from 'lucide-react';

interface LoginProps {
  onLogin: (token: string) => void;
}

const Login: React.FC<LoginProps> = ({ onLogin }) => {
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!password.trim()) {
      setError('请输入密码');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const res = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ password }),
      });

      const data = await res.json();

      if (res.ok) {
        onLogin('session');
        navigate('/');
      } else {
        setError(data.detail || '密码错误，请重试');
      }
    } catch (e) {
      setError('网络连接失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden">
      {/* Animated background orbs */}
      <div className="absolute inset-0 -z-10">
        <motion.div
          animate={{ x: [0, 30, -20, 0], y: [0, -30, 20, 0] }}
          transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut' }}
          className="absolute top-10 left-10 w-72 h-72 bg-accent-primary/20 rounded-full blur-3xl"
        />
        <motion.div
          animate={{ x: [0, -20, 30, 0], y: [0, 20, -30, 0] }}
          transition={{ duration: 10, repeat: Infinity, ease: 'easeInOut' }}
          className="absolute bottom-10 right-10 w-96 h-96 bg-accent-secondary/20 rounded-full blur-3xl"
        />
      </div>

      {/* Glass card */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
        className="w-full max-w-md mx-auto p-10 glass-card"
      >
        <div className="text-center mb-10">
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.2, duration: 0.5 }}
            className="w-16 h-16 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-accent-primary to-accent-secondary flex items-center justify-center text-2xl font-bold shadow-lg"
          >
            <Fish className="text-white" size={32} />
          </motion.div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-accent-primary to-accent-secondary bg-clip-text text-transparent mb-2">
            FishRouter
          </h1>
          <p className="text-text-muted">AI模型智能路由平台</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-2">管理员密码</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input-field"
              placeholder="请输入访问密码"
              autoFocus
            />
          </div>

          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-3 bg-error/15 border border-error/30 rounded-lg text-error text-sm text-center"
            >
              {error}
            </motion.div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-60"
          >
            {loading ? '登录中...' : '登 录'}
          </button>
        </form>

        <div className="mt-8 text-center text-text-muted text-sm">
          <p>默认密码: <code className="px-2 py-1 bg-bg-tertiary/50 rounded text-accent-primary">sk-openfish</code></p>
        </div>
      </motion.div>
    </div>
  );
};

export default Login;
