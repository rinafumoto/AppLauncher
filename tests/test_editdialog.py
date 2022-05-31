import unittest
import os

from PyQt5.QtCore import Qt, QByteArray, QBuffer, QIODevice, QTimer
from PyQt5.QtSql import QSqlQuery
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QAbstractItemView
from PyQt5.QtTest import QTest

from mainwindow import MainWindow
from editdialog import EditDialog


class Test_EditDialog(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.app = QApplication([])
        self.window = MainWindow()

        image = QPixmap("icons/test.png")
        if image.size().width() > image.size().height():
            image = image.scaledToWidth(96)
        else:
            image = image.scaledToHeight(96)
        self.icon = QByteArray()
        buffer = QBuffer(self.icon)
        buffer.open(QIODevice.WriteOnly)
        image.save(buffer, "PNG")

        image = QPixmap("icons/test2.png")
        if image.size().width() > image.size().height():
            image = image.scaledToWidth(96)
        else:
            image = image.scaledToHeight(96)
        self.icon2 = QByteArray()
        buffer = QBuffer(self.icon2)
        buffer.open(QIODevice.WriteOnly)
        image.save(buffer, "PNG")

        query = QSqlQuery()
        query.prepare("INSERT INTO App (Name, Path, Description, Icon, Command, Argument) VALUES (?,?,?,?,?,?)")
        query.bindValue(0, "Test Name")
        query.bindValue(1, "Test Path")
        query.bindValue(2, "Test Description")
        query.bindValue(3, self.icon)
        query.bindValue(4, "Test Command")
        query.bindValue(5, "Test Argument")
        if not query.exec():
            self.assertTrue(False, msg=query.lastError().text())
        self.id = query.lastInsertId()

        query = QSqlQuery()
        query.prepare("INSERT INTO Env (Name, Value, AppID, ExeOrder) VALUES (?,?,?,?)")
        query.bindValue(0, "Test Env Name 1")
        query.bindValue(1, "Test Env Value 1")
        query.bindValue(2, self.id)
        query.bindValue(3, 1)
        if not query.exec():
            self.assertTrue(False, msg=query.lastError().text())
        self.envid = query.lastInsertId()

        query.prepare("INSERT INTO Env (Name, Value, AppID, ExeOrder) VALUES (?,?,?,?)")
        query.bindValue(0, "Test Env Name 2")
        query.bindValue(1, "Test Env Value 2")
        query.bindValue(2, self.id)
        query.bindValue(3, 2)
        if not query.exec():
            self.assertTrue(False, msg=query.lastError().text())

    def setUp(self) :
        self.test = False

    def test_newdialog(self) :
        newdialog = EditDialog()
        self.assertEqual(newdialog.windowTitle(), "Add New")
        self.assertEqual(newdialog.windowType(), Qt.Dialog)

        self.assertEqual(newdialog.id, -1)
        self.assertTrue(newdialog.new)
        self.assertEqual(newdialog.name.text(), "")
        self.assertEqual(newdialog.path.text(), "")
        self.assertEqual(newdialog.description.toPlainText(), "")
        self.assertEqual(newdialog.command.toPlainText(), "")
        self.assertEqual(newdialog.argument.text(), "")
        self.assertTrue(newdialog.icon_img.isEmpty())

        self.assertEqual(newdialog.lookup_btn.size().width(), 28)
        self.assertEqual(newdialog.lookup_btn.size().height(), 28)
        self.assertEqual(newdialog.lookup_btn.iconSize().width(), 16)
        self.assertEqual(newdialog.lookup_btn.iconSize().height(), 16)
        self.assertEqual(newdialog.icon.size().width(), 128)
        self.assertEqual(newdialog.icon.size().height(), 128)
        self.assertEqual(newdialog.icon.iconSize().width(), 96)
        self.assertEqual(newdialog.icon.iconSize().height(), 96)

        self.assertEqual(newdialog.remove_btn.text(), "Remove")
        self.assertEqual(newdialog.env_new_btn.text(), "New")
        self.assertEqual(newdialog.env_edit_btn.text(), "Edit")
        self.assertEqual(newdialog.env_remove_btn.text(), "Remove")
        self.assertEqual(newdialog.save_btn.text(), "Save")

        self.assertFalse(newdialog.env_table.model())

    def test_editdialog(self) :
        editdialog = EditDialog(self.id)
        self.assertEqual(editdialog.windowTitle(), "Edit")
        self.assertEqual(editdialog.windowType(), Qt.Dialog)

        self.assertEqual(editdialog.id, self.id)
        self.assertFalse(editdialog.new)
        self.assertEqual(editdialog.name.text(), "Test Name")
        self.assertEqual(editdialog.path.text(), "Test Path")
        self.assertEqual(editdialog.description.toPlainText(), "Test Description")
        self.assertEqual(editdialog.command.toPlainText(), "Test Command")
        self.assertEqual(editdialog.argument.text(), "Test Argument")
        self.assertEqual(editdialog.icon_img, self.icon)

        self.assertEqual(editdialog.lookup_btn.size().width(), 28)
        self.assertEqual(editdialog.lookup_btn.size().height(), 28)
        self.assertEqual(editdialog.lookup_btn.iconSize().width(), 16)
        self.assertEqual(editdialog.lookup_btn.iconSize().height(), 16)
        self.assertEqual(editdialog.icon.size().width(), 128)
        self.assertEqual(editdialog.icon.size().height(), 128)
        self.assertEqual(editdialog.icon.iconSize().width(), 96)
        self.assertEqual(editdialog.icon.iconSize().height(), 96)

        self.assertEqual(editdialog.remove_btn.text(), "Remove")
        self.assertEqual(editdialog.env_new_btn.text(), "New")
        self.assertEqual(editdialog.env_edit_btn.text(), "Edit")
        self.assertEqual(editdialog.env_remove_btn.text(), "Remove")
        self.assertEqual(editdialog.save_btn.text(), "Save")

        self.assertEqual(editdialog.env_table.horizontalHeader().count(), 5)
        self.assertTrue(editdialog.env_table.isColumnHidden(0))
        self.assertTrue(editdialog.env_table.isColumnHidden(3))
        self.assertTrue(editdialog.env_table.isColumnHidden(4))
        self.assertEqual(editdialog.env_table.horizontalHeader().hiddenSectionCount(), 3)
        self.assertTrue(editdialog.env_table.horizontalHeader().isSectionHidden(0))
        self.assertTrue(editdialog.env_table.horizontalHeader().isSectionHidden(3))
        self.assertTrue(editdialog.env_table.horizontalHeader().isSectionHidden(4))
        self.assertEqual(editdialog.env_table.selectionBehavior(), QAbstractItemView.SelectRows)
        self.assertEqual(editdialog.env_table.selectionMode(), QAbstractItemView.SingleSelection)

        self.assertEqual(editdialog.env_table.model().columnCount(), 5)
        self.assertEqual(editdialog.env_table.model().rowCount(), 2)
        self.assertEqual(editdialog.env_table.model().headerData(0, Qt.Horizontal), "EnvID")
        self.assertEqual(editdialog.env_table.model().headerData(1, Qt.Horizontal), "Name")
        self.assertEqual(editdialog.env_table.model().headerData(2, Qt.Horizontal), "Value")
        self.assertEqual(editdialog.env_table.model().headerData(3, Qt.Horizontal), "ExeOrder")
        self.assertEqual(editdialog.env_table.model().headerData(4, Qt.Horizontal), "AppID")
        self.assertEqual(editdialog.env_table.model().data(editdialog.env_table.model().index(0, 1)), "Test Env Name 1")
        self.assertEqual(editdialog.env_table.model().data(editdialog.env_table.model().index(0, 2)), "Test Env Value 1")
        self.assertEqual(editdialog.env_table.model().data(editdialog.env_table.model().index(1, 1)), "Test Env Name 2")
        self.assertEqual(editdialog.env_table.model().data(editdialog.env_table.model().index(1, 2)), "Test Env Value 2")

    def test_lookup_cancel(self) :
        newdialog = EditDialog()
        qTimer = QTimer(newdialog)
        qTimer.setSingleShot(True)
        qTimer.timeout.connect(self.filedialog_cancel)
        qTimer.start(100)
        QTest.mouseClick(newdialog.lookup_btn, Qt.LeftButton)
        self.assertTrue(self.test, msg="Failed to open File Dialog")
        self.assertEqual(newdialog.path.text(), "")

    def filedialog_cancel(self) :
        widget = self.app.activeModalWidget()
        if(type(widget).__name__ == "QFileDialog") :
            QTest.keyPress(widget, Qt.Key_Escape)
            self.test = True
        else :
            self.test = False

    def test_lookup_save(self) :
        newdialog = EditDialog()
        qTimer = QTimer(newdialog)
        qTimer.setSingleShot(True)
        qTimer.timeout.connect(self.filedialog_open)
        qTimer.start(100)
        QTest.mouseClick(newdialog.lookup_btn, Qt.LeftButton)
        self.assertTrue(self.test, msg="Failed to open File Dialog")
        self.assertEqual(newdialog.path.text(), os.path.abspath(__file__))

    def filedialog_open(self) :
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

    def test_new_pixmap_cancel(self) :
        newdialog = EditDialog()
        qTimer = QTimer(newdialog)
        qTimer.setSingleShot(True)
        qTimer.timeout.connect(self.filedialog_cancel)
        qTimer.start(100)
        QTest.mouseClick(newdialog.icon, Qt.LeftButton)
        self.assertTrue(self.test, msg="Failed to open File Dialog")
        self.assertTrue(newdialog.icon_img.isEmpty())

    def test_update_pixmap_cancel(self) :
        editdialog = EditDialog(self.id)
        old_icon = editdialog.icon_img
        qTimer = QTimer(editdialog)
        qTimer.setSingleShot(True)
        qTimer.timeout.connect(self.filedialog_cancel)
        qTimer.start(100)
        QTest.mouseClick(editdialog.icon, Qt.LeftButton)
        self.assertTrue(self.test, msg="Failed to open File Dialog")
        self.assertEqual(editdialog.icon_img, old_icon)

    def test_new_pixmap_save(self) :
        newdialog = EditDialog()
        qTimer = QTimer(newdialog)
        qTimer.setSingleShot(True)
        qTimer.timeout.connect(self.filedialog_pixmap_save)
        qTimer.start(100)
        QTest.mouseClick(newdialog.icon, Qt.LeftButton)
        self.assertTrue(self.test, msg="Failed to open File Dialog")
        self.assertEqual(newdialog.icon_img.data(), self.icon2.data())

    def test_update_pixmap_save(self) :
        editdialog = EditDialog(self.id)
        qTimer = QTimer(editdialog)
        qTimer.setSingleShot(True)
        qTimer.timeout.connect(self.filedialog_pixmap_save)
        qTimer.start(100)
        QTest.mouseClick(editdialog.icon, Qt.LeftButton)
        self.assertTrue(self.test, msg="Failed to open File Dialog")
        self.assertEqual(editdialog.icon_img.data(), self.icon2.data())

    def filedialog_pixmap_save(self) :
        widget = self.app.activeModalWidget()
        if(type(widget).__name__ == "QFileDialog") :
            qTimer = QTimer(widget)
            qTimer.setSingleShot(True)
            qTimer.timeout.connect(widget.accept)
            qTimer.start(100)
            widget.selectFile(f"{os.path.abspath(os.getcwd())}/icons/test2.png")
            self.test = True
        else :
            self.test = False

    def test_remove_icon(self) :
        editdialog = EditDialog(self.id)
        self.assertEqual(editdialog.icon_img, self.icon)
        editdialog.remove_icon()
        self.assertTrue(editdialog.icon_img.isEmpty())

    def test_env_new(self) :
        newdialog = EditDialog()
        qTimer = QTimer(newdialog)
        qTimer.setSingleShot(True)
        qTimer.timeout.connect(self.envnewdialog)
        qTimer.start(100)
        QTest.mouseClick(newdialog.env_new_btn, Qt.LeftButton)
        self.assertTrue(self.test, msg="Failed to open New Env Dialog")

    def envnewdialog(self) :
        widget = self.app.activeModalWidget()
        if type(widget).__name__ == "EnvDialog" and widget.id == None:
            QTest.keyPress(widget, Qt.Key_Escape)
            self.test = True
        else :
            self.test = False

    def test_env_edit_fail(self) :
        editdialog = EditDialog(self.id)
        editdialog.env_table.selectionModel().clearSelection()
        qTimer = QTimer(editdialog)
        qTimer.setSingleShot(True)
        qTimer.timeout.connect(self.close_messagebox)
        qTimer.start(100)
        QTest.mouseClick(editdialog.env_edit_btn, Qt.LeftButton)
        self.assertTrue(self.test, msg="Failed to open edit Env Dialog")

    def test_env_edit_success(self) :
        editdialog = EditDialog(self.id)
        editdialog.env_table.selectRow(0)
        qTimer = QTimer(editdialog)
        qTimer.setSingleShot(True)
        qTimer.timeout.connect(self.enveditdialog)
        qTimer.start(100)
        QTest.mouseClick(editdialog.env_edit_btn, Qt.LeftButton)
        self.assertTrue(self.test, msg="Failed to open edit Env Dialog")

    def enveditdialog(self) :
        widget = self.app.activeModalWidget()
        if type(widget).__name__ == "EnvDialog" and widget.id == self.envid :
            QTest.keyPress(widget, Qt.Key_Escape)
            self.test = True
        else :
            self.test = False

    def test_env_remove_fail(self) :
        editdialog = EditDialog(self.id)
        editdialog.env_table.selectionModel().clearSelection()
        qTimer = QTimer(editdialog)
        qTimer.setSingleShot(True)
        qTimer.timeout.connect(self.close_messagebox)
        qTimer.start(100)
        QTest.mouseClick(editdialog.env_remove_btn, Qt.LeftButton)
        self.assertTrue(self.test, msg="Failed to Message Box")

    def test_env_remove_success(self) :
        editdialog = EditDialog(self.id)
        editdialog.env_table.selectRow(0)
        QTest.mouseClick(editdialog.env_remove_btn, Qt.LeftButton)
        query = QSqlQuery(f"SELECT AppID FROM Env WHERE EnvID = {self.envid}")
        query.next()
        self.assertEqual(query.value("AppID"), -2)
        self.assertEqual(editdialog.env_table.model().rowCount(), 1)
        self.assertEqual(editdialog.env_table.model().data(editdialog.env_table.model().index(0, 1)), "Test Env Name 2")
        self.assertEqual(editdialog.env_table.model().data(editdialog.env_table.model().index(0, 2)), "Test Env Value 2")

    def test_save_fail(self) :
        newdialog = EditDialog()
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
        newdialog.path.setText("Path")
        qTimer = QTimer(newdialog)
        qTimer.setSingleShot(True)
        qTimer.timeout.connect(self.close_messagebox)
        qTimer.start(100)
        QTest.mouseClick(newdialog.save_btn, Qt.LeftButton)
        self.assertTrue(self.test, msg="Failed to open Message Box")

    def close_messagebox(self) :
        widget = self.app.activeModalWidget()
        if(type(widget).__name__ == "QMessageBox") :
            QTest.keyPress(widget, Qt.Key_Escape)
            self.test = True
        else :
            self.test = False

    def test_save_new(self) :
        # Remove existing test app
        query = QSqlQuery()
        query.prepare("DELETE FROM App WHERE Name = ? AND Path = ? AND Description = ? AND Icon = ? AND Command = ? AND Argument = ?")
        query.bindValue(0, "New Name")
        query.bindValue(1, "New Path")
        query.bindValue(2, "New Description")
        query.bindValue(3, self.icon)
        query.bindValue(4, "New Command")
        query.bindValue(5, "New Argument")
        if not query.exec():
            self.assertTrue(False, msg=query.lastError().text())

        # Get total number of apps before saving
        query = QSqlQuery("SELECT AppID FROM App")
        query.last()
        num_apps = query.at()

        newdialog = EditDialog()
        newdialog.name.setText("New Name")
        newdialog.path.setText("New Path")
        newdialog.description.setPlainText("New Description")
        newdialog.command.setPlainText("New Command")
        newdialog.argument.setText("New Argument")
        newdialog.icon_img = self.icon
        QTest.mouseClick(newdialog.save_btn, Qt.LeftButton)

        query = QSqlQuery()
        query.prepare(f"SELECT * FROM App WHERE Name = ? AND Path = ? AND Description = ? AND Icon = ? AND Command = ? AND Argument = ?")
        query.bindValue(0, "New Name")
        query.bindValue(1, "New Path")
        query.bindValue(2, "New Description")
        query.bindValue(3, self.icon)
        query.bindValue(4, "New Command")
        query.bindValue(5, "New Argument")
        if not query.exec():
            self.assertTrue(False, msg=query.lastError().text())
        query.next()
        self.assertTrue(query.isValid())

        query = QSqlQuery("SELECT AppID FROM App")
        query.last()
        self.assertEqual(query.at(), num_apps+1)

    def test_save_edit(self) :
        editdialog = EditDialog(self.id)
        editdialog.name.setText("New Name")
        editdialog.path.setText("New Path")
        editdialog.description.setPlainText("New Description")
        editdialog.command.setPlainText("New Command")
        editdialog.argument.setText("New Argument")
        editdialog.icon_img = self.icon
        QTest.mouseClick(editdialog.save_btn, Qt.LeftButton)
        query = QSqlQuery(f"SELECT * FROM App WHERE AppID = {self.id}")
        query.next()
        self.assertEqual(query.value("Name"), "New Name")
        self.assertEqual(query.value("Path"), "New Path")
        self.assertEqual(query.value("Description"), "New Description")
        self.assertEqual(query.value("Icon"), self.icon)
        self.assertEqual(query.value("Command"), "New Command")
        self.assertEqual(query.value("Argument"), "New Argument")

    def tearDown(self) :
        self.app.closeAllWindows()

    @classmethod
    def tearDownClass(self) :
        QSqlQuery(f"DELETE FROM App WHERE AppID = {self.id}")
        QSqlQuery(f"DELETE FROM Env WHERE AppID = {self.id}")
        query = QSqlQuery()
        query.prepare("DELETE FROM App WHERE Name = ? AND Path = ? AND Description = ? AND Icon = ? AND Command = ? AND Argument = ?")
        query.bindValue(0, "New Name")
        query.bindValue(1, "New Path")
        query.bindValue(2, "New Description")
        query.bindValue(3, self.icon)
        query.bindValue(4, "New Command")
        query.bindValue(5, "New Argument")
        if not query.exec():
            self.assertTrue(False, msg=query.lastError().text())
        self.window.con.close()
        