import unittest
import time

from appwidget import AppWidget
from mainwindow import MainWindow
from PyQt5.QtCore import QBuffer, QByteArray, QDir, QFile, QIODevice, Qt, QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtSql import QSqlQuery
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication, QMessageBox


class Test_AppWidget(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.app = QApplication([])
        self.window = MainWindow()

        self.image = QPixmap("icons/test.png")
        icon = QByteArray()
        buffer = QBuffer(icon)
        buffer.open(QIODevice.WriteOnly)
        self.image.save(buffer, "PNG")

        query = QSqlQuery()
        query.prepare(
            "INSERT INTO App (Name, Path, Description, Icon, Command, Argument) VALUES (?,?,?,?,?,?)"
        )
        query.bindValue(0, "Test Name")
        query.bindValue(1, "Test Path")
        query.bindValue(2, "Test Description")
        query.bindValue(3, icon)
        query.bindValue(4, "Test Command")
        query.bindValue(5, "Test Argument")
        if not query.exec():
            self.assertTrue(False, msg=query.lastError().text())
        self.id = query.lastInsertId()

        self.widget = AppWidget(self.id)
    
    def setUp(self) :
        self.test = False

    def test_widget(self):
        self.assertEqual(self.widget.size().width(), 220)
        self.assertEqual(self.widget.size().height(), 256)
        self.assertEqual(self.widget.id, self.id)
        self.assertEqual(self.widget.path, "Test Path")
        self.assertEqual(self.widget.command, "Test Command")
        self.assertEqual(self.widget.arg, "Test Argument")

        self.assertEqual(self.widget.launch_btn.size().width(), 200)
        self.assertEqual(self.widget.launch_btn.size().height(), 200)
        self.assertEqual(self.widget.launch_btn.text(), "")
        self.assertEqual(type(self.widget.launch_btn.layout()).__name__, "QVBoxLayout")
        self.assertEqual(self.widget.launch_btn.layout().count(), 2)
        self.assertEqual(self.widget.launch_btn.layout().alignment(), Qt.AlignCenter)
        self.assertEqual(type(self.widget.launch_btn.layout().itemAt(0).widget()).__name__, "QLabel")

        icon = QByteArray()
        buffer = QBuffer(icon)
        buffer.open(QIODevice.WriteOnly)
        self.widget.launch_btn.layout().itemAt(0).widget().pixmap().save(buffer, "PNG")

        image = self.image.scaled(128, 128)
        icon2 = QByteArray()
        buffer = QBuffer(icon2)
        buffer.open(QIODevice.WriteOnly)
        image.save(buffer, "PNG")

        self.assertEqual(icon.data(), icon2.data())
        self.assertEqual(type(self.widget.launch_btn.layout().itemAt(1).widget()).__name__, "QLabel")
        self.assertEqual(self.widget.launch_btn.layout().itemAt(1).widget().text(), "Test Name")
        self.assertEqual(self.widget.launch_btn.layout().itemAt(1).widget().alignment(), Qt.AlignHCenter | Qt.AlignBottom)
        self.assertEqual(self.widget.launch_btn.layout().itemAt(1).widget().height(), 30)
        
        self.assertEqual(self.widget.edit_btn.text(), "Edit")
        self.assertEqual(self.widget.edit_btn.size().width(), 164)
        self.assertEqual(self.widget.edit_btn.size().height(), 28)
        self.assertEqual(self.widget.remove_btn.size().width(), 28)
        self.assertEqual(self.widget.remove_btn.size().height(), 28)
        self.assertEqual(self.widget.remove_btn.iconSize().width(), 16)
        self.assertEqual(self.widget.remove_btn.iconSize().height(), 16)

    def test_widget_noicon(self):
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
        id = query.lastInsertId()

        widget = AppWidget(id)

        self.assertEqual(widget.size().width(), 220)
        self.assertEqual(widget.size().height(), 256)
        self.assertEqual(widget.id, id)
        self.assertEqual(widget.path, "Test Path")
        self.assertEqual(widget.command, "Test Command")
        self.assertEqual(widget.arg, "Test Argument")

        self.assertEqual(widget.launch_btn.size().width(), 200)
        self.assertEqual(widget.launch_btn.size().height(), 200)
        self.assertEqual(widget.launch_btn.text(), "")
        self.assertEqual(type(widget.launch_btn.layout()).__name__, "QVBoxLayout")
        self.assertEqual(widget.launch_btn.layout().count(), 1)
        self.assertEqual(widget.launch_btn.layout().alignment(), Qt.AlignCenter)

        self.assertEqual(type(widget.launch_btn.layout().itemAt(0).widget()).__name__, "QLabel")
        self.assertEqual(widget.launch_btn.layout().itemAt(0).widget().text(), "Test Name")
        self.assertEqual(widget.launch_btn.layout().itemAt(0).widget().alignment(), Qt.AlignHCenter | Qt.AlignBottom)
        self.assertEqual(widget.launch_btn.layout().itemAt(0).widget().height(), 30)
        
        self.assertEqual(widget.edit_btn.text(), "Edit")
        self.assertEqual(widget.edit_btn.size().width(), 164)
        self.assertEqual(widget.edit_btn.size().height(), 28)
        self.assertEqual(widget.remove_btn.size().width(), 28)
        self.assertEqual(widget.remove_btn.size().height(), 28)
        self.assertEqual(widget.remove_btn.iconSize().width(), 16)
        self.assertEqual(widget.remove_btn.iconSize().height(), 16)

        QSqlQuery(f"DELETE FROM App WHERE AppID = {id}")

    def test_replace_env(self):
        self.assertEqual(
            self.widget.replace_env(
                'export LD_LIBRARY_PATH="$LD_LIBRARY_PATH":/opt/rh/python27/root/usr/lib64'
            ),
            f"export LD_LIBRARY_PATH={self.widget.env.value('LD_LIBRARY_PATH')}:/opt/rh/python27/root/usr/lib64",
        )
        self.assertEqual(
            self.widget.replace_env('export NUKE_TEMP_DIR=/transfer/nuke."$USERNAME"'),
            f"export NUKE_TEMP_DIR=/transfer/nuke.{self.widget.env.value('USERNAME')}",
        )

    def test_run_commands(self):
        commands = """export DATE=`date +_%s`
mkdir -p Test_"$USERNAME"
touch Test_"$USERNAME"/test"$DATE".txt"""
        self.assertTrue(self.widget.run_commands(commands))
        self.assertTrue(self.widget.env.contains("DATE"))
        username = self.widget.env.value("USERNAME")
        date = self.widget.env.value("DATE")
        self.assertTrue(QDir(f"Test_{username}").exists())
        self.assertTrue(QFile(f"Test_{username}/test{date}.txt").exists())

        commands = f"""export DATE={date}
rm -f Test_"$USERNAME"/test"$DATE".txt
unset DATE"""
        self.assertTrue(self.widget.run_commands(commands))
        self.assertFalse(QFile(f"Test_{username}/test{date}.txt").exists())
        self.assertFalse(self.widget.env.contains("DATE"))

        self.assertTrue(self.widget.run_commands('rm -rf Test_"$USERNAME"'))
        self.assertFalse(QDir(f"Test_{username}").exists())

    def test_run_commands_fail(self) :
        qTimer = QTimer(self.window)
        qTimer.timeout.connect(self.close_messagebox)
        qTimer.start(100)
        self.widget.run_commands("randomcommands")
        self.assertTrue(self.test, msg="Failed to open Message Box")

    def test_launch_success(self):
        query = QSqlQuery()
        query.prepare(
            "INSERT INTO App (Name, Path, Description, Icon, Command, Argument) VALUES (?,?,?,?,?,?)"
        )
        query.bindValue(0, "Test Name")
        query.bindValue(1, "mkdir")
        query.bindValue(2, "Test Description")
        query.bindValue(3, "")
        query.bindValue(4, "")
        query.bindValue(5, "LaunchTest")
        if not query.exec():
            self.assertTrue(False, msg=query.lastError().text())
        id = query.lastInsertId()

        widget = AppWidget(id)

        QDir("LaunchTest").removeRecursively()
        QTest.mouseClick(widget.launch_btn, Qt.LeftButton)
        time.sleep(1)
        self.assertTrue(QDir("LaunchTest").exists())
        QDir("LaunchTest").removeRecursively()

        QSqlQuery(f"DELETE FROM App WHERE AppID = {id}")

    def test_launch_fail(self):
        query = QSqlQuery()
        query.prepare(
            "INSERT INTO App (Name, Path, Description, Icon, Command, Argument) VALUES (?,?,?,?,?,?)"
        )
        query.bindValue(0, "Test Name")
        query.bindValue(1, "Test Path")
        query.bindValue(2, "Test Description")
        query.bindValue(3, "")
        query.bindValue(4, "")
        query.bindValue(5, "Test Argument")
        if not query.exec():
            self.assertTrue(False, msg=query.lastError().text())
        id = query.lastInsertId()

        widget = AppWidget(id)
        qTimer = QTimer(self.window)
        qTimer.timeout.connect(self.close_messagebox)
        qTimer.start(100)
        QTest.mouseClick(widget.launch_btn, Qt.LeftButton)
        self.assertTrue(self.test, msg="Failed to open Message Box")

        QSqlQuery(f"DELETE FROM App WHERE AppID = {id}")

    def test_edit(self):
        qTimer = QTimer(self.widget)
        qTimer.setSingleShot(True)
        qTimer.timeout.connect(self.close_dialog)
        qTimer.start(100)
        QTest.mouseClick(self.widget.edit_btn, Qt.LeftButton)
        self.assertTrue(self.test, msg="Failed to open Edit Dialog")

    def test_remove_cancel(self):
        qTimer = QTimer(self.window)
        qTimer.timeout.connect(self.close_messagebox)
        qTimer.start(100)
        QTest.mouseClick(self.widget.remove_btn, Qt.LeftButton)
        self.assertTrue(self.test, msg="Failed to open Message Box")
        query = QSqlQuery(f"SELECT * FROM App WHERE AppID = {self.id}")
        query.next()
        self.assertTrue(query.isValid())

    def test_remove_no(self):
        qTimer = QTimer(self.window)
        qTimer.timeout.connect(self.messagebox_no)
        qTimer.start(100)
        QTest.mouseClick(self.widget.remove_btn, Qt.LeftButton)
        self.assertTrue(self.test, msg="Failed to open Message Box")
        query = QSqlQuery(f"SELECT * FROM App WHERE AppID = {self.id}")
        query.next()
        self.assertTrue(query.isValid())

    def test_remove_yes(self):
        qTimer = QTimer(self.window)
        qTimer.timeout.connect(self.messagebox_yes)
        qTimer.start(100)
        QTest.mouseClick(self.widget.remove_btn, Qt.LeftButton)
        self.assertTrue(self.test, msg="Failed to open Message Box")
        query = QSqlQuery(f"SELECT * FROM App WHERE AppID = {self.id}")
        query.next()
        self.assertFalse(query.isValid())

    def close_messagebox(self) :
        widget = self.app.activeModalWidget()
        if(type(widget).__name__ == "QMessageBox") :
            QTest.keyPress(widget, Qt.Key_Escape)
            self.test = True
        else :
            self.test = False
    
    def messagebox_no(self) :
        widget = self.app.activeModalWidget()
        if(type(widget).__name__ == "QMessageBox") :
            QTest.mouseClick(widget.button(QMessageBox.No), Qt.LeftButton)
            self.test = True
        else :
            self.test = False

    def messagebox_yes(self) :
        widget = self.app.activeModalWidget()
        if(type(widget).__name__ == "QMessageBox") :
            QTest.mouseClick(widget.button(QMessageBox.Yes), Qt.LeftButton)
            self.test = True
        else :
            self.test = False

    def close_dialog(self):
        widget = self.app.activeModalWidget()
        if type(widget).__name__ == "EditDialog":
            QTest.keyPress(widget, Qt.Key_Escape)
            self.test = True
        else:
            self.test = False

    def tearDown(self):
        self.app.closeAllWindows()

    @classmethod
    def tearDownClass(self):
        QSqlQuery(f"DELETE FROM App WHERE AppID = {self.id}")
        self.window.con.close()
