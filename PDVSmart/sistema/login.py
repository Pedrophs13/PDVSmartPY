import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox,
    QFrame
)
from PyQt5.QtCore import Qt

class Login(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Login')
        self.setGeometry(400, 200, 400, 300)
        self.setStyleSheet('background: #f5f7fa;')
        self.usuario_autenticado = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(18)

        # Frame principal
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setStyleSheet('background: #ffffff; border-radius: 8px; padding: 20px;')
        vbox = QVBoxLayout(frame)

        # Título
        lbl_titulo = QLabel('<b>Sistema PDV</b>')
        lbl_titulo.setStyleSheet('font-size: 24px; color: #1976d2; margin-bottom: 20px;')
        lbl_titulo.setAlignment(Qt.AlignCenter)
        vbox.addWidget(lbl_titulo)

        # Login
        self.login_label = QLabel('Login:')
        self.login_label.setStyleSheet('font-size: 15px; color: #2e3b4e;')
        self.login_input = QLineEdit()
        self.login_input.setMinimumHeight(32)
        self.login_input.setStyleSheet('font-size: 15px; padding: 4px 8px; border: 1px solid #ccc; border-radius: 4px;')
        vbox.addWidget(self.login_label)
        vbox.addWidget(self.login_input)

        # Senha
        self.senha_label = QLabel('Senha:')
        self.senha_label.setStyleSheet('font-size: 15px; color: #2e3b4e;')
        self.senha_input = QLineEdit()
        self.senha_input.setEchoMode(QLineEdit.Password)
        self.senha_input.setMinimumHeight(32)
        self.senha_input.setStyleSheet('font-size: 15px; padding: 4px 8px; border: 1px solid #ccc; border-radius: 4px;')
        vbox.addWidget(self.senha_label)
        vbox.addWidget(self.senha_input)

        # Botão Entrar
        self.btn_entrar = QPushButton('Entrar')
        self.btn_entrar.setStyleSheet(
            'background: #1976d2; color: white; font-size: 16px; padding: 10px 0;'
            'border-radius: 8px; margin-top: 20px;'
        )
        self.btn_entrar.setMinimumHeight(38)
        self.btn_entrar.clicked.connect(self.fazer_login)
        vbox.addWidget(self.btn_entrar)

        layout.addWidget(frame)
        self.setLayout(layout)

    def fazer_login(self):
        login = self.login_input.text()
        senha = self.senha_input.text()

        if not login or not senha:
            QMessageBox.warning(self, 'Erro', 'Preencha todos os campos!')
            return

        try:
            conn = sqlite3.connect('db/usuarios.db')
            c = conn.cursor()
            c.execute('SELECT id, nome, tipo FROM usuarios WHERE login = ? AND senha = ? AND ativo = 1',
                      (login, senha))
            usuario = c.fetchone()
            conn.close()

            if usuario:
                self.usuario_autenticado = {
                    'id': usuario[0],
                    'nome': usuario[1],
                    'tipo': usuario[2]
                }
                self.accept()
            else:
                QMessageBox.warning(self, 'Erro', 'Login ou senha inválidos!')
        except Exception as e:
            QMessageBox.warning(self, 'Erro', f'Erro ao fazer login: {str(e)}')

    def accept(self):
        self.close()

    def get_usuario(self):
        return self.usuario_autenticado

if __name__ == '__main__':
    app = QApplication(sys.argv)
    login = Login()
    login.show()
    sys.exit(app.exec_())