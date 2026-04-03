"""FishRouter Windows GUI - Full Configuration Manager"""
import sys
import os
import subprocess
import threading
import webbrowser
import time
import signal
import ctypes
import json

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, scrolledtext, filedialog
except ImportError:
    print("Tkinter not available")
    sys.exit(1)


class FishRouterApp:
    """FishRouter Windows GUI Application"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("FishRouter - AI Model Router")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 800) // 2
        y = (self.root.winfo_screenheight() - 600) // 2
        self.root.geometry(f"800x600+{x}+{y}")
        
        self.server_process = None
        self.server_running = False
        self.port = 8080
        self.config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
        self.config = {}
        
        # Load config
        self._load_config_file()
        
        self._setup_ui()
        
        # Auto-start if configured
        if self.auto_start.get():
            self.root.after(1000, self.start_server)

    def _load_config_file(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                self.port = self.config.get("server", {}).get("port", 8080)
            else:
                self._create_default_config()
        except:
            self._create_default_config()

    def _create_default_config(self):
        """Create default configuration"""
        self.config = {
            "server": {"host": "0.0.0.0", "port": 8080, "log_level": "info"},
            "backends": [],
            "routes": [{"name": "default", "models": ["*"], "strategy": "latency", "failover": True, "health_check_interval": 30, "fallback_order": [], "fallback_rules": []}],
            "auth": {"enabled": False, "api_keys": ["sk-fishrouter"]}
        }
        self._save_config()

    def _save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self._log(f"保存配置失败 | Save config error: {e}")

    def _setup_ui(self):
        """Setup the user interface"""
        # Notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Tab 1: Dashboard
        self.tab_dashboard = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_dashboard, text="🏠 控制台 | Dashboard")
        self._setup_dashboard()
        
        # Tab 2: Backends
        self.tab_backends = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_backends, text="🔗 后端 | Backends")
        self._setup_backends_tab()
        
        # Tab 3: Routes
        self.tab_routes = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_routes, text="🛤️ 路由 | Routes")
        self._setup_routes_tab()
        
        # Tab 4: Settings
        self.tab_settings = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_settings, text="⚙️ 设置 | Settings")
        self._setup_settings_tab()
        
        # Tab 5: Update
        self.tab_update = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_update, text="🔄 更新 | Update")
        self._setup_update_tab()

    def _setup_dashboard(self):
        """Setup dashboard tab"""
        # Status frame
        status_frame = ttk.LabelFrame(self.tab_dashboard, text="状态 | Status", padding=10)
        status_frame.pack(fill="x", padx=10, pady=10)
        
        self.status_var = tk.StringVar(value="⏹ 已停止 | Stopped")
        ttk.Label(status_frame, textvariable=self.status_var, font=("Segoe UI", 11)).pack(anchor="w")
        
        self.url_var = tk.StringVar(value=f"地址 | URL: http://localhost:{self.port}")
        ttk.Label(status_frame, textvariable=self.url_var, foreground="#666").pack(anchor="w")
        
        # Buttons
        btn_frame = ttk.Frame(self.tab_dashboard)
        btn_frame.pack(fill="x", padx=10, pady=5)
        
        self.start_btn = ttk.Button(btn_frame, text="▶ 启动 | Start", command=self.start_server)
        self.start_btn.pack(side="left", fill="x", expand=True, padx=5)
        
        self.stop_btn = ttk.Button(btn_frame, text="⏹ 停止 | Stop", command=self.stop_server, state="disabled")
        self.stop_btn.pack(side="left", fill="x", expand=True, padx=5)
        
        ttk.Button(btn_frame, text="🌐 打开面板 | Open Dashboard", command=self.open_dashboard).pack(side="left", fill="x", expand=True, padx=5)
        
        # Log
        log_frame = ttk.LabelFrame(self.tab_dashboard, text="日志 | Log", padding=5)
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, font=("Consolas", 9), bg="#1e1e1e", fg="#d4d4d4", insertbackground="white")
        self.log_text.pack(fill="both", expand=True)

    def _setup_backends_tab(self):
        """Setup backends configuration tab"""
        frame = ttk.Frame(self.tab_backends, padding=10)
        frame.pack(fill="both", expand=True)
        
        # Backend list
        list_frame = ttk.LabelFrame(frame, text="后端列表 | Backend List", padding=5)
        list_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Treeview for backends
        columns = ("name", "type", "url", "enabled")
        self.backend_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        self.backend_tree.heading("name", text="名称 | Name")
        self.backend_tree.heading("type", text="类型 | Type")
        self.backend_tree.heading("url", text="地址 | URL")
        self.backend_tree.heading("enabled", text="状态 | Status")
        self.backend_tree.column("name", width=120)
        self.backend_tree.column("type", width=80)
        self.backend_tree.column("url", width=250)
        self.backend_tree.column("enabled", width=60)
        self.backend_tree.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.backend_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.backend_tree.configure(yscrollcommand=scrollbar.set)
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x")
        
        ttk.Button(btn_frame, text="➕ 添加 | Add", command=self._add_backend).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="✏️ 编辑 | Edit", command=self._edit_backend).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🗑️ 删除 | Delete", command=self._delete_backend).pack(side="left", padx=5)
        
        self._refresh_backend_list()

    def _setup_routes_tab(self):
        """Setup routes configuration tab"""
        frame = ttk.Frame(self.tab_routes, padding=10)
        frame.pack(fill="both", expand=True)
        
        info_frame = ttk.LabelFrame(frame, text="路由配置 | Route Configuration", padding=10)
        info_frame.pack(fill="both", expand=True)
        
        ttk.Label(info_frame, text="路由策略 | Strategy:").grid(row=0, column=0, sticky="w", pady=5)
        self.route_strategy = ttk.Combobox(info_frame, values=["latency", "round_robin", "random", "weighted", "priority", "custom"], width=20)
        self.route_strategy.grid(row=0, column=1, sticky="w", padx=5)
        
        ttk.Label(info_frame, text="回退顺序 | Fallback Order (逗号分隔):").grid(row=1, column=0, sticky="w", pady=5)
        self.fallback_order = ttk.Entry(info_frame, width=50)
        self.fallback_order.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Button(info_frame, text="💾 保存路由 | Save Route", command=self._save_route).grid(row=2, column=0, columnspan=2, pady=10)
        
        self._load_route_config()

    def _setup_settings_tab(self):
        """Setup settings tab"""
        frame = ttk.Frame(self.tab_settings, padding=10)
        frame.pack(fill="both", expand=True)
        
        # Server settings
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
        
        # Auth settings
        auth_frame = ttk.LabelFrame(frame, text="认证 | Authentication", padding=10)
        auth_frame.pack(fill="x", pady=(0, 10))
        
        self.auth_enabled = tk.BooleanVar(value=self.config.get("auth", {}).get("enabled", False))
        ttk.Checkbutton(auth_frame, text="启用 API Key 认证 | Enable API Key Auth", variable=self.auth_enabled).pack(anchor="w", pady=5)
        
        ttk.Label(auth_frame, text="API Keys (每行一个 | One per line):").pack(anchor="w")
        self.api_keys_text = scrolledtext.ScrolledText(auth_frame, height=5, width=50)
        self.api_keys_text.insert("1.0", "\n".join(self.config.get("auth", {}).get("api_keys", [])))
        self.api_keys_text.pack(fill="x", pady=5)
        
        # Auto-start
        startup_frame = ttk.LabelFrame(frame, text="启动 | Startup", padding=10)
        startup_frame.pack(fill="x", pady=(0, 10))
        
        self.auto_start = tk.BooleanVar(value=self._check_autostart())
        ttk.Checkbutton(startup_frame, text="开机自启动 | Auto-start on boot", variable=self.auto_start, command=self._toggle_autostart).pack(anchor="w")
        
        # Save button
        ttk.Button(frame, text="💾 保存设置 | Save Settings", command=self._save_settings).pack(pady=10)
        
        # Config file
        config_frame = ttk.LabelFrame(frame, text="配置文件 | Config File", padding=10)
        config_frame.pack(fill="x")
        
        ttk.Label(config_frame, text=self.config_path).pack(anchor="w")
        ttk.Button(config_frame, text="📂 打开配置文件 | Open Config File", command=lambda: os.startfile(self.config_path) if os.path.exists(self.config_path) else None).pack(anchor="w", pady=5)
        ttk.Button(config_frame, text="📝 编辑配置文件 | Edit Config File", command=self._edit_config_file).pack(anchor="w")

    def _setup_update_tab(self):
        """Setup update tab"""
        frame = ttk.Frame(self.tab_update, padding=20)
        frame.pack(fill="both", expand=True)
        
        ttk.Label(frame, text="🔄 自动更新 | Auto Update", font=("Segoe UI", 14, "bold")).pack(pady=10)
        
        self.update_status = ttk.Label(frame, text="检查中... | Checking...", font=("Segoe UI", 10))
        self.update_status.pack(pady=10)
        
        self.update_info = scrolledtext.ScrolledText(frame, height=10, width=60, font=("Consolas", 9))
        self.update_info.pack(fill="both", expand=True, pady=10)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", pady=10)
        
        ttk.Button(btn_frame, text="🔍 检查更新 | Check for Updates", command=self._check_updates).pack(side="left", padx=5)
        self.update_btn = ttk.Button(btn_frame, text="⬇️ 下载并更新 | Download & Update", command=self._do_update, state="disabled")
        self.update_btn.pack(side="left", padx=5)
        
        self.progress_var = tk.StringVar(value="")
        ttk.Label(frame, textvariable=self.progress_var).pack(pady=5)
        
        # Auto check on tab switch
        self.root.after(500, self._check_updates)

    def _check_autostart(self):
        """Check if auto-start is enabled"""
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run") as key:
                winreg.QueryValueEx(key, "FishRouter")
                return True
        except:
            return False

    def _toggle_autostart(self):
        """Toggle auto-start"""
        try:
            import winreg
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            exe_path = os.path.abspath(sys.argv[0])
            
            if self.auto_start.get():
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
                    winreg.SetValueEx(key, "FishRouter", 0, winreg.REG_SZ, f'"{exe_path}"')
                self._log("已添加开机自启动 | Auto-start enabled")
            else:
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
                        winreg.DeleteValue(key, "FishRouter")
                    self._log("已移除开机自启动 | Auto-start disabled")
                except FileNotFoundError:
                    pass
        except Exception as e:
            self._log(f"设置自启动失败 | Auto-start error: {e}")

    def _log(self, message):
        """Add message to log"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        self.log_text.see("end")

    def start_server(self):
        """Start the FishRouter server"""
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
                
                # Check for separate server exe
                server_exe = os.path.join(base_dir, "fishrouter-server.exe")
                if os.path.exists(server_exe):
                    cmd = [server_exe, "--port", str(self.port)]
                    env = os.environ.copy()
                    self.server_process = subprocess.Popen(
                        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                        text=True, env=env, cwd=base_dir,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    for line in self.server_process.stdout:
                        self.root.after(0, self._log, line.strip())
                    self.server_process.wait()
                else:
                    # Run inline
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
        self.url_var.set(f"地址 | URL: http://localhost:{self.port}")
        self._log(f"服务器已启动 | Server started on port {self.port}")

    def _run_server_inline(self):
        """Run server inline"""
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
        """Stop the server"""
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
        """Handle server stopped"""
        self.server_running = False
        self.server_process = None
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_var.set("⏹ 已停止 | Stopped")
        self._log("服务器已停止 | Server stopped")

    def open_dashboard(self):
        """Open dashboard in browser"""
        webbrowser.open(f"http://localhost:{self.port}")

    # Backend management
    def _refresh_backend_list(self):
        """Refresh backend list in treeview"""
        for item in self.backend_tree.get_children():
            self.backend_tree.delete(item)
        
        for b in self.config.get("backends", []):
            status = "✅" if b.get("enabled", True) else "❌"
            self.backend_tree.insert("", "end", values=(
                b.get("name", ""),
                b.get("type", ""),
                b.get("url", ""),
                status
            ))

    def _add_backend(self):
        """Add new backend"""
        self._open_backend_editor()

    def _edit_backend(self):
        """Edit selected backend"""
        selection = self.backend_tree.selection()
        if not selection:
            messagebox.showwarning("警告 | Warning", "请选择一个后端 | Please select a backend")
            return
        
        item = self.backend_tree.item(selection[0])
        name = item["values"][0]
        self._open_backend_editor(name)

    def _delete_backend(self):
        """Delete selected backend"""
        selection = self.backend_tree.selection()
        if not selection:
            messagebox.showwarning("警告 | Warning", "请选择一个后端 | Please select a backend")
            return
        
        item = self.backend_tree.item(selection[0])
        name = item["values"][0]
        
        if messagebox.askyesno("确认 | Confirm", f"确定删除后端 {name}？"):
            self.config["backends"] = [b for b in self.config.get("backends", []) if b.get("name") != name]
            self._save_config()
            self._refresh_backend_list()
            self._log(f"已删除后端 | Deleted backend: {name}")

    def _open_backend_editor(self, name=None):
        """Open backend editor dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("编辑后端 | Edit Backend" if name else "添加后端 | Add Backend")
        dialog.geometry("500x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Find existing backend data
        backend = {}
        if name:
            for b in self.config.get("backends", []):
                if b.get("name") == name:
                    backend = b
                    break
        
        fields = [
            ("名称 | Name", "name", backend.get("name", "")),
            ("类型 | Type", "type", backend.get("type", "openai")),
            ("地址 | URL", "url", backend.get("url", "")),
            ("API Keys (每行一个)", "api_keys", "\n".join(backend.get("api_keys", []))),
            ("权重 | Weight", "weight", str(backend.get("weight", 10))),
            ("优先级 | Priority", "priority", str(backend.get("priority", 1))),
            ("超时 | Timeout (秒)", "timeout", str(backend.get("timeout", 60))),
        ]
        
        entries = {}
        for i, (label, key, default) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, sticky="w", padx=10, pady=5)
            if key == "api_keys":
                entry = scrolledtext.ScrolledText(dialog, height=4, width=40)
                entry.insert("1.0", default)
                entry.grid(row=i, column=1, padx=5, pady=5)
                entries[key] = entry
            else:
                entry = ttk.Entry(dialog, width=40)
                entry.insert(0, default)
                entry.grid(row=i, column=1, padx=5, pady=5)
                entries[key] = entry
        
        def save():
            api_keys = entries["api_keys"].get("1.0", "end-1c").strip().split("\n")
            api_keys = [k.strip() for k in api_keys if k.strip()]
            
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
                "models": backend.get("models", [{"id": "*", "name": "*", "context_length": 4096, "enabled": True}])
            }
            
            if name:
                # Update existing
                for i, b in enumerate(self.config.get("backends", [])):
                    if b.get("name") == name:
                        self.config["backends"][i] = backend_data
                        break
            else:
                # Add new
                self.config.setdefault("backends", []).append(backend_data)
            
            self._save_config()
            self._refresh_backend_list()
            self._log(f"已保存后端 | Saved backend: {backend_data['name']}")
            dialog.destroy()
        
        ttk.Button(dialog, text="💾 保存 | Save", command=save).grid(row=len(fields), column=0, columnspan=2, pady=20)

    # Route management
    def _load_route_config(self):
        """Load route configuration"""
        route = self.config.get("routes", [{}])[0] if self.config.get("routes") else {}
        self.route_strategy.set(route.get("strategy", "latency"))
        self.fallback_order.delete(0, "end")
        self.fallback_order.insert(0, ", ".join(route.get("fallback_order", [])))

    def _save_route(self):
        """Save route configuration"""
        fallback = [s.strip() for s in self.fallback_order.get().split(",") if s.strip()]
        
        if self.config.get("routes"):
            self.config["routes"][0]["strategy"] = self.route_strategy.get()
            self.config["routes"][0]["fallback_order"] = fallback
        else:
            self.config["routes"] = [{
                "name": "default",
                "models": ["*"],
                "strategy": self.route_strategy.get(),
                "failover": True,
                "health_check_interval": 30,
                "fallback_order": fallback,
                "fallback_rules": []
            }]
        
        self._save_config()
        self._log("路由配置已保存 | Route config saved")
        messagebox.showinfo("成功 | Success", "路由配置已保存 | Route config saved")

    # Settings
    def _save_settings(self):
        """Save settings"""
        self.config["server"]["port"] = int(self.port_entry.get())
        self.config["server"]["log_level"] = self.log_level.get()
        self.config["auth"]["enabled"] = self.auth_enabled.get()
        self.config["auth"]["api_keys"] = [k.strip() for k in self.api_keys_text.get("1.0", "end-1c").split("\n") if k.strip()]
        
        self._save_config()
        self._log("设置已保存 | Settings saved")
        messagebox.showinfo("成功 | Success", "设置已保存 | Settings saved")

    def _edit_config_file(self):
        """Edit config file in default editor"""
        if os.path.exists(self.config_path):
            os.startfile(self.config_path)

    # Update
    def _check_updates(self):
        """Check for updates"""
        def check():
            try:
                import urllib.request
                import ssl
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                
                req = urllib.request.Request(
                    "https://api.github.com/repos/Aobing-code/fishrouter/releases/latest",
                    headers={"Accept": "application/vnd.github.v3+json"}
                )
                with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
                    release = json.loads(resp.read().decode())
                
                tag = release.get("tag_name", "")
                notes = release.get("body", "")
                
                self.root.after(0, lambda: self._show_update_info(tag, notes))
            except Exception as e:
                self.root.after(0, lambda: self.update_status.config(text=f"检查失败 | Check failed: {e}"))

        threading.Thread(target=check, daemon=True).start()

    def _show_update_info(self, tag, notes):
        """Show update information"""
        self.update_info.delete("1.0", "end")
        self.update_info.insert("end", f"最新版本 | Latest: {tag}\n\n")
        self.update_info.insert("end", "更新日志 | Changelog:\n")
        self.update_info.insert("end", notes)
        
        # Check if newer
        try:
            current = int(self.config.get("_version", "0").replace("v0.", "") or "0")
            latest = int(tag.split("-")[0].replace("v0.", ""))
            if latest > current:
                self.update_status.config(text=f"🆕 有新版本可用 | Update available: {tag}", foreground="green")
                self.update_btn.config(state="normal")
            else:
                self.update_status.config(text="✅ 已是最新版本 | Up to date", foreground="green")
        except:
            self.update_status.config(text=f"🆕 最新版本 | Latest: {tag}", foreground="green")
            self.update_btn.config(state="normal")

    def _do_update(self):
        """Download and install update"""
        self.progress_var.set("正在下载... | Downloading...")
        self.update_btn.config(state="disabled")
        
        def download():
            try:
                import urllib.request
                import ssl
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                
                req = urllib.request.Request(
                    "https://api.github.com/repos/Aobing-code/fishrouter/releases/latest",
                    headers={"Accept": "application/vnd.github.v3+json"}
                )
                with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
                    release = json.loads(resp.read().decode())
                
                # Find Windows installer
                download_url = None
                for asset in release.get("assets", []):
                    if asset.get("name", "").endswith(".exe"):
                        download_url = asset.get("browser_download_url")
                        break
                
                if not download_url:
                    self.root.after(0, lambda: self.progress_var.set("未找到 Windows 安装包 | No Windows installer found"))
                    self.root.after(0, lambda: self.update_btn.config(state="normal"))
                    return
                
                # Download
                import tempfile
                temp_file = os.path.join(tempfile.gettempdir(), "FishRouter-Update.exe")
                
                def progress(block, bs, total):
                    pct = min(100, block * bs * 100 // total)
                    self.root.after(0, lambda: self.progress_var.set(f"下载中 | Downloading: {pct}%"))
                
                urllib.request.urlretrieve(download_url, temp_file, progress)
                
                # Run installer
                self.root.after(0, lambda: subprocess.Popen([temp_file]))
                self.root.after(0, lambda: self.progress_var.set("安装程序已启动 | Installer launched"))
                self.root.after(0, self.root.destroy)
                
            except Exception as e:
                self.root.after(0, lambda: self.progress_var.set(f"更新失败 | Update failed: {e}"))
                self.root.after(0, lambda: self.update_btn.config(state="normal"))
        
        threading.Thread(target=download, daemon=True).start()

    def on_close(self):
        """Handle window close"""
        if self.server_running:
            if messagebox.askyesno("确认 | Confirm", "服务器正在运行，是否停止并退出？\nServer is running. Stop and exit?"):
                self.stop_server()
                self.root.destroy()
        else:
            self.root.destroy()

    def run(self):
        """Run the application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()


if __name__ == "__main__":
    app = FishRouterApp()
    app.run()
