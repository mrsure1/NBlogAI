import json
import os
import threading
import time
from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QComboBox,
    QSpinBox, QGroupBox, QSplitter, QFileDialog,
    QScrollArea, QRadioButton, QButtonGroup, QDateTimeEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox,
)
from PySide6.QtCore import Qt, QThread, Signal, QDateTime
from PySide6.QtGui import QFont, QColor

from gui.styles import LOG_STYLE

DATA_DIR = Path(__file__).parent.parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
POSTS_FILE = DATA_DIR / "posts.json"


def load_posts() -> list:
    if POSTS_FILE.exists():
        try:
            return json.loads(POSTS_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def save_posts(posts: list):
    POSTS_FILE.write_text(json.dumps(posts, ensure_ascii=False, indent=2), encoding="utf-8")


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


class PostingTab(QWidget):
    def __init__(self):
        super().__init__()
        self.current_post = None
        self.style_index = 0
        self._setup_ui()

    def _setup_ui(self):
        root = QHBoxLayout(self)
        root.setSpacing(12)

        splitter = QSplitter(Qt.Horizontal)

        # 왼쪽 메인 패널
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setSpacing(10)

        left_layout.addWidget(self._build_input_section())
        left_layout.addWidget(self._build_buttons_section())
        left_layout.addWidget(self._build_preview_section())
        left_layout.addWidget(self._build_log_section())

        splitter.addWidget(left)

        # 오른쪽 사이드 패널
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setSpacing(10)

        right_layout.addWidget(self._build_queue_section())
        right_layout.addWidget(self._build_seo_section())
        right_layout.addWidget(self._build_json_import_section())
        right_layout.addWidget(self._build_rewriter_section())
        right_layout.addStretch()

        right.setMaximumWidth(340)
        splitter.addWidget(right)
        splitter.setSizes([700, 340])

        root.addWidget(splitter)

    def _build_input_section(self) -> QGroupBox:
        box = QGroupBox("글 생성 설정")
        grid = QGridLayout(box)
        grid.setSpacing(8)

        grid.addWidget(QLabel("주제 키워드 *"), 0, 0)
        self.inp_topic = QLineEdit()
        self.inp_topic.setPlaceholderText("예: 제주도 맛집, 초보 재테크")
        grid.addWidget(self.inp_topic, 0, 1, 1, 3)

        grid.addWidget(QLabel("트렌드 키워드"), 1, 0)
        self.inp_trend = QLineEdit()
        self.inp_trend.setPlaceholderText("예: MZ세대, 2026 트렌드 (선택)")
        grid.addWidget(self.inp_trend, 1, 1, 1, 3)

        grid.addWidget(QLabel("시리즈 편수"), 2, 0)
        self.spin_series = QSpinBox()
        self.spin_series.setRange(1, 5)
        self.spin_series.setValue(1)
        grid.addWidget(self.spin_series, 2, 1)

        grid.addWidget(QLabel("글 분량"), 2, 2)
        self.combo_length = QComboBox()
        self.combo_length.addItems(["표준", "짧음", "길게"])
        grid.addWidget(self.combo_length, 2, 3)

        grid.addWidget(QLabel("이미지 크기"), 3, 0)
        self.combo_img_size = QComboBox()
        self.combo_img_size.addItems(["중형", "소형", "대형"])
        grid.addWidget(self.combo_img_size, 3, 1)

        return box

    def _build_buttons_section(self) -> QGroupBox:
        box = QGroupBox("3단계 실행")
        layout = QHBoxLayout(box)
        layout.setSpacing(10)

        self.btn_generate = QPushButton("① 포스트 생성 (AI)")
        self.btn_generate.setObjectName("btnGreen")
        self.btn_generate.setMinimumHeight(44)
        self.btn_generate.clicked.connect(self._on_generate)

        self.btn_image = QPushButton("② 이미지 생성")
        self.btn_image.setObjectName("btnYellow")
        self.btn_image.setMinimumHeight(44)
        self.btn_image.setEnabled(False)
        self.btn_image.clicked.connect(self._on_image_gen)

        self.btn_publish = QPushButton("③ 블로그 발행")
        self.btn_publish.setObjectName("btnRed")
        self.btn_publish.setMinimumHeight(44)
        self.btn_publish.setEnabled(False)
        self.btn_publish.clicked.connect(self._on_publish)

        layout.addWidget(self.btn_generate)
        layout.addWidget(self.btn_image)
        layout.addWidget(self.btn_publish)
        return box

    def _build_preview_section(self) -> QGroupBox:
        box = QGroupBox("생성된 포스트 미리보기")
        layout = QVBoxLayout(box)

        self.lbl_post_title = QLabel("아직 생성된 포스트가 없습니다.")
        self.lbl_post_title.setObjectName("labelTitle")
        self.lbl_post_title.setWordWrap(True)
        layout.addWidget(self.lbl_post_title)

        self.txt_preview = QTextEdit()
        self.txt_preview.setReadOnly(True)
        self.txt_preview.setMaximumHeight(160)
        layout.addWidget(self.txt_preview)

        return box

    def _build_log_section(self) -> QGroupBox:
        box = QGroupBox("실행 로그")
        layout = QVBoxLayout(box)
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setStyleSheet(LOG_STYLE)
        self.txt_log.setMaximumHeight(130)
        layout.addWidget(self.txt_log)

        btn_clear = QPushButton("로그 지우기")
        btn_clear.setMaximumWidth(100)
        btn_clear.clicked.connect(self.txt_log.clear)
        layout.addWidget(btn_clear, alignment=Qt.AlignRight)
        return box

    def _build_queue_section(self) -> QGroupBox:
        box = QGroupBox("📅 예약 발행 큐")
        layout = QVBoxLayout(box)

        self.dt_schedule = QDateTimeEdit()
        self.dt_schedule.setDateTime(QDateTime.currentDateTime())
        self.dt_schedule.setDisplayFormat("yyyy-MM-dd HH:mm")
        layout.addWidget(QLabel("발행 시각:"))
        layout.addWidget(self.dt_schedule)

        btn_add_q = QPushButton("현재 포스트를 큐에 추가")
        btn_add_q.clicked.connect(self._add_to_queue)
        layout.addWidget(btn_add_q)

        self.tbl_queue = QTableWidget(0, 2)
        self.tbl_queue.setHorizontalHeaderLabels(["발행 시각", "제목"])
        self.tbl_queue.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tbl_queue.setMaximumHeight(120)
        layout.addWidget(self.tbl_queue)

        btn_del_q = QPushButton("선택 항목 삭제")
        btn_del_q.setObjectName("btnRed")
        btn_del_q.clicked.connect(self._remove_from_queue_ui)
        layout.addWidget(btn_del_q)

        self._refresh_queue_table()
        return box

    def _build_seo_section(self) -> QGroupBox:
        box = QGroupBox("📊 SEO 분석")
        layout = QVBoxLayout(box)

        self.lbl_seo_score = QLabel("점수: -")
        self.lbl_seo_score.setObjectName("labelTitle")
        layout.addWidget(self.lbl_seo_score)

        self.txt_seo_tips = QTextEdit()
        self.txt_seo_tips.setReadOnly(True)
        self.txt_seo_tips.setMaximumHeight(100)
        layout.addWidget(self.txt_seo_tips)

        btn_seo = QPushButton("SEO 분석 실행")
        btn_seo.clicked.connect(self._run_seo)
        layout.addWidget(btn_seo)
        return box

    def _build_json_import_section(self) -> QGroupBox:
        box = QGroupBox("📂 외부 JSON 파일 발행")
        layout = QVBoxLayout(box)

        btn_open = QPushButton("JSON 파일 열기")
        btn_open.clicked.connect(self._open_json)
        layout.addWidget(btn_open)

        self.lbl_json_file = QLabel("파일 미선택")
        self.lbl_json_file.setObjectName("labelSub")
        self.lbl_json_file.setWordWrap(True)
        layout.addWidget(self.lbl_json_file)

        btn_pub_json = QPushButton("선택 JSON 발행")
        btn_pub_json.setObjectName("btnGreen")
        btn_pub_json.clicked.connect(self._publish_json)
        layout.addWidget(btn_pub_json)
        return box

    def _build_rewriter_section(self) -> QGroupBox:
        box = QGroupBox("♻ 글 리라이터")
        layout = QVBoxLayout(box)
        layout.addWidget(QLabel("현재 포스트를 새 스타일로 재작성합니다."))

        btn_rewrite = QPushButton("현재 글 리라이트")
        btn_rewrite.clicked.connect(self._rewrite_post)
        layout.addWidget(btn_rewrite)
        return box

    # ── 이벤트 핸들러 ─────────────────────────────────────────────────────────

    def _log(self, msg: str):
        self.txt_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
        self.txt_log.ensureCursorVisible()

    def _set_buttons(self, enabled: bool):
        self.btn_generate.setEnabled(enabled)

    def _on_generate(self):
        topic = self.inp_topic.text().strip()
        if not topic:
            self._log("⚠ 주제 키워드를 입력하세요.")
            return

        count = self.spin_series.value()
        self._log(f"AI 포스트 생성 시작: '{topic}' {count}편...")
        self.btn_generate.setEnabled(False)
        self.btn_image.setEnabled(False)
        self.btn_publish.setEnabled(False)

        def task():
            from core.ai_generator import generate_post
            posts = []
            for i in range(count):
                self.log_signal_proxy(f"  {i+1}편 생성 중...")
                post = generate_post(
                    topic=topic,
                    trend_kw=self.inp_trend.text().strip(),
                    length=self.combo_length.currentText(),
                    style_index=self.style_index + i,
                )
                posts.append(post)
            self.style_index += count
            return posts

        self.log_signal_proxy = self._log
        self.worker = WorkerThread(task)
        self.worker.log_signal.connect(self._log)
        self.worker.done_signal.connect(self._on_generate_done)
        self.worker.start()

    def _on_generate_done(self, success: bool, result):
        self.btn_generate.setEnabled(True)
        if not success or not result:
            return
        posts = result
        self.current_post = posts[0]

        existing = load_posts()
        existing.extend(posts)
        save_posts(existing)

        self.lbl_post_title.setText(self.current_post.get("title", ""))
        preview_lines = []
        for sec in self.current_post.get("sections", [])[:2]:
            preview_lines.append(f"▶ {sec.get('h2', '')}")
            for sub in sec.get("subsections", [])[:1]:
                for para in sub.get("paragraphs", [])[:2]:
                    preview_lines.append(para[:100])
        self.txt_preview.setPlainText("\n".join(preview_lines))

        self.btn_image.setEnabled(True)
        self.btn_publish.setEnabled(True)
        self._log(f"✅ {len(posts)}편 생성 완료!")

    def _on_image_gen(self):
        if not self.current_post:
            self._log("⚠ 먼저 포스트를 생성하세요.")
            return
        sections_count = len(self.current_post.get("sections", []))
        self._log(f"AI 이미지 생성 시작 (커버 1장 + 섹션 {sections_count}장, 각 약 20초)...")
        self.btn_image.setEnabled(False)
        size = self.combo_img_size.currentText()

        def task():
            from core.image_generator import generate_post_images
            slug = self.current_post.get("title", "post")[:20].replace(" ", "_")
            result = generate_post_images(
                post_data=self.current_post,
                size=size,
                slug=slug,
                log_callback=self._log,
            )
            return result

        self.worker = WorkerThread(task)
        self.worker.log_signal.connect(self._log)
        self.worker.done_signal.connect(self._on_image_done)
        self.worker.start()

    def _on_image_done(self, success: bool, result):
        self.btn_image.setEnabled(True)
        if success and result:
            cover = result.get("cover", "")
            sections = result.get("sections", [])
            total = (1 if cover else 0) + len(sections)
            self._log(f"✅ 이미지 생성 완료! 커버 {'1장' if cover else '실패'} + 섹션 {len(sections)}장 (총 {total}장)")
        else:
            self._log("❌ 이미지 생성 실패")

    def _on_publish(self):
        if not self.current_post:
            self._log("⚠ 먼저 포스트를 생성하세요.")
            return
        self._log("네이버 블로그 발행 시작...")
        self.btn_publish.setEnabled(False)

        def task():
            from core.naver_automation import publish_post
            return publish_post(self.current_post, log_callback=self._log)

        self.worker = WorkerThread(task)
        self.worker.log_signal.connect(self._log)
        self.worker.done_signal.connect(lambda ok, _: (
            self.btn_publish.setEnabled(True),
            self._log("✅ 발행 완료!" if ok else "❌ 발행 실패")
        ))
        self.worker.start()

    def _run_seo(self):
        if not self.current_post:
            self._log("⚠ 먼저 포스트를 생성하세요.")
            return
        from core.seo_analyzer import analyze_seo
        result = analyze_seo(self.current_post)
        self.lbl_seo_score.setText(f"점수: {result['score']}/100  등급: {result['grade']}")
        tips_text = "\n".join(f"• {t}" for t in result["tips"])
        if not tips_text:
            tips_text = "SEO 최적화 상태가 좋습니다!"
        self.txt_seo_tips.setPlainText(tips_text)

    def _add_to_queue(self):
        if not self.current_post:
            self._log("⚠ 먼저 포스트를 생성하세요.")
            return
        from core.scheduler import add_to_queue
        dt_str = self.dt_schedule.dateTime().toString("yyyy-MM-dd HH:mm")
        add_to_queue(self.current_post, dt_str)
        self._log(f"📅 예약 추가: {dt_str}")
        self._refresh_queue_table()

    def _remove_from_queue_ui(self):
        row = self.tbl_queue.currentRow()
        if row < 0:
            return
        item_id = self.tbl_queue.item(row, 0).data(Qt.UserRole)
        if item_id:
            from core.scheduler import remove_from_queue
            remove_from_queue(item_id)
            self._refresh_queue_table()

    def _refresh_queue_table(self):
        from core.scheduler import load_queue
        queue = load_queue()
        self.tbl_queue.setRowCount(0)
        for item in queue:
            if item.get("status") == "pending":
                row = self.tbl_queue.rowCount()
                self.tbl_queue.insertRow(row)
                dt_item = QTableWidgetItem(item.get("scheduled_time", ""))
                dt_item.setData(Qt.UserRole, item.get("id"))
                self.tbl_queue.setItem(row, 0, dt_item)
                title = item.get("post_data", {}).get("title", "제목 없음")
                self.tbl_queue.setItem(row, 1, QTableWidgetItem(title[:20]))

    def _open_json(self):
        path, _ = QFileDialog.getOpenFileName(self, "JSON 파일 선택", "", "JSON Files (*.json)")
        if path:
            self.json_import_path = path
            self.lbl_json_file.setText(os.path.basename(path))

    def _publish_json(self):
        path = getattr(self, "json_import_path", None)
        if not path:
            self._log("⚠ JSON 파일을 먼저 선택하세요.")
            return
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
            posts = data if isinstance(data, list) else [data]
            self._log(f"JSON 발행 시작: {len(posts)}개 포스트")

            def task():
                from core.naver_automation import publish_post
                for p in posts:
                    publish_post(p, log_callback=self._log)
                    time.sleep(5)
                return True

            self.worker = WorkerThread(task)
            self.worker.log_signal.connect(self._log)
            self.worker.done_signal.connect(lambda ok, _: self._log("JSON 발행 완료!" if ok else "발행 실패"))
            self.worker.start()
        except Exception as e:
            self._log(f"JSON 파일 오류: {e}")

    def _rewrite_post(self):
        if not self.current_post:
            self._log("⚠ 먼저 포스트를 생성하세요.")
            return
        self._log("글 리라이트 시작...")

        def task():
            from core.ai_generator import rewrite_post
            original = "\n".join(
                para
                for sec in self.current_post.get("sections", [])
                for sub in sec.get("subsections", [])
                for para in sub.get("paragraphs", [])
            )
            return rewrite_post(original, self.style_index)

        self.worker = WorkerThread(task)
        self.worker.log_signal.connect(self._log)
        self.worker.done_signal.connect(self._on_generate_done)
        self.worker.start()
