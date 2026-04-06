"""FishRouter Windows Launcher - WebView2 Container"""
import sys
import os
import subprocess
import threading
import time
import json
import signal
import requests
from pathlib import Path

try:
    import webview
except ImportError:
    print("Missing dependencies: pip install pywebview requests")
    sys.exit(1)

logger = print


class FishRouterLauncher:
    def __init__(self):
        self.server_process = None
        self.server_port = 8080
        self.base_dir = self._get_base_dir()
        self.config_path = os.path.join(self.base_dir, "config.json")
        self.config = self._load_config()

    def _get_base_dir(self):
        """确定基目录（打包后为 exe 所在目录）"""
        if getattr(sys, 'frozen', False):
            base = os.path.dirname(sys.executable)
        else:
            base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return base

    def _load_config(self):
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
                self.server_port = cfg.get("server", {}).get("port", 8080)
                return cfg
        except Exception as e:
            print(f"Config load error: {e}, using defaults")
            self.server_port = 8080
            return {"server": {"port": 8080}}

    def start_server(self):
        """后台启动 fishrouter-server.exe"""
        server_exe = os.path.join(self.base_dir, "fishrouter-server.exe")
        if not os.path.exists(server_exe):
            print(f"Server executable not found: {server_exe}")
            return False

        port = self.server_port
        # Windows: hide console window
        creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0

        self.server_process = subprocess.Popen(
            [server_exe, "--port", str(port)],
            cwd=self.base_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            creationflags=creation_flags
        )

        # 启动日志线程（可选输出到文件）
        def log_thread():
            for line in self.server_process.stdout:
                print(f"[SERVER] {line.strip()}")
        threading.Thread(target=log_thread, daemon=True).start()

        # 等待服务器就绪
        for _ in range(30):
            try:
                resp = requests.get(f"http://localhost:{port}/api/session/check", timeout=0.5)
                if resp.status_code == 200:
                    print(f"Server started on port {port}")
                    return True
            except:
                time.sleep(0.5)
        print("Server failed to start")
        return False

    def run(self):
        """启动服务器并打开 Web 窗口"""
        if not self.start_server():
            logger("Failed to start server")
            sys.exit(1)

        # 打开 WebView2 窗口
        url = f"http://localhost:{self.server_port}"
        self.window = webview.create_window(
            "FishRouter",
            url,
            width=1200,
            height=800,
            resizable=True,
            fullscreen=False,
            text_select=True,
            background_color='#0a0a0f'
        )

        # 窗口关闭时清理
        def on_closed():
            logger("Window closed, stopping server...")
            self.stop_server()

        self.window.closed += on_closed

        # 启动 WebView 事件循环
        try:
            webview.start(debug=False, func=None, gui=None)
        except KeyboardInterrupt:
            logger("Interrupted, shutting down...")
        finally:
            self.stop_server()

    def stop_server(self):
        """停止服务器进程"""
        if self.server_process:
            try:
                self.server_process.terminate()
                try:
                    self.server_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.server_process.kill()
                    self.server_process.wait()
                logger("Server stopped")
            except Exception as e:
                logger(f"Error stopping server: {e}")
            finally:
                self.server_process = None


def main():
    launcher = FishRouterLauncher()
    launcher.run()


if __name__ == "__main__":
    main()
