import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QFrame, QDateEdit
)
from PyQt5.QtCore import Qt, QDate
from datetime import datetime

class FechamentoCaixa(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Fechamento de Caixa')
        self.setGeometry(200, 200, 800, 600)
        self.setStyleSheet('background: #f5f7fa;')
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(18)

        # Área de seleção de data
        frame_data = QFrame()
        frame_data.setFrameShape(QFrame.StyledPanel)
        frame_data.setStyleSheet('background: #ffffff; border-radius: 8px; padding: 14px;')
        hbox_data = QHBoxLayout(frame_data)

        self.data_label = QLabel('Data:')
        self.data_label.setStyleSheet('font-size: 15px; color: #2e3b4e;')
        self.data_edit = QDateEdit()
        self.data_edit.setDate(QDate.currentDate())
        self.data_edit.setCalendarPopup(True)
        self.data_edit.setStyleSheet('font-size: 15px; padding: 4px 8px;')
        
        btn_buscar = QPushButton('Buscar Movimentações')
        btn_buscar.setStyleSheet('background: #1976d2; color: white; font-size: 15px; padding: 8px 14px; border-radius: 6px;')
        btn_buscar.clicked.connect(self.buscar_movimentacoes)

        hbox_data.addWidget(self.data_label)
        hbox_data.addWidget(self.data_edit)
        hbox_data.addWidget(btn_buscar)
        hbox_data.addStretch()

        layout.addWidget(frame_data)

        # Área de resumo
        frame_resumo = QFrame()
        frame_resumo.setFrameShape(QFrame.StyledPanel)
        frame_resumo.setStyleSheet('background: #ffffff; border-radius: 8px; padding: 14px;')
        vbox_resumo = QVBoxLayout(frame_resumo)

        lbl_resumo = QLabel('<b>Resumo do Dia</b>')
        lbl_resumo.setStyleSheet('font-size: 18px; color: #1976d2;')
        vbox_resumo.addWidget(lbl_resumo)

        # Labels para totais
        self.total_vendas = QLabel('Total de Vendas: R$ 0,00')
        self.total_vendas.setStyleSheet('font-size: 16px; color: #2e3b4e;')
        self.qtd_vendas = QLabel('Quantidade de Vendas: 0')
        self.qtd_vendas.setStyleSheet('font-size: 16px; color: #2e3b4e;')
        self.ticket_medio = QLabel('Ticket Médio: R$ 0,00')
        self.ticket_medio.setStyleSheet('font-size: 16px; color: #2e3b4e;')

        vbox_resumo.addWidget(self.total_vendas)
        vbox_resumo.addWidget(self.qtd_vendas)
        vbox_resumo.addWidget(self.ticket_medio)

        layout.addWidget(frame_resumo)

        # Área de detalhes das vendas
        frame_vendas = QFrame()
        frame_vendas.setFrameShape(QFrame.StyledPanel)
        frame_vendas.setStyleSheet('background: #ffffff; border-radius: 8px; padding: 14px;')
        vbox_vendas = QVBoxLayout(frame_vendas)

        lbl_vendas = QLabel('<b>Vendas do Dia</b>')
        lbl_vendas.setStyleSheet('font-size: 18px; color: #1976d2;')
        vbox_vendas.addWidget(lbl_vendas)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels(['ID', 'Hora', 'Total', 'Valor Recebido', 'Troco', 'Forma Pagamento'])
        self.tabela.setStyleSheet('font-size: 14px; background: #f8fafc;')
        self.tabela.setAlternatingRowColors(True)
        vbox_vendas.addWidget(self.tabela)

        layout.addWidget(frame_vendas)

        # Botão de fechamento
        btn_fechar = QPushButton('Fechar Caixa')
        btn_fechar.setStyleSheet(
            'background: #43a047; color: white; font-size: 17px;'
            'padding: 12px 24px; border-radius: 8px; margin-top: 10px;'
        )
        btn_fechar.clicked.connect(self.fechar_caixa)
        layout.addWidget(btn_fechar)

        self.setLayout(layout)
        self.buscar_movimentacoes()

    def buscar_movimentacoes(self):
        data = self.data_edit.date().toString('dd/MM/yyyy')
        try:
            conn = sqlite3.connect('db/vendas.db')
            c = conn.cursor()
            
            # Buscar vendas do dia
            c.execute('''
                SELECT id, data, total, valor_recebido, troco, tipo_pagamento 
                FROM vendas 
                WHERE data LIKE ?
            ''', (f'{data}%',))
            vendas = c.fetchall()
            
            # Atualizar tabela
            self.tabela.setRowCount(0)
            total_dia = 0
            for venda in vendas:
                row = self.tabela.rowCount()
                self.tabela.insertRow(row)
                # ID
                self.tabela.setItem(row, 0, QTableWidgetItem(str(venda[0])))
                # Hora
                hora = venda[1].split()[1] if ' ' in venda[1] else ''
                self.tabela.setItem(row, 1, QTableWidgetItem(hora))
                # Total
                self.tabela.setItem(row, 2, QTableWidgetItem(f'R$ {venda[2]:.2f}'))
                total_dia += venda[2]
                # Valor Recebido
                self.tabela.setItem(row, 3, QTableWidgetItem(f'R$ {venda[3]:.2f}'))
                # Troco
                self.tabela.setItem(row, 4, QTableWidgetItem(f'R$ {venda[4]:.2f}'))
                # Forma de Pagamento
                self.tabela.setItem(row, 5, QTableWidgetItem(venda[5]))

            # Atualizar resumo
            qtd_vendas = len(vendas)
            ticket_medio = total_dia / qtd_vendas if qtd_vendas > 0 else 0

            self.total_vendas.setText(f'Total de Vendas: R$ {total_dia:.2f}')
            self.qtd_vendas.setText(f'Quantidade de Vendas: {qtd_vendas}')
            self.ticket_medio.setText(f'Ticket Médio: R$ {ticket_medio:.2f}')

            conn.close()

        except Exception as e:
            QMessageBox.warning(self, 'Erro', f'Erro ao buscar movimentações: {str(e)}')

    def fechar_caixa(self):
        data = self.data_edit.date().toString('dd/MM/yyyy')
        total = float(self.total_vendas.text().split('R$')[1].strip())
        qtd = int(self.qtd_vendas.text().split(':')[1].strip())
        
        msg = f'''Confirma o fechamento do caixa?

Data: {data}
Total de Vendas: R$ {total:.2f}
Quantidade de Vendas: {qtd}'''

        reply = QMessageBox.question(self, 'Confirmação', 
                                   msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                conn = sqlite3.connect('db/vendas.db')
                c = conn.cursor()
                
                # Verificar se já existe fechamento para esta data
                c.execute('SELECT id FROM fechamentos_caixa WHERE data = ?', (data,))
                if c.fetchone():
                    QMessageBox.warning(self, 'Erro', 'Já existe um fechamento para esta data!')
                    return

                # Registrar fechamento
                c.execute('''
                    CREATE TABLE IF NOT EXISTS fechamentos_caixa (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        data TEXT,
                        total_vendas REAL,
                        qtd_vendas INTEGER,
                        data_hora_fechamento TEXT
                    )
                ''')
                
                data_hora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                c.execute('''
                    INSERT INTO fechamentos_caixa (data, total_vendas, qtd_vendas, data_hora_fechamento)
                    VALUES (?, ?, ?, ?)
                ''', (data, total, qtd, data_hora))
                
                conn.commit()
                conn.close()
                
                QMessageBox.information(self, 'Sucesso', 'Caixa fechado com sucesso!')
                
            except Exception as e:
                QMessageBox.warning(self, 'Erro', f'Erro ao fechar caixa: {str(e)}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    janela = FechamentoCaixa()
    janela.show()
    sys.exit(app.exec_())