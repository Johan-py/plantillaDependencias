from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QTextEdit,
    QLabel,
    QLineEdit
)
from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import Signal, QObject
import threading

from core import installer_core as core


class Logger(QObject):

    log_signal = Signal(str)
    ssh_signal = Signal(str)

    def log(self, msg):
        self.log_signal.emit(msg)

    def show_ssh(self, key):
        self.ssh_signal.emit(key)

class VentanaPrincipal(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Plantilla instaladora V1.0")
        self.resize(600, 600)

        layout = QVBoxLayout()

        titulo = QLabel("Instalador de entorno Dev")
        layout.addWidget(titulo)

        self.git_name = QLineEdit()
        self.git_name.setPlaceholderText("Git Username")

        self.git_email = QLineEdit()
        self.git_email.setPlaceholderText("Git Email")

        layout.addWidget(self.git_name)
        layout.addWidget(self.git_email)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)

        layout.addWidget(self.log_box)

        btn_install = QPushButton("correr Instalador :)")
        btn_install.clicked.connect(self.run_installer)

        layout.addWidget(btn_install)

        self.setLayout(layout)

        # logger seguro para threads
        self.logger = Logger()
        self.logger.log_signal.connect(self.log_box.append)
        self.logger.ssh_signal.connect(self.show_ssh_popup)

    # ----------------------

    def run_thread(self, func):
        thread = threading.Thread(target=func)
        thread.start()

    # ----------------------
    def show_ssh_popup(self, key):

        msg = QMessageBox(self)

        msg.setWindowTitle("GitHub SSH Setup")

        msg.setText(
            "Agrega la clave SSH a GitHub siguiendo el enlace y dando a 'add new ssh key', copiando y pegando el contenido de abajo:\n\n"
            "https://github.com/settings/keys\n\n"
            + key
        )

        msg.exec()
    # -----------------------
    def run_installer(self):

        name = self.git_name.text()
        email = self.git_email.text()

        def task():

            log = self.logger.log

            log("Iniciando intalacion...")

            core.install_git(log)
            core.configure_git(name, email, log)

            core.install_git_credentials(log)

            core.setup_github_ssh(email, log, self.logger.show_ssh)
            core.install_node(log)
            core.install_bun(log)

            core.install_supabase(log)
            core.install_prisma(log)

            core.install_eslint(log)
            core.install_prettier(log)

            core.install_husky(log)

            core.configure_git_hooks(log)

            core.configure_prettier(log)
            core.configure_eslint(log)

            log("Entorno Listo")

        self.run_thread(task)