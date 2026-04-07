import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Save, ChevronDown, ChevronUp, GripVertical, Plus, Trash2 } from 'lucide-react';

const Configuration: React.FC = () => {
  const [config, setConfig] = useState<any>(null);
  const [saving, setSaving] = useState(false);
  const [expandedRoute, setExpandedRoute] = useState<string | null>(null);
  const [draggingIdx, setDraggingIdx] = useState<number | null>(null);

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

  const routes = config.routes || [];
  const backends = config.backends || [];
  const backendNames = backends.map((b: any) => b.name);

  const updateRoute = (idx: number, updates: any) => {
    const newRoutes = [...routes];
    newRoutes[idx] = { ...newRoutes[idx], ...updates };
    setConfig({ ...config, routes: newRoutes });
  };

  const onDragStart = (idx: number) => setDraggingIdx(idx);
  const onDragOver = (e: React.DragEvent) => e.preventDefault();
  const onDrop = (e: React.DragEvent, routeIdx: number, dropIdx: number) => {
    e.preventDefault();
    const route = routes[routeIdx];
    const order = [...(route.fallback_order || [])];
    const [item] = order.splice(draggingIdx!, 1);
    order.splice(dropIdx, 0, item);
    updateRoute(routeIdx, { fallback_order: order });
    setDraggingIdx(null);
  };

  const addBackendToOrder = (routeIdx: number, name: string) => {
    const route = routes[routeIdx];
    const order = route.fallback_order || [];
    if (!order.includes(name)) {
      updateRoute(routeIdx, { fallback_order: [...order, name] });
    }
  };

  const removeBackendFromOrder = (routeIdx: number, name: string) => {
    const route = routes[routeIdx];
    const order = (route.fallback_order || []).filter((n: string) => n !== name);
    updateRoute(routeIdx, { fallback_order: order });
  };

  return (
    <div className="max-w-4xl mx-auto px-6 py-8">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8 flex items-center justify-between">
        <h2 className="text-2xl font-bold text-text-primary">系统配置</h2>
        <button onClick={handleSave} className="btn-primary flex items-center gap-2" disabled={saving}>
          <Save size={18} /> {saving ? '保存中...' : '保存'}
        </button>
      </motion.div>

      <div className="space-y-6">
        {/* Server Settings */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="glass-card p-6">
          <h3 className="text-lg font-semibold text-text-primary mb-4">服务器设置</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">监听地址</label>
              <input type="text" className="input-field" value={config.server?.host || ''} onChange={(e) => setConfig({ ...config, server: { ...config.server, host: e.target.value } })} />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">端口</label>
              <input type="number" className="input-field" value={config.server?.port || 8080} onChange={(e) => setConfig({ ...config, server: { ...config.server, port: parseInt(e.target.value) || 8080 } })} />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">日志级别</label>
              <select className="input-field" value={config.server?.log_level || 'info'} onChange={(e) => setConfig({ ...config, server: { ...config.server, log_level: e.target.value } })}>
                <option value="debug">Debug</option>
                <option value="info">Info</option>
                <option value="warning">Warning</option>
                <option value="error">Error</option>
              </select>
            </div>
          </div>
        </motion.div>

        {/* Auth Settings */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="glass-card p-6">
          <h3 className="text-lg font-semibold text-text-primary mb-4">认证设置</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 rounded-xl bg-bg-primary/50">
              <div>
                <p className="font-medium text-text-primary">启用 API 认证</p>
                <p className="text-sm text-text-muted">要求所有请求提供有效的 API Key</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" className="sr-only peer" checked={config.auth?.enabled || false} onChange={(e) => setConfig({ ...config, auth: { ...config.auth, enabled: e.target.checked } })} />
                <div className="w-11 h-6 bg-bg-tertiary rounded-full peer peer-checked:bg-accent-primary transition-colors" />
                <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-5" />
              </label>
            </div>
          </div>
        </motion.div>

        {/* Routes */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="glass-card p-6">
          <h3 className="text-lg font-semibold text-text-primary mb-4">路由配置</h3>
          <div className="space-y-4">
            {routes.map((route: any, idx: number) => (
              <div key={route.name} className="bg-bg-primary/50 rounded-xl overflow-hidden">
                <button className="w-full flex items-center justify-between p-4 hover:bg-bg-tertiary/30 transition-colors" onClick={() => setExpandedRoute(expandedRoute === route.name ? null : route.name)}>
                  <div className="flex items-center gap-4">
                    <span className="font-medium text-text-primary">{route.name}</span>
                    <span className="text-sm text-text-muted">策略: {route.strategy}</span>
                    <span className="text-sm text-text-muted">模型: {Array.isArray(route.models) ? route.models.join(', ') : ''}</span>
                  </div>
                  {expandedRoute === route.name ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                </button>
                {expandedRoute === route.name && (
                  <div className="p-4 border-t border-border space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-text-secondary">故障转移</span>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input type="checkbox" className="sr-only peer" checked={route.failover || false} onChange={(e) => updateRoute(idx, { failover: e.target.checked })} />
                        <div className="w-11 h-6 bg-bg-tertiary rounded-full peer peer-checked:bg-accent-primary transition-colors" />
                        <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-5" />
                      </label>
                    </div>

                    {/* Fallback Order */}
                    <div>
                      <label className="block text-sm font-medium text-text-secondary mb-2">回退顺序（拖拽排序）</label>
                      <div className="space-y-1">
                        {(route.fallback_order || []).map((name: string, orderIdx: number) => (
                          <div
                            key={name}
                            draggable
                            onDragStart={() => onDragStart(orderIdx)}
                            onDragOver={onDragOver}
                            onDrop={(e) => onDrop(e, idx, orderIdx)}
                            className="flex items-center gap-2 p-2 rounded-lg bg-bg-tertiary/50 cursor-grab active:cursor-grabbing"
                          >
                            <GripVertical size={16} className="text-text-muted" />
                            <span className="text-sm text-text-primary flex-1">{name}</span>
                            <button onClick={() => removeBackendFromOrder(idx, name)} className="p-1 hover:text-error"><Trash2 size={14} /></button>
                          </div>
                        ))}
                        {(route.fallback_order || []).length === 0 && (
                          <div className="text-sm text-text-muted py-2 text-center">暂无回退后端</div>
                        )}
                      </div>
                      <div className="mt-2 flex flex-wrap gap-2">
                        {backendNames.filter((n: string) => !(route.fallback_order || []).includes(n)).map((name: string) => (
                          <button key={name} onClick={() => addBackendToOrder(idx, name)} className="text-xs px-2 py-1 rounded bg-bg-tertiary text-text-secondary hover:text-accent-primary hover:bg-accent-primary/10 transition-colors">
                            + {name}
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Health Check Interval */}
                    <div>
                      <label className="block text-sm font-medium text-text-secondary mb-2">健康检查间隔(秒)</label>
                      <input type="number" className="input-field" value={route.health_check_interval || 30} onChange={(e) => updateRoute(idx, { health_check_interval: parseInt(e.target.value) || 30 })} />
                    </div>
                  </div>
                )}
              </div>
            ))}
            {routes.length === 0 && <div className="text-text-muted text-center py-4">暂无路由配置</div>}
          </div>
        </motion.div>

        {/* Backends Summary */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }} className="glass-card p-6">
          <h3 className="text-lg font-semibold text-text-primary mb-4">后端列表</h3>
          <div className="space-y-2">
            {backends.map((b: any) => (
              <div key={b.name} className="flex items-center justify-between p-3 rounded-lg bg-bg-primary/50">
                <div>
                  <span className="font-medium text-text-primary">{b.name}</span>
                  <span className="text-sm text-text-muted ml-2">({b.type})</span>
                </div>
                <span className={`status-badge ${b.enabled ? 'status-healthy' : 'bg-bg-tertiary text-text-muted'}`}>{b.enabled ? '启用' : '禁用'}</span>
              </div>
            ))}
            {backends.length === 0 && <div className="text-text-muted text-center py-4">暂无后端配置</div>}
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Configuration;
