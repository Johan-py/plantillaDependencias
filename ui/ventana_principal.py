from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QTextEdit,
    QLabel,
    QLineEdit,
    QDialog,
    QApplication,
    QMessageBox
)

from PySide6.QtCore import Signal, QObject
import threading

from core import installer_core as core


class Logger(QObject):

    log_signal = Signal(str)
    ssh_signal = Signal(str)
    finished_signal = Signal()

    def log(self, msg):
        self.log_signal.emit(msg)

    def show_ssh(self, key):
        self.ssh_signal.emit(key)

    def finished(self):
        self.finished_signal.emit()


class VentanaPrincipal(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Plantilla instaladora V1.0")
        self.resize(600, 600)

        self.installing = False

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

        self.btn_install = QPushButton("Correr instalador")
        self.btn_install.clicked.connect(self.run_installer)

        layout.addWidget(self.btn_install)

        self.setLayout(layout)

        # logger seguro para threads
        self.logger = Logger()
        self.logger.log_signal.connect(self.log_box.append)
        self.logger.ssh_signal.connect(self.show_ssh_popup)
        self.logger.finished_signal.connect(self.install_finished)

    # ----------------------

    def run_thread(self, func, *args):
        thread = threading.Thread(target=func, args=args, daemon=True)
        thread.start()

    # ----------------------

    def show_ssh_popup(self, key):

        dialog = QDialog(self)
        dialog.setWindowTitle("GitHub SSH Setup")
        dialog.resize(500, 300)

        layout = QVBoxLayout()

        label = QLabel(
            "Agrega esta clave SSH a GitHub:\n\n"
            "https://github.com/settings/keys\n\n"
            "Copia la clave de abajo:"
        )

        layout.addWidget(label)

        text = QTextEdit()
        text.setReadOnly(True)
        text.setText(key)
        text.selectAll()

        layout.addWidget(text)

        btn_copy = QPushButton("Copiar clave")

        def copy_key():
            QApplication.clipboard().setText(key)

        btn_copy.clicked.connect(copy_key)

        layout.addWidget(btn_copy)

        dialog.setLayout(layout)

        dialog.exec()

    # -----------------------

    def task_installer(self, name, email):

        log = self.logger.log

        try:

            log("Iniciando instalación...")

            core.install_git(log)
            core.configure_git(name, email, log)

            core.install_git_credentials(log)

            core.setup_github_ssh(email, log, self.logger.show_ssh)

            core.install_node(log)

            core.install_bun(log)
            core.ensure_bun_path(log)

            core.install_supabase(log)
            core.install_prisma(log)

            core.install_eslint(log)
            core.install_prettier(log)

            core.install_husky(log)

            core.configure_git_hooks(log)

            core.configure_prettier(log)
            core.configure_eslint(log)

            log("Entorno listo")

        except Exception as e:

            log(f"ERROR: {e}")

        finally:

            self.logger.finished()

    # -----------------------

    def install_finished(self):

        self.installing = False
        self.btn_install.setEnabled(True)

        self.logger.log("Instalación finalizada")

    # -----------------------

    def run_installer(self):

        if self.installing:
            return

        name = self.git_name.text().strip()
        email = self.git_email.text().strip()

        if not name or not email:
            QMessageBox.warning(self, "Error", "Debes ingresar Git username y email")
            return

        self.installing = True
        self.btn_install.setEnabled(False)

        self.run_thread(self.task_installer, name, email)