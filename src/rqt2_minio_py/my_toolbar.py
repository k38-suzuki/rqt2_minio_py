import logging
import boto3
from botocore.exceptions import ClientError
import os

from python_qt_binding.QtWidgets import QToolBar
from python_qt_binding.QtWidgets import QAction
from python_qt_binding.QtWidgets import QComboBox
from python_qt_binding.QtWidgets import QDialog
from python_qt_binding.QtWidgets import QDialogButtonBox
from python_qt_binding.QtWidgets import QFileDialog
from python_qt_binding.QtWidgets import QFormLayout
from python_qt_binding.QtWidgets import QInputDialog
from python_qt_binding.QtWidgets import QLineEdit
from python_qt_binding.QtWidgets import QVBoxLayout
from python_qt_binding.QtCore import QDir
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

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok
                                    | QDialogButtonBox.Cancel)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        formLayout = QFormLayout()
        formLayout.addRow('Endpoint url:', self.line1)
        formLayout.addRow('Access key:', self.line2)
        formLayout.addRow('Secret key:', self.line3)

        layout = QVBoxLayout()
        layout.addLayout(formLayout)
        layout.addWidget(self.buttonBox)
        layout.addStretch()
        self.setLayout(layout)

class MyToolBar(QToolBar):

    def __init__(self, parent=None):
        super(MyToolBar, self).__init__(parent)

        credIcon = QIcon.fromTheme('preferences-system-network')
        self.actionCred = QAction(credIcon, '&Cred')
        self.actionCred.setStatusTip('Input a cred')
        self.actionCred.triggered.connect(self.cred)
        self.addAction(self.actionCred)

        self.bucketCombo = QComboBox()
        self.bucketCombo.setStatusTip('Select a bucket')
        self.bucketCombo.currentTextChanged.connect(self.listObjects)
        self.addWidget(self.bucketCombo)

        createIcon = QIcon.fromTheme('list-add')
        self.actionCreate = QAction(createIcon, '&Create')
        self.actionCreate.setStatusTip('Create a bucket')
        self.actionCreate.triggered.connect(self.createBucket)
        self.addAction(self.actionCreate)

        deleteIcon = QIcon.fromTheme('list-remove')
        self.actionDelete = QAction(deleteIcon, '&Delete')
        self.actionDelete.setStatusTip('Delete the bucket')
        self.actionDelete.triggered.connect(self.deleteBucket)
        self.addAction(self.actionDelete)
        self.addSeparator()

        self.objectCombo = QComboBox()
        self.objectCombo.setStatusTip('Select an object')
        self.addWidget(self.objectCombo)

        putIcon = QIcon.fromTheme('list-add')
        self.actionPut = QAction(putIcon, '&Upload')
        self.actionPut.setStatusTip('Upload a object')
        self.actionPut.triggered.connect(self.putObject)
        self.addAction(self.actionPut)

        delete2Icon = QIcon.fromTheme('list-remove')
        self.actionDelete2 = QAction(delete2Icon, '&Delete')
        self.actionDelete2.setStatusTip('Delete the object')
        self.actionDelete2.triggered.connect(self.deleteObject)
        self.addAction(self.actionDelete2)

        getIcon = QIcon.fromTheme('document-save-as')
        self.actionGet = QAction(getIcon, '&Download')
        self.actionGet.setStatusTip('Download the object')
        self.actionGet.triggered.connect(self.getObject)
        self.addAction(self.actionGet)

    def cred(self):
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
                self.s3_client.create_bucket(Bucket=bucket_name)
                print('Bucket: ', bucket_name, ' has been created.')
                self.listBuckets()
                self.bucketCombo.setCurrentText(bucket_name)

            except ClientError as e:
                logging.error(e)
                return False
            return True

    def deleteBucket(self):
        bucket_name = self.bucketCombo.currentText()
        if bucket_name:
            self.s3_client.delete_bucket(Bucket=bucket_name)
            print('Bucket: ', bucket_name, ' has been deleted.')
            self.listBuckets()

    def listBuckets(self):
        response = self.s3_client.list_buckets()

        print('Existing buckets:')
        self.bucketCombo.clear()
        for bucket in response['Buckets']:
            self.bucketCombo.addItem(bucket["Name"])
            print(f'  {bucket["Name"]}')

    def putObject(self):
        bucket_name = self.bucketCombo.currentText()
        if bucket_name:
            dialog = QFileDialog(self)
            dialog.setFileMode(QFileDialog.AnyFile)
            # dialog.setNameFilter("Images (*.png *.xpm *.jpg)")
            dialog.setViewMode(QFileDialog.Detail)

            if dialog.exec_():
                file_names = dialog.selectedFiles()
                for file_name in file_names:
                    object_key = os.path.basename(file_name)
                    if file_name and object_key:
                        self.s3_client.upload_file(Filename=file_name, Bucket=bucket_name, Key=object_key)
                        print('Object: ', object_key, ' has been uploaded from ', bucket_name, ' .')
                        self.listObjects()

    def deleteObject(self):
        bucket_name = self.bucketCombo.currentText()
        object_key = self.objectCombo.currentText()
        if bucket_name and object_key:
            self.s3_client.delete_object(Bucket=bucket_name, Key=object_key)
            print('Object: ', object_key, ' has been deleted from ', bucket_name, " .")
            self.listObjects()

    def getObject(self):
        bucket_name = self.bucketCombo.currentText()
        object_key = self.objectCombo.currentText()
        if bucket_name and object_key:
            dialog = QFileDialog(self)
            dialog.setFileMode(QFileDialog.AnyFile)
            # dialog.setNameFilter("Images (*.png *.xpm *.jpg)")
            dialog.setViewMode(QFileDialog.Detail)
            dialog.setAcceptMode(QFileDialog.AcceptSave)

            if dialog.exec_():
                file_names = dialog.selectedFiles()
                for file_name in file_names:
                    if file_name:
                        self.s3_client.download_file(Bucket=bucket_name, Key=object_key, Filename=file_name)
                        print('Object: ', object_key, ' has been downloaded from ', bucket_name, ' .')

    def listObjects(self):
        bucket_name = self.bucketCombo.currentText()
        if bucket_name:
            try:
                resource = self.s3_resource.Bucket(bucket_name)
                self.objectCombo.clear()
                for summary in resource.objects.all():
                    self.objectCombo.addItem(summary.key)
                    print(summary.key)

            except ClientError as e:
                logging.error(e)
                return False
            return True
