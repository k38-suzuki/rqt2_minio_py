import logging
import boto3
from botocore.exceptions import ClientError
import os

from python_qt_binding.QtWidgets import QMainWindow
from python_qt_binding.QtWidgets import QAbstractItemView
from python_qt_binding.QtWidgets import QAction
from python_qt_binding.QtWidgets import QDialog
from python_qt_binding.QtWidgets import QDialogButtonBox
from python_qt_binding.QtWidgets import QFileDialog
from python_qt_binding.QtWidgets import QFormLayout
from python_qt_binding.QtWidgets import QGroupBox
from python_qt_binding.QtWidgets import QInputDialog
from python_qt_binding.QtWidgets import QLineEdit
from python_qt_binding.QtWidgets import QListWidget
from python_qt_binding.QtWidgets import QListWidgetItem
from python_qt_binding.QtWidgets import QMenu
from python_qt_binding.QtWidgets import QToolBar
from python_qt_binding.QtWidgets import QVBoxLayout
from python_qt_binding.QtWidgets import QWidget
from python_qt_binding.QtCore import QDir
from python_qt_binding.QtCore import Qt
from python_qt_binding.QtCore import Signal
from python_qt_binding.QtGui import QIcon

class MyDialog(QDialog):

    def __init__(self, parent=None):
        super(MyDialog, self).__init__(parent)

        self.line1 = QLineEdit()
        self.line1.setText('http://127.0.0.1:9000')
        self.line2 = QLineEdit()
        self.line2.setText('minioadmin')
        self.line3 = QLineEdit()
        self.line3.setText('minioadmin')

        formLayout = QFormLayout()
        formLayout.addRow('Endpoint url:', self.line1)
        formLayout.addRow('Access key:', self.line2)
        formLayout.addRow('Secret key:', self.line3)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok
                                    | QDialogButtonBox.Cancel)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(formLayout)
        layout.addWidget(self.buttonBox)
        layout.addStretch()

        self.setLayout(layout)
        self.setWindowTitle('Create Cred')

