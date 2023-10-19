import sqlite3

# Conectar ao banco de dados (isso criará o banco se não existir)
conn = sqlite3.connect('historico.db')

# Criar uma tabela para armazenar o histórico
conn.execute('''
    CREATE TABLE IF NOT EXISTS historico (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT,
        data_acesso DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

# Fechar a conexão
conn.close()
