# ============================================================================
# Laboratorio de Estructuras de Datos - UdeA
# Tema: Heap Files - Registros de Longitud Fija (Empaquetados)
# ============================================================================

import os

# --- CONSTANTES DEL ESQUEMA ---
# Definimos los tamaños de cada campo para mantener el control y evitar "números mágicos" en el código.
ID_SIZE = 5
LAST_NAME_SIZE = 15
FIRST_NAME_SIZE = 15
AGE_SIZE = 5
SALARY_SIZE = 10

RECORD_SIZE = ID_SIZE + LAST_NAME_SIZE + FIRST_NAME_SIZE + AGE_SIZE + SALARY_SIZE
FILE_NAME = "my_database.dat" # El archivo de texto que simulará nuestro disco

# ============================================================================
# PASO 1: SERIALIZACIÓN / FORMATEO (De variables a bytes/texto)
# ============================================================================

def format_record(emp_id, last_name, first_name, age, salary):
    """
    Toma los datos de un empleado, aplica el padding necesario 
    y devuelve un string de longitud fija empaquetado.
    """
    # Formateo y padding de campos usando las constantes
    id_str = str(emp_id).rjust(ID_SIZE)
    last_name_str = str(last_name).ljust(LAST_NAME_SIZE)
    first_name_str = str(first_name).ljust(FIRST_NAME_SIZE)
    age_str = str(age).rjust(AGE_SIZE)
    salary_str = str(salary).ljust(SALARY_SIZE) 
    
    # Concatenación directa (Packed)
    record = id_str + last_name_str + first_name_str + age_str + salary_str
    
    # Validación de seguridad
    assert len(record) == RECORD_SIZE, f"Error: El registro mide {len(record)} en lugar de {RECORD_SIZE}"
    
    return record

# ============================================================================
# PASO 2: DESERIALIZACIÓN / PARSEO (De bytes/texto a variables)
# ============================================================================

def parse_record(record_str):
    """
    Toma un string leído del disco, lo corta en pedazos basado 
    en el esquema, limpia los espacios y devuelve los datos originales.
    """
    if len(record_str) != RECORD_SIZE:
        raise ValueError(f"Error: El string mide {len(record_str)}, se esperaban {RECORD_SIZE}.")

    # 1. Cortamos el string usando nuestras constantes (Slicing)
    # Llevamos un puntero (cursor) para saber dónde empieza el siguiente campo
    cursor = 0
    
    id_str = record_str[cursor : cursor + ID_SIZE]
    cursor += ID_SIZE
    
    last_name_str = record_str[cursor : cursor + LAST_NAME_SIZE]
    cursor += LAST_NAME_SIZE
    
    first_name_str = record_str[cursor : cursor + FIRST_NAME_SIZE]
    cursor += FIRST_NAME_SIZE
    
    age_str = record_str[cursor : cursor + AGE_SIZE]
    cursor += AGE_SIZE
    
    salary_str = record_str[cursor : cursor + SALARY_SIZE]
    
    # 2. Limpiamos los espacios (strip) y restauramos los tipos de datos (casting)
    emp_id = int(id_str.strip())
    last_name = last_name_str.strip()
    first_name = first_name_str.strip()
    age = int(age_str.strip())
    salary = salary_str.strip()
    
    return emp_id, last_name, first_name, age, salary

# ============================================================================
# PASO 3: OPERACIONES DE DISCO - ESCRITURA (Append)
# ============================================================================

def insert_record(record_str):
    """
    Abre el archivo en modo append ('a') y escribe el registro de longitud fija.
    """
    # Usamos 'with' para asegurar que el archivo se cierre automáticamente
    # El modo 'a' (append) agrega la información exactamente al final del archivo
    with open(FILE_NAME, "a") as file:
        file.write(record_str)

# ============================================================================
# PASO 4: OPERACIONES DE DISCO - LECTURA Y ACCESO (Full Scan y Seek)
# ============================================================================

def read_all_records():
    """
    Lee el archivo completo saltando en bloques del tamaño del registro (Full Table Scan).
    """
    if not os.path.exists(FILE_NAME):
        return []

    records = []
    with open(FILE_NAME, "r") as file:
        while True:
            # Leemos exactamente un bloque de 50 caracteres
            chunk = file.read(RECORD_SIZE)
            
            # Si el bloque está vacío, llegamos al final del archivo (EOF)
            if not chunk:
                break
                
            # Parseamos el pedazo de texto a variables útiles
            parsed_data = parse_record(chunk)
            records.append(parsed_data)
            
    return records

