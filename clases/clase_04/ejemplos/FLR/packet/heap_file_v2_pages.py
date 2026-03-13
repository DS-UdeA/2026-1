# ============================================================================
# Laboratorio de Estructuras de Datos - UdeA
# Tema: Heap Files v2 - Registros en Páginas (Page Layout & RID)
# ============================================================================

import os
import math

# --- CONSTANTES DEL ESQUEMA (Igual que v1) ---
ID_SIZE = 5
LAST_NAME_SIZE = 15
FIRST_NAME_SIZE = 15
AGE_SIZE = 5
SALARY_SIZE = 10

RECORD_SIZE = ID_SIZE + LAST_NAME_SIZE + FIRST_NAME_SIZE + AGE_SIZE + SALARY_SIZE
FILE_NAME = "my_database_pages.dat" # Nuevo archivo para no dañar el anterior

# --- NUEVAS CONSTANTES DE PAGINACIÓN ---
PAGE_SIZE = 128 # Tamaño didáctico pequeño (en la vida real suele ser 4096 u 8192)
RECORDS_PER_PAGE = PAGE_SIZE // RECORD_SIZE # Cuántos registros enteros caben (128 // 50 = 2)

# ============================================================================
# PASO 1 y 2: SERIALIZACIÓN Y DESERIALIZACIÓN (Sin cambios lógicos)
# ============================================================================

def format_record(emp_id, last_name, first_name, age, salary):
    id_str = str(emp_id).rjust(ID_SIZE)
    last_name_str = str(last_name).ljust(LAST_NAME_SIZE)
    first_name_str = str(first_name).ljust(FIRST_NAME_SIZE)
    age_str = str(age).rjust(AGE_SIZE)
    salary_str = str(salary).ljust(SALARY_SIZE) 
    
    record = id_str + last_name_str + first_name_str + age_str + salary_str
    return record

def parse_record(record_str):
    if len(record_str) != RECORD_SIZE:
        raise ValueError(f"Error en parseo. Tamaño incorrecto.")

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
# PASO 3: ESCRITURA EN DISCO (Ahora orientada a Páginas)
# ============================================================================

def bulk_insert_in_pages(records_data):
    """
    Recibe una lista de datos, los formatea y los escribe en bloques 
    estrictos del tamaño de PAGE_SIZE, simulando la escritura de un DBMS.
    """
    with open(FILE_NAME, "w") as file:
        current_page_data = ""
        records_in_current_page = 0
        current_page_id = 0
        
        for data in records_data:
            rec_str = format_record(*data)
            slot_id = records_in_current_page
            print(f"  RID asignado: ({current_page_id}, {slot_id}) → {data[2]} {data[1]}")
            current_page_data += rec_str
            records_in_current_page += 1
            
            # Si la página se llenó con los registros permitidos (2 en este caso)
            if records_in_current_page == RECORDS_PER_PAGE:
                # Calculamos la fragmentación interna (los bytes que sobran)
                wasted_space = PAGE_SIZE - len(current_page_data)
                
                # Rellenamos el resto de la página con un carácter especial (ej. '-') 
                # para que sea visualmente obvio en el laboratorio el espacio desperdiciado
                current_page_data += "-" * wasted_space
                
                # Escribimos LA PÁGINA COMPLETA en el disco
                file.write(current_page_data)
                
                # Reseteamos para la siguiente página
                current_page_data = ""
                records_in_current_page = 0
                current_page_id += 1
                
        # Si quedaron registros en una página a medio llenar al terminar el ciclo
        if records_in_current_page > 0:
            wasted_space = PAGE_SIZE - len(current_page_data)
            current_page_data += "-" * wasted_space
            file.write(current_page_data)

# ============================================================================
# PASO 4: LECTURA Y ACCESO MEDIANTE R.I.D. (Record ID = Page, Slot)
# ============================================================================

'''
def search_record_by_rid(page_id, slot_id):
    """
    Busca un registro usando su RID (Page ID, Slot ID).
    Calcula el offset considerando las páginas completas.
    """
    if not os.path.exists(FILE_NAME):
        return None

    # Validamos que no nos pidan un slot que no cabe en la página
    if slot_id >= RECORDS_PER_PAGE:
        print(f"Error: El slot {slot_id} no cabe en una página.")
        return None

    # ¡NUEVA FÓRMULA MÁGICA CON PÁGINAS!
    # Offset = (Saltarme X páginas enteras) + (Saltarme Y registros dentro de mi página)
    offset = (page_id * PAGE_SIZE) + (slot_id * RECORD_SIZE)
    
    with open(FILE_NAME, "r") as file:
        file.seek(offset)
        chunk = file.read(RECORD_SIZE)
        
        # Si leímos guiones (espacio vacío) o fin de archivo, no hay registro
        if not chunk or chunk.startswith("-"):
            return None
            
        return parse_record(chunk)

'''

