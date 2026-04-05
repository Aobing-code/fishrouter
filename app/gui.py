"""FishRouter Windows GUI - Modern PySide6 Implementation"""
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
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
        QPushButton, QLabel, QLineEdit, QComboBox, QTextEdit, QScrollArea,
        QGroupBox, QFormLayout, QFrame, QSystemTrayIcon, QMenu,
        QMessageBox, QFileDialog, QCheckBox, QSplitter, QDialog,
        QGridLayout, QListWidget, QListWidgetItem, QAbstractItemView,
        QSizePolicy
    )
    from PySide6.QtCore import (
        Qt, QPropertyAnimation, QEasingCurve, QTimer, Signal, QThread,
        QPoint, QRect, QEvent, QSize, QParallelAnimationGroup
    )
    from PySide6.QtGui import (
        QFont, QIcon, QColor, QPalette, QCursor, QMouseEvent,
        QAction, QLinearGradient, QPainter, QPixmap, QBrush
    )
except ImportError:
    try:
        from PyQt5.QtWidgets import (
            QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
            QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
            QPushButton, QLabel, QLineEdit, QComboBox, QTextEdit, QScrollArea,
            QGroupBox, QFormLayout, QFrame, QSystemTrayIcon, QMenu,
            QMessageBox, QFileDialog, QCheckBox, QSplitter, QDialog,
            QGridLayout, QListWidget, QListWidgetItem, QAbstractItemView,
            QSizePolicy
        )
        from PyQt5.QtCore import (
            Qt, QPropertyAnimation, QEasingCurve, QTimer, pyqtSignal as Signal, QThread,
            QPoint, QRect, QEvent, QSize, QParallelAnimationGroup
        )
        from PyQt5.QtGui import (
            QFont, QIcon, QColor, QPalette, QCursor, QMouseEvent,
            QAction, QLinearGradient, QPainter, QPixmap, QBrush
        )
    except ImportError:
        print("PySide6 or PyQt5 not available. Please install: pip install PySide6")
        sys.exit(1)


class Colors:
    BG_PRIMARY = "#0f172a"
    BG_SECONDARY = "#1e293b"
    BG_TERTIARY = "#334155"
    BG_HOVER = "#475569"
    ACCENT = "#38bdf8"
    ACCENT_HOVER = "#7dd3fc"
    SUCCESS = "#22c55e"
    WARNING = "#f59e0b"
    ERROR = "#ef4444"
    PURPLE = "#a78bfa"
    TEXT_PRIMARY = "#f1f5f9"
    TEXT_SECONDARY = "#94a3b8"
    TEXT_MUTED = "#64748b"
    BORDER = "#334155"
    TABLE_ALT = "#1a2332"


