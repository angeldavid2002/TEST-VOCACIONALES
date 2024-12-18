import sqlite3

# Conectar a la base de datos
conexion = sqlite3.connect('database.db')
cursor = conexion.cursor()

# Consultar la estructura de las tablas
cursor.execute('SELECT sql FROM sqlite_master WHERE type="table"')
filas = cursor.fetchall()

# Abrir un archivo de texto para escribir
with open('descripcion_base_de_datos.txt', 'w', encoding='utf-8') as archivo:
    # Escribir la definición SQL de cada tabla en el archivo
    for fila in filas:
        archivo.write(fila[0] + '\n\n')  # Agrega un salto de línea extra entre tablas

# Cerrar la conexión
conexion.close()