def search_record_by_rid(page_id, slot_id):
    """
    Busca un registro usando su RID.
    Retorna: tupla con datos si existe, 'TOMBSTONE' si fue borrado, None si no existe.
    """
    if not os.path.exists(FILE_NAME):
        return None

    if slot_id >= RECORDS_PER_PAGE:
        return None

    offset = (page_id * PAGE_SIZE) + (slot_id * RECORD_SIZE)
    print(f"  Offset calculado: ({page_id} × {PAGE_SIZE}) + ({slot_id} × {RECORD_SIZE}) = {offset} bytes → file.seek({offset})")

    with open(FILE_NAME, "r") as file:
        file.seek(offset)
        chunk = file.read(RECORD_SIZE)

        if not chunk or chunk.startswith("-"):
            return None

        # Distinguimos lápida de registro válido
        if chunk.startswith("*"):
            return "TOMBSTONE"

        return parse_record(chunk)
        
# ============================================================================
# PASO 5: BORRADO LÓGICO (Tombstones / Lápidas)
# ============================================================================

def delete_record(page_id, slot_id):
    """
    Realiza un borrado lógico marcando el registro con una lápida ('*****' en el ID).
    Operación O(1) usando el modo 'r+' para sobrescribir físicamente el disco.
    """
    if not os.path.exists(FILE_NAME):
        print("Error: El disco no existe.")
        return False

    if slot_id >= RECORDS_PER_PAGE:
        print(f"Error: El slot {slot_id} es inválido para el tamaño de página.")
        return False

    offset = (page_id * PAGE_SIZE) + (slot_id * RECORD_SIZE)

    # Usamos 'r+' para leer y escribir sin truncar (borrar) el archivo
    with open(FILE_NAME, "r+") as file:
        file.seek(offset)
        chunk = file.read(RECORD_SIZE)

        # Verificamos si hay algo válido para borrar
        if not chunk or chunk.startswith("-") or chunk.startswith("*"):
            print(f"No se puede borrar: El RID({page_id}, {slot_id}) está vacío o ya fue borrado.")
            return False

        # Retrocedemos el cabezal del disco exactamente al inicio del registro
        file.seek(offset)
        
        # Creamos la lápida: Pisamos solo el ID con asteriscos, el resto del dato queda como "fantasma"
        tombstone = "*****" + chunk[ID_SIZE:]
        file.write(tombstone)
        
        return True

# ============================================================================
# BLOQUE PRINCIPAL (Pruebas de Escritorio)
# ============================================================================
if __name__ == "__main__":
    print(f"--- Laboratorio: Heap Files con Páginas ---")
    print(f"Tamaño de Página: {PAGE_SIZE} bytes")
    print(f"Tamaño de Registro: {RECORD_SIZE} bytes")
    print(f"Registros por Página: {RECORDS_PER_PAGE}")
    print(f"Fragmentación Interna esperada: {PAGE_SIZE % RECORD_SIZE} bytes por página\n")
    
    simpsons_data = [
        (123, "Simpson", "Homer", 31, "$400"),   # Debería ir a Page 0, Slot 0
        (443, "Simpson", "Marge", 32, "$140"),   # Debería ir a Page 0, Slot 1
        (244, "Flanders", "Ned", 55, "$300"),    # Debería ir a Page 1, Slot 0
        (134, "Skinner", "Seymour", 55, "$400")  # Debería ir a Page 1, Slot 1
    ]
    
    # 1. Guardamos la base de datos en páginas
    print("--- Poblando el Heap File en Páginas ---")
    bulk_insert_in_pages(simpsons_data)
    print("¡Base de datos paginada guardada con éxito!\n")
    
    # 2. Búsqueda por RID (Record ID)
    print("--- Búsqueda Directa O(1) con RID (Page_ID, Slot_ID) ---")
    
    # Busquemos a Ned Flanders (Page 1, Slot 0)
    target_page = 1
    target_slot = 0
    print(f"Buscando RID({target_page}, {target_slot})...")
    
    registro = search_record_by_rid(target_page, target_slot)
    if registro == "TOMBSTONE":
        print(f"RID({target_page}, {target_slot}) → TOMBSTONE (registro borrado lógicamente)")
    elif registro:
        print(f"Encontrado: {registro}")
    else:
        print("Registro vacío o no existe.")
    
    # 3. Probamos el Borrado Lógico (Delete)
    print("\n--- Operación de Borrado (Delete) ---")
    
    # Vamos a borrar a Marge Simpson (Page 0, Slot 1)
    target_page_del = 0
    target_slot_del = 1
    
    print(f"Borrando el registro en RID({target_page_del}, {target_slot_del})...")
    fue_borrado = delete_record(target_page_del, target_slot_del)
    
    if fue_borrado:
        print("Registro borrado exitosamente (Lápida insertada).")
        
    # 4. Verificamos que ya no se puede buscar
    print("\n--- Verificando la búsqueda tras el borrado ---")
    print(f"Buscando RID({target_page_del}, {target_slot_del}) tras el borrado...")
    registro_marge = search_record_by_rid(target_page_del, target_slot_del)
    
    if registro_marge == "TOMBSTONE":
        print(f"RID({target_page_del}, {target_slot_del}) → TOMBSTONE — el registro fue borrado lógicamente.")
        print("El RID sigue existiendo en disco pero el motor lo ignora en búsquedas normales.")
    elif registro_marge:
        print(f"Error: Aún puedo ver a: {registro_marge}")
    else:
        print("Registro vacío o no existe.")