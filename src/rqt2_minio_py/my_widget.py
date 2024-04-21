from python_qt_binding.QtWidgets import QWidget
from python_qt_binding.QtWidgets import QVBoxLayout

from rqt2_minio_py.my_toolbar import MyToolBar

class MyWidget(QWidget):

    def __init__(self, parent=None):
        super(MyWidget, self).__init__(parent)
        self.setWindowTitle('My Widget')

        self.bar = MyToolBar()

        layout = QVBoxLayout()
        layout.addWidget(self.bar)
        layout.addStretch()
        self.setLayout(layout)
