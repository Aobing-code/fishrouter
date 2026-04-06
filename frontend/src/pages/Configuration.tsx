import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Save, Plus, Trash2, ChevronDown, ChevronUp } from 'lucide-react';

interface ConfigData {
  server: { host: string; port: number; log_level: string };
  backends: Array<{
    name: string;
    type: string;
    url: string;
    api_keys: string[];
    weight: number;
    enabled: boolean;
    timeout: number;
    verify_ssl: boolean;
    models: Array<{ id: string; name: string; context_length: number }>;
    rate_limit: { rpm: number; tpm: number; concurrent: number };
    priority: number;
  }>;
  routes: Array<{
    name: string;
    models: string[];
    strategy: string;
    failover: boolean;
    health_check_interval: number;
    fallback_order: string[];
    fallback_rules: Array<{ name: string; condition: string; threshold: number; backends: string[] }>;
  }>;
  auth: { enabled: boolean; api_keys: string[] };
}

const Configuration: React.FC = () => {
  const [config, setConfig] = useState<ConfigData | null>(null);
  const [saving, setSaving] = useState(false);
  const [expandedRoute, setExpandedRoute] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/config')
      .then((res) => res.json())
      .then((data) => setConfig(data))
      .catch(() => {});
  }, []);

  const handleSave = async () => {
    if (!config) return;
    setSaving(true);
    try {
      await fetch('/api/config', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      });
      alert('配置已保存');
    } catch (e) {
      alert('保存失败');
    } finally {
      setSaving(false);
    }
  };

  if (!config) {
    return <div className="flex items-center justify-center h-64 text-text-muted">加载中...</div>;
  }

  return (
    <div className="max-w-4xl mx-auto">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8 flex items-center justify-between">
        <h2 className="text-2xl font-bold text-text-primary">系统配置</h2>
        <button onClick={handleSave} className="btn-primary flex items-center gap-2" disabled={saving}>
          <Save size={18} /> {saving ? '保存中...' : '保存'}
        </button>
      </motion.div>

      <div className="space-y-6">
        {/* Server Settings */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="glass-card p-6"
        >
          <h3 className="text-lg font-semibold text-text-primary mb-4">服务器设置</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
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
                onChange={(e) => setConfig({ ...config, server: { ...config.server, port: parseInt(e.target.value) || 8080 } })}
              />
            </div>
            <div>
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

        {/* Auth Settings */}
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

        {/* Routes */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="glass-card p-6"
        >
          <h3 className="text-lg font-semibold text-text-primary mb-4">路由配置</h3>
          <div className="space-y-4">
            {config.routes.map((route, idx) => (
              <div key={route.name} className="bg-bg-primary/50 rounded-xl overflow-hidden">
                <button
                  className="w-full flex items-center justify-between p-4 hover:bg-bg-tertiary/30 transition-colors"
                  onClick={() => setExpandedRoute(expandedRoute === route.name ? null : route.name)}
                >
                  <div className="flex items-center gap-4">
                    <span className="font-medium text-text-primary">{route.name}</span>
                    <span className="text-sm text-text-muted">策略: {route.strategy}</span>
                    <span className="text-sm text-text-muted">模型: {route.models.join(', ')}</span>
                  </div>
                  {expandedRoute === route.name ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                </button>
                {expandedRoute === route.name && (
                  <div className="p-4 border-t border-border space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-text-secondary">故障转移</span>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          className="sr-only peer"
                          checked={route.failover}
                          onChange={(e) => {
                            const newRoutes = [...config.routes];
                            newRoutes[idx].failover = e.target.checked;
                            setConfig({ ...config, routes: newRoutes });
                          }}
                        />
                        <div className="w-11 h-6 bg-bg-tertiary rounded-full peer peer-checked:bg-accent-primary transition-colors"></div>
                        <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-5" />
                      </label>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-text-secondary mb-2">回退顺序 (逗号分隔)</label>
                      <input
                        type="text"
                        className="input-field font-mono text-sm"
                        value={route.fallback_order.join(', ')}
                        onChange={(e) => {
                          const newRoutes = [...config.routes];
                          newRoutes[idx].fallback_order = e.target.value.split(',').map((s) => s.trim()).filter(Boolean);
                          setConfig({ ...config, routes: newRoutes });
                        }}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-text-secondary mb-2">健康检查间隔(秒)</label>
                      <input
                        type="number"
                        className="input-field"
                        value={route.health_check_interval}
                        onChange={(e) => {
                          const newRoutes = [...config.routes];
                          newRoutes[idx].health_check_interval = parseInt(e.target.value) || 30;
                          setConfig({ ...config, routes: newRoutes });
                        }}
                      />
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Configuration;
