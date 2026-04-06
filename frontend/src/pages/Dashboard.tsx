import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Activity,
  Zap,
  Coins,
  AlertTriangle,
  Server,
  Settings,
  LayoutDashboard,
  ArrowRight,
  RefreshCw,
} from 'lucide-react';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface BackendStatus {
  name: string;
  type: string;
  healthy: boolean;
  latency: number;
  total_requests: number;
  total_tokens: number;
  models: string[];
}

const StatCard: React.FC<{
  title: string;
  value: number | string;
  icon: React.ReactNode;
  color: string;
  delay?: number;
}> = ({ title, value, icon, color, delay = 0 }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay, duration: 0.5, ease: 'easeOut' }}
    className="glass-card p-6 relative overflow-hidden group"
  >
    <div className="absolute inset-0 bg-gradient-to-br from-accent-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
    <div className="flex items-start justify-between">
      <div>
        <p className="text-text-muted text-sm font-medium mb-2">{title}</p>
        <motion.p
          key={value}
          initial={{ scale: 0.95, opacity: 0.5 }}
          animate={{ scale: 1, opacity: 1 }}
          className={`text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r ${color}`}
        >
          {value}
        </motion.p>
      </div>
      <div className={`p-3 rounded-xl bg-gradient-to-br ${color} bg-opacity-20 text-white`}>
        {icon}
      </div>
    </div>
  </motion.div>
);

