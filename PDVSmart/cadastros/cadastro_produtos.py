import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QFrame, QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import Qt

def criar_banco():
    conn = sqlite3.connect('produtos.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            codigo_barras TEXT
        )
    ''')
    conn.commit()
    conn.close()

def carregar_produtos():
    conn = sqlite3.connect('produtos.db')
    c = conn.cursor()
    c.execute('SELECT id, nome, preco, codigo_barras FROM produtos ORDER BY id DESC')
    produtos = c.fetchall()
    conn.close()
    return produtos

class CadastroProdutos(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Cadastro de Produtos')
        self.setGeometry(100, 100, 500, 420)
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
        lbl_titulo = QLabel('<b>Cadastro de Produto</b>')
        lbl_titulo.setStyleSheet('font-size: 18px; color: #1976d2;')
        vbox_cad.addWidget(lbl_titulo)
        self.nome_label = QLabel('Nome do Produto:')
        self.nome_label.setStyleSheet('font-size: 15px; color: #2e3b4e;')
        self.nome_input = QLineEdit()
        self.nome_input.setMinimumHeight(32)
        self.nome_input.setStyleSheet('font-size: 15px; padding: 4px 8px;')
        vbox_cad.addWidget(self.nome_label)
        vbox_cad.addWidget(self.nome_input)
        self.preco_label = QLabel('Preço:')
        self.preco_label.setStyleSheet('font-size: 15px; color: #2e3b4e;')
        self.preco_input = QLineEdit()
        self.preco_input.setMinimumHeight(32)
        self.preco_input.setStyleSheet('font-size: 15px; padding: 4px 8px;')
        vbox_cad.addWidget(self.preco_label)
        vbox_cad.addWidget(self.preco_input)
        self.cod_label = QLabel('Código de Barras:')
        self.cod_label.setStyleSheet('font-size: 15px; color: #2e3b4e;')
        self.cod_input = QLineEdit()
        self.cod_input.setMinimumHeight(32)
        self.cod_input.setStyleSheet('font-size: 15px; padding: 4px 8px;')
        vbox_cad.addWidget(self.cod_label)
        vbox_cad.addWidget(self.cod_input)
        self.btn_salvar = QPushButton('Salvar Produto')
        self.btn_salvar.setStyleSheet('background: #1976d2; color: white; font-size: 16px; padding: 10px 0; border-radius: 8px;')
        self.btn_salvar.setMinimumHeight(38)
        self.btn_salvar.clicked.connect(self.salvar_produto)
        vbox_cad.addWidget(self.btn_salvar)
        layout.addWidget(frame_cad)

        # Área de tabela de produtos
        frame_tab = QFrame()
        frame_tab.setFrameShape(QFrame.StyledPanel)
        frame_tab.setStyleSheet('background: #ffffff; border-radius: 8px; padding: 10px;')
        vbox_tab = QVBoxLayout(frame_tab)
        lbl_lista = QLabel('<b>Produtos Cadastrados</b>')
        lbl_lista.setStyleSheet('font-size: 16px; color: #2e3b4e;')
        vbox_tab.addWidget(lbl_lista)
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(4)
        self.tabela.setHorizontalHeaderLabels(['ID', 'Nome', 'Preço', 'Código de Barras'])
        self.tabela.setStyleSheet('font-size: 14px; background: #f8fafc;')
        self.tabela.setAlternatingRowColors(True)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        vbox_tab.addWidget(self.tabela)
        layout.addWidget(frame_tab)

        self.setLayout(layout)
        self.atualizar_tabela()

    def salvar_produto(self):
        nome = self.nome_input.text()
        preco = self.preco_input.text()
        codigo = self.cod_input.text()
        if not nome or not preco:
            QMessageBox.warning(self, 'Erro', 'Preencha todos os campos obrigatórios!')
            return
        try:
            preco = float(preco)
        except ValueError:
            QMessageBox.warning(self, 'Erro', 'Preço inválido!')
            return
        conn = sqlite3.connect('produtos.db')
        c = conn.cursor()
        c.execute('INSERT INTO produtos (nome, preco, codigo_barras) VALUES (?, ?, ?)', (nome, preco, codigo))
        conn.commit()
        conn.close()
        QMessageBox.information(self, 'Sucesso', 'Produto salvo com sucesso!')
        self.nome_input.clear()
        self.preco_input.clear()
        self.cod_input.clear()
        self.atualizar_tabela()

    def atualizar_tabela(self):
        produtos = carregar_produtos()
        self.tabela.setRowCount(0)
        for prod in produtos:
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            self.tabela.setItem(row, 0, QTableWidgetItem(str(prod[0])))
            self.tabela.setItem(row, 1, QTableWidgetItem(prod[1]))
            self.tabela.setItem(row, 2, QTableWidgetItem(f'R$ {prod[2]:.2f}'))
            self.tabela.setItem(row, 3, QTableWidgetItem(prod[3] if prod[3] else ''))

if __name__ == '__main__':
    criar_banco()
    app = QApplication(sys.argv)
    janela = CadastroProdutos()
    janela.show()
    sys.exit(app.exec_())