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
from python_qt_binding.QtWidgets import QGridLayout
from python_qt_binding.QtWidgets import QGroupBox
from python_qt_binding.QtWidgets import QHBoxLayout
from python_qt_binding.QtWidgets import QInputDialog
from python_qt_binding.QtWidgets import QLabel
from python_qt_binding.QtWidgets import QLineEdit
from python_qt_binding.QtWidgets import QListWidget
from python_qt_binding.QtWidgets import QListWidgetItem
from python_qt_binding.QtWidgets import QMenu
from python_qt_binding.QtWidgets import QToolBar
from python_qt_binding.QtWidgets import QTreeWidget
from python_qt_binding.QtWidgets import QTreeWidgetItem
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

class MyDialog2(QDialog):

    def __init__(self, parent=None):
        super(MyDialog2, self).__init__(parent)

        list1 = []
        list1.append('Info')
        list1.append('Value')

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(list1)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)

        self.buttonBox.accepted.connect(self.accept)

        layout = QVBoxLayout()
        layout.addWidget(self.tree)
        layout.addWidget(self.buttonBox)
        # layout.addStretch()

        self.setLayout(layout)
        self.setWindowTitle('Object Info')

class MyDialog3(QDialog):

    def __init__(self, parent=None):
        super(MyDialog3, self).__init__(parent)

        self.lines1 = []
        self.lines2 = []

        gridLayout = QGridLayout()
        for i in range(10):
            line1 = QLineEdit()
            line2 = QLineEdit()
            gridLayout.addWidget(QLabel("Key" + str(i)), i, 0)
            gridLayout.addWidget(line1, i, 1)
            gridLayout.addWidget(QLabel("Value" + str(i)), i, 2)
            gridLayout.addWidget(line2, i, 3)
            self.lines1.append(line1)
            self.lines2.append(line2)
        
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok
                                    | QDialogButtonBox.Cancel)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(gridLayout)
        layout.addWidget(self.buttonBox)
        # layout.addStretch()

        self.setLayout(layout)
        self.setWindowTitle('Put Object')

