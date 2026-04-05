"""FishRouter Cyberpunk Stylesheet"""
import os

class Colors:
    BG_PRIMARY = "#0a0a0f"
    BG_SECONDARY = "rgba(20, 20, 30, 0.6)"
    BG_TERTIARY = "rgba(30, 30, 50, 0.5)"
    BG_HOVER = "rgba(40, 40, 70, 0.7)"
    ACCENT = "#00eeff"
    ACCENT_HOVER = "#00ccff"
    ACCENT_GLOW = "rgba(0, 238, 255, 0.15)"
    SUCCESS = "#00ff88"
    WARNING = "#ffaa00"
    ERROR = "#ff3344"
    PURPLE = "#aa88ff"
    TEXT_PRIMARY = "#f0f4ff"
    TEXT_SECONDARY = "#8892b0"
    TEXT_MUTED = "#5a6a8a"
    BORDER = "rgba(100, 120, 160, 0.2)"
    TABLE_ALT = "rgba(15, 25, 45, 0.5)"
    GLASS_BLUR = "10px"


def load_stylesheet() -> str:
    """从 cyberpunk.qss 文件加载样式表"""
    try:
        # 从 app 目录向上找项目根目录
        base_dir = os.path.dirname(os.path.abspath(__file__))
        qss_path = os.path.join(base_dir, "..", "cyberpunk.qss")
        if not os.path.exists(qss_path):
            # 回退到当前工作目录
            qss_path = os.path.join(os.getcwd(), "cyberpunk.qss")
        
        if os.path.exists(qss_path):
            with open(qss_path, 'r', encoding='utf-8') as f:
                qss = f.read()
            # 去掉注释行
            lines = []
            for line in qss.split('\n'):
                stripped = line.strip()
                if not stripped.startswith('#') and stripped != '':
                    lines.append(line)
            clean_qss = '\n'.join(lines)
            # 用 Colors 的属性格式化
            return clean_qss % Colors.__dict__
        else:
            print(f"Warning: QSS file not found: {qss_path}")
            return ""
    except Exception as e:
        print(f"Error loading stylesheet: {e}")
        return ""
