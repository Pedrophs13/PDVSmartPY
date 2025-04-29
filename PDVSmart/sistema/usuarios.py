import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox,
    QFrame, QTableWidget, QTableWidgetItem, QComboBox
)
from PyQt5.QtCore import Qt

def criar_banco_usuarios():
    conn = sqlite3.connect('db/usuarios.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            login TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL,
            tipo TEXT NOT NULL,
            ativo INTEGER DEFAULT 1
        )
    ''')
    # Criar usuário admin padrão se não existir
    c.execute('SELECT id FROM usuarios WHERE login = ?', ('admin',))
    if not c.fetchone():
        c.execute('INSERT INTO usuarios (nome, login, senha, tipo) VALUES (?, ?, ?, ?)',
                  ('Administrador', 'admin', 'admin123', 'administrador'))
    conn.commit()
    conn.close()

class CadastroUsuarios(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Cadastro de Usuários')
        self.setGeometry(120, 120, 540, 420)
        self.setStyleSheet('background: #f5f7fa;')
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(18)

        # Área de cadastro
        frame_cad = QFrame()
        frame_cad.setFrameShape(QFrame.StyledPanel)
        frame_cad.setStyleSheet('background: #ffffff; border-radius: 8px; padding: 14px;')
        vbox_cad = QVBoxLayout(frame_cad)
        
        lbl_titulo = QLabel('<b>Cadastro de Usuário</b>')
        lbl_titulo.setStyleSheet('font-size: 18px; color: #1976d2;')
        vbox_cad.addWidget(lbl_titulo)

        # Nome
        self.nome_label = QLabel('Nome:')
        self.nome_label.setStyleSheet('font-size: 15px; color: #2e3b4e;')
        self.nome_input = QLineEdit()
        self.nome_input.setMinimumHeight(32)
        self.nome_input.setStyleSheet('font-size: 15px; padding: 4px 8px;')
        vbox_cad.addWidget(self.nome_label)
        vbox_cad.addWidget(self.nome_input)

        # Login
        self.login_label = QLabel('Login:')
        self.login_label.setStyleSheet('font-size: 15px; color: #2e3b4e;')
        self.login_input = QLineEdit()
        self.login_input.setMinimumHeight(32)
        self.login_input.setStyleSheet('font-size: 15px; padding: 4px 8px;')
        vbox_cad.addWidget(self.login_label)
        vbox_cad.addWidget(self.login_input)

        # Senha
        self.senha_label = QLabel('Senha:')
        self.senha_label.setStyleSheet('font-size: 15px; color: #2e3b4e;')
        self.senha_input = QLineEdit()
        self.senha_input.setEchoMode(QLineEdit.Password)
        self.senha_input.setMinimumHeight(32)
        self.senha_input.setStyleSheet('font-size: 15px; padding: 4px 8px;')
        vbox_cad.addWidget(self.senha_label)
        vbox_cad.addWidget(self.senha_input)

        # Tipo de usuário
        self.tipo_label = QLabel('Tipo de Usuário:')
        self.tipo_label.setStyleSheet('font-size: 15px; color: #2e3b4e;')
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(['administrador', 'operador'])
        self.tipo_combo.setMinimumHeight(32)
        self.tipo_combo.setStyleSheet('font-size: 15px; padding: 4px 8px;')
        vbox_cad.addWidget(self.tipo_label)
        vbox_cad.addWidget(self.tipo_combo)

        # Botão Salvar
        self.btn_salvar = QPushButton('Salvar Usuário')
        self.btn_salvar.setStyleSheet('background: #1976d2; color: white; font-size: 16px; padding: 10px 0; border-radius: 8px;')
        self.btn_salvar.setMinimumHeight(38)
        self.btn_salvar.clicked.connect(self.salvar_usuario)
        vbox_cad.addWidget(self.btn_salvar)

        layout.addWidget(frame_cad)

        # Área de tabela de usuários
        frame_tab = QFrame()
        frame_tab.setFrameShape(QFrame.StyledPanel)
        frame_tab.setStyleSheet('background: #ffffff; border-radius: 8px; padding: 10px;')
        vbox_tab = QVBoxLayout(frame_tab)
        
        lbl_lista = QLabel('<b>Usuários Cadastrados</b>')
        lbl_lista.setStyleSheet('font-size: 16px; color: #2e3b4e;')
        vbox_tab.addWidget(lbl_lista)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(4)
        self.tabela.setHorizontalHeaderLabels(['ID', 'Nome', 'Login', 'Tipo'])
        self.tabela.setStyleSheet('font-size: 14px; background: #f8fafc;')
        self.tabela.setAlternatingRowColors(True)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        vbox_tab.addWidget(self.tabela)

        layout.addWidget(frame_tab)
        self.setLayout(layout)
        self.atualizar_tabela()

    def salvar_usuario(self):
        nome = self.nome_input.text()
        login = self.login_input.text()
        senha = self.senha_input.text()
        tipo = self.tipo_combo.currentText()

        if not nome or not login or not senha:
            QMessageBox.warning(self, 'Erro', 'Preencha todos os campos!')
            return

        try:
            conn = sqlite3.connect('db/usuarios.db')
            c = conn.cursor()
            c.execute('INSERT INTO usuarios (nome, login, senha, tipo) VALUES (?, ?, ?, ?)',
                      (nome, login, senha, tipo))
            conn.commit()
            conn.close()
            QMessageBox.information(self, 'Sucesso', 'Usuário cadastrado com sucesso!')
            self.nome_input.clear()
            self.login_input.clear()
            self.senha_input.clear()
            self.tipo_combo.setCurrentIndex(0)
            self.atualizar_tabela()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, 'Erro', 'Login já existe!')
        except Exception as e:
            QMessageBox.warning(self, 'Erro', f'Erro ao salvar usuário: {str(e)}')

    def atualizar_tabela(self):
        conn = sqlite3.connect('db/usuarios.db')
        c = conn.cursor()
        c.execute('SELECT id, nome, login, tipo FROM usuarios WHERE ativo = 1')
        usuarios = c.fetchall()
        conn.close()

        self.tabela.setRowCount(0)
        for usuario in usuarios:
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            for col, valor in enumerate(usuario):
                self.tabela.setItem(row, col, QTableWidgetItem(str(valor)))

if __name__ == '__main__':
    criar_banco_usuarios()
    app = QApplication(sys.argv)
    janela = CadastroUsuarios()
    janela.show()
    sys.exit(app.exec_())