import sqlite3

conn = sqlite3.connect('../MetricsProto/tracking.db')
cursor = conn.cursor()

# Tabela Device
cursor.execute('''
    CREATE TABLE device (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(80),
        code VARCHAR(8),
        status BOOLEAN,
        brand VARCHAR(80),
        total_positions INTEGER DEFAULT 0,
        total_distance REAL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Tabela Location
cursor.execute('''
    CREATE TABLE location (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_code UUID,
        latitude DOUBLE,
        longitude DOUBLE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Tabela Metrics
cursor.execute('''
    CREATE TABLE metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_code UUID,
        day DATE,
        total_positions INTEGER DEFAULT 0,
        total_distance REAL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(device_code, day) ON CONFLICT REPLACE
    )
''')

conn.commit()
conn.close()