QSS = """
QWidget {
    background-color: %(bg_primary)s;
    color: %(text_primary)s;
    font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
    font-size: 13px;
}

QMainWindow {
    background-color: %(bg_primary)s;
}

#TitleBar {
    background-color: %(bg_secondary)s;
    border-bottom: 1px solid %(border)s;
}
#TitleBar QLabel {
    color: %(text_primary)s;
    font-size: 14px;
    font-weight: bold;
}
#TitleButton {
    background: transparent;
    border: none;
    color: %(text_secondary)s;
    font-size: 16px;
    padding: 4px 12px;
    border-radius: 4px;
}
#TitleButton:hover {
    background-color: %(bg_tertiary)s;
    color: %(text_primary)s;
}
#CloseButton:hover {
    background-color: %(error)s;
    color: white;
}

QTabWidget::pane {
    border: 1px solid %(border)s;
    border-radius: 8px;
    background-color: %(bg_primary)s;
    top: -1px;
}
QTabBar::tab {
    background-color: %(bg_secondary)s;
    color: %(text_secondary)s;
    padding: 10px 20px;
    margin-right: 2px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    border: 1px solid %(border)s;
    border-bottom: none;
    font-size: 13px;
    min-width: 120px;
}
QTabBar::tab:selected {
    background-color: %(bg_primary)s;
    color: %(accent)s;
    border-bottom: 2px solid %(accent)s;
    font-weight: bold;
}
QTabBar::tab:hover:!selected {
    background-color: %(bg_tertiary)s;
    color: %(text_primary)s;
}

QPushButton {
    background-color: %(bg_tertiary)s;
    color: %(text_primary)s;
    border: 1px solid %(border)s;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 500;
    min-height: 20px;
}
QPushButton:hover {
    background-color: %(bg_hover)s;
    border-color: %(accent)s;
    color: %(accent)s;
}
QPushButton:pressed {
    background-color: %(bg_secondary)s;
    border-color: %(accent)s;
}
QPushButton:disabled {
    background-color: %(bg_secondary)s;
    color: %(text_muted)s;
    border-color: %(border)s;
}

#AccentButton {
    background-color: %(accent)s;
    color: %(bg_primary)s;
    border: 1px solid %(accent)s;
    font-weight: bold;
}
#AccentButton:hover {
    background-color: %(accent_hover)s;
    color: %(bg_primary)s;
}
#AccentButton:pressed {
    background-color: %(accent)s;
}

#SuccessButton {
    background-color: %(success)s;
    color: white;
    border: 1px solid %(success)s;
}
#SuccessButton:hover {
    background-color: #16a34a;
}

#DangerButton {
    background-color: %(error)s;
    color: white;
    border: 1px solid %(error)s;
}
#DangerButton:hover {
    background-color: #dc2626;
}

QGroupBox {
    background-color: %(bg_secondary)s;
    border: 1px solid %(border)s;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 16px;
    font-weight: bold;
    color: %(text_primary)s;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: %(accent)s;
    font-size: 13px;
}

QTableWidget {
    background-color: %(bg_primary)s;
    alternate-background-color: %(table_alt)s;
    gridline-color: %(border)s;
    border: 1px solid %(border)s;
    border-radius: 6px;
    selection-background-color: %(accent)s;
    selection-color: %(bg_primary)s;
}
QTableWidget::item {
    padding: 6px;
    border-bottom: 1px solid %(border)s;
}
QTableWidget::item:hover {
    background-color: %(bg_tertiary)s;
}
QTableWidget::item:selected {
    background-color: %(accent)s;
    color: %(bg_primary)s;
}
QHeaderView::section {
    background-color: %(bg_secondary)s;
    color: %(text_secondary)s;
    padding: 8px;
    border: none;
    border-bottom: 2px solid %(border)s;
    border-right: 1px solid %(border)s;
    font-weight: bold;
    font-size: 12px;
}
QHeaderView::section:hover {
    background-color: %(bg_tertiary)s;
    color: %(text_primary)s;
}

QListWidget {
    background-color: %(bg_primary)s;
    border: 1px solid %(border)s;
    border-radius: 6px;
    padding: 4px;
}
QListWidget::item {
    padding: 6px 8px;
    border-radius: 4px;
    margin: 1px 0;
}
QListWidget::item:hover {
    background-color: %(bg_tertiary)s;
}
QListWidget::item:selected {
    background-color: %(accent)s;
    color: %(bg_primary)s;
}

QLineEdit, QComboBox, QTextEdit, QPlainTextEdit {
    background-color: %(bg_primary)s;
    color: %(text_primary)s;
    border: 1px solid %(border)s;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 13px;
}
QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
    border-color: %(accent)s;
}
QLineEdit:hover, QComboBox:hover, QTextEdit:hover {
    border-color: %(bg_hover)s;
}

QComboBox {
    min-height: 24px;
}
QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}
QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid %(text_secondary)s;
    margin-right: 8px;
}
QComboBox QAbstractItemView {
    background-color: %(bg_secondary)s;
    color: %(text_primary)s;
    border: 1px solid %(border)s;
    selection-background-color: %(accent)s;
    selection-color: %(bg_primary)s;
}

QScrollBar:vertical {
    background-color: %(bg_secondary)s;
    width: 10px;
    border-radius: 5px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background-color: %(bg_tertiary)s;
    border-radius: 5px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover {
    background-color: %(bg_hover)s;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar:horizontal {
    background-color: %(bg_secondary)s;
    height: 10px;
    border-radius: 5px;
}
QScrollBar::handle:horizontal {
    background-color: %(bg_tertiary)s;
    border-radius: 5px;
    min-width: 20px;
}
QScrollBar::handle:horizontal:hover {
    background-color: %(bg_hover)s;
}

QCheckBox {
    color: %(text_primary)s;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid %(border)s;
    background-color: %(bg_primary)s;
}
QCheckBox::indicator:checked {
    background-color: %(accent)s;
    border-color: %(accent)s;
}
QCheckBox::indicator:hover {
    border-color: %(accent)s;
}

QLabel {
    color: %(text_primary)s;
}

#StatCard {
    background-color: %(bg_secondary)s;
    border: 1px solid %(border)s;
    border-radius: 12px;
    padding: 12px;
}

QToolTip {
    background-color: %(bg_tertiary)s;
    color: %(text_primary)s;
    border: 1px solid %(border)s;
    border-radius: 4px;
    padding: 4px 8px;
}

QDialog {
    background-color: %(bg_primary)s;
}

QMenu {
    background-color: %(bg_secondary)s;
    border: 1px solid %(border)s;
    border-radius: 8px;
    padding: 4px;
}
QMenu::item {
    padding: 8px 24px;
    border-radius: 4px;
}
QMenu::item:selected {
    background-color: %(bg_tertiary)s;
    color: %(accent)s;
}
QMenu::separator {
    height: 1px;
    background-color: %(border)s;
    margin: 4px 8px;
}
""" % {
    "bg_primary": Colors.BG_PRIMARY,
    "bg_secondary": Colors.BG_SECONDARY,
    "bg_tertiary": Colors.BG_TERTIARY,
    "bg_hover": Colors.BG_HOVER,
    "accent": Colors.ACCENT,
    "accent_hover": Colors.ACCENT_HOVER,
    "success": Colors.SUCCESS,
    "warning": Colors.WARNING,
    "error": Colors.ERROR,
    "purple": Colors.PURPLE,
    "text_primary": Colors.TEXT_PRIMARY,
    "text_secondary": Colors.TEXT_SECONDARY,
    "text_muted": Colors.TEXT_MUTED,
    "border": Colors.BORDER,
    "table_alt": Colors.TABLE_ALT,
}


class TitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TitleBar")
        self.parent_window = parent
        self.drag_pos = None
        self.setFixedHeight(40)
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 8, 0)
        layout.setSpacing(8)

        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "icon.ico")
        self.icon_label = QLabel()
        if os.path.exists(icon_path):
            self.icon_label.setPixmap(QIcon(icon_path).pixmap(20, 20))
        else:
            self.icon_label.setText("🐟")
        self.icon_label.setFixedSize(20, 20)
        layout.addWidget(self.icon_label)

        self.title_label = QLabel("FishRouter - AI Model Router")
        self.title_label.setStyleSheet("color: #f1f5f9; font-weight: bold; font-size: 14px;")
        layout.addWidget(self.title_label)

        layout.addStretch()

        self.min_btn = QPushButton("─")
        self.min_btn.setObjectName("TitleButton")
        self.min_btn.setFixedSize(36, 28)
        self.min_btn.clicked.connect(self.parent_window.showMinimized)
        layout.addWidget(self.min_btn)

        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("CloseButton")
        self.close_btn.setFixedSize(36, 28)
        self.close_btn.clicked.connect(self.parent_window.close)
        layout.addWidget(self.close_btn)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.parent_window.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_pos is not None and event.buttons() == Qt.LeftButton:
            self.parent_window.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()


class StatCard(QFrame):
    def __init__(self, title, value="0", color=Colors.ACCENT, parent=None):
        super().__init__(parent)
        self.setObjectName("StatCard")
        self.value_color = color
        self._setup_ui(title, value)

    def _setup_ui(self, title, value):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: #94a3b8; font-size: 12px;")
        layout.addWidget(self.title_label)

        self.value_label = QLabel(str(value))
        self.value_label.setStyleSheet(f"color: {self.value_color}; font-size: 24px; font-weight: bold;")
        layout.addWidget(self.value_label)

    def set_value(self, value):
        self.value_label.setText(str(value))


