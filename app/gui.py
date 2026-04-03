"""FishRouter Windows GUI - Full Configuration Manager"""
import sys
import os
import subprocess
import threading
import webbrowser
import time
import json
import urllib.request
import ssl

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, scrolledtext
except ImportError:
    print("Tkinter not available")
    sys.exit(1)


class FishRouterApp:
    """FishRouter Windows GUI Application"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("FishRouter - AI Model Router")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 1000) // 2
        y = (self.root.winfo_screenheight() - 700) // 2
        self.root.geometry(f"1000x700+{x}+{y}")
        
        self.server_process = None
        self.server_running = False
        self.config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
        self.config = {}
        self._load_config_file()
        
        # Stats
        self.stats_data = {"total_requests": 0, "total_tokens": 0, "total_errors": 0, "qps": 0}
        self.backend_statuses = []
        
        # Fallback drag state
        self.drag_item = None
        
        self._setup_ui()
        self._start_stats_refresh()
        
        if self.auto_start.get():
            self.root.after(1000, self.start_server)

    def _load_config_file(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
        except:
            self._create_default_config()

    def _create_default_config(self):
        self.config = {
            "server": {"host": "0.0.0.0", "port": 8080, "log_level": "info"},
            "backends": [],
            "routes": [{"name": "default", "models": ["*"], "strategy": "latency", "failover": True, "health_check_interval": 30, "fallback_order": [], "fallback_rules": []}],
            "auth": {"enabled": False, "api_keys": ["sk-fishrouter"]}
        }
        self._save_config()

    def _save_config(self):
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self._log(f"保存配置失败 | Save config error: {e}")

    def _setup_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.tab_dashboard = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_dashboard, text="🏠 控制台 | Dashboard")
        self._setup_dashboard()
        
        self.tab_backends = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_backends, text="🔗 后端 | Backends")
        self._setup_backends_tab()
        
        self.tab_routes = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_routes, text="🛤️ 路由 | Routes")
        self._setup_routes_tab()
        
        self.tab_settings = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_settings, text="⚙️ 设置 | Settings")
        self._setup_settings_tab()
        
        self.tab_update = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_update, text="🔄 更新 | Update")
        self._setup_update_tab()

    # ===== Dashboard =====
    def _setup_dashboard(self):
        # Stats cards
        stats_frame = ttk.Frame(self.tab_dashboard)
        stats_frame.pack(fill="x", padx=10, pady=10)
        
        card_data = [
            ("总请求 | Requests", "requests", "#38bdf8"),
            ("QPS", "qps", "#a78bfa"),
            ("总Token | Tokens", "tokens", "#22c55e"),
            ("错误 | Errors", "errors", "#ef4444")
        ]
        
        self.stat_labels = {}
        for i, (label, key, color) in enumerate(card_data):
            card = ttk.LabelFrame(stats_frame, text=label, padding=10)
            card.grid(row=0, column=i, padx=5, sticky="nsew")
            stats_frame.columnconfigure(i, weight=1)
            val = ttk.Label(card, text="0", font=("Segoe UI", 20, "bold"), foreground=color)
            val.pack()
            self.stat_labels[key] = val
        
        # Server controls
        ctrl_frame = ttk.Frame(self.tab_dashboard)
        ctrl_frame.pack(fill="x", padx=10, pady=5)
        
        self.status_var = tk.StringVar(value="⏹ 已停止 | Stopped")
        ttk.Label(ctrl_frame, textvariable=self.status_var, font=("Segoe UI", 10)).pack(side="left", padx=10)
        
        self.start_btn = ttk.Button(ctrl_frame, text="▶ 启动 | Start", command=self.start_server)
        self.start_btn.pack(side="left", padx=5)
        self.stop_btn = ttk.Button(ctrl_frame, text="⏹ 停止 | Stop", command=self.stop_server, state="disabled")
        self.stop_btn.pack(side="left", padx=5)
        ttk.Button(ctrl_frame, text="🌐 打开面板 | Open Web UI", command=self.open_dashboard).pack(side="left", padx=5)
        ttk.Button(ctrl_frame, text="🔍 健康检查 | Health Check", command=self._trigger_health_check).pack(side="left", padx=5)
        
        # Backend status table
        status_frame = ttk.LabelFrame(self.tab_dashboard, text="后端状态 | Backend Status", padding=5)
        status_frame.pack(fill="x", padx=10, pady=10)
        
        columns = ("name", "type", "healthy", "latency", "requests", "models")
        self.status_tree = ttk.Treeview(status_frame, columns=columns, show="headings", height=5)
        self.status_tree.heading("name", text="名称 | Name")
        self.status_tree.heading("type", text="类型 | Type")
        self.status_tree.heading("healthy", text="状态 | Status")
        self.status_tree.heading("latency", text="延迟 | Latency")
        self.status_tree.heading("requests", text="请求 | Requests")
        self.status_tree.heading("models", text="模型 | Models")
        self.status_tree.column("name", width=100)
        self.status_tree.column("type", width=70)
        self.status_tree.column("healthy", width=60)
        self.status_tree.column("latency", width=80)
        self.status_tree.column("requests", width=70)
        self.status_tree.column("models", width=200)
        self.status_tree.pack(fill="x")
        
        # Log
        log_frame = ttk.LabelFrame(self.tab_dashboard, text="日志 | Log", padding=5)
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, font=("Consolas", 9), bg="#1e1e1e", fg="#d4d4d4", insertbackground="white")
        self.log_text.pack(fill="both", expand=True)

    def _start_stats_refresh(self):
        """Periodically refresh stats from local server"""
        def refresh():
            if self.server_running:
                port = self.config.get("server", {}).get("port", 8080)
                try:
                    ctx = ssl.create_default_context()
                    ctx.check_hostname = False
                    ctx.verify_mode = ssl.CERT_NONE
                    
                    # Stats
                    req = urllib.request.Request(f"http://localhost:{port}/api/monitor/stats")
                    with urllib.request.urlopen(req, context=ctx, timeout=3) as resp:
                        stats = json.loads(resp.read().decode())
                        self.stats_data = stats
                        self.root.after(0, self._update_stats_display)
                    
                    # Backend status
                    req = urllib.request.Request(f"http://localhost:{port}/api/monitor/backends")
                    with urllib.request.urlopen(req, context=ctx, timeout=3) as resp:
                        backends = json.loads(resp.read().decode())
                        self.backend_statuses = backends
                        self.root.after(0, self._update_backend_status)
                except:
                    pass
            self.root.after(3000, refresh)
        
        threading.Thread(target=refresh, daemon=True).start()

    def _update_stats_display(self):
        self.stat_labels["requests"].config(text=str(self.stats_data.get("total_requests", 0)))
        self.stat_labels["qps"].config(text=f"{self.stats_data.get('qps', 0):.2f}")
        self.stat_labels["tokens"].config(text=str(self.stats_data.get("total_tokens", 0)))
        self.stat_labels["errors"].config(text=str(self.stats_data.get("total_errors", 0)))

    def _update_backend_status(self):
        for item in self.status_tree.get_children():
            self.status_tree.delete(item)
        for b in self.backend_statuses:
            healthy = "✅" if b.get("healthy") else "❌"
            self.status_tree.insert("", "end", values=(
                b.get("name", ""),
                b.get("type", ""),
                healthy,
                f"{b.get('latency', 0):.3f}s",
                b.get("total_requests", 0),
                ", ".join(b.get("models", []))
            ))

    def _trigger_health_check(self):
        if self.server_running:
            port = self.config.get("server", {}).get("port", 8080)
            try:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                req = urllib.request.Request(f"http://localhost:{port}/api/monitor/health-check", method="GET")
                urllib.request.urlopen(req, context=ctx, timeout=10)
                self._log("健康检查已触发 | Health check triggered")
            except Exception as e:
                self._log(f"健康检查失败 | Health check failed: {e}")

    # ===== Backends Tab =====
    def _setup_backends_tab(self):
        frame = ttk.Frame(self.tab_backends, padding=10)
        frame.pack(fill="both", expand=True)
        
        list_frame = ttk.LabelFrame(frame, text="后端列表 | Backend List", padding=5)
        list_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        columns = ("name", "type", "url", "keys", "models", "enabled")
        self.backend_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        self.backend_tree.heading("name", text="名称 | Name")
        self.backend_tree.heading("type", text="类型 | Type")
        self.backend_tree.heading("url", text="地址 | URL")
        self.backend_tree.heading("keys", text="Keys")
        self.backend_tree.heading("models", text="模型 | Models")
        self.backend_tree.heading("enabled", text="状态 | Status")
        self.backend_tree.column("name", width=100)
        self.backend_tree.column("type", width=70)
        self.backend_tree.column("url", width=200)
        self.backend_tree.column("keys", width=50)
        self.backend_tree.column("models", width=150)
        self.backend_tree.column("enabled", width=60)
        self.backend_tree.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.backend_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.backend_tree.configure(yscrollcommand=scrollbar.set)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x")
        ttk.Button(btn_frame, text="➕ 添加 | Add", command=self._add_backend).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="✏️ 编辑 | Edit", command=self._edit_backend).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🗑️ 删除 | Delete", command=self._delete_backend).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🔄 刷新 | Refresh", command=self._refresh_backend_list).pack(side="left", padx=5)
        
        self._refresh_backend_list()

    def _refresh_backend_list(self):
        for item in self.backend_tree.get_children():
            self.backend_tree.delete(item)
        for b in self.config.get("backends", []):
            status = "✅" if b.get("enabled", True) else "❌"
            models = ", ".join([m.get("id", "") for m in b.get("models", [])])
            self.backend_tree.insert("", "end", values=(
                b.get("name", ""),
                b.get("type", ""),
                b.get("url", ""),
                len(b.get("api_keys", [])),
                models,
                status
            ))

    def _add_backend(self):
        self._open_backend_editor()

    def _edit_backend(self):
        selection = self.backend_tree.selection()
        if not selection:
            messagebox.showwarning("警告 | Warning", "请选择一个后端 | Please select a backend")
            return
        item = self.backend_tree.item(selection[0])
        self._open_backend_editor(item["values"][0])

    def _delete_backend(self):
        selection = self.backend_tree.selection()
        if not selection:
            messagebox.showwarning("警告 | Warning", "请选择一个后端 | Please select a backend")
            return
        name = self.backend_tree.item(selection[0])["values"][0]
        if messagebox.askyesno("确认 | Confirm", f"确定删除后端 {name}？"):
            self.config["backends"] = [b for b in self.config.get("backends", []) if b.get("name") != name]
            self._save_config()
            self._refresh_backend_list()
            self._log(f"已删除后端 | Deleted backend: {name}")

    def _open_backend_editor(self, name=None):
        dialog = tk.Toplevel(self.root)
        dialog.title("编辑后端 | Edit Backend" if name else "添加后端 | Add Backend")
        dialog.geometry("650x650")
        dialog.transient(self.root)
        dialog.grab_set()
        
        backend = {}
        if name:
            for b in self.config.get("backends", []):
                if b.get("name") == name:
                    backend = b
                    break
        
        # Create scrollable canvas
        canvas = tk.Canvas(dialog)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable = ttk.Frame(canvas)
        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        fields = [
            ("名称 | Name", "name", backend.get("name", "")),
            ("类型 | Type", "type", backend.get("type", "openai")),
            ("地址 | URL", "url", backend.get("url", "")),
            ("权重 | Weight", "weight", str(backend.get("weight", 10))),
            ("优先级 | Priority", "priority", str(backend.get("priority", 1))),
            ("超时 | Timeout (秒)", "timeout", str(backend.get("timeout", 60))),
        ]
        
        entries = {}
        for i, (label, key, default) in enumerate(fields):
            ttk.Label(scrollable, text=label).grid(row=i, column=0, sticky="w", padx=10, pady=5)
            if key == "type":
                entry = ttk.Combobox(scrollable, values=["openai", "anthropic", "google", "ollama"], width=35)
                entry.set(default)
            else:
                entry = ttk.Entry(scrollable, width=40)
                entry.insert(0, default)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries[key] = entry
        
        # API Keys
        ttk.Label(scrollable, text="API Keys (每行一个 | One per line):").grid(row=len(fields), column=0, sticky="w", padx=10, pady=5)
        api_keys_entry = scrolledtext.ScrolledText(scrollable, height=4, width=40)
        api_keys_entry.insert("1.0", "\n".join(backend.get("api_keys", [])))
        api_keys_entry.grid(row=len(fields), column=1, padx=5, pady=5)
        
        # Rate limit
        rl_row = len(fields) + 1
        ttk.Label(scrollable, text="速率限制 | Rate Limit:").grid(row=rl_row, column=0, sticky="w", padx=10, pady=5)
        rl_frame = ttk.Frame(scrollable)
        rl_frame.grid(row=rl_row, column=1, padx=5, pady=5)
        
        rl = backend.get("rate_limit", {})
        ttk.Label(rl_frame, text="RPM:").pack(side="left")
        rpm_entry = ttk.Entry(rl_frame, width=8)
        rpm_entry.insert(0, str(rl.get("rpm", 0)))
        rpm_entry.pack(side="left", padx=3)
        ttk.Label(rl_frame, text="TPM:").pack(side="left", padx=(10, 0))
        tpm_entry = ttk.Entry(rl_frame, width=8)
        tpm_entry.insert(0, str(rl.get("tpm", 0)))
        tpm_entry.pack(side="left", padx=3)
        ttk.Label(rl_frame, text="并发 | Concurrent:").pack(side="left", padx=(10, 0))
        conc_entry = ttk.Entry(rl_frame, width=8)
        conc_entry.insert(0, str(rl.get("concurrent", 0)))
        conc_entry.pack(side="left", padx=3)
        
        # Models
        models_row = rl_row + 1
        ttk.Label(scrollable, text="模型 | Models:").grid(row=models_row, column=0, sticky="nw", padx=10, pady=5)
        
        models_frame = ttk.Frame(scrollable)
        models_frame.grid(row=models_row, column=1, padx=5, pady=5)
        
        models_listbox = tk.Listbox(models_frame, height=5, width=45)
        models_listbox.pack(side="left", fill="x")
        for m in backend.get("models", []):
            models_listbox.insert("end", f"{m.get('id', '')} -> {m.get('name', '')} ({m.get('context_length', 0)} tokens)")
        
        models_btn_frame = ttk.Frame(models_frame)
        models_btn_frame.pack(side="right", fill="y")
        
        def add_model():
            self._open_model_editor(models_listbox)
        def edit_model():
            sel = models_listbox.curselection()
            if not sel:
                return
            idx = sel[0]
            existing_models = backend.get("models", [])
            if idx < len(existing_models):
                self._open_model_editor(models_listbox, existing_models[idx], idx)
        def remove_model():
            sel = models_listbox.curselection()
            if sel:
                models_listbox.delete(sel[0])
        
        ttk.Button(models_btn_frame, text="➕", command=add_model).pack(fill="x", pady=2)
        ttk.Button(models_btn_frame, text="✏️", command=edit_model).pack(fill="x", pady=2)
        ttk.Button(models_btn_frame, text="🗑️", command=remove_model).pack(fill="x", pady=2)
        
        def save():
            api_keys = [k.strip() for k in api_keys_entry.get("1.0", "end-1c").split("\n") if k.strip()]
            
            # Build models from listbox content
            existing_models = backend.get("models", [])
            new_models = []
            for i in range(models_listbox.size()):
                if i < len(existing_models):
                    new_models.append(existing_models[i])
                else:
                    new_models.append({"id": f"model-{i}", "name": f"model-{i}", "context_length": 4096, "enabled": True, "rate_limit": {"rpm": 0, "tpm": 0, "concurrent": 0}})
            
            backend_data = {
                "name": entries["name"].get(),
                "type": entries["type"].get(),
                "url": entries["url"].get(),
                "api_keys": api_keys,
                "weight": int(entries["weight"].get() or 10),
                "priority": int(entries["priority"].get() or 1),
                "timeout": int(entries["timeout"].get() or 60),
                "enabled": True,
                "verify_ssl": True,
                "models": new_models,
                "rate_limit": {
                    "rpm": int(rpm_entry.get() or 0),
                    "tpm": int(tpm_entry.get() or 0),
                    "concurrent": int(conc_entry.get() or 0)
                }
            }
            
            if name:
                for i, b in enumerate(self.config.get("backends", [])):
                    if b.get("name") == name:
                        self.config["backends"][i] = backend_data
                        break
            else:
                self.config.setdefault("backends", []).append(backend_data)
            
            self._save_config()
            self._refresh_backend_list()
            self._log(f"已保存后端 | Saved backend: {backend_data['name']}")
            dialog.destroy()
        
        ttk.Button(scrollable, text="💾 保存 | Save", command=save).grid(row=models_row + 1, column=0, columnspan=2, pady=20)

    def _open_model_editor(self, listbox, model=None, index=None):
        dialog = tk.Toplevel(self.root)
        dialog.title("编辑模型 | Edit Model" if model else "添加模型 | Add Model")
        dialog.geometry("400x350")
        dialog.transient(self.root)
        dialog.grab_set()
        
        model = model or {}
        
        fields = [
            ("模型ID | Model ID (请求时使用)", "id", model.get("id", "")),
            ("实际名称 | Actual Name", "name", model.get("name", "")),
            ("上下文长度 | Context Length", "context_length", str(model.get("context_length", 4096))),
        ]
        
        entries = {}
        for i, (label, key, default) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, sticky="w", padx=10, pady=5)
            entry = ttk.Entry(dialog, width=35)
            entry.insert(0, default)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries[key] = entry
        
        # Rate limit
        ttk.Label(dialog, text="模型限速 | Model Rate Limit:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        rl_frame = ttk.Frame(dialog)
        rl_frame.grid(row=3, column=1, padx=5, pady=5)
        rl = model.get("rate_limit", {})
        ttk.Label(rl_frame, text="RPM:").pack(side="left")
        rpm_e = ttk.Entry(rl_frame, width=6)
        rpm_e.insert(0, str(rl.get("rpm", 0)))
        rpm_e.pack(side="left", padx=2)
        ttk.Label(rl_frame, text="TPM:").pack(side="left", padx=(8, 0))
        tpm_e = ttk.Entry(rl_frame, width=6)
        tpm_e.insert(0, str(rl.get("tpm", 0)))
        tpm_e.pack(side="left", padx=2)
        ttk.Label(rl_frame, text="并发:").pack(side="left", padx=(8, 0))
        conc_e = ttk.Entry(rl_frame, width=6)
        conc_e.insert(0, str(rl.get("concurrent", 0)))
        conc_e.pack(side="left", padx=2)
        
        def save():
            model_data = {
                "id": entries["id"].get(),
                "name": entries["name"].get(),
                "context_length": int(entries["context_length"].get() or 4096),
                "enabled": True,
                "rate_limit": {"rpm": int(rpm_e.get() or 0), "tpm": int(tpm_e.get() or 0), "concurrent": int(conc_e.get() or 0)}
            }
            
            display = f"{model_data['id']} -> {model_data['name']} ({model_data['context_length']} tokens)"
            if index is not None:
                listbox.delete(index)
                listbox.insert(index, display)
            else:
                listbox.insert("end", display)
            
            # Store model data in listbox
            if not hasattr(listbox, '_models'):
                listbox._models = []
            if index is not None:
                listbox._models[index] = model_data
            else:
                listbox._models.append(model_data)
            
            dialog.destroy()
        
        ttk.Button(dialog, text="💾 保存 | Save", command=save).grid(row=4, column=0, columnspan=2, pady=20)

    # ===== Routes Tab =====
    def _setup_routes_tab(self):
        frame = ttk.Frame(self.tab_routes, padding=10)
        frame.pack(fill="both", expand=True)
        
        # Route config
        route_frame = ttk.LabelFrame(frame, text="路由配置 | Route Configuration", padding=10)
        route_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(route_frame, text="策略 | Strategy:").grid(row=0, column=0, sticky="w", pady=5)
        self.route_strategy = ttk.Combobox(route_frame, values=["latency", "round_robin", "random", "weighted", "priority", "custom"], width=20)
        self.route_strategy.grid(row=0, column=1, sticky="w", padx=5)
        
        ttk.Label(route_frame, text="健康检查间隔 | Health Check (秒):").grid(row=1, column=0, sticky="w", pady=5)
        self.hc_interval = ttk.Entry(route_frame, width=10)
        self.hc_interval.grid(row=1, column=1, sticky="w", padx=5)
        
        # Fallback order with drag-and-drop
        fb_frame = ttk.LabelFrame(frame, text="回退顺序 | Fallback Order (拖拽排序 | Drag to reorder)", padding=10)
        fb_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Listbox for fallback
        self.fb_listbox = tk.Listbox(fb_frame, height=8, font=("Consolas", 10))
        self.fb_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Bind drag events
        self.fb_listbox.bind("<Button-1>", self._fb_drag_start)
        self.fb_listbox.bind("<B1-Motion>", self._fb_drag_motion)
        self.fb_listbox.bind("<ButtonRelease-1>", self._fb_drag_release)
        
        # Add/remove buttons
        fb_btn_frame = ttk.Frame(fb_frame)
        fb_btn_frame.pack(fill="x", pady=5)
        
        ttk.Button(fb_btn_frame, text="➕ 添加 | Add", command=self._add_fallback).pack(side="left", padx=5)
        ttk.Button(fb_btn_frame, text="🗑️ 移除 | Remove", command=self._remove_fallback).pack(side="left", padx=5)
        
        # Available backends to add
        avail_frame = ttk.LabelFrame(fb_frame, text="可用后端 | Available Backends", padding=5)
        avail_frame.pack(fill="x", pady=5)
        
        self.avail_frame_inner = ttk.Frame(avail_frame)
        self.avail_frame_inner.pack(fill="x")
        
        ttk.Button(frame, text="💾 保存路由 | Save Route", command=self._save_route).pack(pady=10)
        
        self._load_route_config()
        self._refresh_available_backends()

    def _load_route_config(self):
        route = self.config.get("routes", [{}])[0] if self.config.get("routes") else {}
        self.route_strategy.set(route.get("strategy", "latency"))
        self.hc_interval.delete(0, "end")
        self.hc_interval.insert(0, str(route.get("health_check_interval", 30)))
        self.fb_listbox.delete(0, "end")
        for item in route.get("fallback_order", []):
            self.fb_listbox.insert("end", item)

    def _refresh_available_backends(self):
        for w in self.avail_frame_inner.winfo_children():
            w.destroy()
        
        fallback_items = [self.fb_listbox.get(i) for i in range(self.fb_listbox.size())]
        
        for b in self.config.get("backends", []):
            if not b.get("enabled", True):
                continue
            name = b.get("name", "")
            if name in fallback_items:
                continue
            
            btn = ttk.Button(self.avail_frame_inner, text=f"+ {name} ({b.get('type', '')})",
                           command=lambda n=name: self._add_to_fallback(n))
            btn.pack(side="left", padx=3, pady=3)

    def _add_to_fallback(self, name):
        if name not in [self.fb_listbox.get(i) for i in range(self.fb_listbox.size())]:
            self.fb_listbox.insert("end", name)
            self._refresh_available_backends()

    def _add_fallback(self):
        # Show dialog to pick backend
        dialog = tk.Toplevel(self.root)
        dialog.title("添加回退后端 | Add Fallback Backend")
        dialog.geometry("300x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="选择后端 | Select Backend:").pack(pady=10)
        
        lb = tk.Listbox(dialog, height=8)
        lb.pack(fill="both", expand=True, padx=10)
        for b in self.config.get("backends", []):
            if b.get("enabled", True):
                lb.insert("end", b.get("name", ""))
        
        def select():
            sel = lb.curselection()
            if sel:
                self._add_to_fallback(lb.get(sel[0]))
            dialog.destroy()
        
        ttk.Button(dialog, text="确定 | OK", command=select).pack(pady=10)

    def _remove_fallback(self):
        sel = self.fb_listbox.curselection()
        if sel:
            self.fb_listbox.delete(sel[0])
            self._refresh_available_backends()

    # Drag and drop
    def _fb_drag_start(self, event):
        self.drag_item = self.fb_listbox.nearest(event.y)

    def _fb_drag_motion(self, event):
        i = self.fb_listbox.nearest(event.y)
        if i != self.drag_item and self.drag_item is not None:
            # Swap items
            items = [self.fb_listbox.get(j) for j in range(self.fb_listbox.size())]
            items[self.drag_item], items[i] = items[i], items[self.drag_item]
            self.fb_listbox.delete(0, "end")
            for item in items:
                self.fb_listbox.insert("end", item)
            self.drag_item = i
            self.fb_listbox.selection_clear(0, "end")
            self.fb_listbox.selection_set(i)

    def _fb_drag_release(self, event):
        self.drag_item = None

    def _save_route(self):
        fallback = [self.fb_listbox.get(i) for i in range(self.fb_listbox.size())]
        
        if self.config.get("routes"):
            self.config["routes"][0]["strategy"] = self.route_strategy.get()
            self.config["routes"][0]["health_check_interval"] = int(self.hc_interval.get() or 30)
            self.config["routes"][0]["fallback_order"] = fallback
        else:
            self.config["routes"] = [{
                "name": "default",
                "models": ["*"],
                "strategy": self.route_strategy.get(),
                "failover": True,
                "health_check_interval": int(self.hc_interval.get() or 30),
                "fallback_order": fallback,
                "fallback_rules": []
            }]
        
        self._save_config()
        self._log("路由配置已保存 | Route config saved")
        self._refresh_available_backends()
        messagebox.showinfo("成功 | Success", "路由配置已保存 | Route config saved")

    # ===== Settings Tab =====
    def _setup_settings_tab(self):
        frame = ttk.Frame(self.tab_settings, padding=10)
        frame.pack(fill="both", expand=True)
        
        server_frame = ttk.LabelFrame(frame, text="服务器 | Server", padding=10)
        server_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(server_frame, text="端口 | Port:").grid(row=0, column=0, sticky="w", pady=5)
        self.port_entry = ttk.Entry(server_frame, width=10)
        self.port_entry.insert(0, str(self.config.get("server", {}).get("port", 8080)))
        self.port_entry.grid(row=0, column=1, sticky="w", padx=5)
        
        ttk.Label(server_frame, text="日志级别 | Log Level:").grid(row=1, column=0, sticky="w", pady=5)
        self.log_level = ttk.Combobox(server_frame, values=["debug", "info", "warning", "error"], width=15)
        self.log_level.set(self.config.get("server", {}).get("log_level", "info"))
        self.log_level.grid(row=1, column=1, sticky="w", padx=5)
        
        auth_frame = ttk.LabelFrame(frame, text="认证 | Authentication", padding=10)
        auth_frame.pack(fill="x", pady=(0, 10))
        
        self.auth_enabled = tk.BooleanVar(value=self.config.get("auth", {}).get("enabled", False))
        ttk.Checkbutton(auth_frame, text="启用 API Key 认证 | Enable API Key Auth", variable=self.auth_enabled).pack(anchor="w", pady=5)
        
        ttk.Label(auth_frame, text="API Keys (每行一个 | One per line):").pack(anchor="w")
        self.api_keys_text = scrolledtext.ScrolledText(auth_frame, height=5, width=50)
        self.api_keys_text.insert("1.0", "\n".join(self.config.get("auth", {}).get("api_keys", [])))
        self.api_keys_text.pack(fill="x", pady=5)
        
        startup_frame = ttk.LabelFrame(frame, text="启动 | Startup", padding=10)
        startup_frame.pack(fill="x", pady=(0, 10))
        
        self.auto_start = tk.BooleanVar(value=self._check_autostart())
        ttk.Checkbutton(startup_frame, text="开机自启动 | Auto-start on boot", variable=self.auto_start, command=self._toggle_autostart).pack(anchor="w")
        
        ttk.Button(frame, text="💾 保存设置 | Save Settings", command=self._save_settings).pack(pady=10)
        
        config_frame = ttk.LabelFrame(frame, text="配置文件 | Config File", padding=10)
        config_frame.pack(fill="x")
        ttk.Label(config_frame, text=self.config_path).pack(anchor="w")
        ttk.Button(config_frame, text="📂 打开目录 | Open Folder", command=lambda: os.startfile(os.path.dirname(self.config_path))).pack(anchor="w", pady=5)

    def _check_autostart(self):
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run") as key:
                winreg.QueryValueEx(key, "FishRouter")
                return True
        except:
            return False

    def _toggle_autostart(self):
        try:
            import winreg
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            exe_path = os.path.abspath(sys.argv[0])
            if self.auto_start.get():
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
                    winreg.SetValueEx(key, "FishRouter", 0, winreg.REG_SZ, f'"{exe_path}"')
            else:
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
                        winreg.DeleteValue(key, "FishRouter")
                except FileNotFoundError:
                    pass
        except Exception as e:
            self._log(f"设置自启动失败 | Auto-start error: {e}")

    def _save_settings(self):
        self.config["server"]["port"] = int(self.port_entry.get())
        self.config["server"]["log_level"] = self.log_level.get()
        self.config["auth"]["enabled"] = self.auth_enabled.get()
        self.config["auth"]["api_keys"] = [k.strip() for k in self.api_keys_text.get("1.0", "end-1c").split("\n") if k.strip()]
        self._save_config()
        self._log("设置已保存 | Settings saved")
        messagebox.showinfo("成功 | Success", "设置已保存 | Settings saved")

    # ===== Update Tab =====
    def _setup_update_tab(self):
        frame = ttk.Frame(self.tab_update, padding=20)
        frame.pack(fill="both", expand=True)
        
        ttk.Label(frame, text="🔄 自动更新 | Auto Update", font=("Segoe UI", 14, "bold")).pack(pady=10)
        
        self.update_status = ttk.Label(frame, text="检查中... | Checking...", font=("Segoe UI", 10))
        self.update_status.pack(pady=10)
        
        self.update_info = scrolledtext.ScrolledText(frame, height=10, width=60, font=("Consolas", 9))
        self.update_info.pack(fill="both", expand=True, pady=10)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", pady=10)
        ttk.Button(btn_frame, text="🔍 检查更新 | Check", command=self._check_updates).pack(side="left", padx=5)
        self.update_btn = ttk.Button(btn_frame, text="⬇️ 下载更新 | Download", command=self._do_update, state="disabled")
        self.update_btn.pack(side="left", padx=5)
        
        self.progress_var = tk.StringVar(value="")
        ttk.Label(frame, textvariable=self.progress_var).pack(pady=5)
        
        self.root.after(500, self._check_updates)

    def _check_updates(self):
        def check():
            try:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                req = urllib.request.Request("https://api.github.com/repos/Aobing-code/fishrouter/releases/latest", headers={"Accept": "application/vnd.github.v3+json"})
                with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
                    release = json.loads(resp.read().decode())
                tag = release.get("tag_name", "")
                notes = release.get("body", "")
                self.root.after(0, lambda: self._show_update_info(tag, notes))
            except Exception as e:
                self.root.after(0, lambda: self.update_status.config(text=f"检查失败 | Check failed: {e}"))
        threading.Thread(target=check, daemon=True).start()

    def _show_update_info(self, tag, notes):
        self.update_info.delete("1.0", "end")
        self.update_info.insert("end", f"最新版本 | Latest: {tag}\n\n")
        self.update_info.insert("end", "更新日志 | Changelog:\n")
        self.update_info.insert("end", notes)
        self.update_status.config(text=f"🆕 最新版本 | Latest: {tag}", foreground="green")
        self.update_btn.config(state="normal")

    def _do_update(self):
        self.progress_var.set("正在下载... | Downloading...")
        self.update_btn.config(state="disabled")
        def download():
            try:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                req = urllib.request.Request("https://api.github.com/repos/Aobing-code/fishrouter/releases/latest", headers={"Accept": "application/vnd.github.v3+json"})
                with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
                    release = json.loads(resp.read().decode())
                download_url = None
                for asset in release.get("assets", []):
                    if asset.get("name", "").endswith(".exe"):
                        download_url = asset.get("browser_download_url")
                        break
                if not download_url:
                    self.root.after(0, lambda: self.progress_var.set("未找到安装包 | No installer found"))
                    self.root.after(0, lambda: self.update_btn.config(state="normal"))
                    return
                import tempfile
                temp_file = os.path.join(tempfile.gettempdir(), "FishRouter-Update.exe")
                def progress(block, bs, total):
                    pct = min(100, block * bs * 100 // total)
                    self.root.after(0, lambda: self.progress_var.set(f"下载中 | Downloading: {pct}%"))
                urllib.request.urlretrieve(download_url, temp_file, progress)
                self.root.after(0, lambda: subprocess.Popen([temp_file]))
                self.root.after(0, lambda: self.progress_var.set("安装程序已启动 | Installer launched"))
                self.root.after(0, self.root.destroy)
            except Exception as e:
                self.root.after(0, lambda: self.progress_var.set(f"更新失败 | Update failed: {e}"))
                self.root.after(0, lambda: self.update_btn.config(state="normal"))
        threading.Thread(target=download, daemon=True).start()

    # ===== Server Control =====
    def _log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        self.log_text.see("end")

    def start_server(self):
        if self.server_running:
            return
        self.port = int(self.port_entry.get())
        self.config["server"]["port"] = self.port
        self._save_config()
        self.start_btn.config(state="disabled")
        self.status_var.set("🔄 启动中... | Starting...")
        self._log("正在启动服务器... | Starting server...")
        
        def run_server():
            try:
                base_dir = os.path.dirname(os.path.abspath(__file__))
                server_exe = os.path.join(base_dir, "fishrouter-server.exe")
                if os.path.exists(server_exe):
                    cmd = [server_exe, "--port", str(self.port)]
                    env = os.environ.copy()
                    env["PYTHONIOENCODING"] = "utf-8"
                    self.server_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env, cwd=base_dir, creationflags=subprocess.CREATE_NO_WINDOW)
                    for line in self.server_process.stdout:
                        self.root.after(0, self._log, line.strip())
                    self.server_process.wait()
                else:
                    self._run_server_inline()
                    return
            except Exception as e:
                self.root.after(0, self._log, f"错误 | Error: {e}")
            finally:
                self.root.after(0, self._server_stopped)
        
        threading.Thread(target=run_server, daemon=True).start()
        self.server_running = True
        self.stop_btn.config(state="normal")
        self.status_var.set(f"🟢 运行中 | Running (:{self.port})")

    def _run_server_inline(self):
        def run():
            try:
                import uvicorn
                sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
                from app.main import app, config
                config.server.port = self.port
                self.root.after(0, self._log, "服务器已启动 | Server started")
                uvicorn.run(app, host="0.0.0.0", port=self.port, log_level="info")
            except Exception as e:
                self.root.after(0, self._log, f"错误 | Error: {e}")
            finally:
                self.root.after(0, self._server_stopped)
        threading.Thread(target=run, daemon=True).start()
        self.server_running = True
        self.stop_btn.config(state="normal")
        self.status_var.set(f"🟢 运行中 | Running (:{self.port})")

    def stop_server(self):
        if not self.server_running:
            return
        self._log("正在停止服务器... | Stopping server...")
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
            except:
                self.server_process.kill()
        self._server_stopped()

    def _server_stopped(self):
        self.server_running = False
        self.server_process = None
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_var.set("⏹ 已停止 | Stopped")
        self._log("服务器已停止 | Server stopped")

    def open_dashboard(self):
        webbrowser.open(f"http://localhost:{self.port}")

    def on_close(self):
        if self.server_running:
            if messagebox.askyesno("确认 | Confirm", "服务器正在运行，是否停止并退出？"):
                self.stop_server()
                self.root.destroy()
        else:
            self.root.destroy()

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()


if __name__ == "__main__":
    app = FishRouterApp()
    app.run()
