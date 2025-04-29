import sys
import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QComboBox, QDoubleSpinBox, QFrame, QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import Qt

def criar_banco_os():
    conn = sqlite3.connect('db/os.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS ordens_servico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            data_abertura TEXT,
            descricao TEXT,
            status TEXT,
            valor REAL
        )
    ''')
    conn.commit()
    conn.close()

def carregar_clientes():
    conn = sqlite3.connect('db/clientes.db')
    c = conn.cursor()
    c.execute('SELECT id, nome FROM clientes')
    clientes = c.fetchall()
    conn.close()
    return clientes

def carregar_os():
    try:
        # Consulta as ordens de serviço
        conn = sqlite3.connect('db/os.db')
        c = conn.cursor()
        c.execute('SELECT id, data_abertura, descricao, status, valor, cliente_id FROM ordens_servico ORDER BY id DESC')
        ordens = c.fetchall()
        
        # Busca os nomes dos clientes
        conn_clientes = sqlite3.connect('db/clientes.db')
        c_clientes = conn_clientes.cursor()
        
        # Prepara a lista de resultados com os nomes dos clientes
        resultado = []
        for ordem in ordens:
            cliente_nome = 'Cliente não encontrado'
            if ordem[5]:  # Se tem cliente_id
                c_clientes.execute('SELECT nome FROM clientes WHERE id = ?', (ordem[5],))
                cliente = c_clientes.fetchone()
                if cliente:
                    cliente_nome = cliente[0]
            
            # Reorganiza os dados na ordem esperada: id, nome_cliente, data, descricao, status, valor
            resultado.append((ordem[0], cliente_nome, ordem[1], ordem[2], ordem[3], ordem[4]))
        
        conn.close()
        conn_clientes.close()
        return resultado
    except sqlite3.OperationalError as e:
        print(f"Erro ao carregar ordens de serviço: {e}")
        return []

class CadastroOS(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Cadastro de Ordem de Serviço')
        self.setGeometry(350, 350, 700, 500)
        self.setStyleSheet('background: #f5f7fa;')
        criar_banco_os()
        self.clientes = carregar_clientes()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(18)

        # Área de cadastro
        frame_cad = QFrame()
        frame_cad.setFrameShape(QFrame.StyledPanel)
        frame_cad.setStyleSheet('background: #ffffff; border-radius: 8px; padding: 14px;')
        vbox_cad = QVBoxLayout(frame_cad)
        lbl_titulo = QLabel('<b>Cadastro de Ordem de Serviço</b>')
        lbl_titulo.setStyleSheet('font-size: 18px; color: #1976d2;')
        vbox_cad.addWidget(lbl_titulo)
        hbox_cli = QHBoxLayout()
        lbl_cliente = QLabel('Cliente:')
        lbl_cliente.setStyleSheet('font-size: 15px; color: #2e3b4e;')
        hbox_cli.addWidget(lbl_cliente)
        self.combo_cliente = QComboBox()
        self.combo_cliente.setStyleSheet('font-size: 15px; padding: 4px 8px;')
        self.combo_cliente.setMinimumHeight(32)
        for cli in self.clientes:
            self.combo_cliente.addItem(cli[1], cli[0])
        hbox_cli.addWidget(self.combo_cliente)
        vbox_cad.addLayout(hbox_cli)
        lbl_desc = QLabel('Descrição do Serviço:')
        lbl_desc.setStyleSheet('font-size: 15px; color: #2e3b4e;')
        vbox_cad.addWidget(lbl_desc)
        self.desc_input = QTextEdit()
        self.desc_input.setMinimumHeight(80)
        self.desc_input.setStyleSheet('font-size: 15px; padding: 8px;')
        vbox_cad.addWidget(self.desc_input)
        hbox_valor = QHBoxLayout()
        lbl_valor = QLabel('Valor (R$):')
        lbl_valor.setStyleSheet('font-size: 15px; color: #2e3b4e;')
        hbox_valor.addWidget(lbl_valor)
        self.valor_input = QDoubleSpinBox()
        self.valor_input.setMinimum(0.0)
        self.valor_input.setMaximum(99999.99)
        self.valor_input.setDecimals(2)
        self.valor_input.setMinimumHeight(32)
        self.valor_input.setStyleSheet('font-size: 15px; padding: 4px 8px;')
        hbox_valor.addWidget(self.valor_input)
        vbox_cad.addLayout(hbox_valor)
        hbox_status = QHBoxLayout()
        lbl_status = QLabel('Status:')
        lbl_status.setStyleSheet('font-size: 15px; color: #2e3b4e;')
        hbox_status.addWidget(lbl_status)
        self.combo_status = QComboBox()
        self.combo_status.setStyleSheet('font-size: 15px; padding: 4px 8px;')
        self.combo_status.setMinimumHeight(32)
        self.combo_status.addItems(['Aberta', 'Em andamento', 'Finalizada'])
        hbox_status.addWidget(self.combo_status)
        vbox_cad.addLayout(hbox_status)
        self.btn_salvar = QPushButton('Salvar OS')
        self.btn_salvar.setStyleSheet('background: #1976d2; color: white; font-size: 16px; padding: 10px 0; border-radius: 8px;')
        self.btn_salvar.setMinimumHeight(38)
        self.btn_salvar.clicked.connect(self.salvar_os)
        vbox_cad.addWidget(self.btn_salvar)
        layout.addWidget(frame_cad)

        # Área de tabela de OS
        frame_tab = QFrame()
        frame_tab.setFrameShape(QFrame.StyledPanel)
        frame_tab.setStyleSheet('background: #ffffff; border-radius: 8px; padding: 10px;')
        vbox_tab = QVBoxLayout(frame_tab)
        lbl_lista = QLabel('<b>Ordens de Serviço Cadastradas</b>')
        lbl_lista.setStyleSheet('font-size: 16px; color: #2e3b4e;')
        vbox_tab.addWidget(lbl_lista)
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels(['ID', 'Cliente', 'Data', 'Descrição', 'Status', 'Valor'])
        self.tabela.setStyleSheet('font-size: 14px; background: #f8fafc;')
        self.tabela.setAlternatingRowColors(True)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        vbox_tab.addWidget(self.tabela)
        layout.addWidget(frame_tab)
        self.setLayout(layout)
        self.atualizar_tabela()

    def salvar_os(self):
        cliente_id = self.combo_cliente.currentData()
        descricao = self.desc_input.toPlainText()
        valor = self.valor_input.value()
        status = self.combo_status.currentText()
        data_abertura = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if not descricao.strip():
            QMessageBox.warning(self, 'Erro', 'Preencha a descrição do serviço!')
            return
        conn = sqlite3.connect('db/os.db')
        c = conn.cursor()
        c.execute('INSERT INTO ordens_servico (cliente_id, data_abertura, descricao, status, valor) VALUES (?, ?, ?, ?, ?)',
                  (cliente_id, data_abertura, descricao, status, valor))
        conn.commit()
        conn.close()
        QMessageBox.information(self, 'Sucesso', 'Ordem de serviço cadastrada com sucesso!')
        self.desc_input.clear()
        self.valor_input.setValue(0.0)
        self.combo_status.setCurrentIndex(0)
        self.atualizar_tabela()

    def atualizar_tabela(self):
        ordens = carregar_os()
        self.tabela.setRowCount(0)
        for os in ordens:
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            self.tabela.setItem(row, 0, QTableWidgetItem(str(os[0])))
            self.tabela.setItem(row, 1, QTableWidgetItem(os[1] if os[1] else ''))
            self.tabela.setItem(row, 2, QTableWidgetItem(os[2]))
            self.tabela.setItem(row, 3, QTableWidgetItem(os[3]))
            self.tabela.setItem(row, 4, QTableWidgetItem(os[4]))
            self.tabela.setItem(row, 5, QTableWidgetItem(f'R$ {os[5]:.2f}'))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    janela = CadastroOS()
    janela.show()
    sys.exit(app.exec_())
