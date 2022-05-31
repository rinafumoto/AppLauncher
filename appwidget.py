#!/usr/bin/env python
import os
import re

from PyQt5 import uic
from PyQt5.QtCore import QByteArray, QProcess, QProcessEnvironment, Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtSql import QSqlQuery
from PyQt5.QtWidgets import QLabel, QMessageBox, QVBoxLayout, QWidget

from editdialog import EditDialog


class AppWidget(QWidget):
    """Class for the app widget added to the main window.

    Attributes
    ----------
    removed : pyqtSignal
        Signal to be sent to main window when the remove button is clicked.

    id : int
        The App ID saved in the database.
    
    name : str
        The application name.

    path : str
        The application file path.

    command : str
        Additional command to be executed on before launching the app.

    arg : str
        Arguments for launching the app.

    env : QProcessEnvironment
        System environment variables.
    """

    removed = pyqtSignal()
    id: int = None
    name: str = ""
    path: str = ""
    command: str = ""
    arg: str = ""
    env: QProcessEnvironment = QProcessEnvironment.systemEnvironment()

    def __init__(self, id):
        """Load UI, get data from the database and connect the button to the corresponding functions.

        Parameters
        ----------
        id: int
            The App ID saved in the database.
        """
        super(AppWidget, self).__init__()
        # Load UI
        uic.loadUi("ui/app.ui", self)
        # Set icon for the remove button
        bin_icon = QPixmap("icons/bin.png")
        self.remove_btn.setIcon(QIcon(bin_icon))
        # Set layout for the launch button instead of setting an icon and text as the layout control is limited in that way
        self.launch_btn.setLayout(QVBoxLayout())
        self.id = id
        # Get the app data
        self.get_data()
        # Connect button clicked signal to corresponding functions
        self.launch_btn.clicked.connect(self.launch)
        self.edit_btn.clicked.connect(self.edit)
        self.remove_btn.clicked.connect(self.remove)

    def get_data(self):
        """Function for getting data from the database and set the icon to the launch button."""
        query = QSqlQuery(f"SELECT * FROM App WHERE AppID = {self.id}")
        query.next()
        self.name = query.value("Name")
        icon = query.value("Icon")
        # Clear the launch button layout
        while self.launch_btn.layout().count():
            self.launch_btn.layout().takeAt(0).widget().deleteLater()
        # Set the icon to the launch button if available
        if type(icon) == QByteArray:
            pixmap = QPixmap()
            pixmap.loadFromData(QByteArray(icon), "png")
            button = QLabel()
            pixmap = pixmap.scaled(128, 128)
            button.setPixmap(pixmap)
            self.launch_btn.layout().addWidget(button)
        # Set the app name to the launch button
        label = QLabel()
        label.setText(self.name)
        label.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        label.setFixedHeight(30)
        self.launch_btn.layout().addWidget(label)
        self.launch_btn.layout().setAlignment(Qt.AlignCenter)
        # Set app description to the launch button as a tooltip
        self.launch_btn.setToolTip(query.value("Description"))
        self.path = query.value("Path")
        self.command = query.value("Command")
        self.arg = query.value("Argument")

    def launch(self):
        """Run the additional commands, set environment variables and launch the app."""
        # Try launching the app if no additional commands or commands successfully executed.
        if self.command == "" or self.run_commands(self.command):
            # Get the environment variable from the database and set them to the process in order
            query = QSqlQuery(f"SELECT * FROM Env WHERE AppID = {self.id} ORDER BY ExeOrder ASC")
            while query.next():
                value = query.value("Value")
                value = self.replace_env(value)
                self.env.insert(query.value("Name"), value)
            process = QProcess()
            process.setProgram(self.replace_env(self.path))
            process.setArguments(self.arg.split())
            process.setProcessEnvironment(self.env)
            orig_path = os.environ["PATH"]
            os.environ["PATH"] = process.processEnvironment().value("PATH")
            if process.startDetached()[0] == False:
                QMessageBox.critical(
                    self, "Launch Failed", "Please check the configuration"
                )
            os.environ["PATH"] = orig_path

    def run_commands(self, commands):
        """Run the additional commands. It runs backtick commands first and replace the returned value with the commands.

        Returns
        -------
        bool
            True if commands are successfully executed, otherwise False.
        """
        process = QProcess()

        # Replace backtick commands
        if (count := int(commands.count("`") / 2)) > 0:
            sub = commands
            for i in range(count):
                firstindex = sub.find("`") + 1
                sub = sub[firstindex::]
                secondindex = sub.find("`")
                backtick = sub[0:secondindex]
                sub = sub[secondindex + 1 : :]
                process.start(backtick)
                process.waitForFinished()
                replacement = process.readLine().data().decode()
                commands = commands.replace("`" + backtick + "`", replacement)

        # Run commands
        commands = re.sub(r"(\n+)", r"; ", commands)
        bash = f'bash -c " {commands} ; env"'
        process.start(bash)
        if process.waitForStarted() and process.waitForFinished():
            error = process.readAllStandardError().data().decode()
            # If no error, replace all the system environment variables with the environment variables set with the commands 
            if error == "":
                self.env.clear()
                for env in process.readAll().data().decode().splitlines():
                    if env.count("=") == 1:
                        name = env.split("=")[0]
                        val = env.split("=")[1]
                        self.env.insert(name, val)
                return True
            # Otherwise, pop up a message box and display the error
            else :
                QMessageBox.critical(
                    self, "Run Additional Command Failed", error
                )
                return False
        # Pop up a message box if it failed to execute the commands
        else:
            QMessageBox.critical(
                self, "Run Additional Command Failed", "Please check the configuration"
            )
            return False

    def replace_env(self, text):
        """Replace environment variables in a text with the actual values.

        Returns
        -------
        text : str
            Replaced text.
        """
        if (count := text.count("$")) > 0:
            sub = text
            for i in range(count):
                firstindex = sub.find('"$') + 2
                sub = sub[firstindex::]
                secondindex = sub.find('"')
                v = sub[0:secondindex]
                sub = sub[secondindex + 1 : :]
                replacement = self.env.value(v)
                text = text.replace(f'"${v}"', replacement)
        return text

    def edit(self):
        """Function for Edit button. It displays an Edit Dialog with exisitng data.
        Replace the data with new data if editted. Otherwise, remove the newly added environment variables and get the previously saved ones."""
        self.editdialog = EditDialog(self.id)
        # Update the data if the update on the edit dialog is saved
        if self.editdialog.exec():
            self.get_data()
        # Otherwise, remove the temporary saved environment variables and get the original ones back
        else:
            QSqlQuery("DELETE FROM Env WHERE AppID = -1")
            QSqlQuery(f"UPDATE Env Set AppID = {self.id} WHERE AppID = -2")

    def remove(self):
        """Function for the Remove button. It displays a message box to confirm the action.
        Remove the data from the database and emit the removed signal if confirmed."""
        msg = QMessageBox.question(
            self,
            "Remove App",
            f"Are you sure you want to remove {self.name} ?",
        )
        if msg == QMessageBox.Yes:
            QSqlQuery(f"DELETE FROM App WHERE AppID = {self.id}")
            QSqlQuery(f"DELETE FROM Env WHERE AppID = {self.id}")
            self.removed.emit()
