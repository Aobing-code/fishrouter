import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Plus, Pencil, Trash2, Power, ExternalLink } from 'lucide-react';

interface Backend {
  id: string;
  name: string;
  type: 'openai' | 'anthropic' | 'ollama' | 'custom';
  url: string;
  api_key: string;
  model: string;
  enabled: boolean;
  healthy?: boolean;
  latency?: number;
  requests?: number;
}

const Backends: React.FC = () => {
  const [backends, setBackends] = useState<Backend[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState<Backend | null>(null);
  const [form, setForm] = useState({ name: '', type: 'openai', url: '', api_key: '', model: '' });

  const fetchBackends = async () => {
    try {
      const res = await fetch('/api/backends');
      const data = await res.json();
      setBackends(data);
    } catch (e) {
      console.error('Failed to fetch backends:', e);
    }
  };

  useEffect(() => {
    fetchBackends();
    const interval = setInterval(fetchBackends, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const payload = { ...form, enabled: true };
    try {
      if (editing) {
        await fetch(`/api/backends/${editing.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
      } else {
        await fetch('/api/backends', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
      }
      setShowModal(false);
      setEditing(null);
      setForm({ name: '', type: 'openai', url: '', api_key: '', model: '' });
      fetchBackends();
    } catch (e) {
      alert('保存失败');
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('确定删除？')) return;
    await fetch(`/api/backends/${id}`, { method: 'DELETE' });
    fetchBackends();
  };

  const toggleEnable = async (b: Backend) => {
    await fetch(`/api/backends/${b.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enabled: !b.enabled }),
    });
    fetchBackends();
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <h2 className="text-2xl font-bold text-text-primary">后端管理</h2>
        <button onClick={() => setShowModal(true)} className="btn-primary flex items-center gap-2">
          <Plus size={18} /> 添加后端
        </button>
      </div>

      <div className="glass-card overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="bg-bg-secondary/50 text-left text-xs uppercase tracking-wider text-text-muted">
              <th className="px-6 py-4 font-semibold">名称</th>
              <th className="px-6 py-4 font-semibold">类型</th>
              <th className="px-6 py-4 font-semibold">URL</th>
              <th className="px-6 py-4 font-semibold">模型</th>
              <th className="px-6 py-4 font-semibold">状态</th>
              <th className="px-6 py-4 font-semibold">操作</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {backends.map((b) => (
              <motion.tr
                key={b.id}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="hover:bg-bg-tertiary/30 transition-colors"
              >
                <td className="px-6 py-4 font-medium text-text-primary">{b.name}</td>
                <td className="px-6 py-4 text-text-secondary capitalize">{b.type}</td>
                <td className="px-6 py-4 font-mono text-sm text-text-muted max-w-xs truncate">{b.url}</td>
                <td className="px-6 py-4 text-text-secondary">{b.model}</td>
                <td className="px-6 py-4">
                  <span className={`status-badge ${b.enabled ? 'status-healthy' : 'bg-bg-tertiary text-text-muted'}`}>
                    {b.enabled ? '启用' : '禁用'}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <button onClick={() => toggleEnable(b)} className="p-1 hover:text-accent-primary" title={b.enabled ? '禁用' : '启用'}>
                      <Power size={16} />
                    </button>
                    <button onClick={() => { setEditing(b); setForm({ name: b.name, type: b.type, url: b.url, api_key: b.api_key, model: b.model }); setShowModal(true); }} className="p-1 hover:text-accent-primary" title="编辑">
                      <Pencil size={16} />
                    </button>
                    <button onClick={() => handleDelete(b.id)} className="p-1 hover:text-error" title="删除">
                      <Trash2 size={16} />
                    </button>
                  </div>
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 px-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-card p-8 max-w-lg w-full"
          >
            <h3 className="text-xl font-bold mb-6 text-text-primary">{editing ? '编辑后端' : '添加后端'}</h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">名称</label>
                <input type="text" className="input-field" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">类型</label>
                <select className="input-field" value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value as any })}>
                  <option value="openai">OpenAI</option>
                  <option value="anthropic">Anthropic</option>
                  <option value="ollama">Ollama</option>
                  <option value="custom">Custom</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">API URL</label>
                <input type="url" className="input-field" value={form.url} onChange={(e) => setForm({ ...form, url: e.target.value })} required />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">API Key</label>
                <input type="password" className="input-field" value={form.api_key} onChange={(e) => setForm({ ...form, api_key: e.target.value })} required />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">模型名称</label>
                <input type="text" className="input-field" value={form.model} onChange={(e) => setForm({ ...form, model: e.target.value })} required />
              </div>
              <div className="flex justify-end gap-3 mt-8">
                <button type="button" onClick={() => { setShowModal(false); setEditing(null); }} className="btn-secondary">取消</button>
                <button type="submit" className="btn-primary">保存</button>
              </div>
            </form>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default Backends;
