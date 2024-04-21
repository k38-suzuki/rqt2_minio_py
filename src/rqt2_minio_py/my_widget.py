from python_qt_binding.QtWidgets import QWidget
from python_qt_binding.QtWidgets import QAbstractItemView
from python_qt_binding.QtWidgets import QGroupBox
from python_qt_binding.QtWidgets import QListWidget
from python_qt_binding.QtWidgets import QVBoxLayout

from rqt2_minio_py.my_toolbar import MyToolBar

class MyWidget(QWidget):

    def __init__(self, parent=None):
        super(MyWidget, self).__init__(parent)
        self.setWindowTitle('My Widget')

        self.bar = MyToolBar()
        self.bar.bucketListed.connect(self.list_buckets)
        self.bar.objectListed.connect(self.list_objects)

        self.list1 = QListWidget()
        self.list1.setSelectionMode(QAbstractItemView.ContiguousSelection)
        self.list1.currentTextChanged.connect(self.select_bucket)

        self.list2 = QListWidget()
        self.list2.currentTextChanged.connect(self.select_object)
        self.list2.setSelectionMode(QAbstractItemView.ContiguousSelection)

        layout2 = QVBoxLayout()
        layout2.addWidget(self.list1)
        layout2.addStretch()

        layout3 = QVBoxLayout()
        layout3.addWidget(self.list2)
        layout3.addStretch()

        self.group1 = QGroupBox('Buckets')
        self.group1.setLayout(layout2)   

        self.group2 = QGroupBox('Objects')
        self.group2.setLayout(layout3)

        layout = QVBoxLayout()
        layout.addWidget(self.bar)
        # layout.addWidget(self.group1)
        # layout.addWidget(self.group2)
        layout.addStretch()
        self.setLayout(layout)

    def list_buckets(self, bucket_names):
        self.list1.clear()
        self.list1.addItems(bucket_names)

    def list_objects(self, object_names):
        self.list2.clear()
        self.list2.addItems(object_names)

    def select_bucket(self, currentText):
        self.bar.bucketCombo.setCurrentText(currentText)

    def select_object(self, currentText):
        self.bar.objectCombo.setCurrentText(currentText)