class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle('Minio Client')

        self.createActions()
        self.createMenus()
        self.createToolBars()

        self.line1 = QLineEdit()
        self.line1.setPlaceholderText('Filter Buckets')
        self.line1.textChanged.connect(self.filterBuckets)

        self.line2 = QLineEdit()
        self.line2.setPlaceholderText('Start typing to filter objects in the bucket')
        self.line2.textChanged.connect(self.filterObjects)

        self.list1 = QListWidget()
        # self.list1.setSelectionMode(QAbstractItemView.ContiguousSelection)
        self.list1.currentTextChanged.connect(self.listObjects)
        self.list1.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.list1.customContextMenuRequested.connect(self.contextMenu1)

        self.list2 = QListWidget()
        # self.list2.setSelectionMode(QAbstractItemView.ContiguousSelection)
        self.list2.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list2.customContextMenuRequested.connect(self.contextMenu2)

        layout1 = QHBoxLayout()
        layout1.addWidget(self.line1)
        layout1.addWidget(self.bucketToolBar)

        layout2 = QVBoxLayout()
        layout2.addLayout(layout1)
        layout2.addWidget(self.list1)
        # layout2.addStretch()

        layout3 = QHBoxLayout()
        layout3.addWidget(self.line2)
        layout3.addWidget(self.objectToolBar)

        layout4 = QVBoxLayout()
        layout4.addLayout(layout3)
        layout4.addWidget(self.list2)
        # layout4.addStretch()

        self.group1 = QGroupBox('Buckets')
        self.group1.setLayout(layout2)   

        self.group2 = QGroupBox('Objects')
        self.group2.setLayout(layout4)

        layout = QVBoxLayout()
        layout.addWidget(self.group1)
        layout.addWidget(self.group2)
        # layout.addStretch()

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

        delete1Icon = QIcon.fromTheme('list-remove')
        self.actionDelete1 = QAction(delete1Icon, '&Delete')
        self.actionDelete1.setStatusTip('Delete the checked bucket')
        self.actionDelete1.triggered.connect(self.deleteBucket)

        putIcon = QIcon.fromTheme('document-send')
        self.actionPut = QAction(putIcon, '&Upload')
        self.actionPut.setStatusTip('Upload a object')
        self.actionPut.triggered.connect(self.putObject)

        taggingIcon = QIcon.fromTheme('dialog-information')
        self.actionTagging = QAction(taggingIcon, '&Tagging')
        self.actionTagging.setStatusTip('Put a object tagging')
        self.actionTagging.triggered.connect(self.putObjectTagging)

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

        fileToolBar.setAllowedAreas(Qt.TopToolBarArea | Qt.BottomToolBarArea)
        self.addToolBar(Qt.TopToolBarArea, fileToolBar)

        self.bucketToolBar = self.addToolBar('Bucket')
        self.bucketToolBar.addAction(self.actionCreate)
        self.bucketToolBar.addAction(self.actionDelete1)
        self.bucketToolBar.addSeparator()

        self.objectToolBar = self.addToolBar('Object')
        self.objectToolBar.addAction(self.actionPut)
        self.objectToolBar.addAction(self.actionTagging)
        self.objectToolBar.addAction(self.actionGet)
        self.objectToolBar.addSeparator()

        self.objectToolBar.addAction(self.actionDelete2)
        self.objectToolBar.addSeparator()

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

    def putObjectTagging(self):
        item1 = self.list1.currentItem()
        if item1:
            bucket_name = item1.text()

            dialog = MyDialog3(self)

            if dialog.exec_():
                for i in range(self.list2.count()):
                    item2 = self.list2.item(i)
                    if item2.checkState() == Qt.Checked:
                        object_name = item2.text()

                        tagging = {}
                        tagset = []
                        tagging['TagSet'] = tagset
                        for j in range(10):
                            text1 = dialog.lines1[j].text()
                            text2 = dialog.lines2[j].text()
                            if text1 and text2:
                                tag = {}
                                tag['Key'] = text1
                                tag['Value'] = text2
                                tagset.append(tag)
                        
                        response = self.s3_client.put_object_tagging(Bucket=bucket_name, Key=object_name, Tagging=tagging)
                        print('Object:', object_name, 'has been updated.')

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

            # response = self.s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=1000)
            # self.list2.clear()
            # object_names = []
            # for object_name in response['Contents']:
            #     item = QListWidgetItem()
            #     item.setText(object_name['Key'])
            #     item.setCheckState(Qt.Unchecked)
            #     self.list2.addItem(item)
            #     self.list2.setCurrentItem(item)
            #     object_names.append(object_name['Key'])
            #     print(object_name['Key'])
            # self.objectListed.emit(object_names)

            resource = self.s3_resource.Bucket(bucket_name)
            self.list2.clear()
            object_names = []
            for summary in resource.objects.all():
                object_name = summary.key
                item = QListWidgetItem()
                item.setText(object_name)
                item.setCheckState(Qt.Unchecked)
                self.list2.addItem(item)
                self.list2.setCurrentItem(item)
                object_names.append(object_name)
                print(object_name)
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
        item = self.list1.currentItem()
        if item:
            menu = QMenu()
            infoIcon = QIcon.fromTheme('document-properties')
            actionInfo = QAction(infoIcon, '&Info')
            actionInfo.triggered.connect(self.showBucketInfo)
            menu.addAction(actionInfo)
            menu.exec_(self.list1.mapToGlobal(pos))

    def contextMenu2(self, pos):
        item = self.list2.currentItem()
        if item:
            menu = QMenu()
            infoIcon = QIcon.fromTheme('dialog-information')
            actionInfo = QAction(infoIcon, '&Info')
            actionInfo.triggered.connect(self.showObjectInfo)
            menu.addAction(actionInfo)
            menu.exec_(self.list2.mapToGlobal(pos))
    
    def showBucketInfo(self):
        print('bucket info')
    
    def showObjectInfo(self):
        item1 = self.list1.currentItem()
        item2 = self.list2.currentItem()
        if item1 and item2:
            bucket_name = item1.text()
            object_name = item2.text()

            response = self.s3_client.head_object(Bucket=bucket_name, Key=object_name)
            response2 = self.s3_client.get_object_tagging(Bucket=bucket_name, Key=object_name)

            text1 = str(response['ContentLength'])
            text2 = response['ContentType']
            text3 = response['ETag']
            text4 = response['LastModified'].strftime('%Y/%m/%d %H:%M:%S.%f')

            dialog = MyDialog2(self)
            item1 = QTreeWidgetItem()
            item1.setText(0, 'ContentLength [bytes]')
            item1.setText(1, text1)
            dialog.tree.addTopLevelItem(item1)

            item2 = QTreeWidgetItem()
            item2.setText(0, 'ContentType')
            item2.setText(1, text2)
            dialog.tree.addTopLevelItem(item2)

            item3 = QTreeWidgetItem()
            item3.setText(0, 'ETag')
            item3.setText(1, text3)
            dialog.tree.addTopLevelItem(item3)

            item4 = QTreeWidgetItem()
            item4.setText(0, 'LastModified')
            item4.setText(1, text4)
            dialog.tree.addTopLevelItem(item4)

            tagset = response2['TagSet']
            for tag in tagset:
                key = tag['Key']
                value = tag['Value']
                item = QTreeWidgetItem()
                item.setText(0, 'Key:' + key)
                item.setText(1, value)
                dialog.tree.addTopLevelItem(item)

            if dialog.exec_():
                print('Close the info dialog')

    def filterBuckets(self, text):
        self.listBuckets()
        if text:
            bucket_names = []
            for i in range(self.list1.count()):
                item = self.list1.item(i)
                bucket_name = item.text()
                if text in bucket_name:
                    bucket_names.append(bucket_name)
            
            self.list1.clear()
            for bucket_name in bucket_names:
                item = QListWidgetItem()
                item.setText(bucket_name)
                item.setCheckState(Qt.Unchecked)
                self.list1.addItem(item)
                self.list1.setCurrentItem(item)
            print('Filtered buckets:', bucket_names)

    def filterObjects(self, text):
        self.listObjects()
        if text:
            object_names = []
            for i in range(self.list2.count()):
                item = self.list2.item(i)
                object_name = item.text()
                if text in object_name:
                    object_names.append(object_name)

            self.list2.clear()
            for object_name in object_names:
                item = QListWidgetItem()
                item.setText(object_name)
                item.setCheckState(Qt.Unchecked)
                self.list2.addItem(item)
                self.list2.setCurrentItem(item)
            print('Filtered objects:', object_names)

    bucketListed = Signal(list)

    objectListed = Signal(list)
