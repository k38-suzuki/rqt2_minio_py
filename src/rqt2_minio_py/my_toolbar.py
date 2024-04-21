import logging
import boto3
from botocore.exceptions import ClientError
import os

from python_qt_binding.QtWidgets import QToolBar
from python_qt_binding.QtWidgets import QAbstractItemView
from python_qt_binding.QtWidgets import QAction
from python_qt_binding.QtWidgets import QComboBox
from python_qt_binding.QtWidgets import QDialog
from python_qt_binding.QtWidgets import QDialogButtonBox
from python_qt_binding.QtWidgets import QFileDialog
from python_qt_binding.QtWidgets import QFormLayout
from python_qt_binding.QtWidgets import QInputDialog
from python_qt_binding.QtWidgets import QLineEdit
from python_qt_binding.QtWidgets import QListWidget
from python_qt_binding.QtWidgets import QVBoxLayout
from python_qt_binding.QtCore import QDir
from python_qt_binding.QtCore import Signal
from python_qt_binding.QtGui import QIcon

class MyDialog(QDialog):

    def __init__(self, parent=None):
        super(MyDialog, self).__init__(parent)
        self.setWindowTitle('MyDialog')

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

class MyDialog2(QDialog):

    def __init__(self, parent=None):
        super(MyDialog2, self).__init__(parent)
        self.setWindowTitle('Select Objects')

        self.list = QListWidget()
        self.list.setSelectionMode(QAbstractItemView.ContiguousSelection)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok
                                    | QDialogButtonBox.Cancel)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.list)
        layout.addWidget(self.buttonBox)
        layout.addStretch()
        self.setLayout(layout)

class MyToolBar(QToolBar):

    def __init__(self, parent=None):
        super(MyToolBar, self).__init__(parent)

        credIcon = QIcon.fromTheme('preferences-system-network')
        self.actionCred = QAction(credIcon, '&Cred')
        self.actionCred.setStatusTip('Input a cred')
        self.actionCred.triggered.connect(self.create_cred)
        self.addAction(self.actionCred)

        self.bucketCombo = QComboBox()
        self.bucketCombo.setStatusTip('Select a bucket')
        self.bucketCombo.currentTextChanged.connect(self.list_objects)
        self.addWidget(self.bucketCombo)

        createIcon = QIcon.fromTheme('list-add')
        self.actionCreate = QAction(createIcon, '&Create')
        self.actionCreate.setStatusTip('Create a bucket')
        self.actionCreate.triggered.connect(self.create_bucket)
        self.addAction(self.actionCreate)

        deleteIcon = QIcon.fromTheme('list-remove')
        self.actionDelete = QAction(deleteIcon, '&Delete')
        self.actionDelete.setStatusTip('Delete the bucket')
        self.actionDelete.triggered.connect(self.delete_bucket)
        self.addAction(self.actionDelete)
        self.addSeparator()

        self.objectCombo = QComboBox()
        self.objectCombo.setStatusTip('Select an object')
        self.addWidget(self.objectCombo)

        putIcon = QIcon.fromTheme('list-add')
        self.actionPut = QAction(putIcon, '&Upload')
        self.actionPut.setStatusTip('Upload a object')
        self.actionPut.triggered.connect(self.put_object)
        self.addAction(self.actionPut)

        delete2Icon = QIcon.fromTheme('list-remove')
        self.actionDelete2 = QAction(delete2Icon, '&Delete')
        self.actionDelete2.setStatusTip('Delete the object')
        self.actionDelete2.triggered.connect(self.delete_object)
        self.addAction(self.actionDelete2)

        getIcon = QIcon.fromTheme('document-save-as')
        self.actionGet = QAction(getIcon, '&Download')
        self.actionGet.setStatusTip('Download the object')
        self.actionGet.triggered.connect(self.get_object)
        self.addAction(self.actionGet)

    def create_cred(self):
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
                self.list_buckets()

    def create_bucket(self):
        text, ok = QInputDialog().getText(self, "Create Bucket",
            "Bucket name:", QLineEdit.Normal,
            QDir().home().dirName())

        if ok and text:
            bucket_name = text
            if bucket_name:
                try:
                    response = self.s3_client.create_bucket(Bucket=bucket_name)
                    print('Bucket:', bucket_name, 'has been created.')
                    self.list_buckets()
                    self.bucketCombo.setCurrentText(bucket_name)
                except ClientError as e:
                    logging.error(e)
                    return False
                return True

    def delete_bucket(self):
        bucket_name = self.bucketCombo.currentText()
        if bucket_name:
            self.delete_selected_bucket(bucket_name)
    
    def delete_selected_bucket(self, bucket_name):
        if bucket_name:
            response = self.s3_client.delete_bucket(Bucket=bucket_name)
            print('Bucket:', bucket_name, 'has been deleted.')
            self.list_buckets()

    def list_buckets(self):
        response = self.s3_client.list_buckets()

        print('Existing buckets:')
        self.bucketCombo.clear()
        bucket_names = []
        for bucket in response['Buckets']:
            self.bucketCombo.addItem(bucket["Name"])
            bucket_names.append(bucket["Name"])
            print(f'  {bucket["Name"]}')
        self.bucketListed.emit(bucket_names)

    def put_object(self):
        bucket_name = self.bucketCombo.currentText()
        if bucket_name:
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
                            self.list_objects()
                        except ClientError as e:
                            logging.error(e)
                            return False
                        return True

    def delete_object(self):
        object_name = self.objectCombo.currentText()
        if object_name:
            self.delete_selected_object(object_name)

    def delete_selected_object(self, object_name):
        bucket_name = self.bucketCombo.currentText()
        if bucket_name and object_name:
            response = self.s3_client.delete_object(Bucket=bucket_name, Key=object_name)
            print('Object:', object_name, 'has been deleted from', bucket_name, ".")
            self.list_objects()

    def get_object(self):
        bucket_name = self.bucketCombo.currentText()
        if bucket_name:
            dialog = MyDialog2(self)
            for i in range(self.objectCombo.count()):
                dialog.list.addItem(self.objectCombo.itemText(i))

            if dialog.exec_():
                selected_items = dialog.list.selectedItems()

                if len(selected_items) > 0:
                    dir = QFileDialog.getExistingDirectory(self, "Open Directory",
                                                        QDir().home().dirName(),
                                                        QFileDialog.ShowDirsOnly
                                                        | QFileDialog.DontResolveSymlinks)
                    if dir:
                        for selected_item in selected_items:
                            object_name = selected_item.text()
                            file_name = dir + '/' + object_name
                            self.s3_client.download_file(Bucket=bucket_name, Key=object_name, Filename=file_name)
                            print('Object:', object_name, 'has been downloaded from', bucket_name, '.')

    def list_objects(self):
        bucket_name = self.bucketCombo.currentText()
        if bucket_name:
            resource = self.s3_resource.Bucket(bucket_name)
            self.objectCombo.clear()
            object_names = []
            for summary in resource.objects.all():
                self.objectCombo.addItem(summary.key)
                object_names.append(summary.key)
                print(summary.key)
            self.objectListed.emit(object_names)

    bucketListed = Signal(list)

    objectListed = Signal(list)
