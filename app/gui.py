"""FishRouter Windows GUI Launcher"""
import sys
import os
import subprocess
import threading
import webbrowser
import time
import signal
import ctypes

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
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 500) // 2
        y = (self.root.winfo_screenheight() - 400) // 2
        self.root.geometry(f"500x400+{x}+{y}")
        
        self.server_process = None
        self.server_running = False
        self.port = 8080
        self.config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
        
        # Check if running as admin
        self.is_admin = self._is_admin()
        
        self._setup_ui()
        self._load_config()
        
        # Auto-start if configured
        if self.auto_start.get():
            self.root.after(1000, self.start_server)

    def _is_admin(self):
        """Check if running with admin privileges"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def _setup_ui(self):
        """Setup the user interface"""
        # Title
        title_frame = tk.Frame(self.root, bg="#0f172a", height=60)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)
        
        tk.Label(title_frame, text="🐟 FishRouter", font=("Segoe UI", 20, "bold"), 
                bg="#0f172a", fg="#38bdf8").pack(expand=True)
        
        # Main content
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Status
        status_frame = tk.LabelFrame(main_frame, text="状态 | Status", padx=10, pady=10)
        status_frame.pack(fill="x", pady=(0, 10))
        
        self.status_var = tk.StringVar(value="⏹ 已停止 | Stopped")
        tk.Label(status_frame, textvariable=self.status_var, 
                font=("Segoe UI", 10), anchor="w").pack(fill="x")
        
        self.url_var = tk.StringVar(value=f"地址: http://localhost:{self.port}")
        tk.Label(status_frame, textvariable=self.url_var, 
                font=("Segoe UI", 9), fg="#64748b", anchor="w").pack(fill="x")
        
        # Settings
        settings_frame = tk.LabelFrame(main_frame, text="设置 | Settings", padx=10, pady=10)
        settings_frame.pack(fill="x", pady=(0, 10))
        
        # Port
        port_frame = tk.Frame(settings_frame)
        port_frame.pack(fill="x", pady=2)
        tk.Label(port_frame, text="端口 | Port:", width=15, anchor="w").pack(side="left")
        self.port_var = tk.StringVar(value="8080")
        tk.Entry(port_frame, textvariable=self.port_var, width=10).pack(side="left", padx=5)
        
        # Auto-start
        self.auto_start = tk.BooleanVar(value=False)
        auto_frame = tk.Frame(settings_frame)
        auto_frame.pack(fill="x", pady=2)
        tk.Checkbutton(auto_frame, text="开机自启动 | Auto-start on boot", 
                      variable=self.auto_start, command=self._toggle_autostart).pack(anchor="w")
        
        # Buttons
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=10)
        
        self.start_btn = tk.Button(btn_frame, text="▶ 启动 | Start", bg="#22c55e", fg="white",
                                   font=("Segoe UI", 10, "bold"), command=self.start_server,
                                   activebackground="#16a34a")
        self.start_btn.pack(side="left", fill="x", expand=True, padx=5)
        
        self.stop_btn = tk.Button(btn_frame, text="⏹ 停止 | Stop", bg="#ef4444", fg="white",
                                  font=("Segoe UI", 10, "bold"), command=self.stop_server,
                                  state="disabled", activebackground="#dc2626")
        self.stop_btn.pack(side="left", fill="x", expand=True, padx=5)
        
        tk.Button(btn_frame, text="🌐 打开面板 | Open Dashboard", bg="#38bdf8", fg="#0f172a",
                 font=("Segoe UI", 10, "bold"), command=self.open_dashboard,
                 activebackground="#7dd3fc").pack(side="left", fill="x", expand=True, padx=5)
        
        # Log
        log_frame = tk.LabelFrame(main_frame, text="日志 | Log", padx=5, pady=5)
        log_frame.pack(fill="both", expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, font=("Consolas", 9),
                                                   bg="#1e293b", fg="#e2e8f0",
                                                   insertbackground="white")
        self.log_text.pack(fill="both", expand=True)
        
        # Footer
        tk.Label(self.root, text="FishRouter v1.0 | MIT License", 
                font=("Segoe UI", 8), fg="#64748b").pack(pady=5)
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _load_config(self):
        """Load configuration"""
        try:
            import json
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                self.port_var.set(str(config.get("server", {}).get("port", 8080)))
        except:
            pass

    def _toggle_autostart(self):
        """Toggle auto-start on boot"""
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
        
        self.port = int(self.port_var.get())
        self.start_btn.config(state="disabled")
        self.status_var.set("🔄 启动中... | Starting...")
        self._log("正在启动服务器... | Starting server...")
        
        def run_server():
            try:
                # Find the server executable or script
                base_dir = os.path.dirname(os.path.abspath(__file__))
                
                # Check if running from PyInstaller bundle
                if getattr(sys, 'frozen', False):
                    # Running as compiled exe
                    if hasattr(sys, '_MEIPASS'):
                        # Check if there's a separate server exe
                        server_exe = os.path.join(base_dir, "fishrouter-server.exe")
                        if os.path.exists(server_exe):
                            cmd = [server_exe, "--port", str(self.port)]
                        else:
                            # Single exe mode - run server in thread
                            self._run_server_inline()
                            return
                    else:
                        cmd = [sys.executable, "-m", "app.main", "--port", str(self.port)]
                else:
                    # Running from source
                    cmd = [sys.executable, "-m", "app.main", "--port", str(self.port)]
                
                # Set environment
                env = os.environ.copy()
                env["PYTHONIOENCODING"] = "utf-8"
                
                self.server_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    env=env,
                    cwd=base_dir,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
                )
                
                # Read output
                for line in self.server_process.stdout:
                    self.root.after(0, self._log, line.strip())
                
                self.server_process.wait()
                
            except Exception as e:
                self.root.after(0, self._log, f"错误 | Error: {e}")
            finally:
                self.root.after(0, self._server_stopped)
        
        threading.Thread(target=run_server, daemon=True).start()
        self.server_running = True
        self.stop_btn.config(state="normal")
        self.status_var.set(f"🟢 运行中 | Running (:{self.port})")
        self._log(f"服务器已启动 | Server started on port {self.port}")

    def _run_server_inline(self):
        """Run server inline (for single exe mode)"""
        def run():
            try:
                import uvicorn
                import asyncio
                
                # Import the app
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
        """Stop the FishRouter server"""
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
        self.root.mainloop()


if __name__ == "__main__":
    app = FishRouterApp()
    app.run()
