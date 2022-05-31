import os
import unittest

from envdialog import EnvDialog
from mainwindow import MainWindow
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtSql import QSqlQuery
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication

class Test_EnvDialog(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.app = QApplication([])
        self.window = MainWindow()

        query = QSqlQuery()
        query.prepare(
            "INSERT INTO App (Name, Path, Description, Icon, Command, Argument) VALUES (?,?,?,?,?,?)"
        )
        query.bindValue(0, "Test Name")
        query.bindValue(1, "Test Path")
        query.bindValue(2, "Test Description")
        query.bindValue(3, "")
        query.bindValue(4, "Test Command")
        query.bindValue(5, "Test Argument")
        if not query.exec():
            self.assertTrue(False, msg=query.lastError().text())
        self.appid = query.lastInsertId()

        query = QSqlQuery()
        query.prepare("INSERT INTO Env (Name, Value, AppID, ExeOrder) VALUES (?,?,?,?)")
        query.bindValue(0, "Test Name")
        query.bindValue(1, "Test Value")
        query.bindValue(2, self.appid)
        query.bindValue(3, 1)
        if not query.exec():
            self.assertTrue(False, msg=query.lastError().text())
        self.envid = query.lastInsertId()

    def setUp(self):
        self.test = False

    def test_newdialog(self):
        newdialog = EnvDialog(self.appid)
        self.assertEqual(newdialog.windowTitle(), "Environment Variable")
        self.assertEqual(newdialog.windowType(), Qt.Dialog)

        self.assertEqual(newdialog.id, None)
        self.assertEqual(newdialog.order, 0)
        self.assertEqual(newdialog.appid, self.appid)
        self.assertEqual(newdialog.name.text(), "")
        self.assertEqual(newdialog.value.text(), "")

        self.assertEqual(newdialog.directory_btn.text(), "Browse Directory")
        self.assertEqual(newdialog.file_btn.text(), "Browse File")
        self.assertEqual(newdialog.save_btn.text(), "Save")

    def test_editdialog(self):
        editdialog = EnvDialog(self.appid, self.envid)
        self.assertEqual(editdialog.windowTitle(), "Environment Variable")
        self.assertEqual(editdialog.windowType(), Qt.Dialog)

        self.assertEqual(editdialog.id, self.envid)
        self.assertEqual(editdialog.order, 1)
        self.assertEqual(editdialog.appid, self.appid)
        self.assertEqual(editdialog.name.text(), "Test Name")
        self.assertEqual(editdialog.value.text(), "Test Value")

        self.assertEqual(editdialog.directory_btn.text(), "Browse Directory")
        self.assertEqual(editdialog.file_btn.text(), "Browse File")
        self.assertEqual(editdialog.save_btn.text(), "Save")

    def test_directory_cancel(self):
        newdialog = EnvDialog(self.appid)
        qTimer = QTimer(newdialog)
        qTimer.setSingleShot(True)
        qTimer.timeout.connect(self.filedialog_cancel)
        qTimer.start(100)
        QTest.mouseClick(newdialog.directory_btn, Qt.LeftButton)
        self.assertTrue(self.test, msg="Failed to open File Dialog")
        self.assertEqual(newdialog.value.text(), "")

    def test_file_cancel(self):
        newdialog = EnvDialog(self.appid)
        qTimer = QTimer(newdialog)
        qTimer.setSingleShot(True)
        qTimer.timeout.connect(self.filedialog_cancel)
        qTimer.start(100)
        QTest.mouseClick(newdialog.file_btn, Qt.LeftButton)
        self.assertTrue(self.test, msg="Failed to open File Dialog")
        self.assertEqual(newdialog.value.text(), "")

    def filedialog_cancel(self):
        widget = self.app.activeModalWidget()
        if type(widget).__name__ == "QFileDialog":
            QTest.keyPress(widget, Qt.Key_Escape)
            self.test = True
        else:
            self.test = False

    def test_directory_open(self):
        newdialog = EnvDialog(self.appid)
        qTimer = QTimer(newdialog)
        qTimer.setSingleShot(True)
        qTimer.timeout.connect(self.filedialog_dir_open)
        qTimer.start(100)
        QTest.mouseClick(newdialog.directory_btn, Qt.LeftButton)
        self.assertTrue(self.test, msg="Failed to open File Dialog")
        self.assertEqual(newdialog.value.text(), os.getcwd())

    def filedialog_dir_open(self) :
        widget = self.app.activeModalWidget()
        if(type(widget).__name__ == "QFileDialog") :
            qTimer = QTimer(widget)
            qTimer.setSingleShot(True)
            qTimer.timeout.connect(widget.accept)
            qTimer.start(100)
            widget.setDirectory(os.getcwd())
            self.test = True
        else :
            self.test = False

    def test_file_open(self):
        newdialog = EnvDialog(self.appid)
        qTimer = QTimer(newdialog)
        qTimer.setSingleShot(True)
        qTimer.timeout.connect(self.filedialog_file_open)
        qTimer.start(100)
        QTest.mouseClick(newdialog.file_btn, Qt.LeftButton)
        self.assertTrue(self.test, msg="Failed to open File Dialog")
        self.assertEqual(newdialog.value.text(), os.path.abspath(__file__))

    def filedialog_file_open(self) :
        widget = self.app.activeModalWidget()
        if(type(widget).__name__ == "QFileDialog") :
            qTimer = QTimer(widget)
            qTimer.setSingleShot(True)
            qTimer.timeout.connect(widget.accept)
            qTimer.start(100)
            widget.selectFile(os.path.abspath(__file__))
            self.test = True
        else :
            self.test = False

    def test_save_fail(self):
        newdialog = EnvDialog(self.appid)
        qTimer = QTimer(newdialog)
        qTimer.setSingleShot(True)
        qTimer.timeout.connect(self.close_messagebox)
        qTimer.start(100)
        QTest.mouseClick(newdialog.save_btn, Qt.LeftButton)
        self.assertTrue(self.test, msg="Failed to open Message Box")

        newdialog.name.setText("Name")
        qTimer = QTimer(newdialog)
        qTimer.setSingleShot(True)
        qTimer.timeout.connect(self.close_messagebox)
        qTimer.start(100)
        QTest.mouseClick(newdialog.save_btn, Qt.LeftButton)
        self.assertTrue(self.test, msg="Failed to open Message Box")

        newdialog.name.setText("")
        newdialog.value.setText("Value")
        qTimer = QTimer(newdialog)
        qTimer.setSingleShot(True)
        qTimer.timeout.connect(self.close_messagebox)
        qTimer.start(100)
        QTest.mouseClick(newdialog.save_btn, Qt.LeftButton)
        self.assertTrue(self.test, msg="Failed to open Message Box")

    def close_messagebox(self):
        widget = self.app.activeModalWidget()
        if type(widget).__name__ == "QMessageBox":
            QTest.keyPress(widget, Qt.Key_Escape)
            self.test = True
        else:
            self.test = False

    def test_save_new(self):
        # Remove existing test env
        query = QSqlQuery()
        query.prepare("DELETE FROM Env WHERE Name = ? AND Value = ? AND AppID = ?")
        query.bindValue(0, "New Name")
        query.bindValue(1, "New Value")
        query.bindValue(2, -1)
        if not query.exec():
            self.assertTrue(False, msg=query.lastError().text())

        # Get total number of apps before saving
        query = QSqlQuery("SELECT EnvID FROM Env")
        query.last()
        num_envs = query.at()

        newdialog = EnvDialog(self.appid)
        newdialog.name.setText("New Name")
        newdialog.value.setText("New Value")
        QTest.mouseClick(newdialog.save_btn, Qt.LeftButton)

        query = QSqlQuery()
        query.prepare(f"SELECT * FROM Env WHERE Name = ? AND Value = ? AND AppID = ?")
        query.bindValue(0, "New Name")
        query.bindValue(1, "New Value")
        query.bindValue(2, -1)
        if not query.exec():
            self.assertTrue(False, msg=query.lastError().text())
        query.next()
        self.assertTrue(query.isValid())

        query = QSqlQuery("SELECT EnvID FROM Env")
        query.last()
        self.assertEqual(query.at(), num_envs + 1)

    def test_save_edit(self):
        # Remove existing test env
        query = QSqlQuery()
        query.prepare("DELETE FROM Env WHERE Name = ? AND Value = ? AND AppID = ?")
        query.bindValue(0, "New Name")
        query.bindValue(1, "New Value")
        query.bindValue(2, -1)
        if not query.exec():
            self.assertTrue(False, msg=query.lastError().text())

        # Get total number of apps before saving
        query = QSqlQuery("SELECT EnvID FROM Env")
        query.last()
        num_envs = query.at()

        editdialog = EnvDialog(self.appid, self.envid)
        editdialog.name.setText("New Name")
        editdialog.value.setText("New Value")
        QTest.mouseClick(editdialog.save_btn, Qt.LeftButton)

        query = QSqlQuery()
        query.prepare(f"SELECT * FROM Env WHERE Name = ? AND Value = ? AND AppID = ?")
        query.bindValue(0, "New Name")
        query.bindValue(1, "New Value")
        query.bindValue(2, -1)
        if not query.exec():
            self.assertTrue(False, msg=query.lastError().text())
        query.next()
        self.assertTrue(query.isValid())

        query = QSqlQuery(f"SELECT * FROM Env WHERE EnvID = {self.envid}")
        query.next()
        self.assertEqual(query.value("Name"), "Test Name")
        self.assertEqual(query.value("Value"), "Test Value")
        self.assertEqual(query.value("AppID"), -2)

        query = QSqlQuery("SELECT EnvID FROM Env")
        query.last()
        self.assertEqual(query.at(), num_envs + 1)

    def tearDown(self):
        self.app.closeAllWindows()

    @classmethod
    def tearDownClass(self) :
        QSqlQuery(f"DELETE FROM App WHERE AppID = {self.appid}")
        QSqlQuery(f"DELETE FROM Env WHERE EnvID = {self.envid}")
        self.window.con.close()
