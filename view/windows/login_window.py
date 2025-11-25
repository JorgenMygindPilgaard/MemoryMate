import sys

from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QLabel, QApplication
from configuration.language import Texts

class LoginWindow():
    def __init__(self,
             title=Texts.get("login_window_title"),
             message=None,
             user=None,
             request_user=True,
             user_label=Texts.get("login_window_user_label"),
             protect_user_field=False,
             password=None,
             request_password=True,
             password_label=Texts.get("login_window_password_label"),
             protect_password_field=False,
             mfa_code=None,
             request_mfa_code=False,
             mfa_code_label=Texts.get("login_window_mfa_code_label")
             ):
        self.title = title
        self.message = message
        self.user = user
        self.request_user=request_user
        self.user_label = user_label
        self.protect_user_field = protect_user_field
        self.password = password
        self.request_password=request_password
        self.password_label = password_label
        self.protect_password_field = protect_password_field
        self.mfa_code = mfa_code
        self.request_mfa_code = request_mfa_code
        self.mfa_code_label = mfa_code_label
        self.button=None


    def show(self):
        while True:
            dialog=QDialog()
            dialog.setWindowTitle(self.title)
            layout = QFormLayout(dialog)
            dialog.setLayout(layout)

            # User field
            user_edit = QLineEdit(self.user if self.user else "")
            user_edit.setMinimumWidth(200)
            if self.request_user:
                if self.protect_user_field:
                    user_edit.setReadOnly(True)
                layout.addRow(self.user_label, user_edit)

            # Password field
            password_edit = QLineEdit(self.password if self.password else "")
            if self.request_password:
                password_edit.setEchoMode(QLineEdit.EchoMode.Password)
                if self.protect_password_field:
                    password_edit.setReadOnly(True)
                layout.addRow(self.password_label, password_edit)

            # MFA field (optional)
            mfa_edit = QLineEdit()
            if self.request_mfa_code:
                layout.addRow(self.mfa_code_label, mfa_edit)
                mfa_edit.setFocus() # Place cursor in MFA field

            # Message-field
            if self.message:
                message_label = QLabel(self.message)
                layout.addRow(message_label, QLabel())

            # Set focus to one of the input fields in prioritized order
            if self.request_user and user_edit.text() == "":   # ...priority 1: First blank, requested field
                user_edit.setFocus()
            elif self.request_password and password_edit.text() == "":
                password_edit.setFocus()
            elif self.request_mfa_code and mfa_edit.text() == "":
                mfa_edit.setFocus()
            elif self.request_mfa_code:                       # ...priority 2: Last requested (nonblank) field
                mfa_edit.setFocus()
            elif self.request_password:
                password_edit.setFocus()
            elif self.request_user:
                password_edit.setFocus()

            # OK/Cancel buttons
            buttons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
            )
            buttons.button(QDialogButtonBox.StandardButton.Ok).setText(Texts.get("general_ok"))
            buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(Texts.get("general_cancel"))
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addRow(buttons)


        # Run dialog
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.user = user_edit.text().strip()
                if self.user == "":
                    self.user = None
                self.password = password_edit.text().strip()
                if self.password == "":
                    self.password = None
                self.mfa_code = mfa_edit.text().strip()
                if self.mfa_code == "":
                    self.mfa_code = None

                if not self.user and self.request_user and not self.protect_user_field:
                    self.message=Texts.get("login_window_message_user_missing")
                    continue

                if not self.password and self.request_password and not self.protect_password_field:
                    self.message=Texts.get("login_window_message_password_missing")
                    continue

                if not self.mfa_code and self.request_mfa_code:
                    self.message=Texts.get("login_window_message_mfa_code_missing")
                    continue
                self.button="ok"
            else:
                self.button="cancel"
            return self.button,self.user, self.password, self.mfa_code

    def getInfo(self):
        return self.button,self.user,self.password,self.mfa_code

