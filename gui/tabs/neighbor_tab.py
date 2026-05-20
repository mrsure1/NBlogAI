from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QGroupBox,
    QSpinBox, QCheckBox, QTextEdit,
)
from PySide6.QtCore import QThread, Signal

from gui.styles import LOG_STYLE


class WorkerThread(QThread):
    log_signal = Signal(str)
    done_signal = Signal(bool, object)

    def __init__(self, task_fn, *args, **kwargs):
        super().__init__()
        self.task_fn = task_fn
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            result = self.task_fn(*self.args, **self.kwargs)
            self.done_signal.emit(True, result)
        except Exception as e:
            self.log_signal.emit(f"❌ 오류: {e}")
            self.done_signal.emit(False, None)


class NeighborTab(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        layout.addWidget(self._build_follow_section())
        layout.addWidget(self._build_feed_section())
        layout.addWidget(self._build_reply_section())
        layout.addWidget(self._build_log_section())
        layout.addStretch()

    def _build_follow_section(self) -> QGroupBox:
        box = QGroupBox("서로이웃 신청 봇")
        grid = QGridLayout(box)
        grid.setSpacing(8)

        grid.addWidget(QLabel("검색 키워드"), 0, 0)
        self.inp_keyword = QLineEdit()
        self.inp_keyword.setPlaceholderText("예: 육아소통, IT리뷰, 재테크")
        grid.addWidget(self.inp_keyword, 0, 1, 1, 3)

        grid.addWidget(QLabel("최대 신청 수"), 1, 0)
        self.spin_max = QSpinBox()
        self.spin_max.setRange(1, 50)
        self.spin_max.setValue(10)
        grid.addWidget(self.spin_max, 1, 1)

        self.chk_do_follow = QCheckBox("서로이웃 신청")
        self.chk_do_follow.setChecked(True)
        grid.addWidget(self.chk_do_follow, 1, 2)

        self.chk_do_like = QCheckBox("최신글 좋아요")
        self.chk_do_like.setChecked(True)
        grid.addWidget(self.chk_do_like, 1, 3)

        self.chk_ai_comment = QCheckBox("AI 맞춤 메시지 (서이추 시)")
        grid.addWidget(self.chk_ai_comment, 2, 0, 1, 2)

        self.btn_start_follow = QPushButton("서이추 봇 시작")
        self.btn_start_follow.setObjectName("btnGreen")
        self.btn_start_follow.setMinimumHeight(40)
        self.btn_start_follow.clicked.connect(self._on_start_follow)
        grid.addWidget(self.btn_start_follow, 2, 2, 1, 2)

        return box

    def _build_feed_section(self) -> QGroupBox:
        box = QGroupBox("이웃 피드 공감")
        layout = QHBoxLayout(box)

        layout.addWidget(QLabel("공감 수:"))
        self.spin_feed_count = QSpinBox()
        self.spin_feed_count.setRange(1, 100)
        self.spin_feed_count.setValue(20)
        layout.addWidget(self.spin_feed_count)

        self.btn_feed_like = QPushButton("피드 공감 실행")
        self.btn_feed_like.clicked.connect(self._on_feed_like)
        layout.addWidget(self.btn_feed_like)
        layout.addStretch()
        return box

    def _build_reply_section(self) -> QGroupBox:
        box = QGroupBox("AI 댓글 자동 답글")
        layout = QHBoxLayout(box)
        layout.addWidget(QLabel("내 블로그 최신 댓글에 AI가 자동으로 답글을 달아드립니다."))
        self.btn_auto_reply = QPushButton("자동 답글 실행")
        self.btn_auto_reply.clicked.connect(self._on_auto_reply)
        layout.addWidget(self.btn_auto_reply)
        return box

    def _build_log_section(self) -> QGroupBox:
        box = QGroupBox("실행 로그")
        layout = QVBoxLayout(box)
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setStyleSheet(LOG_STYLE)
        self.txt_log.setMinimumHeight(180)
        layout.addWidget(self.txt_log)

        btn_clear = QPushButton("로그 지우기")
        btn_clear.setMaximumWidth(100)
        btn_clear.clicked.connect(self.txt_log.clear)
        layout.addWidget(btn_clear)
        return box

    def _log(self, msg: str):
        self.txt_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
        self.txt_log.ensureCursorVisible()

    def _on_start_follow(self):
        keyword = self.inp_keyword.text().strip()
        if not keyword:
            self._log("⚠ 검색 키워드를 입력하세요.")
            return

        self.btn_start_follow.setEnabled(False)
        self._log(f"서이추 봇 시작: '{keyword}'")

        def task():
            from core.naver_automation import run_neighbor_bot
            return run_neighbor_bot(
                keyword=keyword,
                max_count=self.spin_max.value(),
                do_follow=self.chk_do_follow.isChecked(),
                do_like=self.chk_do_like.isChecked(),
                ai_comment=self.chk_ai_comment.isChecked(),
                log_callback=self._log,
            )

        self.worker = WorkerThread(task)
        self.worker.log_signal.connect(self._log)
        self.worker.done_signal.connect(lambda ok, r: (
            self.btn_start_follow.setEnabled(True),
            self._log(f"✅ 서이추 봇 완료: {r}명 신청" if ok else "❌ 실패")
        ))
        self.worker.start()

    def _on_feed_like(self):
        self.btn_feed_like.setEnabled(False)
        self._log("피드 공감 시작...")

        def task():
            from core.naver_automation import run_feed_like
            return run_feed_like(
                max_count=self.spin_feed_count.value(),
                log_callback=self._log,
            )

        self.worker = WorkerThread(task)
        self.worker.log_signal.connect(self._log)
        self.worker.done_signal.connect(lambda ok, r: (
            self.btn_feed_like.setEnabled(True),
            self._log(f"✅ 피드 공감 {r}개 완료" if ok else "❌ 실패")
        ))
        self.worker.start()

    def _on_auto_reply(self):
        self.btn_auto_reply.setEnabled(False)
        self._log("자동 답글 시작...")

        def task():
            from core.naver_automation import run_auto_reply
            return run_auto_reply(log_callback=self._log)

        self.worker = WorkerThread(task)
        self.worker.log_signal.connect(self._log)
        self.worker.done_signal.connect(lambda ok, r: (
            self.btn_auto_reply.setEnabled(True),
            self._log(f"✅ 자동 답글 {r}개 완료" if ok else "❌ 실패")
        ))
        self.worker.start()
