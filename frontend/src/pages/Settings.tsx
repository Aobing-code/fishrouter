import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FileText, Download, Power, RotateCcw, Info, RefreshCw } from 'lucide-react';

const Settings: React.FC = () => {
  const [logs, setLogs] = useState<string[]>([]);
  const [version, setVersion] = useState('1.0.0');
  const [loadingLogs, setLoadingLogs] = useState(false);

  const fetchLogs = async () => {
    setLoadingLogs(true);
    try {
      const res = await fetch('/api/logs?lines=100');
      const data = await res.json();
      setLogs(data.logs || []);
    } catch (e) {
      console.error('Failed to fetch logs:', e);
    } finally {
      setLoadingLogs(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  const restartServer = async () => {
    if (confirm('确定重启服务器？')) {
      try {
        await fetch('/api/restart', { method: 'POST' });
        alert('正在重启...');
      } catch (e) {
        alert('重启请求已发送');
      }
    }
  };

  const downloadConfig = async () => {
    try {
      const res = await fetch('/api/config');
      const data = await res.json();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'fishrouter-config.json';
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      alert('下载配置失败');
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
        <h2 className="text-2xl font-bold text-text-primary mb-2">系统设置</h2>
        <p className="text-text-muted">管理配置、日志和系统操作</p>
      </motion.div>

      <div className="space-y-6">
        {/* Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="glass-card p-6"
        >
          <h3 className="text-lg font-semibold text-text-primary mb-4">系统操作</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button onClick={downloadConfig} className="btn-secondary flex items-center justify-center gap-2">
              <Download size={18} /> 下载配置
            </button>
            <button onClick={restartServer} className="btn-secondary flex items-center justify-center gap-2 text-warning border-warning/30 hover:bg-warning/10">
              <Power size={18} /> 重启服务器
            </button>
            <button onClick={fetchLogs} className="btn-secondary flex items-center justify-center gap-2">
              <RefreshCw size={18} /> 刷新日志
            </button>
          </div>
        </motion.div>

        {/* Version */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="glass-card p-6"
        >
          <h3 className="text-lg font-semibold text-text-primary mb-4">关于</h3>
          <div className="space-y-3 text-text-secondary">
            <div className="flex items-center gap-3">
              <Info size={20} className="text-accent-primary" />
              <span>FishRouter v{version}</span>
            </div>
            <div className="flex items-center gap-3">
              <FileText size={20} className="text-accent-secondary" />
              <span>MIT Licensed • OpenAI/Anthropic/Google/Ollama 智能路由</span>
            </div>
          </div>
        </motion.div>

        {/* Logs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="glass-card p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-text-primary">最近日志</h3>
            <button onClick={fetchLogs} className="btn-secondary text-sm" disabled={loadingLogs}>
              {loadingLogs ? '加载中...' : '刷新'}
            </button>
          </div>
          <div className="bg-bg-primary/50 rounded-xl p-4 font-mono text-xs overflow-x-auto max-h-96 overflow-y-auto">
            {logs.length === 0 ? (
              <div className="text-text-muted">暂无日志</div>
            ) : (
              <pre className="whitespace-pre-wrap text-text-secondary">{logs.join('\n')}</pre>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Settings;
