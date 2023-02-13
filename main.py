import sys



from PyQt6.QtCore import QSize, Qt, QRect
from PyQt6.QtGui import QAction, QIcon, QKeySequence
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QLabel,
    QMainWindow,
    QStatusBar,
    QToolBar
)

from gui import qtelements


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(900,1650)
        dia_size = (1050,550)
        dia = qtelements.DiaWidget(self)
        dia.setGeometry(QRect(0, 0, 1050, 550))
    
    def update(self):
        print("update 1")

if __name__ == "__main__":

    app = QApplication(sys.argv)
    mainwindow = MainWindow()
    #mainwindow.showFullScreen()
    mainwindow.show()
    app.exec()
