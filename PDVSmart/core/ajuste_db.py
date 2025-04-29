import sqlite3

conn = sqlite3.connect('vendas.db')
c = conn.cursor()
try:
    c.execute("ALTER TABLE vendas ADD COLUMN tipo_pagamento TEXT;")
    print("Coluna 'tipo_pagamento' adicionada com sucesso!")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("A coluna 'tipo_pagamento' já existe.")
    else:
        print("Erro:", e)
conn.commit()
conn.close()