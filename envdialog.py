#!/usr/bin/env python
from tkinter import E
from PyQt5 import uic
from PyQt5.QtSql import QSqlQuery
from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox


class EnvDialog(QDialog):
    """Class for the edit dialog used for adding new application and editing the exiting applications.

    Attributes
    ----------
    id : int
        The Env ID saved in the database.
    
    order : int
        The execution order of the environment variable.

    appid : int
        The App ID saved in the database.

    """

    id: int = None
    order: int = 0
    appid: int = None

    def __init__(self, appid, id=None):
        """Load UI, connect the button to the corresponding functions, and fill the existing data in the form if it is for editing.

        Parameters
        ----------
        appid : int
            The App ID saved in the database.

        id: int
            The Env ID saved in the database.
        """
        super(EnvDialog, self).__init__()
        # Load UI
        uic.loadUi("ui/env.ui", self)
        self.id = id
        self.appid = appid
        # Connect the button clicked signals to the corresponding functions.
        self.directory_btn.clicked.connect(self.directory)
        self.file_btn.clicked.connect(self.file)
        self.save_btn.clicked.connect(self.save)

        # Set the existing data to the dialog if it is for editing
        if self.id != None:
            query = QSqlQuery(f"SELECT * FROM Env WHERE EnvID = {self.id}")
            query.next()
            self.name.setText(query.value("Name"))
            self.value.setText(query.value("Value"))
            self.order = query.value("ExeOrder")
            self.appid = query.value("AppID")

    def directory(self):
        """Display a file dialog and let user to select a existing directory as an environment variable."""
        dir = QFileDialog.getExistingDirectory(
            self,
            "Select Directory",
            "/",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks,
        )
        if dir != "":
            self.value.setText(dir)

    def file(self):
        """Display a file dialog and let user to select a existing file as an environment variable."""
        fname = QFileDialog.getOpenFileName(self, "Select File", "/", "All files (*);;")
        if fname[0] != "":
            self.value.setText(fname[0])

    def save(self):
        """Function for the save button.
        It checks if the value is set and warn the user to fill the form if not set.
        Otherwise, it insert the new data into the database or update the existing data."""
        # Pop up a message box if name or value or both are not set
        if self.name.text() == "" or self.value.text() == "":
            QMessageBox.critical(self, "Values not set", "Please fill in all values")
        else :
            # If editing the variable and AppID is already set to -1, just update the value
            if self.id != None and self.appid == -1 :
                query = QSqlQuery()
                query.prepare("UPDATE Env Set Name = ?, Value = ? WHERE EnvID = ?")
                query.bindValue(0, self.name.text())
                query.bindValue(1, self.value.text())
                query.bindValue(2, self.id)
                if not query.exec():
                    print("Error ", query.lastError().text())
            # If adding a new environment variable, get the max execution order number and set as the last one and insert.
            elif self.id == None :
                if self.appid == -1 :
                    query = QSqlQuery(f"SELECT MAX(ExeOrder) FROM Env WHERE AppID = -1")
                else :
                    query = QSqlQuery(f"SELECT MAX(ExeOrder) FROM Env WHERE AppID = {self.appid} OR AppID = -1")
                query.next()
                if query.isNull('MAX(ExeOrder)') :
                    self.order = 1
                else :
                    self.order = query.value('MAX(ExeOrder)') + 1

                query = QSqlQuery()
                query.prepare("INSERT INTO Env (Name, Value, ExeOrder, AppID) VALUES (?,?,?,-1)")
                query.bindValue(0, self.name.text())
                query.bindValue(1, self.value.text())
                query.bindValue(2, self.order)
                if not query.exec():
                    print("Error ", query.lastError().text())
            # If editing the variable and AppID is not set to -1, insert a new environment variable with AppID as a temporal varlue and store the old one by setting the AppID to -2
            else :
                query = QSqlQuery()
                query.prepare("INSERT INTO Env (Name, Value, ExeOrder, AppID) VALUES (?,?,?,-1)")
                query.bindValue(0, self.name.text())
                query.bindValue(1, self.value.text())
                query.bindValue(2, self.order)
                if not query.exec():
                    print("Error ", query.lastError().text())
                query = QSqlQuery()
                query.prepare("UPDATE Env Set AppID = -2 WHERE EnvID = ?")
                query.bindValue(0, self.id)
                if not query.exec():
                    print("Error ", query.lastError().text())
            
            self.accept()