class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle('Minio Client')

        self.createActions()
        self.createMenus()
        self.createToolBars()

        self.list1 = QListWidget()
        # self.list1.setSelectionMode(QAbstractItemView.ContiguousSelection)
        self.list1.currentTextChanged.connect(self.listObjects)
        self.list1.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list1.customContextMenuRequested.connect(self.contextMenu1)

        self.list2 = QListWidget()
        # self.list2.setSelectionMode(QAbstractItemView.ContiguousSelection)
        self.list2.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list2.customContextMenuRequested.connect(self.contextMenu2)

        layout1 = QVBoxLayout()
        layout1.addWidget(self.list1)
        layout1.addStretch()

        layout2 = QVBoxLayout()
        layout2.addWidget(self.list2)
        layout2.addStretch()

        self.group1 = QGroupBox('Buckets')
        self.group1.setLayout(layout1)   

        self.group2 = QGroupBox('Objects')
        self.group2.setLayout(layout2)

        layout = QVBoxLayout()
        layout.addWidget(self.group1)
        layout.addWidget(self.group2)
        layout.addStretch()

        centralWidget = QWidget(self)
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

    def createActions(self):
        credIcon = QIcon.fromTheme('contact-new')
        self.actionCred = QAction(credIcon, '&Cred')
        self.actionCred.setStatusTip('Input a cred')
        self.actionCred.triggered.connect(self.createCred)

        createIcon = QIcon.fromTheme('list-add')
        self.actionCreate = QAction(createIcon, '&Create')
        self.actionCreate.setStatusTip('Create a bucket')
        self.actionCreate.triggered.connect(self.createBucket)

        deleteIcon = QIcon.fromTheme('list-remove')
        self.actionDelete1 = QAction(deleteIcon, '&Delete')
        self.actionDelete1.setStatusTip('Delete the checked bucket')
        self.actionDelete1.triggered.connect(self.deleteBucket)

        putIcon = QIcon.fromTheme('document-send')
        self.actionPut = QAction(putIcon, '&Upload')
        self.actionPut.setStatusTip('Upload a object')
        self.actionPut.triggered.connect(self.putObject)

        delete2Icon = QIcon.fromTheme('user-trash')
        self.actionDelete2 = QAction(delete2Icon, '&Delete')
        self.actionDelete2.setStatusTip('Delete the checked object')
        self.actionDelete2.triggered.connect(self.deleteObject)

        getIcon = QIcon.fromTheme('document-save')
        self.actionGet = QAction(getIcon, '&Download')
        self.actionGet.setStatusTip('Download the checked object')
        self.actionGet.triggered.connect(self.getObject)

        self.actionCheckAll1 = QAction('&Check all')
        self.actionCheckAll1.setStatusTip('Check all buckets')
        self.actionCheckAll1.triggered.connect(self.checkAllBuckets)

        self.actionCheckAll2 = QAction('&Check all')
        self.actionCheckAll2.setStatusTip('Check all objects')
        self.actionCheckAll2.triggered.connect(self.checkAllObjects)

        self.actionUncheckAll1 = QAction('&Uncheck all')
        self.actionUncheckAll1.setStatusTip('Uncheck all buckets')
        self.actionUncheckAll1.triggered.connect(self.uncheckAllBuckets)

        self.actionUncheckAll2 = QAction('&Uncheck all')
        self.actionUncheckAll2.setStatusTip('Uncheck all objects')
        self.actionUncheckAll2.triggered.connect(self.uncheckAllObjects)

    def createMenus(self):
        fileMenu = self.menuBar().addMenu("&File")
        fileMenu.addAction(self.actionCreate)
        fileMenu.addAction(self.actionDelete1)
        fileMenu.addSeparator()

        fileMenu.addAction(self.actionPut)
        fileMenu.addAction(self.actionGet)
        fileMenu.addSeparator()

        bucketMenu = self.menuBar().addMenu("&Bucket")
        bucketMenu.addAction(self.actionCheckAll1)
        bucketMenu.addAction(self.actionUncheckAll1)
        bucketMenu.addSeparator()

        objectMenu = self.menuBar().addMenu("&Object")
        objectMenu.addAction(self.actionCheckAll2)
        objectMenu.addAction(self.actionUncheckAll2)
        objectMenu.addSeparator()

    def createToolBars(self):
        fileToolBar = self.addToolBar("File")
        fileToolBar.addAction(self.actionCred)
        fileToolBar.addSeparator()

        fileToolBar.addAction(self.actionPut)
        fileToolBar.addAction(self.actionGet)
        fileToolBar.addSeparator()

        fileToolBar.addAction(self.actionDelete2)
        fileToolBar.addSeparator()

        fileToolBar.setAllowedAreas(Qt.TopToolBarArea | Qt.BottomToolBarArea)
        self.addToolBar(Qt.TopToolBarArea, fileToolBar)

    def createCred(self):
        dialog = MyDialog(self)

        if dialog.exec_():
            endpoint_url = dialog.line1.text()
            access_key = dialog.line2.text()
            secret_key = dialog.line3.text()

            if endpoint_url and access_key and secret_key:
                self.s3_client = boto3.client('s3', endpoint_url=endpoint_url, aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key)
                self.s3_resource = boto3.resource('s3', endpoint_url=endpoint_url, aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key)

                print('S3 client has been created.')
                print(endpoint_url, access_key, secret_key)
                self.listBuckets()

    def createBucket(self):
        text, ok = QInputDialog().getText(self, "Create Bucket",
            "Bucket name:", QLineEdit.Normal,
            QDir().home().dirName())

        if ok and text:
            bucket_name = text

            try:
                response = self.s3_client.create_bucket(Bucket=bucket_name)
                print('Bucket:', bucket_name, 'has been created.')
                self.listBuckets()
            except ClientError as e:
                logging.error(e)
                return False
            return True

    def deleteBucket(self):
        for i in range(self.list1.count()):
            item = self.list1.item(i)
            if item.checkState() == Qt.Checked:
                bucket_name = item.text()

                response = self.s3_client.delete_bucket(Bucket=bucket_name)
                print('Bucket:', bucket_name, 'has been deleted.')
                self.listBuckets()

    def listBuckets(self):
        response = self.s3_client.list_buckets()

        print('Existing buckets:')
        self.list1.clear()
        bucket_names = []
        for bucket in response['Buckets']:
            item = QListWidgetItem()
            item.setText(bucket["Name"])
            item.setCheckState(Qt.Unchecked)
            self.list1.addItem(item)
            self.list1.setCurrentItem(item)
            bucket_names.append(bucket["Name"])
            print(f'  {bucket["Name"]}')
        self.bucketListed.emit(bucket_names)

    def checkAllBuckets(self):
        for i in range(self.list1.count()):
            item = self.list1.item(i)
            item.setCheckState(Qt.Checked)

    def uncheckAllBuckets(self):
        for i in range(self.list1.count()):
            item = self.list1.item(i)
            item.setCheckState(Qt.Unchecked)

    def putObject(self):
        item = self.list1.currentItem()
        if item:
            bucket_name = item.text()

            dialog = QFileDialog(self)
            dialog.setFileMode(QFileDialog.AnyFile)
            # dialog.setNameFilter("Images (*.png *.xpm *.jpg)")
            dialog.setViewMode(QFileDialog.Detail)

            if dialog.exec_():
                file_names = dialog.selectedFiles()
                for file_name in file_names:
                    object_name = os.path.basename(file_name)
                    if file_name and object_name:
                        try:
                            response = self.s3_client.upload_file(Filename=file_name, Bucket=bucket_name, Key=object_name)
                            print('Object:', object_name, 'has been uploaded from', bucket_name, '.')
                            self.listObjects()
                        except ClientError as e:
                            logging.error(e)
                            return False
                        return True

    def deleteObject(self):
        item1 = self.list1.currentItem()
        if item1:
            bucket_name = item1.text()

            for i in range(self.list2.count()):
                item2 = self.list2.item(i)
                if item2.checkState() == Qt.Checked:
                    object_name = item2.text()

                    response = self.s3_client.delete_object(Bucket=bucket_name, Key=object_name)
                    print('Object:', object_name, 'has been deleted from', bucket_name, ".")
                    self.listObjects()

    def getObject(self):
        item1 = self.list1.currentItem()
        if item1:
            bucket_name = item1.text()

            object_names = []
            for i in range(self.list2.count()):
                item2 = self.list2.item(i)
                if item2.checkState() == Qt.Checked:
                    object_names.append(item2.text())

            if len(object_names) > 0:
                dir = QFileDialog.getExistingDirectory(self, "Open Directory",
                                                    QDir().home().dirName(),
                                                    QFileDialog.ShowDirsOnly
                                                    | QFileDialog.DontResolveSymlinks)
                if dir:
                    for object_name in object_names:
                        file_name = dir + '/' + object_name
                        self.s3_client.download_file(Bucket=bucket_name, Key=object_name, Filename=file_name)
                        print('Object:', object_name, 'has been downloaded from', bucket_name, '.')

    def listObjects(self):
        item = self.list1.currentItem()
        if item:
            bucket_name = item.text()

            resource = self.s3_resource.Bucket(bucket_name)
            self.list2.clear()
            object_names = []
            for summary in resource.objects.all():
                item = QListWidgetItem()
                item.setText(summary.key)
                item.setCheckState(Qt.Unchecked)
                self.list2.addItem(item)
                self.list2.setCurrentItem(item)
                object_names.append(summary.key)
                print(summary.key)
            self.objectListed.emit(object_names)

    def checkAllObjects(self):
        for i in range(self.list2.count()):
            item = self.list2.item(i)
            item.setCheckState(Qt.Checked)

    def uncheckAllObjects(self):
        for i in range(self.list2.count()):
            item = self.list2.item(i)
            item.setCheckState(Qt.Unchecked)

    def contextMenu1(self, pos):
        menu = QMenu()
        infoIcon = QIcon.fromTheme('dialog-information')
        actionInfo = QAction(infoIcon, '&Info')
        actionInfo.triggered.connect(self.showBucketInfo)
        menu.addAction(actionInfo)
        menu.exec_(self.list1.mapToGlobal(pos))

    def contextMenu2(self, pos):
        menu = QMenu()
        infoIcon = QIcon.fromTheme('dialog-information')
        actionInfo = QAction(infoIcon, '&Info')
        actionInfo.triggered.connect(self.showObjectInfo)
        menu.addAction(actionInfo)
        menu.exec_(self.list2.mapToGlobal(pos))
    
    def showBucketInfo(self):
        print('bucket info')
    
    def showObjectInfo(self):
        print('object info')

    bucketListed = Signal(list)

    objectListed = Signal(list)