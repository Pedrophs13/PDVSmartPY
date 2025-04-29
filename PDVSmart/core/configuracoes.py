import sys
import os
import shutil
import zipfile
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFileDialog, QMessageBox, QFrame, QTableWidget, QTableWidgetItem, QComboBox,
    QDialog, QFormLayout, QTabWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from sistema.usuarios import criar_banco_usuarios

CONFIG_DB = 'configuracoes.db'

def criar_banco_config():
    conn = sqlite3.connect(CONFIG_DB)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS empresa (
            id INTEGER PRIMARY KEY,
            nome TEXT,
            cnpj TEXT,
            endereco TEXT,
            certificado_digital TEXT,
            senha_certificado TEXT,
            ambiente_nfce TEXT DEFAULT 'homologacao',
            serie_nfce TEXT DEFAULT '1',
            proxima_numeracao INTEGER DEFAULT 1
        )
    ''')
    c.execute("SELECT COUNT(*) FROM empresa")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO empresa (id, nome, cnpj, endereco) VALUES (1, '', '', '')")
    conn.commit()
    conn.close()

def carregar_configuracoes():
    conn = sqlite3.connect(CONFIG_DB)
    c = conn.cursor()
    c.execute('SELECT nome, cnpj, endereco, certificado_digital, senha_certificado, ambiente_nfce, serie_nfce, proxima_numeracao FROM empresa WHERE id=1')
    row = c.fetchone()
    conn.close()
    return row if row else ('', '', '', '', '', 'homologacao', '1', 1)

def salvar_configuracoes(nome, cnpj, endereco, certificado_digital, senha_certificado, ambiente_nfce, serie_nfce, proxima_numeracao):
    conn = sqlite3.connect(CONFIG_DB)
    c = conn.cursor()
    c.execute('UPDATE empresa SET nome=?, cnpj=?, endereco=?, certificado_digital=?, senha_certificado=?, ambiente_nfce=?, serie_nfce=?, proxima_numeracao=? WHERE id=1', 
              (nome, cnpj, endereco, certificado_digital, senha_certificado, ambiente_nfce, serie_nfce, proxima_numeracao))
    conn.commit()
    conn.close()

class Configuracoes(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Configurações do Sistema')
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet('background: #f0f2f5;')
        criar_banco_config()
        criar_banco_usuarios()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Criação das abas
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet('''
            QTabWidget::pane { border: 1px solid #cccccc; }
            QTabBar::tab { 
                background: #e0e0e0; 
                padding: 10px 15px;
                margin-right: 2px;
            }
            QTabBar::tab:selected { 
                background: #2196f3; 
                color: white;
            }
        ''')
        
        # Aba de Dados da Empresa
        tab_empresa = QWidget()
        tab_empresa.setStyleSheet('background: white; padding: 20px;')
        self.criar_aba_empresa(tab_empresa)
        tab_widget.addTab(tab_empresa, 'Dados da Empresa')
        
        # Aba de Configurações Fiscais
        tab_fiscal = QWidget()
        tab_fiscal.setStyleSheet('background: white; padding: 20px;')
        self.criar_aba_fiscal(tab_fiscal)
        tab_widget.addTab(tab_fiscal, 'Configurações Fiscais')
        
        # Aba de Backup
        tab_backup = QWidget()
        tab_backup.setStyleSheet('background: white; padding: 20px;')
        self.criar_aba_backup(tab_backup)
        tab_widget.addTab(tab_backup, 'Backup')
        
        layout.addWidget(tab_widget)
        self.setLayout(layout)

    def criar_aba_empresa(self, tab):
        layout = QVBoxLayout()
        
        # Logo
        frame_logo = QFrame()
        frame_logo.setStyleSheet('background: #f8f9fa; border-radius: 8px; padding: 15px;')
        logo_layout = QVBoxLayout(frame_logo)
        
        self.logo_label = QLabel()
        self.logo_label.setFixedSize(200, 100)
        self.logo_label.setStyleSheet('border: 2px dashed #ccc; background: white;')
        self.carregar_logo()
        
        btn_logo = QPushButton('Selecionar Logo')
        btn_logo.setStyleSheet('background: #2196f3; color: white; padding: 10px; border-radius: 4px;')
        btn_logo.clicked.connect(self.selecionar_logo)
        
        logo_layout.addWidget(self.logo_label, alignment=Qt.AlignCenter)
        logo_layout.addWidget(btn_logo)
        
        # Dados da empresa
        nome, cnpj, endereco, *_ = carregar_configuracoes()
        
        self.nome_input = QLineEdit(nome)
        self.cnpj_input = QLineEdit(cnpj)
        self.endereco_input = QLineEdit(endereco)
        
        for widget in [self.nome_input, self.cnpj_input, self.endereco_input]:
            widget.setStyleSheet('padding: 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px;')
        
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.addRow('Nome da Empresa:', self.nome_input)
        form_layout.addRow('CNPJ:', self.cnpj_input)
        form_layout.addRow('Endereço:', self.endereco_input)
        
        btn_salvar = QPushButton('Salvar Dados da Empresa')
        btn_salvar.setStyleSheet('background: #4caf50; color: white; padding: 12px; border-radius: 4px; font-weight: bold;')
        btn_salvar.clicked.connect(self.salvar_empresa)
        
        layout.addWidget(frame_logo)
        layout.addSpacing(20)
        layout.addLayout(form_layout)
        layout.addSpacing(20)
        layout.addWidget(btn_salvar)
        layout.addStretch()
        
        tab.setLayout(layout)

    def criar_aba_fiscal(self, tab):
        layout = QVBoxLayout()
        
        _, _, _, cert_digital, senha_cert, ambiente, serie, prox_num = carregar_configuracoes()
        
        self.cert_digital_input = QLineEdit(cert_digital)
        self.senha_cert_input = QLineEdit(senha_cert)
        self.senha_cert_input.setEchoMode(QLineEdit.Password)
        self.ambiente_combo = QComboBox()
        self.ambiente_combo.addItems(['homologacao', 'producao'])
        self.ambiente_combo.setCurrentText(ambiente)
        self.serie_input = QLineEdit(serie)
        self.prox_num_input = QLineEdit(str(prox_num))
        
        for widget in [self.cert_digital_input, self.senha_cert_input, self.ambiente_combo, self.serie_input, self.prox_num_input]:
            widget.setStyleSheet('padding: 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px;')
        
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        btn_certificado = QPushButton('Selecionar Certificado')
        btn_certificado.setStyleSheet('background: #2196f3; color: white; padding: 8px; border-radius: 4px;')
        btn_certificado.clicked.connect(self.selecionar_certificado)
        
        form_layout.addRow('Certificado Digital (A1):', self.cert_digital_input)
        form_layout.addRow('', btn_certificado)
        form_layout.addRow('Senha do Certificado:', self.senha_cert_input)
        form_layout.addRow('Ambiente NFCe:', self.ambiente_combo)
        form_layout.addRow('Série NFCe:', self.serie_input)
        form_layout.addRow('Próxima Numeração:', self.prox_num_input)
        
        btn_salvar = QPushButton('Salvar Configurações Fiscais')
        btn_salvar.setStyleSheet('background: #4caf50; color: white; padding: 12px; border-radius: 4px; font-weight: bold;')
        btn_salvar.clicked.connect(self.salvar_fiscal)
        
        layout.addLayout(form_layout)
        layout.addSpacing(20)
        layout.addWidget(btn_salvar)
        layout.addStretch()
        
        tab.setLayout(layout)

    def criar_aba_backup(self, tab):
        layout = QVBoxLayout()
        
        info_label = QLabel('Faça backup dos dados do sistema regularmente para evitar perdas de informações.')
        info_label.setStyleSheet('color: #666; margin-bottom: 20px;')
        info_label.setWordWrap(True)
        
        btn_backup = QPushButton('Realizar Backup Agora')
        btn_backup.setStyleSheet('''
            QPushButton {
                background: #ff9800;
                color: white;
                padding: 15px;
                border-radius: 4px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #f57c00;
            }
        ''')
        btn_backup.clicked.connect(self.fazer_backup)
        
        btn_restaurar = QPushButton('Restaurar Backup')
        btn_restaurar.setStyleSheet('''
            QPushButton {
                background: #2196f3;
                color: white;
                padding: 15px;
                border-radius: 4px;
                font-size: 16px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background: #1976d2;
            }
        ''')
        btn_restaurar.clicked.connect(self.restaurar_backup)
        
        layout.addWidget(info_label)
        layout.addWidget(btn_backup)
        layout.addWidget(btn_restaurar)
        layout.addStretch()
        
        tab.setLayout(layout)

    def selecionar_logo(self):
        arquivo, _ = QFileDialog.getOpenFileName(self, 'Selecione a logo', '', 'Imagens (*.png *.jpg *.jpeg)')
        if arquivo:
            shutil.copyfile(arquivo, 'logo_empresa.png')
            self.carregar_logo()

    def carregar_logo(self):
        try:
            pixmap = QPixmap('logo_empresa.png')
            if not pixmap.isNull():
                self.logo_label.setPixmap(pixmap.scaled(self.logo_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                self.logo_label.setText('Sem logo')
        except:
            self.logo_label.setText('Sem logo')

    def selecionar_certificado(self):
        arquivo, _ = QFileDialog.getOpenFileName(self, 'Selecionar Certificado Digital', '', 'Certificado Digital (*.pfx)')
        if arquivo:
            self.cert_digital_input.setText(arquivo)

    def salvar_empresa(self):
        _, _, _, cert_digital, senha_cert, ambiente, serie, prox_num = carregar_configuracoes()
        salvar_configuracoes(
            self.nome_input.text(),
            self.cnpj_input.text(),
            self.endereco_input.text(),
            cert_digital, senha_cert, ambiente, serie, prox_num
        )
        QMessageBox.information(self, 'Sucesso', 'Dados da empresa salvos com sucesso!')
        self.parent().setWindowTitle(f'Sistema de Gestão Comercial - {self.nome_input.text()}')
        self.parent().update()

    def salvar_fiscal(self):
        nome, cnpj, endereco, _, _, _, _, _ = carregar_configuracoes()
        try:
            prox_num = int(self.prox_num_input.text())
            salvar_configuracoes(
                nome, cnpj, endereco,
                self.cert_digital_input.text(),
                self.senha_cert_input.text(),
                self.ambiente_combo.currentText(),
                self.serie_input.text(),
                prox_num
            )
            QMessageBox.information(self, 'Sucesso', 'Configurações fiscais salvas com sucesso!')
        except ValueError:
            QMessageBox.warning(self, 'Erro', 'A próxima numeração deve ser um número inteiro!')

    def fazer_backup(self):
        arquivos = ['produtos.db', 'clientes.db', 'vendas.db', CONFIG_DB, 'logo_empresa.png']
        arquivos_existentes = [arq for arq in arquivos if os.path.exists(arq)]
        
        if not arquivos_existentes:
            QMessageBox.warning(self, 'Erro', 'Nenhum banco de dados encontrado para backup!')
            return
            
        caminho, _ = QFileDialog.getSaveFileName(self, 'Salvar Backup', '', 'Arquivo ZIP (*.zip)')
        if caminho:
            if not caminho.endswith('.zip'):
                caminho += '.zip'
            try:
                with zipfile.ZipFile(caminho, 'w') as backup_zip:
                    for arq in arquivos_existentes:
                        backup_zip.write(arq)
                QMessageBox.information(self, 'Sucesso', 'Backup realizado com sucesso!')
            except Exception as e:
                QMessageBox.critical(self, 'Erro', f'Erro ao realizar backup: {str(e)}')

    def restaurar_backup(self):
        caminho, _ = QFileDialog.getOpenFileName(self, 'Selecionar Backup', '', 'Arquivo ZIP (*.zip)')
        if not caminho:
            return

        try:
            # Verificar se o arquivo é um ZIP válido e contém os arquivos esperados
            arquivos_esperados = {'produtos.db', 'clientes.db', 'vendas.db', CONFIG_DB}
            with zipfile.ZipFile(caminho, 'r') as backup_zip:
                arquivos_backup = set(backup_zip.namelist())
                if not arquivos_esperados.intersection(arquivos_backup):
                    QMessageBox.warning(self, 'Erro', 'Arquivo de backup inválido ou corrompido!')
                    return

                # Confirmar com o usuário
                resposta = QMessageBox.question(self, 'Confirmação',
                    'A restauração do backup substituirá todos os dados atuais. Deseja continuar?',
                    QMessageBox.Yes | QMessageBox.No)
                
                if resposta == QMessageBox.Yes:
                    # Fechar conexões com os bancos de dados
                    for arquivo in arquivos_backup:
                        if arquivo.endswith('.db') and os.path.exists(arquivo):
                            try:
                                conn = sqlite3.connect(arquivo)
                                conn.close()
                            except:
                                pass

                    # Restaurar os arquivos
                    backup_zip.extractall()
                    
                    # Recarregar a interface
                    self.carregar_logo()
                    nome, cnpj, endereco, *_ = carregar_configuracoes()
                    self.nome_input.setText(nome)
                    self.cnpj_input.setText(cnpj)
                    self.endereco_input.setText(endereco)
                    
                    QMessageBox.information(self, 'Sucesso', 'Backup restaurado com sucesso! Reinicie o sistema para aplicar todas as alterações.')

        except zipfile.BadZipFile:
            QMessageBox.critical(self, 'Erro', 'O arquivo selecionado não é um arquivo ZIP válido!')
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Erro ao restaurar backup: {str(e)}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    janela = Configuracoes()
    janela.show()
    sys.exit(app.exec_())
