#!/usr/bin/env python
from PyQt5 import uic
from PyQt5.QtCore import QBuffer, QByteArray, QIODevice, Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtSql import QSqlQuery, QSqlQueryModel
from PyQt5.QtWidgets import QAbstractItemView, QDialog, QFileDialog, QMessageBox

from envdialog import EnvDialog


class EditDialog(QDialog):
    """Class for the edit dialog used for adding new application and editing the exiting applications.

    Attributes
    ----------
    icon_img : QByteArray
        The icon image saved as QByteArray

    id : int
        The Application ID saved in the database. -1 for the new application.

    new : bool
        Boolean value to check if the dialog is for new application or an existing application.
    """

    icon_img: QByteArray = QByteArray()
    id: int = -1
    new: bool = True

    def __init__(self, id=-1):
        """Load UI, connect the button to the corresponding functions, and fill the existing data in the form if it is for editing.

        Parameters
        ----------
        id: int
            The Application ID saved in the database. -1 for the new application.
        """
        super(EditDialog, self).__init__()
        # Load UI
        uic.loadUi("ui/edit.ui", self)
        self.id = id
        self.icon_img.clear()
        # Set icons to the toolbuttons
        lookup_icon = QPixmap("icons/lookup.png")
        up_icon = QPixmap("icons/up-arrow.png")
        down_icon = QPixmap("icons/down-arrow.png")
        self.lookup_btn.setIcon(QIcon(lookup_icon))
        self.up_btn.setIcon(QIcon(up_icon))
        self.down_btn.setIcon(QIcon(down_icon))
        # Connect button clicked signals to corresponding functions
        self.lookup_btn.clicked.connect(self.lookup)
        self.up_btn.clicked.connect(self.up)
        self.down_btn.clicked.connect(self.down)
        self.icon.clicked.connect(self.set_pixmap)
        self.save_btn.clicked.connect(self.save)
        self.remove_btn.clicked.connect(self.remove_icon)
        self.env_new_btn.clicked.connect(self.env_new)
        self.env_edit_btn.clicked.connect(self.env_edit)
        self.env_remove_btn.clicked.connect(self.env_remove)

        # If it is edit dialog, set the existing data to the dialog
        if self.id != -1:
            self.new = False
            self.setWindowTitle("Edit")
            query = QSqlQuery(f"SELECT * FROM App WHERE AppID = {self.id}")
            query.next()
            # Set the icon to the icon button if available
            icon = query.value("Icon")
            if type(icon) == QByteArray:
                pixmap = QPixmap()
                pixmap.loadFromData(QByteArray(icon), "png")
                self.icon.setIcon(QIcon(pixmap))
                buffer = QBuffer(self.icon_img)
                buffer.open(QIODevice.WriteOnly)
                pixmap.save(buffer, "PNG")
            self.name.setText(query.value("Name"))
            self.path.setText(query.value("Path"))
            self.description.setPlainText(query.value("Description"))
            self.command.setPlainText(query.value("Command"))
            self.argument.setText(query.value("Argument"))
            # Add environment variables
            self.add_envs()

    def add_envs(self):
        """Function to get data from database and add environment variables in the table view in the dialog."""
        self.query = QSqlQueryModel()
        self.query.setQuery(
            f"SELECT EnvID, Name, Value, ExeOrder, AppID FROM Env WHERE AppID = {self.id} OR AppID = -1 ORDER BY ExeOrder ASC"
        )
        self.env_table.setModel(self.query)
        # Hide EnvID, ExeOrder and AppID
        self.env_table.hideColumn(0)
        self.env_table.hideColumn(3)
        self.env_table.hideColumn(4)
        # Force mouse click on a cell in the table to select the whole row
        self.env_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        # Only allow to select one row.
        self.env_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.env_table.horizontalHeader().setStretchLastSection(True)

    def lookup(self):
        """Function for the look up button. It allows the user to select an application file and sets the path in the path input field."""
        fname = QFileDialog.getOpenFileName(
            self, "Select App File", "/", "All files (*);;"
        )
        if fname[0] != "":
            self.path.setText(fname[0])

    def set_pixmap(self):
        """Function for the icon button. It allows the user to select an image file, sets the selected image to the button and save the data in buffer."""
        fname = QFileDialog.getOpenFileName(
            self, "Select Image", "/", "Image Files (*.jpg *.png)"
        )
        if fname[0] != "":
            image = QPixmap(fname[0])
            if image.size().width() > image.size().height():
                image = image.scaledToWidth(96)
            else:
                image = image.scaledToHeight(96)
            self.icon.setIcon(QIcon(image))
            buffer = QBuffer(self.icon_img)
            buffer.open(QIODevice.WriteOnly)
            image.save(buffer, "PNG")

    def save(self):
        """Function for the save button. It inserts a new data into database for add new dialog and update data for edit dialog."""
        if self.name.text() == "" or self.path.text() == "":
            QMessageBox.critical(self, "Values not set", "Please fill in Name and Path")
        elif self.new:
            # Insert new app
            query = QSqlQuery()
            query.prepare(
                "INSERT INTO App (Name, Path, Description, Icon, Command, Argument) VALUES (?,?,?,?,?,?)"
            )
            query.bindValue(0, self.name.text())
            query.bindValue(1, self.path.text())
            query.bindValue(2, self.description.toPlainText())
            query.bindValue(3, self.icon_img)
            query.bindValue(4, self.command.toPlainText())
            query.bindValue(5, self.argument.text())
            if not query.exec():
                print("Error ", query.lastError().text())
            id = query.lastInsertId()
            # Update the AppID of the temporary added environment variables to the new AppID
            query = QSqlQuery()
            query.prepare("UPDATE Env Set AppID = ? WHERE AppID = -1")
            query.bindValue(0, id)
            if not query.exec():
                print("Error ", query.lastError().text())
            # Remove environment variables whose AppID had been set to -2 to hide from the table temporary
            QSqlQuery("DELETE FROM Env WHERE AppID = -2")
            self.accept()
        else:
            # Update the app data with the user inputs
            query = QSqlQuery()
            query.prepare(
                "UPDATE App SET Name = ?, Path = ?, Description = ?, Icon = ?, Command = ?, Argument = ? WHERE AppID = ?"
            )
            query.bindValue(0, self.name.text())
            query.bindValue(1, self.path.text())
            query.bindValue(2, self.description.toPlainText())
            query.bindValue(3, self.icon_img)
            query.bindValue(4, self.command.toPlainText())
            query.bindValue(5, self.argument.text())
            query.bindValue(6, self.id)
            if not query.exec():
                print("Error ", query.lastError().text())
            # Update the AppID of the temporary added environment variables to the new AppID
            query = QSqlQuery()
            query.prepare("UPDATE Env Set AppID = ? WHERE AppID = -1")
            query.bindValue(0, self.id)
            if not query.exec():
                print("Error ", query.lastError().text())
            # Remove environment variables whose AppID had been set to -2 to hide from the table temporary
            QSqlQuery("DELETE FROM Env WHERE AppID = -2")
            self.accept()

    def remove_icon(self):
        """Function for the remove button. It removes the icon from the button and data from the buffer."""
        self.icon_img.clear()
        self.icon.setIcon(QIcon())

    def up(self):
        """Function for Up button in the environment variable section.
        It switches the execution order of the selected environment variable with the one above if a variable is selected.
        Otherwise, it displays a message box to ask user to select a variable."""
        # Check if model is set and a row is selected
        if self.env_table.selectionModel() != None and self.env_table.selectionModel().hasSelection():
            row = self.env_table.selectionModel().selectedRows()[0].row()
            id = self.query.data(self.query.index(row, 0))
            name = self.query.data(self.query.index(row, 1))
            value = self.query.data(self.query.index(row, 2))
            order = self.query.data(self.query.index(row, 3))
            appid = self.query.data(self.query.index(row, 4))

            replaceid = self.query.data(self.query.index(row-1, 0))
            replacename = self.query.data(self.query.index(row-1, 1))
            replacevalue = self.query.data(self.query.index(row-1, 2))
            replaceorder = self.query.data(self.query.index(row-1, 3))
            replaceappid = self.query.data(self.query.index(row-1, 4))

            # If the AppID of the selected environment variable is already set to -1, just update the execution order
            if appid == -1:
                QSqlQuery(f"UPDATE Env Set ExeOrder = {replaceorder} WHERE EnvID = {id}")
            else:
                # Otherwise, insert new one with the current name and value and new execution order as a temporal value (AppID = -1)
                query = QSqlQuery()
                query.prepare("INSERT INTO Env (Name, Value, ExeOrder, AppID) VALUES (?,?,?,-1)")
                query.bindValue(0, name)
                query.bindValue(1, value)
                query.bindValue(2, replaceorder)
                if not query.exec():
                    print("Error ", query.lastError().text())
                # If it is an edit dialog, store the old data by update the AppID to -2
                if self.id != -1:
                    QSqlQuery(f"UPDATE Env Set AppID = -2 WHERE EnvID = {id}")

            # If the AppID of the replaced environment variable is already set to -1, just update the execution order
            if replaceappid == -1:
                QSqlQuery(f"UPDATE Env Set ExeOrder = {order} WHERE EnvID = {replaceid}")
            else:
                # Otherwise, insert new one with the current name and value and new execution order as a temporal value (AppID = -1)
                query = QSqlQuery()
                query.prepare("INSERT INTO Env (Name, Value, ExeOrder, AppID) VALUES (?,?,?,-1)")
                query.bindValue(0, replacename)
                query.bindValue(1, replacevalue)
                query.bindValue(2, order)
                if not query.exec():
                    print("Error ", query.lastError().text())
                # If it is an edit dialog, store the old data by update the AppID to -2
                if self.id != -1:
                    QSqlQuery(f"UPDATE Env Set AppID = -2 WHERE EnvID = {replaceid}")
            # Update the environment variable table
            self.add_envs()
        # Pop up a message box if no row is selected
        else:
            QMessageBox.warning(
                self,
                "Environment variable not selected",
                "Please select an environment variable to edit",
            )

    def down(self):
        """Function for Down button in the environment variable section.
        It switches the execution order of the selected environment variable with the one below if a variable is selected.
        Otherwise, it displays a message box to ask user to select a variable."""
        # Check if model is set and a row is selected
        if self.env_table.selectionModel() != None and self.env_table.selectionModel().hasSelection():
            row = self.env_table.selectionModel().selectedRows()[0].row()
            id = self.query.data(self.query.index(row, 0))
            name = self.query.data(self.query.index(row, 1))
            value = self.query.data(self.query.index(row, 2))
            order = self.query.data(self.query.index(row, 3))
            appid = self.query.data(self.query.index(row, 4))

            replaceid = self.query.data(self.query.index(row+1, 0))
            replacename = self.query.data(self.query.index(row+1, 1))
            replacevalue = self.query.data(self.query.index(row+1, 2))
            replaceorder = self.query.data(self.query.index(row+1, 3))
            replaceappid = self.query.data(self.query.index(row+1, 4))

            # If the AppID of the selected environment variable is already set to -1, just update the execution order
            if appid == -1:
                QSqlQuery(f"UPDATE Env Set ExeOrder = {replaceorder} WHERE EnvID = {id}")
            else:
                # Otherwise, insert new one with the current name and value and new execution order as a temporal value (AppID = -1)
                query = QSqlQuery()
                query.prepare("INSERT INTO Env (Name, Value, ExeOrder, AppID) VALUES (?,?,?,-1)")
                query.bindValue(0, name)
                query.bindValue(1, value)
                query.bindValue(2, replaceorder)
                if not query.exec():
                    print("Error ", query.lastError().text())
                # If it is an edit dialog, store the old data by update the AppID to -2
                if self.id != -1:
                    QSqlQuery(f"UPDATE Env Set AppID = -2 WHERE EnvID = {id}")

            # If the AppID of the replaced environment variable is already set to -1, just update the execution order
            if replaceappid == -1:
                QSqlQuery(f"UPDATE Env Set ExeOrder = {order} WHERE EnvID = {replaceid}")
            else:
                # Otherwise, insert new one with the current name and value and new execution order as a temporal value (AppID = -1)
                query = QSqlQuery()
                query.prepare("INSERT INTO Env (Name, Value, ExeOrder, AppID) VALUES (?,?,?,-1)")
                query.bindValue(0, replacename)
                query.bindValue(1, replacevalue)
                query.bindValue(2, order)
                if not query.exec():
                    print("Error ", query.lastError().text())
                # If it is an edit dialog, store the old data by update the AppID to -2
                if self.id != -1:
                    QSqlQuery(f"UPDATE Env Set AppID = -2 WHERE EnvID = {replaceid}")
            # Update the environment variable table
            self.add_envs()
        # Pop up a message box if no row is selected
        else:
            QMessageBox.warning(
                self,
                "Environment variable not selected",
                "Please select an environment variable to edit",
            )

    def env_new(self):
        """Function for New button in the environment variable section.
        It opens an empty environment variable dialog and updates the environment variable table when new variable is added.
        """
        self.envdialog = EnvDialog(self.id)
        if self.envdialog.exec():
            self.add_envs()

    def env_edit(self):
        """Function for Edit button in the environment variable section.
        It opens the environment variable dialog with the existing data and updates the data on return if a variable is selected.
        Otherwise, it displays a message box to ask user to select a variable."""
        if self.env_table.selectionModel() != None and self.env_table.selectionModel().hasSelection():
            row = self.env_table.selectionModel().selectedRows()[0].row()
            envid = self.query.data(self.query.index(row, 0))
            self.envdialog = EnvDialog(self.id, envid)
            if self.envdialog.exec():
                self.add_envs()
        else:
            QMessageBox.warning(
                self,
                "Environment variable not selected",
                "Please select an environment variable to edit",
            )

    def env_remove(self):
        """Function for Remove button in the environment variable section.
        It removes the selected environment variable from the database and update the environment variable table in the dialog.
        It displays a message box to ask user to select a variable if not selected."""
        if self.env_table.selectionModel() != None and self.env_table.selectionModel().hasSelection():
            row = self.env_table.selectionModel().selectedRows()[0].row()
            envid = self.query.data(self.query.index(row, 0))
            # If the environment variable is a temporal value, just delete it from the database
            if self.query.data(self.query.index(row, 4)) == -1:
                QSqlQuery(f"DELETE FROM Env WHERE EnvID = {envid}")
            # Otherwise, store it by setting its AppID to -2
            else :
                QSqlQuery(f"UPDATE Env Set AppID = -2 WHERE EnvID = {envid}")
            self.add_envs()
        else:
            QMessageBox.warning(
                self,
                "Environment variable not selected",
                "Please select an environment variable to remove",
            )
