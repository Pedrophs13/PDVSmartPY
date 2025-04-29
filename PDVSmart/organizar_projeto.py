import os
import shutil

# Caminho raiz do projeto
base_path = r"C:\pdvsmart"

# Estrutura desejada
folders = {
    "db": ["clientes.db", "os.db", "produtos.db", "vendas.db", "configuracoes.db"],
    "core": ["ajuste_db.py", "configuracoes.py"],
    "cadastros": ["cadastro_clientes.py", "cadastro_os.py", "cadastro_produtos.py"],
    "consultas": ["consulta_clientes.py", "consulta_os.py", "consulta_produtos.py", "consulta_vendas.py"],
    "sistema": ["pdv.py", "relatorios.py"],
    "assets": ["logo_empresa.png"]
}

# Criar as pastas e mover arquivos
for folder, files in folders.items():
    folder_path = os.path.join(base_path, folder)
    os.makedirs(folder_path, exist_ok=True)
    for file in files:
        src = os.path.join(base_path, file)
        dst = os.path.join(folder_path, file)
        if os.path.exists(src):
            shutil.move(src, dst)
            print(f"Movido: {file} → {folder}/")

print("Organização concluída!")
