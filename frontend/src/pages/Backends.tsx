import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Plus, Pencil, Trash2, Power, RefreshCw } from 'lucide-react';

interface ModelConfig {
  id: string;
  name: string;
  context_length: number;
  enabled: boolean;
  rate_limit: { rpm: number; tpm: number; concurrent: number };
}

interface Backend {
  name: string;
  type: string;
  url: string;
  api_keys: string[];
  weight: number;
  enabled: boolean;
  timeout: number;
  verify_ssl: boolean;
  models: ModelConfig[];
  rate_limit: { rpm: number; tpm: number; concurrent: number };
  priority: number;
}

interface BackendForm {
  name: string;
  type: string;
  url: string;
  api_keys: string;
  weight: number;
  timeout: number;
  verify_ssl: boolean;
  models: string;
  rate_limit_rpm: number;
  rate_limit_tpm: number;
  rate_limit_concurrent: number;
  priority: number;
}

const emptyForm: BackendForm = {
  name: '',
  type: 'openai',
  url: '',
  api_keys: '',
  weight: 1,
  timeout: 60,
  verify_ssl: true,
  models: '',
  rate_limit_rpm: 0,
  rate_limit_tpm: 0,
  rate_limit_concurrent: 0,
  priority: 1,
};

const Backends: React.FC = () => {
  const [backends, setBackends] = useState<Backend[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState<string | null>(null);
  const [form, setForm] = useState<BackendForm>(emptyForm);
  const [loading, setLoading] = useState(false);

  const fetchBackends = async () => {
    try {
      const res = await fetch('/api/config');
      const data = await res.json();
      setBackends(data.backends || []);
    } catch (e) {
      console.error('Failed to fetch backends:', e);
    }
  };

  useEffect(() => {
    fetchBackends();
  }, []);

  const openEdit = (b: Backend) => {
    setEditing(b.name);
    setForm({
      name: b.name,
      type: b.type,
      url: b.url,
      api_keys: b.api_keys.join('\n'),
      weight: b.weight,
      timeout: b.timeout,
      verify_ssl: b.verify_ssl,
      models: b.models.map((m) => m.id).join('\n'),
      rate_limit_rpm: b.rate_limit.rpm,
      rate_limit_tpm: b.rate_limit.tpm,
      rate_limit_concurrent: b.rate_limit.concurrent,
      priority: b.priority,
    });
    setShowModal(true);
  };

  const openAdd = () => {
    setEditing(null);
    setForm(emptyForm);
    setShowModal(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    const modelsList = form.models
      .split('\n')
      .filter(Boolean)
      .map((id) => ({
        id: id.trim(),
        name: id.trim(),
        context_length: 4096,
        enabled: true,
        rate_limit: { rpm: 0, tpm: 0, concurrent: 0 },
      }));

    const payload = {
      name: form.name,
      type: form.type,
      url: form.url,
      api_keys: form.api_keys
        .split('\n')
        .filter(Boolean)
        .map((k) => k.trim()),
      weight: form.weight,
      enabled: true,
      timeout: form.timeout,
      verify_ssl: form.verify_ssl,
      models: modelsList,
      rate_limit: {
        rpm: form.rate_limit_rpm,
        tpm: form.rate_limit_tpm,
        concurrent: form.rate_limit_concurrent,
      },
      priority: form.priority,
    };

    try {
      let res: Response;
      if (editing) {
        res = await fetch(`/api/config/backends/${encodeURIComponent(editing)}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
      } else {
        res = await fetch('/api/config/backends', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
      }

      if (res.ok) {
        setShowModal(false);
        setEditing(null);
        setForm(emptyForm);
        fetchBackends();
      } else {
        const err = await res.json();
        alert(err.detail || '保存失败');
      }
    } catch (e) {
      alert('保存失败');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (name: string) => {
    if (!confirm(`确定删除后端 "${name}"？`)) return;
    try {
      const res = await fetch(`/api/config/backends/${encodeURIComponent(name)}`, { method: 'DELETE' });
      if (res.ok) {
        fetchBackends();
      } else {
        const err = await res.json();
        alert(err.detail || '删除失败');
      }
    } catch (e) {
      alert('删除失败');
    }
  };

  const toggleEnable = async (b: Backend) => {
    try {
      const res = await fetch(`/api/config/backends/${encodeURIComponent(b.name)}/toggle`, {
        method: 'PUT',
      });
      if (res.ok) {
        fetchBackends();
      }
    } catch (e) {
      console.error('Failed to toggle backend:', e);
    }
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <h2 className="text-2xl font-bold text-text-primary">后端管理</h2>
        <div className="flex items-center gap-3">
          <button onClick={fetchBackends} className="btn-secondary flex items-center gap-2">
            <RefreshCw size={16} /> 刷新
          </button>
          <button onClick={openAdd} className="btn-primary flex items-center gap-2">
            <Plus size={18} /> 添加后端
          </button>
        </div>
      </div>

      <div className="glass-card overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="bg-bg-secondary/50 text-left text-xs uppercase tracking-wider text-text-muted">
              <th className="px-6 py-4 font-semibold">名称</th>
              <th className="px-6 py-4 font-semibold">类型</th>
              <th className="px-6 py-4 font-semibold">URL</th>
              <th className="px-6 py-4 font-semibold">模型数</th>
              <th className="px-6 py-4 font-semibold">优先级</th>
              <th className="px-6 py-4 font-semibold">状态</th>
              <th className="px-6 py-4 font-semibold">操作</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {backends.length === 0 && (
              <tr>
                <td colSpan={7} className="px-6 py-8 text-center text-text-muted">
                  暂无后端，点击上方"添加后端"开始配置
                </td>
              </tr>
            )}
            {backends.map((b) => (
              <motion.tr
                key={b.name}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="hover:bg-bg-tertiary/30 transition-colors"
              >
                <td className="px-6 py-4 font-medium text-text-primary">{b.name}</td>
                <td className="px-6 py-4 text-text-secondary capitalize">{b.type}</td>
                <td className="px-6 py-4 font-mono text-sm text-text-muted max-w-xs truncate">{b.url}</td>
                <td className="px-6 py-4 text-text-secondary">{b.models?.length || 0}</td>
                <td className="px-6 py-4 text-text-secondary">{b.priority}</td>
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
                    <button onClick={() => openEdit(b)} className="p-1 hover:text-accent-primary" title="编辑">
                      <Pencil size={16} />
                    </button>
                    <button onClick={() => handleDelete(b.name)} className="p-1 hover:text-error" title="删除">
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
            className="glass-card p-8 max-w-lg w-full max-h-[90vh] overflow-y-auto"
          >
            <h3 className="text-xl font-bold mb-6 text-text-primary">{editing ? '编辑后端' : '添加后端'}</h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">名称</label>
                <input type="text" className="input-field" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required placeholder="例如: openai" />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">类型</label>
                <select className="input-field" value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value })}>
                  <option value="openai">OpenAI</option>
                  <option value="anthropic">Anthropic</option>
                  <option value="google">Google</option>
                  <option value="ollama">Ollama</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">API URL</label>
                <input type="url" className="input-field" value={form.url} onChange={(e) => setForm({ ...form, url: e.target.value })} required placeholder="https://api.openai.com/v1" />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">API Keys (每行一个)</label>
                <textarea className="input-field font-mono text-sm" rows={3} value={form.api_keys} onChange={(e) => setForm({ ...form, api_keys: e.target.value })} placeholder="sk-..." />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">模型 (每行一个)</label>
                <textarea className="input-field font-mono text-sm" rows={3} value={form.models} onChange={(e) => setForm({ ...form, models: e.target.value })} placeholder="gpt-4&#10;gpt-3.5-turbo" />
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-text-secondary mb-1">优先级</label>
                  <input type="number" className="input-field" value={form.priority} onChange={(e) => setForm({ ...form, priority: parseInt(e.target.value) })} min={1} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-text-secondary mb-1">权重</label>
                  <input type="number" className="input-field" value={form.weight} onChange={(e) => setForm({ ...form, weight: parseInt(e.target.value) })} min={1} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-text-secondary mb-1">超时(秒)</label>
                  <input type="number" className="input-field" value={form.timeout} onChange={(e) => setForm({ ...form, timeout: parseInt(e.target.value) })} min={10} />
                </div>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-text-secondary mb-1">RPM 限制</label>
                  <input type="number" className="input-field" value={form.rate_limit_rpm} onChange={(e) => setForm({ ...form, rate_limit_rpm: parseInt(e.target.value) })} min={0} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-text-secondary mb-1">TPM 限制</label>
                  <input type="number" className="input-field" value={form.rate_limit_tpm} onChange={(e) => setForm({ ...form, rate_limit_tpm: parseInt(e.target.value) })} min={0} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-text-secondary mb-1">并发限制</label>
                  <input type="number" className="input-field" value={form.rate_limit_concurrent} onChange={(e) => setForm({ ...form, rate_limit_concurrent: parseInt(e.target.value) })} min={0} />
                </div>
              </div>
              <div className="flex items-center gap-3">
                <input type="checkbox" id="verify_ssl" checked={form.verify_ssl} onChange={(e) => setForm({ ...form, verify_ssl: e.target.checked })} />
                <label htmlFor="verify_ssl" className="text-sm text-text-secondary">验证 SSL 证书</label>
              </div>
              <div className="flex justify-end gap-3 mt-6">
                <button type="button" onClick={() => { setShowModal(false); setEditing(null); }} className="btn-secondary">取消</button>
                <button type="submit" className="btn-primary" disabled={loading}>
                  {loading ? '保存中...' : '保存'}
                </button>
              </div>
            </form>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default Backends;
