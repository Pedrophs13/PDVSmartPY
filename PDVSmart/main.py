from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QStatusBar, QMessageBox
)
from sistema.login import Login
from sistema.usuarios import CadastroUsuarios, criar_banco_usuarios
from sistema.fechamento_caixa import FechamentoCaixa
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from cadastros.cadastro_produtos import CadastroProdutos
from consultas.consulta_produtos import ConsultaProdutos
from cadastros.cadastro_clientes import CadastroClientes
from consultas.consulta_clientes import ConsultaClientes
from cadastros.cadastro_os import CadastroOS
from consultas.consulta_os import ConsultaOS
from sistema.relatorios import Relatorios
from core.configuracoes import Configuracoes
from sistema.pdv import PDV

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Sistema de Gestão Comercial')
        self.setGeometry(200, 100, 1000, 650)
        self.setStyleSheet('background: #f5f7fa;')
        self.usuario = None
        self.tabs = None
        self.fazer_login()

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        # Topo com logo e nome da empresa
        hbox_top = QHBoxLayout()
        logo = QLabel()
        pixmap = QPixmap('assets/logo_empresa.png')
        if not pixmap.isNull():
            logo.setPixmap(pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            logo.setText('Logo não encontrada')
            logo.setStyleSheet('font-size: 18px; color: #888;')
        hbox_top.addWidget(logo)
        nome_empresa = QLabel('EMPRESA EXEMPLO LTDA')
        nome_empresa.setStyleSheet('font-size: 22px; font-weight: bold; color: #2e3b4e;')
        hbox_top.addWidget(nome_empresa)
        hbox_top.addStretch()
        layout.addLayout(hbox_top)

        # Linha divisória
        frame_div = QFrame()
        frame_div.setFrameShape(QFrame.HLine)
        frame_div.setFrameShadow(QFrame.Sunken)
        layout.addWidget(frame_div)

        # Botão PDV destacado
        btn_pdv = QPushButton('Abrir PDV')
        btn_pdv.setStyleSheet(
            'font-size:18px; background:#1976d2; color:white; padding:14px 48px; border-radius:22px; margin:16px 0; font-weight:bold;'
        )
        btn_pdv.setMinimumHeight(48)
        btn_pdv.setMaximumWidth(280)
        btn_pdv.setCursor(Qt.PointingHandCursor)
        btn_pdv.clicked.connect(self.abrir_pdv)
        layout.addWidget(btn_pdv, alignment=Qt.AlignHCenter)

        # Abas para módulos administrativos
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet('QTabBar::tab { height: 38px; width: 180px; font-size: 15px; }')
        self.tabs.addTab(CadastroProdutos(), 'Cadastro de Produtos')
        self.tabs.addTab(ConsultaProdutos(), 'Consulta de Produtos')
        self.tabs.addTab(CadastroClientes(), 'Cadastro de Clientes')
        self.tabs.addTab(ConsultaClientes(), 'Consulta de Clientes')
        self.tabs.addTab(CadastroOS(), 'Cadastro OS')
        self.tabs.addTab(ConsultaOS(), 'Consulta OS')
        self.tabs.addTab(Relatorios(), 'Relatórios')
        self.tabs.addTab(Configuracoes(), 'Configurações')
        layout.addWidget(self.tabs)

        # Barra de status
        status = QStatusBar()
        status.showMessage('Usuário: admin | Versão 1.0 | ')
        self.setStatusBar(status)

        self.setCentralWidget(central_widget)

    def fazer_login(self):
        login = Login()
        login.show()
        login.exec_()
        self.usuario = login.get_usuario()
        if not self.usuario:
            sys.exit()
        self.configurar_interface()

    def configurar_interface(self):
        # Configura a interface baseada no tipo de usuário
        if not self.tabs:
            central_widget = QWidget()
            layout = QVBoxLayout(central_widget)

            # Topo com logo e nome da empresa
            hbox_top = QHBoxLayout()
            logo = QLabel()
            pixmap = QPixmap('assets/logo_empresa.png')
            if not pixmap.isNull():
                logo.setPixmap(pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                logo.setText('Logo não encontrada')
                logo.setStyleSheet('font-size: 18px; color: #888;')
            hbox_top.addWidget(logo)
            nome_empresa = QLabel('EMPRESA EXEMPLO LTDA')
            nome_empresa.setStyleSheet('font-size: 22px; font-weight: bold; color: #2e3b4e;')
            hbox_top.addWidget(nome_empresa)
            hbox_top.addStretch()
            layout.addLayout(hbox_top)

            # Linha divisória
            frame_div = QFrame()
            frame_div.setFrameShape(QFrame.HLine)
            frame_div.setFrameShadow(QFrame.Sunken)
            layout.addWidget(frame_div)

            # Botão PDV destacado
            btn_pdv = QPushButton('Abrir PDV')
            btn_pdv.setStyleSheet(
                'font-size:18px; background:#1976d2; color:white; padding:14px 48px; border-radius:22px; margin:16px 0; font-weight:bold;'
            )
            btn_pdv.setMinimumHeight(48)
            btn_pdv.setMaximumWidth(280)
            btn_pdv.setCursor(Qt.PointingHandCursor)
            btn_pdv.clicked.connect(self.abrir_pdv)
            layout.addWidget(btn_pdv, alignment=Qt.AlignHCenter)

            # Abas para módulos administrativos
            self.tabs = QTabWidget()
            self.tabs.setStyleSheet('QTabBar::tab { height: 38px; width: 180px; font-size: 15px; }')
            self.tabs.addTab(CadastroProdutos(), 'Cadastro de Produtos')
            self.tabs.addTab(ConsultaProdutos(), 'Consulta de Produtos')
            self.tabs.addTab(CadastroClientes(), 'Cadastro de Clientes')
            self.tabs.addTab(ConsultaClientes(), 'Consulta de Clientes')
            self.tabs.addTab(CadastroOS(), 'Cadastro OS')
            self.tabs.addTab(ConsultaOS(), 'Consulta OS')
            self.tabs.addTab(Relatorios(), 'Relatórios')
            self.tabs.addTab(Configuracoes(), 'Configurações')
            layout.addWidget(self.tabs)

            # Barra de status
            status = QStatusBar()
            status.showMessage('Usuário: admin | Versão 1.0 | ')
            self.setStatusBar(status)

            self.setCentralWidget(central_widget)

        if self.usuario['tipo'] == 'operador':
            # Operador só vê o PDV
            self.tabs.setVisible(False)
            self.abrir_pdv()
        else:
            # Administrador vê tudo
            self.tabs.addTab(CadastroUsuarios(), 'Cadastro de Usuários')
            self.tabs.addTab(FechamentoCaixa(), 'Fechamento de Caixa')

    def abrir_pdv(self):
        # Abre o PDV em uma janela separada
        self.janela_pdv = PDV()
        self.janela_pdv.showMaximized()  # ou .show() se não quiser tela cheia

if __name__ == '__main__':
    import sys
    import os
    from cadastros.cadastro_produtos import criar_banco
    from cadastros.cadastro_clientes import criar_banco_clientes
    from cadastros.cadastro_os import criar_banco_os
    from core.configuracoes import criar_banco_config
    from sistema.pdv import criar_banco_vendas
    
    # Cria o diretório db se não existir
    if not os.path.exists('db'):
        os.makedirs('db')
    
    # Inicializa todos os bancos de dados
    criar_banco()
    criar_banco_clientes()
    criar_banco_os()
    criar_banco_config()
    criar_banco_vendas()
    criar_banco_usuarios()
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())