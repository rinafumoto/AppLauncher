#!/usr/bin/env python
import sys

from PyQt5 import uic
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from PyQt5.QtWidgets import QApplication, QMainWindow

from appwidget import AppWidget
from editdialog import EditDialog


class MainWindow(QMainWindow):
    """Class for the main window displaying app widgets for all the applications.
    User can add new applications from here and edit the existing application configuration.

    Attributes
    ----------
    col : int
        The number of columns for the grid layout displaying the app widgets.

    con : QSqlDatabase
        The database storing all the application configurations.
    """

    col: int = 0
    con = QSqlDatabase.addDatabase("QSQLITE")

    def __init__(self):
        """Load UI, connect to the database and add the existing app widgets."""
        super(MainWindow, self).__init__()
        # Load UI
        uic.loadUi("ui/main.ui", self)
        # Maximize the main window
        self.showMaximized()
        # Calculate the number of columns of the grid layout for responsive layout
        self.col = int((self.size().width() - 36) / 238)
        # Initalise the database connection.
        self.con.setDatabaseName("AppDatabase.db")
        self.con.open()
        # Connect signals to corresponding functions
        self.add_new_btn.clicked.connect(self.new)
        self.search.textChanged.connect(self.add_widgets)
        # Add widgets
        self.add_widgets()

    def add_widgets(self):
        """Function for getting data from database and adding app widgets to the main window."""
        # Remove all widgets
        while self.frame_layout.count():
            self.frame_layout.takeAt(0).widget().deleteLater()
        # If there is no input in the search box, get all apps
        if self.search.text() == "":
            query = QSqlQuery("SELECT AppID FROM App ORDER BY Name ASC")
        # Otherwise, get apps whose name matches with the input in the search box
        else :
            query = QSqlQuery(f"SELECT AppID FROM App WHERE Name LIKE '%{self.search.text()}%' ORDER BY Name ASC")
        # Add the app widgets
        row = 0
        column = 0
        while query.next():
            app = AppWidget(query.value(0))
            self.frame_layout.addWidget(app, row, column)
            # Connect the removed signal, which the app widget emits when removed, to add_widgets function to remove the widget from the window
            app.removed.connect(self.add_widgets)
            column = column + 1
            if column >= self.col:
                column = 0
                row = row + 1

    def new(self):
        """This function opens an Add New Dialog.
        It updates the app widgets displaying on the main window when a new application is added.
        Otherwise, it removes the temporary saved environment variables."""
        self.editdialog = EditDialog()
        # Call add_widgets function to add the newly added app when it was saved
        if self.editdialog.exec():
            self.add_widgets()
        # Otherwise, remove the temporary saved environment variables
        else:
            QSqlQuery("DELETE FROM Env WHERE AppID = -1 OR AppID = -2")

    def resizeEvent(self, event):
        """Override function to change the number of columns for the grid layout depending on the window width."""
        # Calculate the number of columns of the grid layout and check if it's changed.
        # It also changes if the database is connected to avoid calling add_widgets function before the connection is initialised.
        if int((self.size().width() - 36) / 238) != self.col and self.con.isOpen():
            self.col = int((self.size().width() - 36) / 238)
            self.add_widgets()
        QMainWindow.resizeEvent(self, event)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
