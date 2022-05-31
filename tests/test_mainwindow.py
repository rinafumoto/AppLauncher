import math
import unittest

from mainwindow import MainWindow
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtSql import QSqlQuery
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication


class Test_MainWindow(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.app = QApplication([])

    def setUp(self):
        self.window = MainWindow()
        self.test = False

    def test_window(self):
        self.assertEqual(self.window.windowTitle(), "App Launcher")
        self.assertEqual(self.window.windowType(), Qt.Window)
        self.assertTrue(self.window.isWindow())
        self.assertEqual(self.window.windowState(), Qt.WindowMaximized)
        self.assertTrue(self.window.isMaximized())
        self.assertTrue(self.window.size().width() >= 202)
        self.assertTrue(self.window.size().height() >= 290)
        self.assertTrue(self.window.isVisible())
        self.assertEqual(self.window.add_new_btn.text(), "Add New")
        self.assertEqual(self.window.search.text(), "")
        self.assertEqual(self.window.col, int((self.window.size().width() - 36) / 238))

    def test_database(self):
        self.assertTrue(self.window.con.isOpen())
        self.assertEqual(self.window.con.driverName(), "QSQLITE")
        self.assertEqual(self.window.con.databaseName(), "AppDatabase.db")
        self.assertTrue("App" in self.window.con.tables())
        self.assertTrue("Env" in self.window.con.tables())

    def test_add_widgets(self):
        query = QSqlQuery("SELECT AppID FROM App")
        query.last()
        self.assertEqual(self.window.frame_layout.count(), query.at() + 1)
        self.assertEqual(
            self.window.frame_layout.columnCount(),
            int((self.window.size().width() - 36) / 238),
        )
        self.assertEqual(
            self.window.frame_layout.rowCount(),
            math.ceil((query.at() + 1) / int((self.window.size().width() - 36) / 238)),
        )

    def test_resize(self):
        self.window.resize(1280, 720)
        self.assertEqual(self.window.size().width(), 1280)
        self.assertEqual(self.window.size().height(), 720)
        self.assertEqual(self.window.col, 5)
        self.window.resize(1920, 1080)
        self.assertEqual(self.window.size().width(), 1920)
        self.assertEqual(self.window.size().height(), 1080)
        self.assertEqual(self.window.col, 7)
        self.window.resize(10, 10)
        self.assertEqual(self.window.size().width(), 274)
        self.assertEqual(self.window.size().height(), 362)
        self.assertEqual(self.window.col, 1)

    def test_new(self):
        qTimer = QTimer(self.window)
        qTimer.setSingleShot(True)
        qTimer.timeout.connect(self.close_dialog)
        qTimer.start(100)
        QTest.mouseClick(self.window.add_new_btn, Qt.LeftButton)
        self.assertTrue(self.test, msg="Failed to open Add New Dialog")

    def close_dialog(self):
        widget = self.app.activeModalWidget()
        if type(widget).__name__ == "EditDialog":
            QTest.keyPress(widget, Qt.Key_Escape)
            self.test = True
        else:
            self.test = False

    def tearDown(self) :
        self.app.closeAllWindows()
        self.window.con.close()