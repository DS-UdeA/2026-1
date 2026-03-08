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
    pass # Lo construiremos en el siguiente paso

# ============================================================================
# PASO 3: OPERACIONES DE DISCO - ESCRITURA (Append)
# ============================================================================

def insert_record(record_str):
    """
    Abre el archivo en modo append ('a') y escribe el registro de longitud fija.
    """
    pass # Lo construiremos más adelante

# ============================================================================
# PASO 4: OPERACIONES DE DISCO - LECTURA Y ACCESO (Full Scan y Seek)
# ============================================================================

def read_all_records():
    """
    Lee el archivo completo saltando en bloques del tamaño del registro (Full Table Scan).
    """
    pass # Lo construiremos más adelante

def search_record_by_index(index):
    """
    Calcula el offset (index * RECORD_SIZE) y salta directamente a esa posición
    en el archivo para leer exactamente 1 registro en O(1).
    """
    pass # Lo construiremos más adelante

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