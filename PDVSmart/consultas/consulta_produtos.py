import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QInputDialog, QFrame
)
from PyQt5.QtCore import Qt

class ConsultaProdutos(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Consulta de Produtos')
        self.setGeometry(150, 150, 650, 460)
        self.setStyleSheet('background: #f5f7fa;')
        self.init_ui()
        self.carregar_produtos()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(18)

        # Barra de busca/filtros
        frame_filtro = QFrame()
        frame_filtro.setFrameShape(QFrame.StyledPanel)
        frame_filtro.setStyleSheet('background: #e3f2fd; border-radius: 8px; padding: 12px;')
        hbox = QHBoxLayout(frame_filtro)
        self.pesquisa_input = QLineEdit()
        self.pesquisa_input.setPlaceholderText('Pesquisar por nome ou código de barras...')
        self.pesquisa_input.setMinimumHeight(32)
        self.pesquisa_input.setStyleSheet('font-size: 15px; padding: 4px 8px; border: 1px solid #ccc; border-radius: 4px;')
        btn_pesquisar = QPushButton('Pesquisar')
        btn_pesquisar.setStyleSheet('background: #1976d2; color: white; font-size: 15px; padding: 8px 20px; border-radius: 8px;')
        btn_pesquisar.setMinimumHeight(32)
        btn_pesquisar.clicked.connect(self.pesquisar_produtos)
        hbox.addWidget(self.pesquisa_input)
        hbox.addWidget(btn_pesquisar)
        layout.addWidget(frame_filtro)

        # Área de tabela de produtos
        frame_tab = QFrame()
        frame_tab.setFrameShape(QFrame.StyledPanel)
        frame_tab.setStyleSheet('background: #ffffff; border-radius: 8px; padding: 10px;')
        vbox_tab = QVBoxLayout(frame_tab)
        lbl_lista = QLabel('<b>Produtos Encontrados</b>')
        lbl_lista.setStyleSheet('font-size: 16px; color: #2e3b4e;')
        vbox_tab.addWidget(lbl_lista)
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(4)
        self.tabela.setHorizontalHeaderLabels(['ID', 'Nome', 'Preço', 'Código de Barras'])
        self.tabela.setStyleSheet('font-size: 15px; background: #f8fafc;')
        self.tabela.horizontalHeader().setStyleSheet('font-size: 15px; font-weight: bold; padding: 8px;')
        self.tabela.verticalHeader().setStyleSheet('font-size: 15px;')
        self.tabela.setAlternatingRowColors(True)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        vbox_tab.addWidget(self.tabela)
        layout.addWidget(frame_tab)

        # Botões de ação
        hbox2 = QHBoxLayout()
        btn_editar = QPushButton('Editar')
        btn_editar.setStyleSheet('background: #0288d1; color: white; font-size: 15px; padding: 8px 20px; border-radius: 8px;')
        btn_editar.clicked.connect(self.editar_produto)
        btn_excluir = QPushButton('Excluir')
        btn_excluir.setStyleSheet('background: #ef5350; color: white; font-size: 15px; padding: 8px 20px; border-radius: 8px;')
        btn_excluir.clicked.connect(self.excluir_produto)
        hbox2.addWidget(btn_editar)
        hbox2.addWidget(btn_excluir)
        layout.addLayout(hbox2)

        self.setLayout(layout)

    def carregar_produtos(self, filtro=None):
        conn = sqlite3.connect('produtos.db')
        c = conn.cursor()
        if filtro:
            c.execute("SELECT * FROM produtos WHERE nome LIKE ? OR codigo_barras LIKE ?", (f'%{filtro}%', f'%{filtro}%'))
        else:
            c.execute("SELECT * FROM produtos")
        produtos = c.fetchall()
        conn.close()

        self.tabela.setRowCount(0)
        for row_idx, row_data in enumerate(produtos):
            self.tabela.insertRow(row_idx)
            for col_idx, value in enumerate(row_data):
                self.tabela.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

    def pesquisar_produtos(self):
        filtro = self.pesquisa_input.text()
        self.carregar_produtos(filtro)

    def editar_produto(self):
        row = self.tabela.currentRow()
        if row == -1:
            QMessageBox.warning(self, 'Atenção', 'Selecione um produto para editar!')
            return
        id_produto = self.tabela.item(row, 0).text()
        nome = self.tabela.item(row, 1).text()
        preco = self.tabela.item(row, 2).text()
        codigo = self.tabela.item(row, 3).text()

        # Caixa de diálogo simples para editar
        novo_nome, ok1 = QInputDialog.getText(self, 'Editar Produto', 'Nome:', text=nome)
        novo_preco, ok2 = QInputDialog.getText(self, 'Editar Produto', 'Preço:', text=preco)
        novo_codigo, ok3 = QInputDialog.getText(self, 'Editar Produto', 'Código de Barras:', text=codigo)
        if ok1 and ok2 and ok3:
            try:
                novo_preco = float(novo_preco)
            except ValueError:
                QMessageBox.warning(self, 'Erro', 'Preço inválido!')
                return
            conn = sqlite3.connect('produtos.db')
            c = conn.cursor()
            c.execute('UPDATE produtos SET nome=?, preco=?, codigo_barras=? WHERE id=?', (novo_nome, novo_preco, novo_codigo, id_produto))
            conn.commit()
            conn.close()
            QMessageBox.information(self, 'Sucesso', 'Produto atualizado!')
            self.carregar_produtos()

    def excluir_produto(self):
        row = self.tabela.currentRow()
        if row == -1:
            QMessageBox.warning(self, 'Atenção', 'Selecione um produto para excluir!')
            return
        id_produto = self.tabela.item(row, 0).text()
        resposta = QMessageBox.question(self, 'Confirmação', f'Tem certeza que deseja excluir o produto ID {id_produto}?', QMessageBox.Yes | QMessageBox.No)
        if resposta == QMessageBox.Yes:
            conn = sqlite3.connect('produtos.db')
            c = conn.cursor()
            c.execute('DELETE FROM produtos WHERE id=?', (id_produto,))
            conn.commit()
            conn.close()
            QMessageBox.information(self, 'Sucesso', 'Produto excluído!')
            self.carregar_produtos()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    janela = ConsultaProdutos()
    janela.show()
    sys.exit(app.exec_())
