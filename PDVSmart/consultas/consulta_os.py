import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QComboBox, QTextEdit, QDoubleSpinBox, QInputDialog, QFrame
)
from PyQt5.QtCore import Qt

def buscar_nome_cliente(cliente_id):
    if not cliente_id:
        return 'Não informado'
    try:
        conn = sqlite3.connect('clientes.db')
        c = conn.cursor()
        c.execute('SELECT nome FROM clientes WHERE id=?', (cliente_id,))
        row = c.fetchone()
        conn.close()
        return row[0] if row else 'Não informado'
    except:
        return 'Não informado'

class ConsultaOS(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Consulta de Ordens de Serviço')
        self.setGeometry(400, 400, 1000, 520)
        self.setStyleSheet('background: #f5f7fa;')
        self.init_ui()
        self.carregar_os()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(18)
        # Filtro por status e busca
        frame_filtro = QFrame()
        frame_filtro.setFrameShape(QFrame.StyledPanel)
        frame_filtro.setStyleSheet('background: #e3f2fd; border-radius: 8px; padding: 12px;')
        hbox = QHBoxLayout(frame_filtro)
        hbox.addWidget(QLabel('Status:'))
        self.combo_status = QComboBox()
        self.combo_status.addItem('Todas')
        self.combo_status.addItems(['Aberta', 'Em andamento', 'Finalizada'])
        hbox.addWidget(self.combo_status)
        self.pesquisa_input = QLineEdit()
        self.pesquisa_input.setPlaceholderText('Pesquisar por cliente ou descrição...')
        self.pesquisa_input.setMinimumHeight(32)
        self.pesquisa_input.setStyleSheet('font-size: 15px; padding: 4px 8px; border: 1px solid #ccc; border-radius: 4px;')
        btn_pesquisar = QPushButton('Pesquisar')
        btn_pesquisar.setStyleSheet('background: #1976d2; color: white; font-size: 15px; padding: 8px 20px; border-radius: 8px;')
        btn_pesquisar.setMinimumHeight(32)
        btn_pesquisar.clicked.connect(self.pesquisar_os)
        hbox.addWidget(self.pesquisa_input)
        hbox.addWidget(btn_pesquisar)
        layout.addWidget(frame_filtro)
        # Tabela de OS
        frame_tab = QFrame()
        frame_tab.setFrameShape(QFrame.StyledPanel)
        frame_tab.setStyleSheet('background: #ffffff; border-radius: 8px; padding: 10px;')
        vbox_tab = QVBoxLayout(frame_tab)
        lbl_lista = QLabel('<b>Ordens de Serviço</b>')
        lbl_lista.setStyleSheet('font-size: 16px; color: #2e3b4e;')
        vbox_tab.addWidget(lbl_lista)
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels(['ID', 'Cliente', 'Data', 'Descrição', 'Status', 'Valor'])
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela.setStyleSheet('font-size: 15px; background: #f8fafc;')
        self.tabela.horizontalHeader().setStyleSheet('font-size: 15px; font-weight: bold; padding: 8px;')
        self.tabela.verticalHeader().setStyleSheet('font-size: 15px;')
        self.tabela.setAlternatingRowColors(True)
        self.tabela.cellDoubleClicked.connect(self.editar_os)
        vbox_tab.addWidget(self.tabela)
        layout.addWidget(frame_tab)
        # Botões de ação
        hbox2 = QHBoxLayout()
        btn_editar = QPushButton('Editar')
        btn_editar.setStyleSheet('background: #0288d1; color: white; font-size: 15px; padding: 8px 20px; border-radius: 8px;')
        btn_editar.clicked.connect(self.editar_os_btn)
        btn_status = QPushButton('Mudar Status')
        btn_status.setStyleSheet('background: #efb400; color: white; font-size: 15px; padding: 8px 20px; border-radius: 8px;')
        btn_status.clicked.connect(self.mudar_status_btn)
        hbox2.addWidget(btn_editar)
        hbox2.addWidget(btn_status)
        layout.addLayout(hbox2)
        self.setLayout(layout)

    def carregar_os(self, filtro=None, status=None):
        conn = sqlite3.connect('os.db')
        c = conn.cursor()
        query = 'SELECT * FROM ordens_servico'
        params = []
        if status and status != 'Todas':
            query += ' WHERE status=?'
            params.append(status)
        c.execute(query, params)
        ordens = c.fetchall()
        conn.close()
        self.tabela.setRowCount(0)
        idx = 0
        for os in ordens:
            cliente_nome = buscar_nome_cliente(os[1])
            if filtro and filtro.lower() not in cliente_nome.lower() and filtro.lower() not in os[3].lower():
                continue
            self.tabela.insertRow(idx)
            self.tabela.setItem(idx, 0, QTableWidgetItem(str(os[0])))
            self.tabela.setItem(idx, 1, QTableWidgetItem(cliente_nome))
            self.tabela.setItem(idx, 2, QTableWidgetItem(os[2]))
            self.tabela.setItem(idx, 3, QTableWidgetItem(os[3]))
            self.tabela.setItem(idx, 4, QTableWidgetItem(os[4]))
            self.tabela.setItem(idx, 5, QTableWidgetItem(f'R$ {os[5]:.2f}'))
            idx += 1

    def pesquisar_os(self):
        filtro = self.pesquisa_input.text()
        status = self.combo_status.currentText()
        self.carregar_os(filtro, status)

    def editar_os(self, row, column):
        id_os = self.tabela.item(row, 0).text()
        conn = sqlite3.connect('os.db')
        c = conn.cursor()
        c.execute('SELECT cliente_id, descricao, status, valor FROM ordens_servico WHERE id=?', (id_os,))
        os_data = c.fetchone()
        conn.close()
        if not os_data:
            QMessageBox.warning(self, 'Erro', 'Ordem de serviço não encontrada!')
            return
        # Diálogo simples para editar status e valor
        status_list = ['Aberta', 'Em andamento', 'Finalizada']
        status_atual = os_data[2] if os_data[2] in status_list else 'Aberta'
        status, ok1 = QInputDialog.getItem(self, 'Editar Status', 'Status:', status_list, status_list.index(status_atual), False)
        valor, ok2 = QInputDialog.getDouble(self, 'Editar Valor', 'Valor:', value=os_data[3], min=0.0, max=99999.99, decimals=2)
        if ok1 and ok2:
            conn = sqlite3.connect('os.db')
            c = conn.cursor()
            c.execute('UPDATE ordens_servico SET status=?, valor=? WHERE id=?', (status, valor, id_os))
            conn.commit()
            conn.close()
            QMessageBox.information(self, 'Sucesso', 'Ordem de serviço atualizada!')
            self.carregar_os()

    def editar_os_btn(self):
        row = self.tabela.currentRow()
        if row == -1:
            QMessageBox.warning(self, 'Atenção', 'Selecione uma ordem de serviço para editar!')
            return
        id_os = self.tabela.item(row, 0).text()
        conn = sqlite3.connect('os.db')
        c = conn.cursor()
        c.execute('SELECT descricao, valor FROM ordens_servico WHERE id=?', (id_os,))
        os_data = c.fetchone()
        conn.close()
        if not os_data:
            QMessageBox.warning(self, 'Erro', 'Ordem de serviço não encontrada!')
            return
        descricao, ok1 = QInputDialog.getMultiLineText(self, 'Editar Descrição', 'Descrição:', os_data[0])
        valor, ok2 = QInputDialog.getDouble(self, 'Editar Valor', 'Valor:', value=os_data[1], min=0.0, max=99999.99, decimals=2)
        if ok1 and ok2:
            conn = sqlite3.connect('os.db')
            c = conn.cursor()
            c.execute('UPDATE ordens_servico SET descricao=?, valor=? WHERE id=?', (descricao, valor, id_os))
            conn.commit()
            conn.close()
            QMessageBox.information(self, 'Sucesso', 'Ordem de serviço atualizada!')
            self.carregar_os()

    def mudar_status_btn(self):
        row = self.tabela.currentRow()
        if row == -1:
            QMessageBox.warning(self, 'Atenção', 'Selecione uma ordem de serviço para mudar o status!')
            return
        id_os = self.tabela.item(row, 0).text()
        conn = sqlite3.connect('os.db')
        c = conn.cursor()
        c.execute('SELECT status FROM ordens_servico WHERE id=?', (id_os,))
        os_data = c.fetchone()
        conn.close()
        if not os_data:
            QMessageBox.warning(self, 'Erro', 'Ordem de serviço não encontrada!')
            return
        status_list = ['Aberta', 'Em andamento', 'Finalizada']
        status_atual = os_data[0] if os_data[0] in status_list else 'Aberta'
        status, ok = QInputDialog.getItem(self, 'Mudar Status', 'Status:', status_list, status_list.index(status_atual), False)
        if ok:
            conn = sqlite3.connect('os.db')
            c = conn.cursor()
            c.execute('UPDATE ordens_servico SET status=? WHERE id=?', (status, id_os))
            conn.commit()
            conn.close()
            QMessageBox.information(self, 'Sucesso', 'Status atualizado!')
            self.carregar_os()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    janela = ConsultaOS()
    janela.show()
    sys.exit(app.exec_())
