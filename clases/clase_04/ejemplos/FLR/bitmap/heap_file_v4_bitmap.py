# ============================================================================
# Laboratorio de Estructuras de Datos - UdeA
# Tema: Heap Files v4 - Manejo de Espacio Libre con Bitmaps y Headers
# ============================================================================

import os

# --- CONSTANTES DEL ESQUEMA ---
ID_SIZE = 5
LAST_NAME_SIZE = 15
FIRST_NAME_SIZE = 15
AGE_SIZE = 5
SALARY_SIZE = 10

RECORD_SIZE = ID_SIZE + LAST_NAME_SIZE + FIRST_NAME_SIZE + AGE_SIZE + SALARY_SIZE
FILE_NAME = "my_database_v4.dat"

# --- NUEVAS CONSTANTES DE ARQUITECTURA (BITMAPS) ---
PAGE_SIZE = 128
HEADER_SIZE = 28 
RECORDS_PER_PAGE = (PAGE_SIZE - HEADER_SIZE) // RECORD_SIZE # (128 - 28) // 50 = 2 slots

# ============================================================================
# FUNCIONES AUXILIARES DE FORMATEO (Sin cambios en la lógica base)
# ============================================================================

def format_record(emp_id, last_name, first_name, age, salary):
    id_str = str(emp_id).rjust(ID_SIZE)
    last_name_str = str(last_name).ljust(LAST_NAME_SIZE)
    first_name_str = str(first_name).ljust(FIRST_NAME_SIZE)
    age_str = str(age).rjust(AGE_SIZE)
    salary_str = str(salary).ljust(SALARY_SIZE) 
    return id_str + last_name_str + first_name_str + age_str + salary_str

def parse_record(record_str):
    if len(record_str) != RECORD_SIZE or record_str.strip() == "": return None
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
    return (int(id_str.strip()), last_name_str.strip(), first_name_str.strip(), 
            int(age_str.strip()), salary_str.strip())

# ============================================================================
# GESTIÓN DEL ENCABEZADO DE PÁGINA (PAGE HEADER)
# ============================================================================

def create_empty_page():
    """Genera un bloque de 128 bytes con el header inicializado en '00'."""
    # Bitmap inicial: '00' (Ambos slots vacíos)
    bitmap = "0" * RECORDS_PER_PAGE
    # Relleno del header para alcanzar los 28 bytes
    header_padding = "=" * (HEADER_SIZE - RECORDS_PER_PAGE)
    header = bitmap + header_padding
    
    # Relleno de los slots de datos (100 bytes de espacios vacíos)
    empty_slots = " " * (RECORDS_PER_PAGE * RECORD_SIZE)
    
    return header + empty_slots

def read_page_bitmap(page_id):
    """Lee exclusivamente el bitmap del encabezado de una página."""
    if not os.path.exists(FILE_NAME):
        return None
        
    offset = page_id * PAGE_SIZE
    with open(FILE_NAME, "r") as file:
        file.seek(offset)
        header = file.read(HEADER_SIZE)
        if not header:
            return None
        # Retornamos solo los primeros caracteres que representan los bits
        return header[:RECORDS_PER_PAGE]

def update_page_bitmap(page_id, new_bitmap):
    """Sobrescribe el bitmap en el disco sin tocar los datos de los registros."""
    offset = page_id * PAGE_SIZE
    with open(FILE_NAME, "r+") as file:
        file.seek(offset)
        file.write(new_bitmap)

# ============================================================================
# OPERACIONES DML (INSERT, DELETE, SELECT) MEDIANTE BITMAPS
# ============================================================================

