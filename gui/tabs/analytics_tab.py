from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QGroupBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QLabel, QTextEdit,
)
from PySide6.QtCore import QThread, Signal, Qt

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


class AnalyticsTab(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # 요약 카드
        summary_box = QGroupBox("성과 요약")
        summary_layout = QHBoxLayout(summary_box)

        self.lbl_total_posts = self._stat_card("전체 포스트", "0")
        self.lbl_total_views = self._stat_card("총 조회수", "0")
        self.lbl_total_likes = self._stat_card("총 공감수", "0")
        self.lbl_total_comments = self._stat_card("총 댓글수", "0")

        summary_layout.addWidget(self.lbl_total_posts)
        summary_layout.addWidget(self.lbl_total_views)
        summary_layout.addWidget(self.lbl_total_likes)
        summary_layout.addWidget(self.lbl_total_comments)

        layout.addWidget(summary_box)

        # 포스트 테이블
        table_box = QGroupBox("포스트별 상세 통계")
        table_layout = QVBoxLayout(table_box)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["제목", "조회수", "공감수", "댓글수"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        table_layout.addWidget(self.table)

        btn_refresh = QPushButton("통계 새로고침")
        btn_refresh.setObjectName("btnGreen")
        btn_refresh.setMinimumHeight(40)
        btn_refresh.clicked.connect(self._fetch_stats)
        table_layout.addWidget(btn_refresh)

        layout.addWidget(table_box)

        # 로그
        log_box = QGroupBox("로그")
        log_layout = QVBoxLayout(log_box)
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setStyleSheet(LOG_STYLE)
        self.txt_log.setMaximumHeight(100)
        log_layout.addWidget(self.txt_log)
        layout.addWidget(log_box)

    def _stat_card(self, title: str, value: str) -> QGroupBox:
        box = QGroupBox(title)
        layout = QVBoxLayout(box)
        lbl = QLabel(value)
        lbl.setObjectName("labelTitle")
        lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl)
        box._value_label = lbl
        return box

    def _log(self, msg: str):
        self.txt_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
        self.txt_log.ensureCursorVisible()

    def _fetch_stats(self):
        self._log("블로그 통계 수집 중...")

        def task():
            from core.naver_automation import fetch_blog_stats
            return fetch_blog_stats(log_callback=self._log)

        self.worker = WorkerThread(task)
        self.worker.log_signal.connect(self._log)
        self.worker.done_signal.connect(self._on_stats_done)
        self.worker.start()

    def _on_stats_done(self, success: bool, result):
        if not success or not result:
            self._log("통계 수집 실패 또는 데이터 없음")
            return

        stats = result
        self.table.setRowCount(0)

        total_views = sum(s["views"] for s in stats)
        total_likes = sum(s["likes"] for s in stats)
        total_comments = sum(s["comments"] for s in stats)

        self.lbl_total_posts._value_label.setText(str(len(stats)))
        self.lbl_total_views._value_label.setText(f"{total_views:,}")
        self.lbl_total_likes._value_label.setText(f"{total_likes:,}")
        self.lbl_total_comments._value_label.setText(f"{total_comments:,}")

        for s in sorted(stats, key=lambda x: x["views"], reverse=True):
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(s["title"]))
            self.table.setItem(row, 1, QTableWidgetItem(str(s["views"])))
            self.table.setItem(row, 2, QTableWidgetItem(str(s["likes"])))
            self.table.setItem(row, 3, QTableWidgetItem(str(s["comments"])))

        self._log(f"✅ 통계 수집 완료: {len(stats)}개 포스트")
