import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QFrame, QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import Qt

def criar_banco_clientes():
    conn = sqlite3.connect('db/clientes.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cpf_cnpj TEXT,
            telefone TEXT,
            email TEXT
        )
    ''')
    conn.commit()
    conn.close()

def carregar_clientes():
    conn = sqlite3.connect('db/clientes.db')
    c = conn.cursor()
    c.execute('SELECT id, nome, cpf_cnpj, telefone, email FROM clientes ORDER BY id DESC')
    clientes = c.fetchall()
    conn.close()
    return clientes

class CadastroClientes(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Cadastro de Clientes')
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
        lbl_titulo = QLabel('<b>Cadastro de Cliente</b>')
        lbl_titulo.setStyleSheet('font-size: 18px; color: #1976d2;')
        vbox_cad.addWidget(lbl_titulo)
        self.nome_label = QLabel('Nome do Cliente:')
        self.nome_label.setStyleSheet('font-size: 15px; color: #2e3b4e;')
        self.nome_input = QLineEdit()
        self.nome_input.setMinimumHeight(32)
        self.nome_input.setStyleSheet('font-size: 15px; padding: 4px 8px;')
        vbox_cad.addWidget(self.nome_label)
        vbox_cad.addWidget(self.nome_input)
        self.cpf_label = QLabel('CPF/CNPJ:')
        self.cpf_label.setStyleSheet('font-size: 15px; color: #2e3b4e;')
        self.cpf_input = QLineEdit()
        self.cpf_input.setMinimumHeight(32)
        self.cpf_input.setStyleSheet('font-size: 15px; padding: 4px 8px;')
        vbox_cad.addWidget(self.cpf_label)
        vbox_cad.addWidget(self.cpf_input)
        self.tel_label = QLabel('Telefone:')
        self.tel_label.setStyleSheet('font-size: 15px; color: #2e3b4e;')
        self.tel_input = QLineEdit()
        self.tel_input.setMinimumHeight(32)
        self.tel_input.setStyleSheet('font-size: 15px; padding: 4px 8px;')
        vbox_cad.addWidget(self.tel_label)
        vbox_cad.addWidget(self.tel_input)
        self.email_label = QLabel('E-mail:')
        self.email_label.setStyleSheet('font-size: 15px; color: #2e3b4e;')
        self.email_input = QLineEdit()
        self.email_input.setMinimumHeight(32)
        self.email_input.setStyleSheet('font-size: 15px; padding: 4px 8px;')
        vbox_cad.addWidget(self.email_label)
        vbox_cad.addWidget(self.email_input)
        self.btn_salvar = QPushButton('Salvar Cliente')
        self.btn_salvar.setStyleSheet('background: #1976d2; color: white; font-size: 16px; padding: 10px 0; border-radius: 8px;')
        self.btn_salvar.setMinimumHeight(38)
        self.btn_salvar.clicked.connect(self.salvar_cliente)
        vbox_cad.addWidget(self.btn_salvar)
        layout.addWidget(frame_cad)

        # Área de tabela de clientes
        frame_tab = QFrame()
        frame_tab.setFrameShape(QFrame.StyledPanel)
        frame_tab.setStyleSheet('background: #ffffff; border-radius: 8px; padding: 10px;')
        vbox_tab = QVBoxLayout(frame_tab)
        lbl_lista = QLabel('<b>Clientes Cadastrados</b>')
        lbl_lista.setStyleSheet('font-size: 16px; color: #2e3b4e;')
        vbox_tab.addWidget(lbl_lista)
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(5)
        self.tabela.setHorizontalHeaderLabels(['ID', 'Nome', 'CPF/CNPJ', 'Telefone', 'E-mail'])
        self.tabela.setStyleSheet('font-size: 14px; background: #f8fafc;')
        self.tabela.setAlternatingRowColors(True)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        vbox_tab.addWidget(self.tabela)
        layout.addWidget(frame_tab)

        self.setLayout(layout)
        self.atualizar_tabela()

    def salvar_cliente(self):
        nome = self.nome_input.text()
        cpf = self.cpf_input.text()
        telefone = self.tel_input.text()
        email = self.email_input.text()
        if not nome:
            QMessageBox.warning(self, 'Erro', 'Preencha o nome do cliente!')
            return
        conn = sqlite3.connect('db/clientes.db')
        c = conn.cursor()
        c.execute('INSERT INTO clientes (nome, cpf_cnpj, telefone, email) VALUES (?, ?, ?, ?)', (nome, cpf, telefone, email))
        conn.commit()
        conn.close()
        QMessageBox.information(self, 'Sucesso', 'Cliente salvo com sucesso!')
        self.nome_input.clear()
        self.cpf_input.clear()
        self.tel_input.clear()
        self.email_input.clear()
        self.atualizar_tabela()

    def atualizar_tabela(self):
        clientes = carregar_clientes()
        self.tabela.setRowCount(0)
        for cli in clientes:
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            for col in range(5):
                self.tabela.setItem(row, col, QTableWidgetItem(str(cli[col])))

if __name__ == '__main__':
    criar_banco_clientes()
    app = QApplication(sys.argv)
    janela = CadastroClientes()
    janela.show()
    sys.exit(app.exec_())