const Dashboard: React.FC<{ onLogout: () => void }> = ({ onLogout }) => {
  const location = useLocation();
  const [backends, setBackends] = useState<BackendStatus[]>([]);
  const [timelineData, setTimelineData] = useState<{ time: string; requests: number; tokens: number; errors: number }[]>([]);
  const [stats, setStats] = useState({
    totalRequests: 0,
    qps: 0,
    totalTokens: 0,
    totalErrors: 0,
  });
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const [statusRes, timelineRes] = await Promise.all([
        fetch('/api/monitor/status'),
        fetch('/api/monitor/timeline?minutes=30'),
      ]);

      const statusData = await statusRes.json();
      const timelineRaw = await timelineRes.json();

      setBackends(statusData.backends || []);
      setStats({
        totalRequests: statusData.stats?.total_requests || 0,
        qps: statusData.stats?.qps || 0,
        totalTokens: statusData.stats?.total_tokens || 0,
        totalErrors: statusData.stats?.total_errors || 0,
      });

      const formatted = (timelineRaw || []).map((item: any) => ({
        time: new Date(item.time).toLocaleTimeString('zh-CN', { hour12: false, hour: '2-digit', minute: '2-digit' }),
        requests: item.requests || 0,
        tokens: item.tokens || 0,
        errors: item.errors || 0,
      }));
      setTimelineData(formatted);
    } catch (e) {
      console.error('Failed to fetch dashboard data:', e);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const navItems = [
    { path: '/', label: '监控', icon: <Activity size={20} /> },
    { path: '/backends', label: '后端', icon: <Server size={20} /> },
    { path: '/config', label: '配置', icon: <Settings size={20} /> },
    { path: '/settings', label: '设置', icon: <LayoutDashboard size={20} /> },
  ];

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-border/40 bg-bg-secondary/60 backdrop-blur-md sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-primary to-accent-secondary flex items-center justify-center text-xl font-bold shadow-lg group-hover:shadow-accent-glow/30 transition-shadow">
              F
            </div>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-accent-primary to-accent-secondary bg-clip-text text-transparent">
                FishRouter
              </h1>
              <p className="text-xs text-text-muted">AI模型智能路由</p>
            </div>
          </Link>

          <nav className="flex items-center gap-2">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-accent-primary/15 text-accent-primary border border-accent-primary/30'
                      : 'text-text-secondary hover:text-accent-primary hover:bg-bg-tertiary/50'
                  }`}
                >
                  {item.icon}
                  {item.label}
                </Link>
              );
            })}
          </nav>

          <button onClick={onLogout} className="btn-secondary">
            退出
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-6 py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="总请求数"
            value={stats.totalRequests.toLocaleString()}
            icon={<Activity className="text-accent-primary" />}
            color="from-accent-primary to-accent-secondary"
            delay={0}
          />
          <StatCard
            title="QPS"
            value={stats.qps.toFixed(1)}
            icon={<Zap className="text-success" />}
            color="from-success to-green-400"
            delay={0.1}
          />
          <StatCard
            title="总 Token 数"
            value={stats.totalTokens.toLocaleString()}
            icon={<Coins className="text-purple-400" />}
            color="from-purple-400 to-purple-300"
            delay={0.2}
          />
          <StatCard
            title="错误数"
            value={stats.totalErrors.toLocaleString()}
            icon={<AlertTriangle className="text-error" />}
            color="from-error to-red-400"
            delay={0.3}
          />
        </div>

        {/* Charts & Tables */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Request Trend */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="lg:col-span-2 glass-card p-6"
          >
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-text-primary">请求趋势</h3>
              <button onClick={fetchData} className="p-2 hover:bg-bg-tertiary rounded-lg transition-colors">
                <RefreshCw size={16} className="text-text-muted" />
              </button>
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={timelineData}>
                  <defs>
                    <linearGradient id="colorRequests" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#00eeff" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#00eeff" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(100,120,160,0.1)" />
                  <XAxis dataKey="time" stroke="#8892b0" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="#8892b0" fontSize={12} tickLine={false} axisLine={false} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'rgba(20,20,30,0.9)',
                      border: '1px solid rgba(100,120,160,0.2)',
                      borderRadius: '12px',
                      color: '#f0f4ff',
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="requests"
                    stroke="#00eeff"
                    fillOpacity={1}
                    fill="url(#colorRequests)"
                    strokeWidth={2}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

          {/* System Status */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="glass-card p-6"
          >
            <h3 className="text-lg font-semibold text-text-primary mb-4">路由策略</h3>
            <div className="space-y-3">
              {backends.slice(0, 5).map((b) => (
                <div key={b.name} className="flex items-center justify-between">
                  <span className="text-text-muted text-sm">{b.name}</span>
                  <span className={`status-badge ${b.healthy ? 'status-healthy' : 'status-unhealthy'}`}>
                    {b.healthy ? '正常' : '异常'}
                  </span>
                </div>
              ))}
              {backends.length === 0 && (
                <div className="text-text-muted text-sm text-center py-4">暂无后端</div>
              )}
            </div>
          </motion.div>
        </div>

        {/* Backends Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="glass-card overflow-hidden"
        >
          <div className="p-6 border-b border-border">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-text-primary">后端状态</h3>
              <Link to="/backends" className="flex items-center gap-2 text-accent-primary hover:underline text-sm">
                管理 <ArrowRight size={14} />
              </Link>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-bg-secondary/50 text-left text-xs uppercase tracking-wider text-text-muted">
                  <th className="px-6 py-4 font-semibold">名称</th>
                  <th className="px-6 py-4 font-semibold">类型</th>
                  <th className="px-6 py-4 font-semibold">状态</th>
                  <th className="px-6 py-4 font-semibold">延迟</th>
                  <th className="px-6 py-4 font-semibold">请求数</th>
                  <th className="px-6 py-4 font-semibold">模型</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {backends.length === 0 && !loading && (
                  <tr>
                    <td colSpan={6} className="px-6 py-8 text-center text-text-muted">
                      暂无后端数据
                    </td>
                  </tr>
                )}
                {backends.map((backend, idx) => (
                  <motion.tr
                    key={backend.name}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.7 + idx * 0.05 }}
                    className="hover:bg-bg-tertiary/30 transition-colors"
                  >
                    <td className="px-6 py-4 font-medium text-text-primary">{backend.name}</td>
                    <td className="px-6 py-4 text-text-secondary capitalize">{backend.type}</td>
                    <td className="px-6 py-4">
                      <span className={`status-badge ${backend.healthy ? 'status-healthy' : 'status-unhealthy'}`}>
                        {backend.healthy ? '正常' : '异常'}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-16 h-1.5 bg-bg-tertiary rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full transition-all ${
                              backend.latency < 100
                                ? 'bg-success'
                                : backend.latency < 300
                                ? 'bg-warning'
                                : 'bg-error'
                            }`}
                            style={{ width: `${Math.min(100, backend.latency / 2)}%` }}
                          />
                        </div>
                        <span className="font-mono text-sm text-text-secondary">{backend.latency}ms</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 font-mono text-text-secondary">{backend.total_requests.toLocaleString()}</td>
                    <td className="px-6 py-4 text-text-muted text-sm">
                      {Array.isArray(backend.models) ? backend.models.join(', ') : backend.models}
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>
      </main>

      {/* Floating particles (optional visual flair) */}
      <div className="fixed inset-0 pointer-events-none -z-10 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-accent-primary/5 rounded-full blur-3xl animate-pulse-slow" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-accent-secondary/5 rounded-full blur-3xl animate-float" />
      </div>
    </div>
  );
};

export default Dashboard;
