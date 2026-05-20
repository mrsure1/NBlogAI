MAIN_STYLE = """
QMainWindow, QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: 'Malgun Gothic', '맑은 고딕', sans-serif;
    font-size: 14px;
}

QLabel {
    color: #cdd6f4;
    padding: 4px 2px 4px 2px;
    min-height: 22px;
}

QTabWidget::pane {
    border: 1px solid #313244;
    background-color: #1e1e2e;
    border-radius: 6px;
}

QTabBar::tab {
    background-color: #181825;
    color: #a6adc8;
    padding: 14px 22px 14px 22px;
    border: none;
    font-size: 14px;
    min-width: 140px;
    min-height: 44px;
}

QTabBar::tab:selected {
    background-color: #89b4fa;
    color: #1e1e2e;
    font-weight: bold;
    border-radius: 4px 4px 0 0;
}

QTabBar::tab:hover:!selected {
    background-color: #313244;
    color: #cdd6f4;
}

QPushButton {
    background-color: #89b4fa;
    color: #1e1e2e;
    border: none;
    border-radius: 6px;
    padding: 12px 18px 12px 18px;
    font-weight: bold;
    font-size: 13px;
    min-height: 40px;
}

QPushButton:hover {
    background-color: #b4d0ff;
}

QPushButton:pressed {
    background-color: #6b9de8;
}

QPushButton:disabled {
    background-color: #45475a;
    color: #6c7086;
}

QPushButton#btnGreen {
    background-color: #a6e3a1;
}
QPushButton#btnGreen:hover { background-color: #c3f0bc; }

QPushButton#btnRed {
    background-color: #f38ba8;
}
QPushButton#btnRed:hover { background-color: #f5a3b8; }

QPushButton#btnYellow {
    background-color: #f9e2af;
    color: #1e1e2e;
}
QPushButton#btnYellow:hover { background-color: #fbecc2; }

QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 10px 12px 10px 12px;
    color: #cdd6f4;
    selection-background-color: #89b4fa;
}

QLineEdit {
    min-height: 24px;
}

QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #89b4fa;
}

QComboBox {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 10px 12px 10px 12px;
    color: #cdd6f4;
    min-width: 100px;
    min-height: 40px;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox QAbstractItemView {
    background-color: #313244;
    border: 1px solid #45475a;
    color: #cdd6f4;
    selection-background-color: #89b4fa;
    selection-color: #1e1e2e;
}

QSpinBox {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 10px 12px 10px 12px;
    color: #cdd6f4;
    min-height: 40px;
}

QGroupBox {
    border: 1px solid #45475a;
    border-radius: 8px;
    margin-top: 20px;
    padding-top: 12px;
    font-weight: bold;
    color: #89b4fa;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 2px 8px 0px 8px;
    left: 12px;
    top: -11px;
    background-color: #1e1e2e;
}

QScrollBar:vertical {
    background-color: #181825;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background-color: #45475a;
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #89b4fa;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

QLabel#labelTitle {
    font-size: 16px;
    font-weight: bold;
    color: #89b4fa;
    min-height: 26px;
    padding: 4px 2px;
}

QLabel#labelSub {
    color: #a6adc8;
    font-size: 12px;
    min-height: 18px;
    padding: 2px;
}

QCheckBox {
    spacing: 8px;
    color: #cdd6f4;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 2px solid #45475a;
    border-radius: 4px;
    background-color: #313244;
}

QCheckBox::indicator:checked {
    background-color: #89b4fa;
    border-color: #89b4fa;
}

QRadioButton {
    spacing: 8px;
    color: #cdd6f4;
}

QRadioButton::indicator {
    width: 14px;
    height: 14px;
    border: 2px solid #45475a;
    border-radius: 7px;
    background-color: #313244;
}

QRadioButton::indicator:checked {
    background-color: #89b4fa;
    border-color: #89b4fa;
}

QProgressBar {
    border: 1px solid #45475a;
    border-radius: 6px;
    background-color: #313244;
    text-align: center;
    color: #cdd6f4;
    height: 20px;
}

QProgressBar::chunk {
    background-color: #89b4fa;
    border-radius: 5px;
}

QTableWidget {
    background-color: #313244;
    alternate-background-color: #2a2a3e;
    border: 1px solid #45475a;
    border-radius: 6px;
    gridline-color: #45475a;
}

QTableWidget::item {
    padding: 6px;
    color: #cdd6f4;
}

QTableWidget::item:selected {
    background-color: #89b4fa;
    color: #1e1e2e;
}

QHeaderView::section {
    background-color: #181825;
    color: #89b4fa;
    padding: 8px;
    border: none;
    border-bottom: 1px solid #45475a;
    font-weight: bold;
}

QSplitter::handle {
    background-color: #45475a;
    width: 2px;
}

QDateTimeEdit {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 6px 10px;
    color: #cdd6f4;
}
"""

LOG_STYLE = """
QTextEdit {
    background-color: #11111b;
    color: #a6e3a1;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    border: 1px solid #313244;
    border-radius: 6px;
    padding: 8px;
}
"""

CARD_STYLE = """
QGroupBox {
    background-color: #24273a;
    border: 1px solid #313244;
    border-radius: 10px;
}
"""
