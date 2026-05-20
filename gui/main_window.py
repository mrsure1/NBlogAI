from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QLineEdit, QPushButton,
    QGroupBox, QMessageBox,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QIcon

from gui.styles import MAIN_STYLE
from gui.tabs.posting_tab import PostingTab
from gui.tabs.neighbor_tab import NeighborTab
from gui.tabs.analytics_tab import AnalyticsTab
from gui.tabs.guide_tab import GuideTab
from utils.config import load_config, save_config
from core.scheduler import SchedulerThread, get_pending_posts


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NBlogAI — 네이버 블로그 AI 자동화")
        self.setMinimumSize(1200, 800)
        self.resize(1280, 860)
        self.setStyleSheet(MAIN_STYLE)

        self._setup_ui()
        self._load_settings()
        self._start_scheduler()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(8)
        root.setContentsMargins(12, 10, 12, 10)

        root.addWidget(self._build_header())
        root.addWidget(self._build_settings_bar())
        root.addWidget(self._build_tabs())

    def _build_header(self) -> QWidget:
        w = QWidget()
        layout = QHBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("NBlogAI")
        title.setObjectName("labelTitle")
        title.setFont(QFont("Malgun Gothic", 20, QFont.Bold))

        subtitle = QLabel("네이버 블로그 AI 자동화 도구")
        subtitle.setObjectName("labelSub")
        subtitle.setFont(QFont("Malgun Gothic", 11))

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch()

        self.lbl_status = QLabel("⚪ 대기 중")
        self.lbl_status.setObjectName("labelSub")
        layout.addWidget(self.lbl_status)

        return w

    def _build_settings_bar(self) -> QGroupBox:
        box = QGroupBox("공통 설정")
        layout = QHBoxLayout(box)
        layout.setSpacing(10)

        layout.addWidget(QLabel("Naver ID"))
        self.inp_naver_id = QLineEdit()
        self.inp_naver_id.setPlaceholderText("네이버 아이디")
        self.inp_naver_id.setMaximumWidth(160)
        layout.addWidget(self.inp_naver_id)

        layout.addWidget(QLabel("Naver PW"))
        self.inp_naver_pw = QLineEdit()
        self.inp_naver_pw.setPlaceholderText("비밀번호")
        self.inp_naver_pw.setEchoMode(QLineEdit.Password)
        self.inp_naver_pw.setMaximumWidth(160)
        layout.addWidget(self.inp_naver_pw)

        layout.addWidget(QLabel("Gemini API Key"))
        self.inp_gemini_key = QLineEdit()
        self.inp_gemini_key.setPlaceholderText("AIza...")
        self.inp_gemini_key.setEchoMode(QLineEdit.Password)
        self.inp_gemini_key.setMaximumWidth(260)
        layout.addWidget(self.inp_gemini_key)

        btn_show = QPushButton("👁")
        btn_show.setMaximumWidth(36)
        btn_show.setCheckable(True)
        btn_show.toggled.connect(self._toggle_pw_visibility)
        layout.addWidget(btn_show)

        btn_save = QPushButton("설정 저장 (.env)")
        btn_save.setObjectName("btnGreen")
        btn_save.clicked.connect(self._save_settings)
        layout.addWidget(btn_save)

        layout.addStretch()
        return box

    def _build_tabs(self) -> QTabWidget:
        tabs = QTabWidget()

        self.posting_tab = PostingTab()
        self.neighbor_tab = NeighborTab()
        self.analytics_tab = AnalyticsTab()
        self.guide_tab = GuideTab()

        tabs.addTab(self.posting_tab, "📝 블로그 자동 포스팅")
        tabs.addTab(self.neighbor_tab, "🤝 이웃 늘리기")
        tabs.addTab(self.analytics_tab, "📊 성과 분석")
        tabs.addTab(self.guide_tab, "⚡ 퀵 가이드")

        return tabs

    def _load_settings(self):
        cfg = load_config()
        self.inp_naver_id.setText(cfg.get("NAVER_ID", ""))
        self.inp_naver_pw.setText(cfg.get("NAVER_PW", ""))
        self.inp_gemini_key.setText(cfg.get("GEMINI_API_KEY", ""))

    def _save_settings(self):
        naver_id = self.inp_naver_id.text().strip()
        naver_pw = self.inp_naver_pw.text()
        gemini_key = self.inp_gemini_key.text().strip()

        if not naver_id or not naver_pw:
            QMessageBox.warning(self, "경고", "네이버 ID와 비밀번호를 입력해주세요.")
            return

        save_config(naver_id, naver_pw, gemini_key)
        self.lbl_status.setText("✅ 설정 저장 완료")

        QTimer.singleShot(3000, lambda: self.lbl_status.setText("⚪ 대기 중"))

    def _toggle_pw_visibility(self, checked: bool):
        mode = QLineEdit.Normal if checked else QLineEdit.Password
        self.inp_naver_pw.setEchoMode(mode)
        self.inp_gemini_key.setEchoMode(mode)

    def _start_scheduler(self):
        def publish_callback(post_data):
            from core.naver_automation import publish_post
            publish_post(post_data)

        self.scheduler = SchedulerThread(publish_callback)
        self.scheduler.start()

    def closeEvent(self, event):
        if hasattr(self, "scheduler"):
            self.scheduler.stop()
        event.accept()