def insert_record(emp_id, last_name, first_name, age, salary):
    """
    Busca la primera página con un bit en '0', actualiza el bitmap a '1' 
    y escribe el registro físicamente. Si no hay espacio, crea una nueva página.
    """
    record_str = format_record(emp_id, last_name, first_name, age, salary)
    page_id = 0
    
    # 1. Búsqueda de espacio libre (Escaneo de Bitmaps)
    while True:
        bitmap = read_page_bitmap(page_id)
        
        # Si el bitmap es None, significa que llegamos al final del archivo.
        # Debemos crear una nueva página en el disco.
        if bitmap is None:
            with open(FILE_NAME, "a") as file:
                file.write(create_empty_page())
            bitmap = "0" * RECORDS_PER_PAGE # La nueva página está vacía ('00')
            
        # Revisamos si hay algún '0' en el bitmap actual
        if '0' in bitmap:
            slot_id = bitmap.find('0') # Encuentra el primer índice con '0'
            break
            
        page_id += 1 # Si la página está llena ('11'), revisamos la siguiente
        
    # 2. Actualizamos el Bitmap en RAM y luego en Disco
    new_bitmap_list = list(bitmap)
    new_bitmap_list[slot_id] = '1'
    new_bitmap = "".join(new_bitmap_list)
    update_page_bitmap(page_id, new_bitmap)
    
    # 3. Escribimos el dato en su offset exacto
    # FÓRMULA ACTUALIZADA CON HEADER_SIZE
    offset = (page_id * PAGE_SIZE) + HEADER_SIZE + (slot_id * RECORD_SIZE)
    
    with open(FILE_NAME, "r+") as file:
        file.seek(offset)
        file.write(record_str)
        
    print(f"[INSERT] {first_name} insertado en RID({page_id}, {slot_id}). Bitmap actualizado a '{new_bitmap}'")

def delete_record(page_id, slot_id):
    """
    Borrado lógico ultra rápido: Solo cambia un '1' a '0' en el encabezado.
    No es necesario sobrescribir el registro con asteriscos.
    """
    bitmap = read_page_bitmap(page_id)
    if not bitmap or bitmap[slot_id] == '0':
        print(f"[DELETE] Error: El slot {slot_id} en la página {page_id} ya está vacío o no existe.")
        return False
        
    # Cambiamos el bit a '0'
    new_bitmap_list = list(bitmap)
    new_bitmap_list[slot_id] = '0'
    new_bitmap = "".join(new_bitmap_list)
    
    # Guardamos el nuevo estado en el disco
    update_page_bitmap(page_id, new_bitmap)
    print(f"[DELETE] Registro en RID({page_id}, {slot_id}) eliminado lógicamente. Bitmap ahora es '{new_bitmap}'")
    return True

def search_record_by_rid(page_id, slot_id):
    """
    Verifica primero el Bitmap. Si es '0', retorna None inmediatamente 
    sin necesidad de leer el bloque de datos.
    """
    bitmap = read_page_bitmap(page_id)
    if not bitmap or slot_id >= RECORDS_PER_PAGE:
        return None
        
    # Si el mapa de bits dice que está libre, el motor no pierde tiempo leyendo el disco
    if bitmap[slot_id] == '0':
        return None
        
    offset = (page_id * PAGE_SIZE) + HEADER_SIZE + (slot_id * RECORD_SIZE)
    with open(FILE_NAME, "r") as file:
        file.seek(offset)
        chunk = file.read(RECORD_SIZE)
        return parse_record(chunk)

# ============================================================================
# BLOQUE PRINCIPAL (Pruebas de Escritorio)
# ============================================================================
if __name__ == "__main__":
    # Limpieza inicial para la prueba
    if os.path.exists(FILE_NAME): os.remove(FILE_NAME)

    print(f"--- Laboratorio: Heap Files v4 (Bitmaps) ---\n")
    
    print("1. Inserciones Iniciales:")
    insert_record(123, "Simpson", "Homer", 31, "$400")   # Page 0, Slot 0
    insert_record(443, "Simpson", "Marge", 32, "$140")   # Page 0, Slot 1
    insert_record(244, "Flanders", "Ned", 55, "$300")    # Page 1, Slot 0 (Genera nueva página)
    insert_record(134, "Skinner", "Seymour", 55, "$400") # Page 1, Slot 1
    
    print("\n2. Estado tras borrado (Deletes):")
    # Borramos a Marge. El motor solo cambiará el bitmap de '11' a '10'
    delete_record(0, 1)
    
    print("\n3. Búsqueda tras borrado:")
    registro = search_record_by_rid(0, 1)
    if not registro:
        print("Marge no fue encontrada (El Bitmap reporta el slot como '0').")
        
    print("\n4. Inserción de reciclaje:")
    # Lisa debería escanear las páginas, ver que la Página 0 tiene un '0' 
    # en su bitmap, e insertarse reciclando el espacio de Marge de inmediato.
    insert_record(999, "Simpson", "Lisa", 8, "$10")