class AnimatedButton(QPushButton):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)

    def enterEvent(self, event):
        super().enterEvent(event)
        self.setCursor(QCursor(Qt.PointingHandCursor))

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.unsetCursor()


class BackendEditorDialog(QDialog):
    def __init__(self, parent=None, backend=None):
        super().__init__(parent)
        self.backend = backend or {}
        self.is_edit = bool(backend)
        self.setWindowTitle("编辑后端 | Edit Backend" if self.is_edit else "添加后端 | Add Backend")
        self.setMinimumSize(600, 550)
        self.setModal(True)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        content = QWidget()
        form = QFormLayout(content)
        form.setSpacing(10)
        form.setContentsMargins(16, 16, 16, 16)

        b = self.backend

        self.name_entry = QLineEdit(b.get("name", ""))
        form.addRow("名称 | Name", self.name_entry)

        self.type_combo = QComboBox()
        self.type_combo.addItems(["openai", "anthropic", "google", "ollama"])
        self.type_combo.setCurrentText(b.get("type", "openai"))
        form.addRow("类型 | Type", self.type_combo)

        self.url_entry = QLineEdit(b.get("url", ""))
        form.addRow("地址 | URL", self.url_entry)

        self.weight_entry = QLineEdit(str(b.get("weight", 10)))
        form.addRow("权重 | Weight", self.weight_entry)

        self.priority_entry = QLineEdit(str(b.get("priority", 1)))
        form.addRow("优先级 | Priority", self.priority_entry)

        self.timeout_entry = QLineEdit(str(b.get("timeout", 60)))
        form.addRow("超时 | Timeout (秒)", self.timeout_entry)

        self.api_keys_text = QTextEdit()
        self.api_keys_text.setMaximumHeight(80)
        self.api_keys_text.setPlainText("\n".join(b.get("api_keys", [])))
        form.addRow("API Keys (每行一个)", self.api_keys_text)

        rl = b.get("rate_limit", {})
        rl_layout = QHBoxLayout()
        self.rpm_entry = QLineEdit(str(rl.get("rpm", 0)))
        self.rpm_entry.setFixedWidth(60)
        self.tpm_entry = QLineEdit(str(rl.get("tpm", 0)))
        self.tpm_entry.setFixedWidth(60)
        self.conc_entry = QLineEdit(str(rl.get("concurrent", 0)))
        self.conc_entry.setFixedWidth(60)
        rl_layout.addWidget(QLabel("RPM:"))
        rl_layout.addWidget(self.rpm_entry)
        rl_layout.addWidget(QLabel("TPM:"))
        rl_layout.addWidget(self.tpm_entry)
        rl_layout.addWidget(QLabel("并发:"))
        rl_layout.addWidget(self.conc_entry)
        rl_layout.addStretch()
        form.addRow("速率限制 | Rate Limit", rl_layout)

        self.models_list = QListWidget()
        for m in b.get("models", []):
            self.models_list.addItem(f"{m.get('id', '')} -> {m.get('name', '')} ({m.get('context_length', 0)} tokens)")
        self.models_list._models = list(b.get("models", []))

        models_btn_layout = QHBoxLayout()
        add_model_btn = AnimatedButton("➕")
        add_model_btn.clicked.connect(self._add_model)
        edit_model_btn = AnimatedButton("✏️")
        edit_model_btn.clicked.connect(self._edit_model)
        remove_model_btn = AnimatedButton("🗑️")
        remove_model_btn.clicked.connect(self._remove_model)
        models_btn_layout.addWidget(add_model_btn)
        models_btn_layout.addWidget(edit_model_btn)
        models_btn_layout.addWidget(remove_model_btn)
        models_btn_layout.addStretch()

        models_layout = QVBoxLayout()
        models_layout.addWidget(self.models_list)
        models_layout.addLayout(models_btn_layout)
        form.addRow("模型 | Models", models_layout)

        scroll.setWidget(content)
        layout.addWidget(scroll)

        btn_layout = QHBoxLayout()
        save_btn = AnimatedButton("💾 保存 | Save")
        save_btn.setObjectName("AccentButton")
        save_btn.clicked.connect(self._save)
        cancel_btn = AnimatedButton("取消 | Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def _add_model(self):
        dialog = ModelEditorDialog(self)
        if dialog.exec() == QDialog.Accepted:
            model = dialog.get_model()
            self.models_list._models.append(model)
            self.models_list.addItem(f"{model['id']} -> {model['name']} ({model['context_length']} tokens)")

    def _edit_model(self):
        row = self.models_list.currentRow()
        if row < 0 or row >= len(self.models_list._models):
            return
        dialog = ModelEditorDialog(self, self.models_list._models[row])
        if dialog.exec() == QDialog.Accepted:
            model = dialog.get_model()
            self.models_list._models[row] = model
            self.models_list.item(row).setText(f"{model['id']} -> {model['name']} ({model['context_length']} tokens)")

    def _remove_model(self):
        row = self.models_list.currentRow()
        if row >= 0:
            self.models_list.takeItem(row)
            if row < len(self.models_list._models):
                del self.models_list._models[row]

    def _save(self):
        if not self.name_entry.text().strip():
            QMessageBox.warning(self, "警告 | Warning", "名称不能为空 | Name is required")
            return
        self.accept()

    def get_backend_data(self):
        api_keys = [k.strip() for k in self.api_keys_text.toPlainText().split("\n") if k.strip()]
        return {
            "name": self.name_entry.text().strip(),
            "type": self.type_combo.currentText(),
            "url": self.url_entry.text().strip(),
            "api_keys": api_keys,
            "weight": int(self.weight_entry.text() or 10),
            "priority": int(self.priority_entry.text() or 1),
            "timeout": int(self.timeout_entry.text() or 60),
            "enabled": True,
            "verify_ssl": True,
            "models": list(self.models_list._models),
            "rate_limit": {
                "rpm": int(self.rpm_entry.text() or 0),
                "tpm": int(self.tpm_entry.text() or 0),
                "concurrent": int(self.conc_entry.text() or 0)
            }
        }


class ModelEditorDialog(QDialog):
    def __init__(self, parent=None, model=None):
        super().__init__(parent)
        self.model = model or {}
        self.setWindowTitle("编辑模型 | Edit Model" if self.model else "添加模型 | Add Model")
        self.setMinimumSize(380, 300)
        self.setModal(True)
        self._setup_ui()

    def _setup_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 16, 16, 16)

        self.id_entry = QLineEdit(self.model.get("id", ""))
        layout.addRow("模型ID | Model ID", self.id_entry)

        self.name_entry = QLineEdit(self.model.get("name", ""))
        layout.addRow("实际名称 | Actual Name", self.name_entry)

        self.context_entry = QLineEdit(str(self.model.get("context_length", 4096)))
        layout.addRow("上下文长度 | Context Length", self.context_entry)

        rl = self.model.get("rate_limit", {})
        rl_layout = QHBoxLayout()
        self.rpm_entry = QLineEdit(str(rl.get("rpm", 0)))
        self.rpm_entry.setFixedWidth(60)
        self.tpm_entry = QLineEdit(str(rl.get("tpm", 0)))
        self.tpm_entry.setFixedWidth(60)
        self.conc_entry = QLineEdit(str(rl.get("concurrent", 0)))
        self.conc_entry.setFixedWidth(60)
        rl_layout.addWidget(QLabel("RPM:"))
        rl_layout.addWidget(self.rpm_entry)
        rl_layout.addWidget(QLabel("TPM:"))
        rl_layout.addWidget(self.tpm_entry)
        rl_layout.addWidget(QLabel("并发:"))
        rl_layout.addWidget(self.conc_entry)
        rl_layout.addStretch()
        layout.addRow("模型限速 | Model Rate Limit", rl_layout)

        btn_layout = QHBoxLayout()
        save_btn = AnimatedButton("💾 保存 | Save")
        save_btn.setObjectName("AccentButton")
        save_btn.clicked.connect(self.accept)
        cancel_btn = AnimatedButton("取消 | Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow("", btn_layout)

    def get_model(self):
        return {
            "id": self.id_entry.text().strip(),
            "name": self.name_entry.text().strip(),
            "context_length": int(self.context_entry.text() or 4096),
            "enabled": True,
            "rate_limit": {
                "rpm": int(self.rpm_entry.text() or 0),
                "tpm": int(self.tpm_entry.text() or 0),
                "concurrent": int(self.conc_entry.text() or 0)
            }
        }


class FishRouterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.server_process = None
        self.server_running = False
        self.config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
        self.config = {}
        self.stats_data = {"total_requests": 0, "total_tokens": 0, "total_errors": 0, "qps": 0}
        self.backend_statuses = []
        self.tray_icon = None
        self.is_minimized_to_tray = False

        self._load_config_file()
        self._setup_window()
        self._setup_ui()
        self._setup_system_tray()
        self._start_stats_refresh()

        self.setWindowOpacity(0)
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(300)
        self.fade_anim.setStartValue(0)
        self.fade_anim.setEndValue(1)
        self.fade_anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.fade_anim.start()

        if self._check_autostart():
            QTimer.singleShot(1000, self.start_server)

    def _load_config_file(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                self._create_default_config()
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

    def _setup_window(self):
        self.setWindowTitle("FishRouter - AI Model Router")
        self.resize(1050, 720)
        self.setMinimumSize(850, 600)

        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.title_bar = TitleBar(self)
        main_layout.addWidget(self.title_bar)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(12, 12, 12, 12)
        content_layout.setSpacing(10)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        content_layout.addWidget(self.tabs)

        self._setup_dashboard_tab()
        self._setup_backends_tab()
        self._setup_routes_tab()
        self._setup_settings_tab()
        self._setup_update_tab()

        main_layout.addWidget(content)

    def _setup_dashboard_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(10)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(10)

        self.card_requests = StatCard("总请求 | Requests", "0", Colors.ACCENT)
        self.card_qps = StatCard("QPS", "0.00", Colors.PURPLE)
        self.card_tokens = StatCard("总Token | Tokens", "0", Colors.SUCCESS)
        self.card_errors = StatCard("错误 | Errors", "0", Colors.ERROR)

        for card in [self.card_requests, self.card_qps, self.card_tokens, self.card_errors]:
            cards_layout.addWidget(card, 1)

        layout.addLayout(cards_layout)

        ctrl_frame = QFrame()
        ctrl_frame.setStyleSheet("background-color: #1e293b; border-radius: 8px; border: 1px solid #334155;")
        ctrl_layout = QHBoxLayout(ctrl_frame)
        ctrl_layout.setContentsMargins(12, 8, 12, 8)

        self.status_label = QLabel("⏹ 已停止 | Stopped")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #94a3b8;")
        ctrl_layout.addWidget(self.status_label)

        ctrl_layout.addStretch()

        self.start_btn = AnimatedButton("▶ 启动 | Start")
        self.start_btn.setObjectName("SuccessButton")
        self.start_btn.clicked.connect(self.start_server)
        ctrl_layout.addWidget(self.start_btn)

        self.stop_btn = AnimatedButton("⏹ 停止 | Stop")
        self.stop_btn.setObjectName("DangerButton")
        self.stop_btn.clicked.connect(self.stop_server)
        self.stop_btn.setEnabled(False)
        ctrl_layout.addWidget(self.stop_btn)

        open_btn = AnimatedButton("🌐 打开面板 | Open Web UI")
        open_btn.clicked.connect(self.open_dashboard)
        ctrl_layout.addWidget(open_btn)

        health_btn = AnimatedButton("🔍 健康检查 | Health Check")
        health_btn.clicked.connect(self._trigger_health_check)
        ctrl_layout.addWidget(health_btn)

        layout.addWidget(ctrl_frame)

        status_group = QGroupBox("后端状态 | Backend Status")
        status_layout = QVBoxLayout(status_group)

        self.status_table = QTableWidget()
        self.status_table.setColumnCount(6)
        self.status_table.setHorizontalHeaderLabels(["名称 | Name", "类型 | Type", "状态 | Status", "延迟 | Latency", "请求 | Requests", "模型 | Models"])
        self.status_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.status_table.setAlternatingRowColors(True)
        self.status_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.status_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.status_table.verticalHeader().setVisible(False)
        self.status_table.setShowGrid(False)
        status_layout.addWidget(self.status_table)

        layout.addWidget(status_group)

        log_group = QGroupBox("日志 | Log")
        log_layout = QVBoxLayout(log_group)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #0d1117;
                color: #c9d1d9;
                font-family: "Consolas", "Courier New", monospace;
                font-size: 12px;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        log_layout.addWidget(self.log_text)

        layout.addWidget(log_group, 1)

        self.tabs.addTab(tab, "🏠 控制台 | Dashboard")

    def _setup_backends_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(4, 4, 4, 4)

        list_group = QGroupBox("后端列表 | Backend List")
        list_layout = QVBoxLayout(list_group)

        self.backend_table = QTableWidget()
        self.backend_table.setColumnCount(6)
        self.backend_table.setHorizontalHeaderLabels(["名称 | Name", "类型 | Type", "地址 | URL", "Keys", "模型 | Models", "状态 | Status"])
        self.backend_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.backend_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Interactive)
        self.backend_table.setAlternatingRowColors(True)
        self.backend_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.backend_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.backend_table.verticalHeader().setVisible(False)
        self.backend_table.setShowGrid(False)
        self.backend_table.setSelectionMode(QAbstractItemView.SingleSelection)
        list_layout.addWidget(self.backend_table)

        layout.addWidget(list_group, 1)

        btn_layout = QHBoxLayout()
        add_btn = AnimatedButton("➕ 添加 | Add")
        add_btn.clicked.connect(self._add_backend)
        btn_layout.addWidget(add_btn)

        edit_btn = AnimatedButton("✏️ 编辑 | Edit")
        edit_btn.clicked.connect(self._edit_backend)
        btn_layout.addWidget(edit_btn)

        delete_btn = AnimatedButton("🗑️ 删除 | Delete")
        delete_btn.setObjectName("DangerButton")
        delete_btn.clicked.connect(self._delete_backend)
        btn_layout.addWidget(delete_btn)

        refresh_btn = AnimatedButton("🔄 刷新 | Refresh")
        refresh_btn.clicked.connect(self._refresh_backend_list)
        btn_layout.addWidget(refresh_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self._refresh_backend_list()
        self.tabs.addTab(tab, "🔗 后端 | Backends")

    def _setup_routes_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(10)

        route_group = QGroupBox("路由配置 | Route Configuration")
        route_form = QFormLayout(route_group)
        route_form.setSpacing(10)

        self.route_strategy = QComboBox()
        self.route_strategy.addItems(["latency", "round_robin", "random", "weighted", "priority", "custom"])
        route_form.addRow("策略 | Strategy", self.route_strategy)

        self.hc_interval = QLineEdit("30")
        self.hc_interval.setFixedWidth(80)
        route_form.addRow("健康检查间隔 | Health Check (秒)", self.hc_interval)

        layout.addWidget(route_group)

        fb_group = QGroupBox("回退顺序 | Fallback Order (拖拽排序 | Drag to reorder)")
        fb_layout = QVBoxLayout(fb_group)

        self.fb_list = QListWidget()
        self.fb_list.setDragDropMode(QAbstractItemView.InternalMove)
        self.fb_list.setDefaultDropAction(Qt.MoveAction)
        self.fb_list.setSelectionMode(QAbstractItemView.SingleSelection)
        fb_layout.addWidget(self.fb_list)

        avail_group = QGroupBox("可用后端 | Available Backends")
        avail_layout = QHBoxLayout(avail_group)
        self.avail_layout_inner = QHBoxLayout()
        self.avail_layout_inner.setSpacing(6)
        avail_layout.addLayout(self.avail_layout_inner)
        avail_layout.addStretch()
        fb_layout.addWidget(avail_group)

        fb_btn_layout = QHBoxLayout()
        add_fb_btn = AnimatedButton("➕ 添加 | Add")
        add_fb_btn.clicked.connect(self._add_fallback)
        fb_btn_layout.addWidget(add_fb_btn)

        remove_fb_btn = AnimatedButton("🗑️ 移除 | Remove")
        remove_fb_btn.clicked.connect(self._remove_fallback)
        fb_btn_layout.addWidget(remove_fb_btn)
        fb_btn_layout.addStretch()
        fb_layout.addLayout(fb_btn_layout)

        layout.addWidget(fb_group, 1)

        save_route_btn = AnimatedButton("💾 保存路由 | Save Route")
        save_route_btn.setObjectName("AccentButton")
        save_route_btn.clicked.connect(self._save_route)
        save_route_btn.setMinimumHeight(36)
        layout.addWidget(save_route_btn)

        self._load_route_config()
        self._refresh_available_backends()
        self.tabs.addTab(tab, "🛤️ 路由 | Routes")

    def _setup_settings_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(10)

        server_group = QGroupBox("服务器 | Server")
        server_form = QFormLayout(server_group)
        server_form.setSpacing(10)

        self.port_entry = QLineEdit(str(self.config.get("server", {}).get("port", 8080)))
        self.port_entry.setFixedWidth(100)
        server_form.addRow("端口 | Port", self.port_entry)

        self.log_level = QComboBox()
        self.log_level.addItems(["debug", "info", "warning", "error"])
        self.log_level.setCurrentText(self.config.get("server", {}).get("log_level", "info"))
        server_form.addRow("日志级别 | Log Level", self.log_level)

        layout.addWidget(server_group)

        auth_group = QGroupBox("认证 | Authentication")
        auth_layout = QVBoxLayout(auth_group)

        self.auth_enabled = QCheckBox("启用 API Key 认证 | Enable API Key Auth")
        self.auth_enabled.setChecked(self.config.get("auth", {}).get("enabled", False))
        auth_layout.addWidget(self.auth_enabled)

        auth_layout.addWidget(QLabel("API Keys (每行一个 | One per line):"))
        self.api_keys_text = QTextEdit()
        self.api_keys_text.setMaximumHeight(100)
        self.api_keys_text.setPlainText("\n".join(self.config.get("auth", {}).get("api_keys", [])))
        auth_layout.addWidget(self.api_keys_text)

        layout.addWidget(auth_group)

        startup_group = QGroupBox("启动 | Startup")
        startup_layout = QVBoxLayout(startup_group)

        self.auto_start = QCheckBox("开机自启动 | Auto-start on boot")
        self.auto_start.setChecked(self._check_autostart())
        self.auto_start.stateChanged.connect(self._toggle_autostart)
        startup_layout.addWidget(self.auto_start)

        layout.addWidget(startup_group)

        config_group = QGroupBox("配置文件 | Config File")
        config_layout = QVBoxLayout(config_group)

        config_path_label = QLabel(self.config_path)
        config_path_label.setStyleSheet("color: #94a3b8; font-family: Consolas, monospace;")
        config_layout.addWidget(config_path_label)

        open_folder_btn = AnimatedButton("📂 打开目录 | Open Folder")
        open_folder_btn.clicked.connect(lambda: os.startfile(os.path.dirname(self.config_path)))
        config_layout.addWidget(open_folder_btn)

        layout.addWidget(config_group)

        save_btn = AnimatedButton("💾 保存设置 | Save Settings")
        save_btn.setObjectName("AccentButton")
        save_btn.clicked.connect(self._save_settings)
        save_btn.setMinimumHeight(36)
        layout.addWidget(save_btn)

        layout.addStretch()
        self.tabs.addTab(tab, "⚙️ 设置 | Settings")

    def _setup_update_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("🔄 自动更新 | Auto Update")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #f1f5f9;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.update_status = QLabel("检查中... | Checking...")
        self.update_status.setStyleSheet("color: #94a3b8; font-size: 14px;")
        self.update_status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.update_status)

        self.update_info = QTextEdit()
        self.update_info.setReadOnly(True)
        self.update_info.setStyleSheet("""
            QTextEdit {
                background-color: #0d1117;
                color: #c9d1d9;
                font-family: "Consolas", "Courier New", monospace;
                font-size: 12px;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        layout.addWidget(self.update_info, 1)

        btn_layout = QHBoxLayout()
        check_btn = AnimatedButton("🔍 检查更新 | Check")
        check_btn.clicked.connect(self._check_updates)
        btn_layout.addWidget(check_btn)

        self.update_btn = AnimatedButton("⬇️ 下载更新 | Download")
        self.update_btn.setObjectName("AccentButton")
        self.update_btn.clicked.connect(self._do_update)
        self.update_btn.setEnabled(False)
        btn_layout.addWidget(self.update_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.progress_label = QLabel("")
        self.progress_label.setStyleSheet("color: #94a3b8;")
        self.progress_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.progress_label)

        self.tabs.addTab(tab, "🔄 更新 | Update")

        QTimer.singleShot(500, self._check_updates)

    def _setup_system_tray(self):
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "icon.ico")
        tray_icon = QIcon(icon_path) if os.path.exists(icon_path) else QIcon()

        self.tray_icon = QSystemTrayIcon(tray_icon, self)
        self.tray_icon.setToolTip("FishRouter - AI Model Router")

        tray_menu = QMenu()

        show_action = QAction("📺 显示窗口 | Show", self)
        show_action.triggered.connect(self._show_from_tray)
        tray_menu.addAction(show_action)

        tray_menu.addSeparator()

        self.tray_start_action = QAction("▶ 启动服务 | Start", self)
        self.tray_start_action.triggered.connect(self.start_server)
        tray_menu.addAction(self.tray_start_action)

        self.tray_stop_action = QAction("⏹ 停止服务 | Stop", self)
        self.tray_stop_action.triggered.connect(self.stop_server)
        self.tray_stop_action.setEnabled(False)
        tray_menu.addAction(self.tray_stop_action)

        tray_menu.addSeparator()

        open_action = QAction("🌐 打开面板 | Open Web UI", self)
        open_action.triggered.connect(self.open_dashboard)
        tray_menu.addAction(open_action)

        tray_menu.addSeparator()

        quit_action = QAction("🚪 退出 | Quit", self)
        quit_action.triggered.connect(self._quit_app)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._tray_activated)
        self.tray_icon.show()

    def _tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self._show_from_tray()

    def _show_from_tray(self):
        self.showNormal()
        self.activateWindow()
        self.raise_()
        self.is_minimized_to_tray = False

    def _quit_app(self):
        if self.server_running:
            self.stop_server()
        self.tray_icon.hide()
        QApplication.quit()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.is_minimized_to_tray = True
        self.tray_icon.showMessage(
            "FishRouter",
            "已最小化到托盘 | Minimized to tray",
            QSystemTrayIcon.Information,
            2000
        )

    def _start_stats_refresh(self):
        def refresh():
            while True:
                if self.server_running:
                    port = self.config.get("server", {}).get("port", 8080)
                    try:
                        ctx = ssl.create_default_context()
                        ctx.check_hostname = False
                        ctx.verify_mode = ssl.CERT_NONE

                        req = urllib.request.Request(f"http://localhost:{port}/api/monitor/stats")
                        with urllib.request.urlopen(req, context=ctx, timeout=3) as resp:
                            stats = json.loads(resp.read().decode())
                            self.stats_data = stats
                            QTimer.singleShot(0, self._update_stats_display)

                        req = urllib.request.Request(f"http://localhost:{port}/api/monitor/backends")
                        with urllib.request.urlopen(req, context=ctx, timeout=3) as resp:
                            backends = json.loads(resp.read().decode())
                            self.backend_statuses = backends
                            QTimer.singleShot(0, self._update_backend_status)
                    except:
                        pass
                time.sleep(3)

        threading.Thread(target=refresh, daemon=True).start()

    def _update_stats_display(self):
        self.card_requests.set_value(str(self.stats_data.get("total_requests", 0)))
        self.card_qps.set_value(f"{self.stats_data.get('qps', 0):.2f}")
        self.card_tokens.set_value(str(self.stats_data.get("total_tokens", 0)))
        self.card_errors.set_value(str(self.stats_data.get("total_errors", 0)))

    def _update_backend_status(self):
        self.status_table.setRowCount(0)
        for b in self.backend_statuses:
            row = self.status_table.rowCount()
            self.status_table.insertRow(row)
            healthy = "✅ 健康" if b.get("healthy") else "❌ 异常"
            items = [
                b.get("name", ""),
                b.get("type", ""),
                healthy,
                f"{b.get('latency', 0):.3f}s",
                str(b.get("total_requests", 0)),
                ", ".join(b.get("models", []))
            ]
            for col, val in enumerate(items):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                self.status_table.setItem(row, col, item)

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

    def _refresh_backend_list(self):
        self.backend_table.setRowCount(0)
        for b in self.config.get("backends", []):
            row = self.backend_table.rowCount()
            self.backend_table.insertRow(row)
            status = "✅" if b.get("enabled", True) else "❌"
            models = ", ".join([m.get("id", "") for m in b.get("models", [])])
            items = [
                b.get("name", ""),
                b.get("type", ""),
                b.get("url", ""),
                str(len(b.get("api_keys", []))),
                models,
                status
            ]
            for col, val in enumerate(items):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                self.backend_table.setItem(row, col, item)

    def _add_backend(self):
        dialog = BackendEditorDialog(self)
        if dialog.exec() == QDialog.Accepted:
            backend_data = dialog.get_backend_data()
            self.config.setdefault("backends", []).append(backend_data)
            self._save_config()
            self._refresh_backend_list()
            self._log(f"已添加后端 | Added backend: {backend_data['name']}")

    def _edit_backend(self):
        row = self.backend_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "警告 | Warning", "请选择一个后端 | Please select a backend")
            return
        name = self.backend_table.item(row, 0).text()
        backend = None
        for b in self.config.get("backends", []):
            if b.get("name") == name:
                backend = b
                break
        if backend:
            dialog = BackendEditorDialog(self, backend)
            if dialog.exec() == QDialog.Accepted:
                backend_data = dialog.get_backend_data()
                for i, b in enumerate(self.config.get("backends", [])):
                    if b.get("name") == name:
                        self.config["backends"][i] = backend_data
                        break
                self._save_config()
                self._refresh_backend_list()
                self._log(f"已更新后端 | Updated backend: {backend_data['name']}")

    def _delete_backend(self):
        row = self.backend_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "警告 | Warning", "请选择一个后端 | Please select a backend")
            return
        name = self.backend_table.item(row, 0).text()
        if QMessageBox.question(self, "确认 | Confirm", f"确定删除后端 {name}？", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.config["backends"] = [b for b in self.config.get("backends", []) if b.get("name") != name]
            self._save_config()
            self._refresh_backend_list()
            self._log(f"已删除后端 | Deleted backend: {name}")

    def _load_route_config(self):
        route = self.config.get("routes", [{}])[0] if self.config.get("routes") else {}
        self.route_strategy.setCurrentText(route.get("strategy", "latency"))
        self.hc_interval.setText(str(route.get("health_check_interval", 30)))
        self.fb_list.clear()
        for item in route.get("fallback_order", []):
            self.fb_list.addItem(item)

    def _refresh_available_backends(self):
        while self.avail_layout_inner.count():
            item = self.avail_layout_inner.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        fallback_items = [self.fb_list.item(i).text() for i in range(self.fb_list.count())]

        for b in self.config.get("backends", []):
            if not b.get("enabled", True):
                continue
            name = b.get("name", "")
            if name in fallback_items:
                continue
            btn = AnimatedButton(f"+ {name} ({b.get('type', '')})")
            btn.clicked.connect(lambda checked, n=name: self._add_to_fallback(n))
            self.avail_layout_inner.addWidget(btn)

    def _add_to_fallback(self, name):
        existing = [self.fb_list.item(i).text() for i in range(self.fb_list.count())]
        if name not in existing:
            self.fb_list.addItem(name)
            self._refresh_available_backends()

    def _add_fallback(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("添加回退后端 | Add Fallback Backend")
        dialog.setMinimumSize(280, 200)
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("选择后端 | Select Backend:"))

        lb = QListWidget()
        for b in self.config.get("backends", []):
            if b.get("enabled", True):
                lb.addItem(b.get("name", ""))
        layout.addWidget(lb)

        def select():
            if lb.currentRow() >= 0:
                self._add_to_fallback(lb.currentItem().text())
            dialog.accept()

        ok_btn = AnimatedButton("确定 | OK")
        ok_btn.setObjectName("AccentButton")
        ok_btn.clicked.connect(select)
        layout.addWidget(ok_btn)

        dialog.exec()

    def _remove_fallback(self):
        row = self.fb_list.currentRow()
        if row >= 0:
            self.fb_list.takeItem(row)
            self._refresh_available_backends()

    def _save_route(self):
        fallback = [self.fb_list.item(i).text() for i in range(self.fb_list.count())]

        if self.config.get("routes"):
            self.config["routes"][0]["strategy"] = self.route_strategy.currentText()
            self.config["routes"][0]["health_check_interval"] = int(self.hc_interval.text() or 30)
            self.config["routes"][0]["fallback_order"] = fallback
        else:
            self.config["routes"] = [{
                "name": "default",
                "models": ["*"],
                "strategy": self.route_strategy.currentText(),
                "failover": True,
                "health_check_interval": int(self.hc_interval.text() or 30),
                "fallback_order": fallback,
                "fallback_rules": []
            }]

        self._save_config()
        self._log("路由配置已保存 | Route config saved")
        self._refresh_available_backends()
        QMessageBox.information(self, "成功 | Success", "路由配置已保存 | Route config saved")

    def _check_autostart(self):
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run") as key:
                winreg.QueryValueEx(key, "FishRouter")
                return True
        except:
            return False

    def _toggle_autostart(self, state):
        try:
            import winreg
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            exe_path = os.path.abspath(sys.argv[0])
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
                if state == Qt.Checked:
                    winreg.SetValueEx(key, "FishRouter", 0, winreg.REG_SZ, f'"{exe_path}"')
                else:
                    try:
                        winreg.DeleteValue(key, "FishRouter")
                    except FileNotFoundError:
                        pass
        except Exception as e:
            self._log(f"设置自启动失败 | Auto-start error: {e}")

    def _save_settings(self):
        self.config["server"]["port"] = int(self.port_entry.text())
        self.config["server"]["log_level"] = self.log_level.currentText()
        self.config["auth"]["enabled"] = self.auth_enabled.isChecked()
        self.config["auth"]["api_keys"] = [k.strip() for k in self.api_keys_text.toPlainText().split("\n") if k.strip()]
        self._save_config()
        self._log("设置已保存 | Settings saved")
        QMessageBox.information(self, "成功 | Success", "设置已保存 | Settings saved")

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
                QTimer.singleShot(0, lambda: self._show_update_info(tag, notes))
            except Exception as e:
                QTimer.singleShot(0, lambda: self.update_status.setText(f"检查失败 | Check failed: {e}"))
        threading.Thread(target=check, daemon=True).start()

    def _show_update_info(self, tag, notes):
        self.update_info.setPlainText(f"最新版本 | Latest: {tag}\n\n更新日志 | Changelog:\n{notes}")
        self.update_status.setText(f"🆕 最新版本 | Latest: {tag}")
        self.update_status.setStyleSheet("color: #22c55e; font-size: 14px;")
        self.update_btn.setEnabled(True)

    def _do_update(self):
        self.progress_label.setText("正在下载... | Downloading...")
        self.update_btn.setEnabled(False)
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
                    QTimer.singleShot(0, lambda: self.progress_label.setText("未找到安装包 | No installer found"))
                    QTimer.singleShot(0, lambda: self.update_btn.setEnabled(True))
                    return
                import tempfile
                temp_file = os.path.join(tempfile.gettempdir(), "FishRouter-Update.exe")
                def progress(block, bs, total):
                    pct = min(100, block * bs * 100 // total)
                    QTimer.singleShot(0, lambda: self.progress_label.setText(f"下载中 | Downloading: {pct}%"))
                urllib.request.urlretrieve(download_url, temp_file, progress)
                QTimer.singleShot(0, lambda: subprocess.Popen([temp_file]))
                QTimer.singleShot(0, lambda: self.progress_label.setText("安装程序已启动 | Installer launched"))
                QTimer.singleShot(0, self.close)
            except Exception as e:
                QTimer.singleShot(0, lambda: self.progress_label.setText(f"更新失败 | Update failed: {e}"))
                QTimer.singleShot(0, lambda: self.update_btn.setEnabled(True))
        threading.Thread(target=download, daemon=True).start()

    def _log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())

    def start_server(self):
        if self.server_running:
            return
        port = int(self.port_entry.text())
        self.config["server"]["port"] = port
        self._save_config()
        self.start_btn.setEnabled(False)
        self.status_label.setText("🔄 启动中... | Starting...")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #f59e0b;")
        self._log("正在启动服务器... | Starting server...")

        def run_server():
            try:
                # Determine base directory: if running as exe (PyInstaller), use executable dir; otherwise use script dir
                if getattr(sys, 'frozen', False):
                    base_dir = os.path.dirname(sys.executable)
                else:
                    base_dir = os.path.dirname(os.path.abspath(__file__))
                server_exe = os.path.join(base_dir, "fishrouter-server.exe")
                if os.path.exists(server_exe):
                    cmd = [server_exe, "--port", str(port)]
                    env = os.environ.copy()
                    env["PYTHONIOENCODING"] = "utf-8"
                    # Start without CREATE_NO_WINDOW to see errors if any
                    self.server_process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        env=env,
                        cwd=base_dir
                    )
                    for line in self.server_process.stdout:
                        QTimer.singleShot(0, lambda l=line.strip(): self._log(l))
                    self.server_process.wait()
                    self._log("服务器进程已退出 | Server process exited")
                else:
                    self._log(f"未找到服务器可执行文件: {server_exe}，切换到内联模式 | Server executable not found, falling back to inline mode")
                    self._run_server_inline()
                    return
            except Exception as e:
                QTimer.singleShot(0, lambda: self._log(f"错误 | Error: {e}"))
                import traceback
                QTimer.singleShot(0, lambda: self._log(traceback.format_exc()))
            finally:
                QTimer.singleShot(0, self._server_stopped)

        threading.Thread(target=run_server, daemon=True).start()
        self.server_running = True
        self.stop_btn.setEnabled(True)
        self.status_label.setText(f"🟢 运行中 | Running (:{port})")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #22c55e;")
        self.tray_start_action.setEnabled(False)
        self.tray_stop_action.setEnabled(True)

    def _run_server_inline(self):
        def run():
            try:
                import uvicorn
                sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
                from app.main import app, config
                config.server.port = int(self.port_entry.text())
                QTimer.singleShot(0, lambda: self._log("服务器已启动 | Server started"))
                uvicorn.run(app, host="0.0.0.0", port=int(self.port_entry.text()), log_level="info")
            except Exception as e:
                QTimer.singleShot(0, lambda: self._log(f"错误 | Error: {e}"))
            finally:
                QTimer.singleShot(0, self._server_stopped)
        threading.Thread(target=run, daemon=True).start()
        self.server_running = True
        self.stop_btn.setEnabled(True)
        self.status_label.setText(f"🟢 运行中 | Running (:{int(self.port_entry.text())})")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #22c55e;")
        self.tray_start_action.setEnabled(False)
        self.tray_stop_action.setEnabled(True)

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
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("⏹ 已停止 | Stopped")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #94a3b8;")
        self._log("服务器已停止 | Server stopped")
        self.tray_start_action.setEnabled(True)
        self.tray_stop_action.setEnabled(False)

    def open_dashboard(self):
        port = self.config.get("server", {}).get("port", 8080)
        webbrowser.open(f"http://localhost:{port}")


if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    app.setStyleSheet(QSS)
    app.setApplicationName("FishRouter")

    window = FishRouterApp()
    window.show()
    sys.exit(app.exec())
