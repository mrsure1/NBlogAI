import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("NBlogAI")
    app.setOrganizationName("NBlogAI")

    font = QFont("Malgun Gothic", 10)
    font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    app.setFont(font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