def search_record_by_index(index):
    """
    Calcula el offset (index * RECORD_SIZE) y salta directamente a esa posición
    en el archivo para leer exactamente 1 registro en O(1).
    """
    if not os.path.exists(FILE_NAME):
        return None

    # ¡LA FÓRMULA MÁGICA DE LOS HEAP FILES DE LONGITUD FIJA!
    offset = index * RECORD_SIZE
    
    with open(FILE_NAME, "r") as file:
        # Movemos el puntero de lectura directamente al byte calculado
        file.seek(offset)
        
        # Leemos solo los 50 caracteres que nos interesan
        chunk = file.read(RECORD_SIZE)
        
        # Si leímos algo menor al tamaño esperado, el índice no existe
        if not chunk or len(chunk) < RECORD_SIZE:
            return None
            
        return parse_record(chunk)

# ============================================================================
# BLOQUE PRINCIPAL (Pruebas de Escritorio)
# ============================================================================
if __name__ == "__main__":
    print(f"--- Iniciando Laboratorio Heap Files ---")
    print(f"Tamaño esperado del registro: {RECORD_SIZE} bytes\n")
    
    # 1. Probamos la función de formateo
    homer_record = format_record(123, "Simpson", "Homer", 31, "$400")
    print("Regla: 12345678901234567890123456789012345678901234567890")
    print(f"Dato : {homer_record}")

    # 2. Probamos la función de parseo
    print("\n--- Probando el Parseo (Deserialización) ---")
    parsed_data = parse_record(homer_record)
    
    print(f"Registro crudo (disco): '{homer_record}'")
    print(f"Datos recuperados (RAM): {parsed_data}")
    print(f"Tipo de dato del ID recuperado: {type(parsed_data[0])}")
    """
    print(f"Tipo de dato del apellido recuperado: {type(parsed_data[1])}")
    print(f"Tipo de dato del nombre recuperado: {type(parsed_data[2])}")
    print(f"Tipo de dato de la edad recuperada: {type(parsed_data[3])}")
    print(f"Tipo de dato del salario recuperado: {type(parsed_data[4])}")
    """

    # 3. Probamos la inserción en disco (Poblar el Heap File)
    print("\n--- Poblando el Heap File en Disco ---")
    
    # Si el archivo ya existe de una prueba anterior, lo borramos para empezar limpios
    if os.path.exists(FILE_NAME):
        os.remove(FILE_NAME)
        print(f"Archivo viejo '{FILE_NAME}' eliminado.")
        
    # Datos de la tabla
    simpsons_data = [
        (123, "Simpson", "Homer", 31, "$400"),
        (443, "Simpson", "Marge", 32, "$140"),
        (244, "Flanders", "Ned", 55, "$300"),
        (134, "Skinner", "Seymour", 55, "$400")
    ]
    
    # Formateamos e insertamos uno por uno
    for emp_id, last_name, first_name, age, salary in simpsons_data:
        record_str = format_record(emp_id, last_name, first_name, age, salary)
        insert_record(record_str)
        print(f"Insertado: {first_name} {last_name}")
        
    print(f"\n¡Base de datos guardada en '{FILE_NAME}'!")
    # Verificamos el tamaño real del archivo en el sistema operativo
    file_size = os.path.getsize(FILE_NAME)
    print(f"Tamaño del archivo en disco: {file_size} bytes.")
    print(f"Registros esperados: {file_size / RECORD_SIZE}")

    # 4. Probamos la Lectura Completa (Full Scan)
    print("\n--- Lectura Secuencial (Full Table Scan) ---")
    all_records = read_all_records()
    for i, record in enumerate(all_records):
        print(f"Registro en índice {i}: {record}")

    # 5. Probamos el Acceso Directo (Seek)
    print("\n--- Acceso Aleatorio O(1) con Seek ---")
    
    indice_a_buscar = 2
    print(f"Buscando directamente el registro en el índice {indice_a_buscar}...")
    
    # Esto debería traer a Ned Flanders sin leer a Homer ni a Marge
    registro_encontrado = search_record_by_index(indice_a_buscar)
    
    if registro_encontrado:
        print(f"¡Éxito! Encontrado: {registro_encontrado[2]} {registro_encontrado[1]}")
    else:
        print("Registro no encontrado (Índice fuera de rango).")
        
    print("\n--- Fin del Laboratorio ---")
