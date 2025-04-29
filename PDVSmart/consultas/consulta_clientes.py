import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QInputDialog, QFrame
)
from PyQt5.QtCore import Qt

class ConsultaClientes(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Consulta de Clientes')
        self.setGeometry(170, 170, 700, 460)
        self.setStyleSheet('background: #f5f7fa;')
        self.init_ui()
        self.carregar_clientes()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(18)

        # Barra de busca/filtros
        frame_filtro = QFrame()
        frame_filtro.setFrameShape(QFrame.StyledPanel)
        frame_filtro.setStyleSheet('background: #e3f2fd; border-radius: 8px; padding: 12px;')
        hbox = QHBoxLayout(frame_filtro)
        self.pesquisa_input = QLineEdit()
        self.pesquisa_input.setPlaceholderText('Pesquisar por nome, CPF ou telefone...')
        self.pesquisa_input.setMinimumHeight(32)
        self.pesquisa_input.setStyleSheet('font-size: 15px; padding: 4px 8px; border: 1px solid #ccc; border-radius: 4px;')
        btn_pesquisar = QPushButton('Pesquisar')
        btn_pesquisar.setStyleSheet('background: #1976d2; color: white; font-size: 15px; padding: 8px 20px; border-radius: 8px;')
        btn_pesquisar.setMinimumHeight(32)
        btn_pesquisar.clicked.connect(self.pesquisar_clientes)
        hbox.addWidget(self.pesquisa_input)
        hbox.addWidget(btn_pesquisar)
        layout.addWidget(frame_filtro)

        # Área de tabela de clientes
        frame_tab = QFrame()
        frame_tab.setFrameShape(QFrame.StyledPanel)
        frame_tab.setStyleSheet('background: #ffffff; border-radius: 8px; padding: 10px;')
        vbox_tab = QVBoxLayout(frame_tab)
        lbl_lista = QLabel('<b>Clientes Encontrados</b>')
        lbl_lista.setStyleSheet('font-size: 16px; color: #2e3b4e;')
        vbox_tab.addWidget(lbl_lista)
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(5)
        self.tabela.setHorizontalHeaderLabels(['ID', 'Nome', 'CPF/CNPJ', 'Telefone', 'E-mail'])
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
        btn_editar.clicked.connect(self.editar_cliente)
        btn_excluir = QPushButton('Excluir')
        btn_excluir.setStyleSheet('background: #ef5350; color: white; font-size: 15px; padding: 8px 20px; border-radius: 8px;')
        btn_excluir.clicked.connect(self.excluir_cliente)
        hbox2.addWidget(btn_editar)
        hbox2.addWidget(btn_excluir)
        layout.addLayout(hbox2)

        self.setLayout(layout)

    def carregar_clientes(self, filtro=None):
        conn = sqlite3.connect('db/clientes.db')
        c = conn.cursor()
        if filtro:
            c.execute("SELECT * FROM clientes WHERE nome LIKE ? OR cpf_cnpj LIKE ? OR telefone LIKE ?", (f'%{filtro}%', f'%{filtro}%', f'%{filtro}%'))
        else:
            c.execute("SELECT * FROM clientes")
        clientes = c.fetchall()
        conn.close()

        self.tabela.setRowCount(0)
        for row_idx, row_data in enumerate(clientes):
            self.tabela.insertRow(row_idx)
            for col_idx, value in enumerate(row_data):
                self.tabela.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

    def pesquisar_clientes(self):
        filtro = self.pesquisa_input.text()
        self.carregar_clientes(filtro)

    def editar_cliente(self):
        row = self.tabela.currentRow()
        if row == -1:
            QMessageBox.warning(self, 'Atenção', 'Selecione um cliente para editar!')
            return
        id_cliente = self.tabela.item(row, 0).text()
        nome = self.tabela.item(row, 1).text()
        cpf = self.tabela.item(row, 2).text()
        telefone = self.tabela.item(row, 3).text()
        email = self.tabela.item(row, 4).text()

        novo_nome, ok1 = QInputDialog.getText(self, 'Editar Cliente', 'Nome:', text=nome)
        novo_cpf, ok2 = QInputDialog.getText(self, 'Editar Cliente', 'CPF/CNPJ:', text=cpf)
        novo_telefone, ok3 = QInputDialog.getText(self, 'Editar Cliente', 'Telefone:', text=telefone)
        novo_email, ok4 = QInputDialog.getText(self, 'Editar Cliente', 'E-mail:', text=email)
        if ok1 and ok2 and ok3 and ok4:
            conn = sqlite3.connect('clientes.db')
            c = conn.cursor()
            c.execute('UPDATE clientes SET nome=?, cpf_cnpj=?, telefone=?, email=? WHERE id=?', (novo_nome, novo_cpf, novo_telefone, novo_email, id_cliente))
            conn.commit()
            conn.close()
            QMessageBox.information(self, 'Sucesso', 'Cliente atualizado!')
            self.carregar_clientes()

    def excluir_cliente(self):
        row = self.tabela.currentRow()
        if row == -1:
            QMessageBox.warning(self, 'Atenção', 'Selecione um cliente para excluir!')
            return
        id_cliente = self.tabela.item(row, 0).text()
        resposta = QMessageBox.question(self, 'Confirmação', f'Tem certeza que deseja excluir o cliente ID {id_cliente}?', QMessageBox.Yes | QMessageBox.No)
        if resposta == QMessageBox.Yes:
            conn = sqlite3.connect('clientes.db')
            c = conn.cursor()
            c.execute('DELETE FROM clientes WHERE id=?', (id_cliente,))
            conn.commit()
            conn.close()
            QMessageBox.information(self, 'Sucesso', 'Cliente excluído!')
            self.carregar_clientes()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    janela = ConsultaClientes()
    janela.show()
    sys.exit(app.exec_())
