import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
)
from PyQt5.QtCore import Qt

def buscar_nome_cliente(cliente_id):
    if not cliente_id:
        return 'Consumidor Final'
    try:
        conn = sqlite3.connect('clientes.db')
        c = conn.cursor()
        c.execute('SELECT nome FROM clientes WHERE id=?', (cliente_id,))
        row = c.fetchone()
        conn.close()
        return row[0] if row else 'Consumidor Final'
    except:
        return 'Consumidor Final'

class ConsultaVendas(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Consulta de Vendas')
        self.setGeometry(220, 220, 800, 500)
        self.init_ui()
        self.carregar_vendas()

    def init_ui(self):
        layout = QVBoxLayout()

        # Filtro simples por cliente
        hbox = QHBoxLayout()
        self.pesquisa_input = QLineEdit()
        self.pesquisa_input.setPlaceholderText('Pesquisar por nome do cliente...')
        btn_pesquisar = QPushButton('Pesquisar')
        btn_pesquisar.clicked.connect(self.pesquisar_vendas)
        hbox.addWidget(self.pesquisa_input)
        hbox.addWidget(btn_pesquisar)
        layout.addLayout(hbox)

        # Tabela de vendas
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels(['ID', 'Data', 'Cliente', 'Total', 'Valor Recebido', 'Troco'])
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela.cellDoubleClicked.connect(self.mostrar_itens_venda)
        layout.addWidget(self.tabela)

        self.setLayout(layout)

    def carregar_vendas(self, filtro=None):
        conn = sqlite3.connect('vendas.db')
        c = conn.cursor()
        c.execute('SELECT * FROM vendas')
        vendas = c.fetchall()
        conn.close()

        self.tabela.setRowCount(0)
        for row_idx, venda in enumerate(vendas):
            cliente_nome = buscar_nome_cliente(venda[2])
            if filtro and filtro.lower() not in cliente_nome.lower():
                continue
            self.tabela.insertRow(row_idx)
            self.tabela.setItem(row_idx, 0, QTableWidgetItem(str(venda[0])))
            self.tabela.setItem(row_idx, 1, QTableWidgetItem(str(venda[1])))
            self.tabela.setItem(row_idx, 2, QTableWidgetItem(cliente_nome))
            self.tabela.setItem(row_idx, 3, QTableWidgetItem(f'R$ {venda[3]:.2f}'))
            self.tabela.setItem(row_idx, 4, QTableWidgetItem(f'R$ {venda[4]:.2f}'))
            self.tabela.setItem(row_idx, 5, QTableWidgetItem(f'R$ {venda[5]:.2f}'))

    def pesquisar_vendas(self):
        filtro = self.pesquisa_input.text()
        self.carregar_vendas(filtro)

    def mostrar_itens_venda(self, row, column):
        venda_id = self.tabela.item(row, 0).text()
        conn = sqlite3.connect('vendas.db')
        c = conn.cursor()
        c.execute('SELECT produto_id, quantidade, preco_unitario, subtotal FROM itens_venda WHERE venda_id=?', (venda_id,))
        itens = c.fetchall()
        conn.close()

        # Buscar nome dos produtos
        conn = sqlite3.connect('produtos.db')
        c = conn.cursor()
        itens_detalhados = []
        for item in itens:
            c.execute('SELECT nome FROM produtos WHERE id=?', (item[0],))
            nome_prod = c.fetchone()
            nome_prod = nome_prod[0] if nome_prod else 'Produto removido'
            itens_detalhados.append((nome_prod, item[1], item[2], item[3]))
        conn.close()

        texto = 'Itens da venda:\n\n'
        for nome, qtd, preco, subtotal in itens_detalhados:
            texto += f'{nome} - Qtd: {qtd} - Preço: R$ {preco:.2f} - Subtotal: R$ {subtotal:.2f}\n'
        QMessageBox.information(self, 'Itens da Venda', texto)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    janela = ConsultaVendas()
    janela.show()
    sys.exit(app.exec_())
