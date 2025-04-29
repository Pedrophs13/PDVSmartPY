import sys
import sqlite3
import csv
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QFileDialog, QDateEdit, QMessageBox, QInputDialog, QFrame
)
from PyQt5.QtCore import QDate

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

class Relatorios(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Relatórios Centralizados')
        self.setGeometry(250, 250, 1050, 650)
        self.setStyleSheet('background: #f5f7fa;')
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(18)
        # Filtros de data
        frame_filtros = QFrame()
        frame_filtros.setFrameShape(QFrame.StyledPanel)
        frame_filtros.setStyleSheet('background: #e3f2fd; border-radius: 8px; padding: 12px;')
        hbox = QHBoxLayout(frame_filtros)
        hbox.addWidget(QLabel('Data inicial:'))
        self.data_inicial = QDateEdit()
        self.data_inicial.setDate(QDate.currentDate().addMonths(-1))
        self.data_inicial.setCalendarPopup(True)
        hbox.addWidget(self.data_inicial)
        hbox.addWidget(QLabel('Data final:'))
        self.data_final = QDateEdit()
        self.data_final.setDate(QDate.currentDate())
        self.data_final.setCalendarPopup(True)
        hbox.addWidget(self.data_final)
        layout.addWidget(frame_filtros)
        # Botões de relatório
        frame_botoes = QFrame()
        frame_botoes.setFrameShape(QFrame.StyledPanel)
        frame_botoes.setStyleSheet('background: #ffffff; border-radius: 8px; padding: 10px;')
        hbox2 = QHBoxLayout(frame_botoes)
        btn_vendas = QPushButton('Relatório de Vendas')
        btn_vendas.setStyleSheet('background: #1976d2; color: white; font-size: 15px; padding: 10px 24px; border-radius: 8px;')
        btn_vendas.clicked.connect(self.gerar_relatorio_vendas)
        btn_clientes = QPushButton('Vendas por Cliente')
        btn_clientes.setStyleSheet('background: #0288d1; color: white; font-size: 15px; padding: 10px 24px; border-radius: 8px;')
        btn_clientes.clicked.connect(self.gerar_relatorio_clientes)
        btn_produtos = QPushButton('Produtos Mais Vendidos')
        btn_produtos.setStyleSheet('background: #388e3c; color: white; font-size: 15px; padding: 10px 24px; border-radius: 8px;')
        btn_produtos.clicked.connect(self.gerar_relatorio_produtos)
        btn_os = QPushButton('Relatório de Ordens de Serviço')
        btn_os.setStyleSheet('background: #efb400; color: white; font-size: 15px; padding: 10px 24px; border-radius: 8px;')
        btn_os.clicked.connect(self.gerar_relatorio_os)
        hbox2.addWidget(btn_vendas)
        hbox2.addWidget(btn_clientes)
        hbox2.addWidget(btn_produtos)
        hbox2.addWidget(btn_os)
        layout.addWidget(frame_botoes)
        # Tabela de exibição
        frame_tab = QFrame()
        frame_tab.setFrameShape(QFrame.StyledPanel)
        frame_tab.setStyleSheet('background: #ffffff; border-radius: 8px; padding: 10px;')
        vbox_tab = QVBoxLayout(frame_tab)
        lbl_lista = QLabel('<b>Resultado do Relatório</b>')
        lbl_lista.setStyleSheet('font-size: 16px; color: #2e3b4e;')
        vbox_tab.addWidget(lbl_lista)
        self.tabela = QTableWidget()
        self.tabela.setStyleSheet('font-size: 14px; background: #f8fafc;')
        self.tabela.setAlternatingRowColors(True)
        vbox_tab.addWidget(self.tabela)
        layout.addWidget(frame_tab)
        # Botão exportar
        btn_exportar = QPushButton('Exportar para CSV')
        btn_exportar.setStyleSheet('background: #1976d2; color: white; font-size: 15px; padding: 10px 24px; border-radius: 8px;')
        btn_exportar.clicked.connect(self.exportar_csv)
        layout.addWidget(btn_exportar)
        self.setLayout(layout)
        self.ultimo_relatorio = []
        self.ultimo_cabecalho = []

    def gerar_relatorio_vendas(self):
        data_ini = self.data_inicial.date().toString('yyyy-MM-dd')
        data_fim = self.data_final.date().toString('yyyy-MM-dd')
        conn = sqlite3.connect('vendas.db')
        c = conn.cursor()
        c.execute("SELECT * FROM vendas WHERE date(data) BETWEEN ? AND ?", (data_ini, data_fim))
        vendas = c.fetchall()
        conn.close()
        cabecalho = ['ID', 'Data', 'Cliente', 'Total', 'Valor Recebido', 'Troco']
        self.tabela.setColumnCount(len(cabecalho))
        self.tabela.setHorizontalHeaderLabels(cabecalho)
        self.tabela.setRowCount(0)
        relatorio = []
        for idx, venda in enumerate(vendas):
            cliente_nome = buscar_nome_cliente(venda[2])
            row = [venda[0], venda[1], cliente_nome, f'{venda[3]:.2f}', f'{venda[4]:.2f}', f'{venda[5]:.2f}']
            self.tabela.insertRow(idx)
            for col, val in enumerate(row):
                self.tabela.setItem(idx, col, QTableWidgetItem(str(val)))
            relatorio.append(row)
        self.ultimo_relatorio = relatorio
        self.ultimo_cabecalho = cabecalho

    def gerar_relatorio_clientes(self):
        data_ini = self.data_inicial.date().toString('yyyy-MM-dd')
        data_fim = self.data_final.date().toString('yyyy-MM-dd')
        conn = sqlite3.connect('vendas.db')
        c = conn.cursor()
        c.execute("SELECT cliente_id, SUM(total) FROM vendas WHERE date(data) BETWEEN ? AND ? GROUP BY cliente_id", (data_ini, data_fim))
        dados = c.fetchall()
        conn.close()
        cabecalho = ['Cliente', 'Total em Vendas']
        self.tabela.setColumnCount(len(cabecalho))
        self.tabela.setHorizontalHeaderLabels(cabecalho)
        self.tabela.setRowCount(0)
        relatorio = []
        for idx, row in enumerate(dados):
            cliente_nome = buscar_nome_cliente(row[0])
            linha = [cliente_nome, f'{row[1]:.2f}']
            self.tabela.insertRow(idx)
            for col, val in enumerate(linha):
                self.tabela.setItem(idx, col, QTableWidgetItem(str(val)))
            relatorio.append(linha)
        self.ultimo_relatorio = relatorio
        self.ultimo_cabecalho = cabecalho

    def gerar_relatorio_produtos(self):
        data_ini = self.data_inicial.date().toString('yyyy-MM-dd')
        data_fim = self.data_final.date().toString('yyyy-MM-dd')
        conn = sqlite3.connect('vendas.db')
        c = conn.cursor()
        c.execute("""
            SELECT produto_id, SUM(quantidade), SUM(subtotal)
            FROM itens_venda
            WHERE venda_id IN (SELECT id FROM vendas WHERE date(data) BETWEEN ? AND ?)
            GROUP BY produto_id
        """, (data_ini, data_fim))
        dados = c.fetchall()
        conn.close()
        cabecalho = ['Produto', 'Quantidade Vendida', 'Total em Vendas']
        self.tabela.setColumnCount(len(cabecalho))
        self.tabela.setHorizontalHeaderLabels(cabecalho)
        self.tabela.setRowCount(0)
        relatorio = []
        for idx, row in enumerate(dados):
            # Buscar nome do produto
            conn2 = sqlite3.connect('produtos.db')
            c2 = conn2.cursor()
            c2.execute('SELECT nome FROM produtos WHERE id=?', (row[0],))
            prod_nome = c2.fetchone()
            prod_nome = prod_nome[0] if prod_nome else 'Produto removido'
            conn2.close()
            linha = [prod_nome, row[1], f'{row[2]:.2f}']
            self.tabela.insertRow(idx)
            for col, val in enumerate(linha):
                self.tabela.setItem(idx, col, QTableWidgetItem(str(val)))
            relatorio.append(linha)
        self.ultimo_relatorio = relatorio
        self.ultimo_cabecalho = cabecalho

    def gerar_relatorio_os(self):
        from PyQt5.QtWidgets import QInputDialog
        data_ini = self.data_inicial.date().toString('yyyy-MM-dd')
        data_fim = self.data_final.date().toString('yyyy-MM-dd')
        # Pergunta status
        status_list = ['Todas', 'Aberta', 'Em andamento', 'Finalizada']
        status, ok = QInputDialog.getItem(self, 'Status da OS', 'Filtrar por status:', status_list, 0, False)
        if not ok:
            return
        conn = sqlite3.connect('os.db')
        c = conn.cursor()
        query = "SELECT * FROM ordens_servico WHERE date(data_abertura) BETWEEN ? AND ?"
        params = [data_ini, data_fim]
        if status != 'Todas':
            query += " AND status=?"
            params.append(status)
        c.execute(query, params)
        ordens = c.fetchall()
        conn.close()
        cabecalho = ['ID', 'Data', 'Cliente', 'Descrição', 'Status', 'Valor']
        self.tabela.setColumnCount(len(cabecalho))
        self.tabela.setHorizontalHeaderLabels(cabecalho)
        self.tabela.setRowCount(0)
        relatorio = []
        for idx, os in enumerate(ordens):
            cliente_nome = buscar_nome_cliente(os[1])
            row = [os[0], os[2], cliente_nome, os[3], os[4], f'{os[5]:.2f}']
            self.tabela.insertRow(idx)
            for col, val in enumerate(row):
                self.tabela.setItem(idx, col, QTableWidgetItem(str(val)))
            relatorio.append(row)
        self.ultimo_relatorio = relatorio
        self.ultimo_cabecalho = cabecalho

    def exportar_csv(self):
        if not self.ultimo_relatorio or not self.ultimo_cabecalho:
            QMessageBox.warning(self, 'Atenção', 'Nenhum relatório gerado ainda!')
            return
        caminho, _ = QFileDialog.getSaveFileName(self, 'Salvar Relatório', '', 'CSV Files (*.csv)')
        if caminho:
            with open(caminho, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(self.ultimo_cabecalho)
                writer.writerows(self.ultimo_relatorio)
            QMessageBox.information(self, 'Sucesso', 'Relatório exportado com sucesso!')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    janela = Relatorios()
    janela.show()
    sys.exit(app.exec_())
