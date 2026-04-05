import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Save } from 'lucide-react';

const Configuration: React.FC = () => {
  const [config, setConfig] = useState({
    server: { host: '0.0.0.0', port: 8080, log_level: 'info' },
    auth: { enabled: false, api_keys: [''] },
  });

  useEffect(() => {
    fetch('/api/config')
      .then((res) => res.json())
      .then((data) => setConfig(data))
      .catch(() => {});
  }, []);

  const handleSave = async () => {
    await fetch('/api/config', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config),
    });
    alert('配置已保存');
  };

  return (
    <div className="max-w-3xl mx-auto">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8 flex items-center justify-between">
        <h2 className="text-2xl font-bold text-text-primary">系统配置</h2>
        <button onClick={handleSave} className="btn-primary flex items-center gap-2">
          <Save size={18} /> 保存
        </button>
      </motion.div>

      <div className="space-y-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="glass-card p-6"
        >
          <h3 className="text-lg font-semibold text-text-primary mb-4">服务器设置</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">监听地址</label>
              <input
                type="text"
                className="input-field"
                value={config.server.host}
                onChange={(e) => setConfig({ ...config, server: { ...config.server, host: e.target.value } })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">端口</label>
              <input
                type="number"
                className="input-field"
                value={config.server.port}
                onChange={(e) => setConfig({ ...config, server: { ...config.server, port: parseInt(e.target.value) } })}
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-text-secondary mb-2">日志级别</label>
              <select
                className="input-field"
                value={config.server.log_level}
                onChange={(e) => setConfig({ ...config, server: { ...config.server, log_level: e.target.value } })}
              >
                <option value="debug">Debug</option>
                <option value="info">Info</option>
                <option value="warning">Warning</option>
                <option value="error">Error</option>
              </select>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="glass-card p-6"
        >
          <h3 className="text-lg font-semibold text-text-primary mb-4">认证设置</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 rounded-xl bg-bg-primary/50">
              <div>
                <p className="font-medium text-text-primary">启用 API 认证</p>
                <p className="text-sm text-text-muted">要求所有请求提供有效的 API Key</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  className="sr-only peer"
                  checked={config.auth.enabled}
                  onChange={(e) => setConfig({ ...config, auth: { ...config.auth, enabled: e.target.checked } })}
                />
                <div className="w-11 h-6 bg-bg-tertiary rounded-full peer peer-checked:bg-accent-primary transition-colors"></div>
                <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-5" />
              </label>
            </div>

            {config.auth.enabled && (
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">API Keys (每行一个)</label>
                <textarea
                  className="input-field font-mono text-sm"
                  rows={4}
                  value={config.auth.api_keys.join('\n')}
                  onChange={(e) => setConfig({ ...config, auth: { ...config.auth, api_keys: e.target.value.split('\n').filter(Boolean) } })}
                  placeholder="sk-..."
                />
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Configuration;
