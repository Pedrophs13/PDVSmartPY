from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QComboBox, QSpinBox,
    QShortcut, QDialog, QFrame
)
from PyQt5.QtGui import QTextDocument, QImage, QPainter, QKeySequence
from PyQt5.QtCore import QSizeF, Qt
import os
import qrcode
import sqlite3
from datetime import datetime

def criar_banco_vendas():
    conn = sqlite3.connect('db/vendas.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            cliente_id INTEGER,
            total REAL,
            valor_recebido REAL,
            troco REAL,
            tipo_pagamento TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS itens_venda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venda_id INTEGER,
            produto_id INTEGER,
            quantidade INTEGER,
            preco_unitario REAL,
            subtotal REAL
        )
    ''')
    conn.commit()
    conn.close()

def carregar_produtos():
    conn = sqlite3.connect('db/produtos.db')
    c = conn.cursor()
    c.execute('SELECT id, nome, preco, codigo_barras FROM produtos')
    produtos = c.fetchall()
    conn.close()
    return produtos

def carregar_clientes():
    conn = sqlite3.connect('db/clientes.db')
    c = conn.cursor()
    c.execute('SELECT id, nome FROM clientes')
    clientes = c.fetchall()
    conn.close()
    return clientes

class ConsultaProdutoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Consulta de Produto')
        self.setMinimumWidth(400)
        self.produto_selecionado = None
        layout = QVBoxLayout(self)
        self.input_pesquisa = QLineEdit()
        self.input_pesquisa.setPlaceholderText('Digite nome ou código de barras...')
        self.input_pesquisa.setMinimumHeight(32)
        self.input_pesquisa.setStyleSheet('font-size: 15px; padding: 4px 8px; border: 1px solid #ccc; border-radius: 4px;')
        self.input_pesquisa.textChanged.connect(self.buscar)
        layout.addWidget(self.input_pesquisa)
        self.tabela = QTableWidget(0, 3)
        self.tabela.setHorizontalHeaderLabels(['ID', 'Nome', 'Preço'])
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.setSelectionMode(QTableWidget.SingleSelection)
        self.tabela.setStyleSheet('font-size: 15px; background: #f8fafc;')
        self.tabela.horizontalHeader().setStyleSheet('font-size: 15px; font-weight: bold; padding: 8px;')
        self.tabela.verticalHeader().setStyleSheet('font-size: 15px;')
        self.tabela.setAlternatingRowColors(True)
        layout.addWidget(self.tabela)
        btn_add = QPushButton('Adicionar à Venda')
        btn_add.clicked.connect(self.adicionar_a_venda)
        layout.addWidget(btn_add)
        self.buscar()
    def buscar(self):
        termo = self.input_pesquisa.text().strip().lower()
        import sqlite3
        conn = sqlite3.connect('db/produtos.db')
        c = conn.cursor()
        if termo:
            c.execute('SELECT id, nome, preco, codigo_barras FROM produtos WHERE LOWER(nome) LIKE ? OR codigo_barras LIKE ?', (f'%{termo}%', f'%{termo}%'))
        else:
            c.execute('SELECT id, nome, preco, codigo_barras FROM produtos')
        produtos = c.fetchall()
        conn.close()
        self.tabela.setRowCount(0)
        for prod in produtos:
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            self.tabela.setItem(row, 0, QTableWidgetItem(str(prod[0])))
            self.tabela.setItem(row, 1, QTableWidgetItem(prod[1]))
            self.tabela.setItem(row, 2, QTableWidgetItem(f'R$ {prod[2]:.2f}'))
    def adicionar_a_venda(self):
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, 'Seleção', 'Selecione um produto na lista.')
            return
        id_prod = int(self.tabela.item(row, 0).text())
        nome_prod = self.tabela.item(row, 1).text()
        preco_prod = float(self.tabela.item(row, 2).text().replace('R$','').replace(',','.'))
        self.produto_selecionado = (id_prod, nome_prod, preco_prod)
        self.accept()

class PDV(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet('background: #f5f7fa;')
        self.setWindowTitle('PDV - Ponto de Venda')
        self.setGeometry(200, 200, 700, 500)
        self.produtos = carregar_produtos()
        self.clientes = carregar_clientes()
        self.itens_venda = []  # Lista de itens: [produto_id, nome, quantidade, preco_unitario, subtotal]
        self.init_ui()
        self.atualizar_total()
        # Atalhos de teclado
        QShortcut(QKeySequence('F3'), self, activated=self.adicionar_item)
        QShortcut(QKeySequence('F4'), self, activated=self.finalizar_venda)
        QShortcut(QKeySequence('F5'), self, activated=self.reimprimir_ultima_venda)
        QShortcut(QKeySequence('Esc'), self, activated=self.limpar_venda)
        QShortcut(QKeySequence('F2'), self, activated=self.abrir_consulta_produto)
        # F2 reservado para consulta de produto

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(18)

        # Área de produtos e busca
        frame_prod = QFrame()
        frame_prod.setFrameShape(QFrame.StyledPanel)
        frame_prod.setStyleSheet('background: #ffffff; border-radius: 8px; padding: 10px;')
        vbox_prod = QVBoxLayout(frame_prod)
        hbox_busca = QHBoxLayout()
        hbox_busca.addWidget(QLabel('<b>Produto/Código:</b>'))
        self.input_busca = QLineEdit()
        self.input_busca.setMinimumHeight(32)
        hbox_busca.addWidget(self.input_busca)
        self.input_qtd = QSpinBox()
        self.input_qtd.setValue(1)
        self.input_qtd.setMinimum(1)
        self.input_qtd.setMaximum(999)
        hbox_busca.addWidget(QLabel('Qtd:'))
        hbox_busca.addWidget(self.input_qtd)
        btn_add = QPushButton('Adicionar (F3)')
        btn_add.setStyleSheet('background: #1976d2; color: white; font-size: 15px; padding: 8px 14px; border-radius: 6px;')
        btn_add.clicked.connect(self.adicionar_item)
        hbox_busca.addWidget(btn_add)
        vbox_prod.addLayout(hbox_busca)
        # Botão consultar produto
        btn_consultar = QPushButton('Consultar Produto (F2)')
        btn_consultar.setStyleSheet('background: #90caf9; color: #263238; font-size: 14px; padding: 6px 10px; border-radius: 6px;')
        btn_consultar.clicked.connect(self.abrir_consulta_produto)
        vbox_prod.addWidget(btn_consultar)
        layout.addWidget(frame_prod)

        # Área de itens da venda
        frame_itens = QFrame()
        frame_itens.setFrameShape(QFrame.StyledPanel)
        frame_itens.setStyleSheet('background: #ffffff; border-radius: 8px; padding: 10px;')
        vbox_itens = QVBoxLayout(frame_itens)
        lbl_itens = QLabel('<b>Itens da Venda</b>')
        lbl_itens.setStyleSheet('font-size: 16px; color: #2e3b4e;')
        vbox_itens.addWidget(lbl_itens)
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(5)
        self.tabela.setHorizontalHeaderLabels(['#', 'Produto', 'Qtd', 'Unitário', 'Subtotal'])
        self.tabela.setStyleSheet('font-size: 14px; background: #f8fafc;')
        self.tabela.setMinimumHeight(160)
        vbox_itens.addWidget(self.tabela)
        layout.addWidget(frame_itens)

        # Área de total e pagamentos
        frame_tot = QFrame()
        frame_tot.setFrameShape(QFrame.StyledPanel)
        frame_tot.setStyleSheet('background: #e3f2fd; border-radius: 8px; padding: 10px;')
        vbox_tot = QVBoxLayout(frame_tot)
        hbox_total = QHBoxLayout()
        self.label_total = QLabel('Total: R$ 0.00')
        self.label_total.setStyleSheet('font-size: 28px; font-weight: bold; color: #1976d2;')
        hbox_total.addStretch()
        hbox_total.addWidget(self.label_total)
        vbox_tot.addLayout(hbox_total)
        hbox_pag = QHBoxLayout()
        hbox_pag.addWidget(QLabel('Tipo de pagamento:'))
        self.combo_pagamento = QComboBox()
        self.combo_pagamento.addItems(['Dinheiro', 'Cartão de Crédito', 'Cartão de Débito', 'PIX'])
        self.combo_pagamento.currentIndexChanged.connect(self.atualizar_valor_recebido_pagamento)
        hbox_pag.addWidget(self.combo_pagamento)
        hbox_pag.addWidget(QLabel('Valor recebido:'))
        self.input_recebido = QLineEdit()
        self.input_recebido.setMinimumWidth(90)
        hbox_pag.addWidget(self.input_recebido)
        self.label_troco = QLabel('Troco: R$ 0.00')
        hbox_pag.addWidget(self.label_troco)
        vbox_tot.addLayout(hbox_pag)
        layout.addWidget(frame_tot)

        # Área de botões de ação
        hbox_acoes = QHBoxLayout()
        btn_finalizar = QPushButton('Finalizar Venda (F4)')
        btn_finalizar.setStyleSheet('background: #43a047; color: white; font-size: 17px; padding: 12px 24px; border-radius: 8px;')
        btn_finalizar.clicked.connect(self.finalizar_venda)
        hbox_acoes.addWidget(btn_finalizar)
        btn_reimprimir = QPushButton('Reimprimir Última Venda (F5)')
        btn_reimprimir.setStyleSheet('background: #0288d1; color: white; font-size: 17px; padding: 12px 18px; border-radius: 8px;')
        btn_reimprimir.clicked.connect(self.reimprimir_ultima_venda)
        hbox_acoes.addWidget(btn_reimprimir)
        btn_limpar = QPushButton('Limpar Venda (ESC)')
        btn_limpar.setStyleSheet('background: #ef5350; color: white; font-size: 17px; padding: 12px 18px; border-radius: 8px;')
        btn_limpar.clicked.connect(self.limpar_venda)
        hbox_acoes.addWidget(btn_limpar)
        layout.addLayout(hbox_acoes)

        self.setLayout(layout)

    def adicionar_item(self):
        termo = self.input_busca.text().strip()
        qtd = self.input_qtd.value()
        if not termo:
            QMessageBox.warning(self, 'Atenção', 'Digite o código de barras ou nome do produto!')
            return
        produto = None
        for prod in self.produtos:
            if termo == prod[3] or termo.lower() in prod[1].lower():
                produto = prod
                break
        if not produto:
            QMessageBox.warning(self, 'Erro', 'Produto não encontrado!')
            return
        subtotal = qtd * produto[2]
        self.itens_venda.append([produto[0], produto[1], qtd, produto[2], subtotal])
        self.atualizar_tabela()
        self.atualizar_total()
        self.input_busca.clear()
        self.input_qtd.setValue(1)

    def adicionar_item_por_id(self, id_prod, nome_prod, preco_prod):
        # Checa se já existe esse produto na venda
        for idx, item in enumerate(self.itens_venda):
            if item[0] == id_prod:
                self.itens_venda[idx] = (item[0], item[1], item[2]+1, item[3], (item[2]+1)*item[3])
                self.atualizar_tabela()
                self.atualizar_total()
                return
        # Se não existe, adiciona novo
        self.itens_venda.append((id_prod, nome_prod, 1, preco_prod, preco_prod))
        self.atualizar_tabela()
        self.atualizar_total()

    def atualizar_tabela(self):
        self.tabela.setRowCount(0)
        for idx, item in enumerate(self.itens_venda):
            self.tabela.insertRow(idx)
            for col, val in enumerate(item):
                self.tabela.setItem(idx, col, QTableWidgetItem(str(val)))

    def atualizar_total(self):
        total = sum(item[4] for item in self.itens_venda)
        self.label_total.setText(f'Total: R$ {total:.2f}')
        self.atualizar_troco()

    def atualizar_troco(self):
        try:
            recebido = float(self.input_recebido.text())
        except:
            recebido = 0.0
        total = sum(item[4] for item in self.itens_venda)
        troco = recebido - total
        self.label_troco.setText(f'Troco: R$ {troco:.2f}')

    def atualizar_valor_recebido_pagamento(self):
        tipo = self.combo_pagamento.currentText()
        if tipo in ['PIX', 'Cartão de Crédito', 'Cartão de Débito']:
            self.input_recebido.setText(f'{self.calcular_total():.2f}')
        else:
            self.input_recebido.clear()

    def calcular_total(self):
        return sum(item[4] for item in self.itens_venda)

    def finalizar_venda(self):
        if not self.itens_venda:
            QMessageBox.warning(self, 'Erro', 'Nenhum produto adicionado!')
            return
        try:
            valor_recebido = float(self.input_recebido.text())
        except:
            QMessageBox.warning(self, 'Erro', 'Valor recebido inválido!')
            return
        total = sum(item[4] for item in self.itens_venda)
        if valor_recebido < total:
            QMessageBox.warning(self, 'Erro', 'Valor recebido menor que o total!')
            return
        cliente_id = 0
        troco = valor_recebido - total
        data = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        tipo_pagamento = self.combo_pagamento.currentText()
        # Salvar venda
        conn = sqlite3.connect('vendas.db')
        c = conn.cursor()
        c.execute('INSERT INTO vendas (data, cliente_id, total, valor_recebido, troco, tipo_pagamento) VALUES (?, ?, ?, ?, ?, ?)',
                  (data, cliente_id, total, valor_recebido, troco, tipo_pagamento))
        venda_id = c.lastrowid
        for item in self.itens_venda:
            c.execute('INSERT INTO itens_venda (venda_id, produto_id, quantidade, preco_unitario, subtotal) VALUES (?, ?, ?, ?, ?)',
                      (venda_id, item[0], item[2], item[3], item[4]))
        conn.commit()
        conn.close()
        QMessageBox.information(self, 'Sucesso', f'Venda finalizada! Troco: R$ {troco:.2f}')
        # Imprimir recibo automaticamente com novo layout
        self.imprimir_recibo(finalizada=True, total=total, valor_recebido=valor_recebido, troco=troco, venda_id=venda_id, data=data, tipo_pagamento=tipo_pagamento)
        self.itens_venda = []
        self.atualizar_tabela()
        self.atualizar_total()
        self.input_recebido.clear()
        self.label_troco.setText('Troco: R$ 0.00')

    def reimprimir_ultima_venda(self):
        import sqlite3
        conn = sqlite3.connect('vendas.db')
        c = conn.cursor()
        c.execute('SELECT id, data, cliente_id, total, valor_recebido, troco, tipo_pagamento FROM vendas ORDER BY id DESC LIMIT 1')
        venda = c.fetchone()
        if not venda:
            QMessageBox.information(self, 'Reimprimir', 'Nenhuma venda encontrada para reimpressão.')
            return
        venda_id, data, cliente_id, total, valor_recebido, troco, tipo_pagamento = venda
        c.execute('SELECT produto_id, quantidade, preco_unitario, subtotal FROM itens_venda WHERE venda_id=?', (venda_id,))
        itens = c.fetchall()
        itens_venda = []
        for item in itens:
            produto_id, qtd, preco, subtotal = item
            # Buscar nome do produto em produtos.db
            conn_prod = sqlite3.connect('produtos.db')
            c_prod = conn_prod.cursor()
            c_prod.execute('SELECT nome FROM produtos WHERE id=?', (produto_id,))
            nome = c_prod.fetchone()
            conn_prod.close()
            nome = nome[0] if nome else 'Produto'
            itens_venda.append((produto_id, nome, qtd, preco, subtotal))
        conn.close()
        # Imprimir cupom com dados recuperados
        self.imprimir_recibo(finalizada=True, total=total, valor_recebido=valor_recebido, troco=troco, venda_id=venda_id, data=data, tipo_pagamento=tipo_pagamento, itens_venda=itens_venda)

    def abrir_consulta_produto(self):
        dlg = ConsultaProdutoDialog(self)
        if dlg.exec_() == QDialog.Accepted and dlg.produto_selecionado:
            id_prod, nome_prod, preco_prod = dlg.produto_selecionado
            # Adicionar produto à venda com quantidade 1
            self.adicionar_item_por_id(id_prod, nome_prod, preco_prod)

    def imprimir_recibo(self, finalizada=False, total=None, valor_recebido=None, troco=None, venda_id=None, data=None, tipo_pagamento='Dinheiro', itens_venda=None):
        # Modelo de cupom estilo brasileiro (não fiscal)
        empresa_nome = 'EMPRESA EXEMPLO LTDA'
        empresa_cnpj = '12.345.678/0001-99'
        empresa_ie = 'ISENTO'
        empresa_im = '1234567'
        empresa_end = 'Rua Exemplo, 123 - Centro'
        operador = 'CAIXA01'
        # QR Code NFC-e (simulado)
        url_qr = 'https://www.sefaz.rs.gov.br/NFCE/ConsultaPublicaNFCe.aspx?p=12345678901234567890123456789012345678901234'
        qr_path = 'qrcode_tmp.png'
        self.gerar_qrcode(url_qr, qr_path)
        # Cabeçalho
        recibo = ''
        recibo += 'ECF AUTORIZADO EXCLUSIVAMENTE P/ TREIN./DESEN.\n'
        recibo += 'SEM VALOR FISCAL\n'
        recibo += f'CNPJ: {empresa_cnpj}   IE: {empresa_ie}\n'
        recibo += f'IM: {empresa_im}\n'
        recibo += f'{empresa_nome}\n{empresa_end}\n'
        recibo += '-'*40 + '\n'
        if data is None:
            from datetime import datetime
            data = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        recibo += f'{data}   CUPOM: {venda_id if venda_id else "000001"}\n'
        recibo += '-'*40 + '\n'
        recibo += 'ITEM CÓDIGO   DESCRIÇÃO      QTD VL.UNIT VL.ITEM\n'
        recibo += '-'*40 + '\n'
        lista_itens = itens_venda if itens_venda is not None else self.itens_venda
        for idx, item in enumerate(lista_itens, 1):
            nome = item[1][:12].ljust(12)
            codigo = str(item[0]).zfill(6)
            qtd = str(item[2]).rjust(3)
            preco = f'{item[3]:.2f}'.rjust(7)
            subtotal = f'{item[4]:.2f}'.rjust(7)
            recibo += f'{idx:>2} {codigo} {nome} {qtd} {preco} {subtotal}\n'
        recibo += '-'*40 + '\n'
        recibo += f'TOTAL R$:{total:>30.2f}\n'
        recibo += f'Pagamento: {tipo_pagamento}\n'
        recibo += f'Valor Recebido: R$ {valor_recebido:.2f}\nTroco: R$ {troco:.2f}\n'
        recibo += '-'*40 + '\n'
        recibo += f'Operador: {operador}\n'
        recibo += 'Obrigado pela preferência!\n'
        recibo += '-'*40 + '\n'
        recibo += f'FAB: P0810100000000   00444\n'
        # Envia para impressão
        self.imprimir_texto(recibo, qr_path)
        # Remove QR temporário
        if os.path.exists(qr_path):
            os.remove(qr_path)

    def gerar_qrcode(self, url, path):
        img = qrcode.make(url)
        img.save(path)

    def imprimir_texto(self, texto, qr_path=None):
        from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
        from PyQt5.QtGui import QTextDocument, QImage, QPainter
        from PyQt5.QtCore import QSizeF
        import os
        printer = QPrinter()
        dialog = QPrintDialog(printer, self)
        if dialog.exec_() == QPrintDialog.Accepted:
            painter = QPainter(printer)
            # Tentar desenhar a logo se existir
            y_offset = 0
            if os.path.exists('logo_empresa.png'):
                logo = QImage('logo_empresa.png')
                if not logo.isNull():
                    rect = painter.viewport()
                    width = rect.width()
                    painter.drawImage((width-logo.width())//2, 0, logo.scaledToWidth(min(200, width)))
                    y_offset = logo.scaledToWidth(min(200, width)).height() + 10
            # Texto do recibo
            doc = QTextDocument()
            doc.setPlainText(texto)
            doc.setPageSize(QSizeF(printer.pageRect().size()))
            painter.save()
            painter.translate(0, y_offset)
            doc.drawContents(painter)
            painter.restore()
            # Desenhar QR Code se existir
            if qr_path and os.path.exists(qr_path):
                qr_img = QImage(qr_path)
                if not qr_img.isNull():
                    rect = painter.viewport()
                    width = rect.width()
                    qr_size = min(120, width)
                    x_qr = int((width - qr_size) // 2)
                    y_qr = int(y_offset + doc.size().height() + 10)
                    painter.drawImage(x_qr, y_qr, qr_img.scaled(qr_size, qr_size))
            painter.end()

    def limpar_venda(self):
        # Limpa todos os campos da venda atual
        self.itens_venda.clear()
        self.atualizar_tabela()
        self.input_busca.clear()
        self.input_qtd.setValue(1)
        self.input_recebido.clear()
        self.label_troco.setText('Troco: R$ 0.00')
        self.label_total.setText('Total: R$ 0.00')

if __name__ == '__main__':
    criar_banco_vendas()
    app = QApplication(sys.argv)
    janela = PDV()
    janela.show()
    sys.exit(app.exec_())
