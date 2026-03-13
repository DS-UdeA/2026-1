# ============================================================================
# Laboratorio de Estructuras de Datos - UdeA
# Tema: Heap Files v3 - Reciclaje de Espacio (Free List / Lista Enlazada)
# ============================================================================

import os

# --- CONSTANTES DEL ESQUEMA ---
ID_SIZE = 5
LAST_NAME_SIZE = 15
FIRST_NAME_SIZE = 15
AGE_SIZE = 5
SALARY_SIZE = 10

RECORD_SIZE = ID_SIZE + LAST_NAME_SIZE + FIRST_NAME_SIZE + AGE_SIZE + SALARY_SIZE
FILE_NAME = "my_database_v3.dat"

PAGE_SIZE = 128
RECORDS_PER_PAGE = PAGE_SIZE // RECORD_SIZE

# --- ESTADO DEL MOTOR (En RAM) ---
# En un DBMS real, esto se guarda en una "Header Page" (Página 0).
# Por simplicidad del laboratorio, lo mantenemos en la memoria RAM del script.
free_list_head = None  # Tupla (page_id, slot_id) que apunta al primer hueco libre

# ============================================================================
# PASO 1 y 2: FORMATEO Y PARSEO (Sin cambios lógicos)
# ============================================================================

def format_record(emp_id, last_name, first_name, age, salary):
    id_str = str(emp_id).rjust(ID_SIZE)
    last_name_str = str(last_name).ljust(LAST_NAME_SIZE)
    first_name_str = str(first_name).ljust(FIRST_NAME_SIZE)
    age_str = str(age).rjust(AGE_SIZE)
    salary_str = str(salary).ljust(SALARY_SIZE)
    return id_str + last_name_str + first_name_str + age_str + salary_str

def parse_record(record_str):
    if len(record_str) != RECORD_SIZE: return None
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
# PASO 3: ESCRITURA INICIAL (Bulk Insert para poblar el archivo)
# ============================================================================

def bulk_insert_in_pages(records_data):
    """Crea el archivo paginado inicial."""
    with open(FILE_NAME, "w") as file:
        current_page_data = ""
        records_in_current_page = 0
        current_page_id = 0
        for data in records_data:
            slot_id = records_in_current_page
            print(f"  RID asignado: ({current_page_id}, {slot_id}) -> {data[2]} {data[1]}")
            current_page_data += format_record(*data)
            records_in_current_page += 1
            if records_in_current_page == RECORDS_PER_PAGE:
                current_page_data += "-" * (PAGE_SIZE - len(current_page_data))
                file.write(current_page_data)
                current_page_data = ""
                records_in_current_page = 0
                current_page_id += 1
        if records_in_current_page > 0:
            current_page_data += "-" * (PAGE_SIZE - len(current_page_data))
            file.write(current_page_data)

# ============================================================================
# PASO 4: FREE SPACE MANAGEMENT (Borrado y Reciclaje)
# ============================================================================

def delete_record_and_link(page_id, slot_id):
    """
    Borra un registro y lo convierte en un nodo de la Free List.
    Escribe un puntero al siguiente hueco dentro de los 50 bytes disponibles.
    """
    global free_list_head
    offset = (page_id * PAGE_SIZE) + (slot_id * RECORD_SIZE)

    # 1. Construimos el puntero (Lapida inteligente)
    if free_list_head is None:
        next_ptr = "*FREE*NONE"
    else:
        next_page, next_slot = free_list_head
        next_ptr = f"*FREE*P{next_page:04d}S{next_slot:04d}"

    # Rellenamos con puntos para completar los 50 bytes
    tombstone = next_ptr.ljust(RECORD_SIZE, ".")

    # 2. Escribimos la lapida en el disco
    with open(FILE_NAME, "r+") as file:
        file.seek(offset)
        file.write(tombstone)

    # 3. Actualizamos la cabeza de la lista en RAM
    free_list_head = (page_id, slot_id)
    print(f"  [DELETE] RID({page_id}, {slot_id}) -> lapida escrita: '{next_ptr}'")
    print(f"           Free List head -> RID({page_id}, {slot_id})")

def insert_recycled_record(emp_id, last_name, first_name, age, salary):
    """
    Inserta un nuevo registro reutilizando un hueco si existe (O(1)).
    """
    global free_list_head

    if free_list_head is None:
        print("[INSERT] No hay espacio libre. Se requiere hacer Append (Omitido).")
        return False

    # 1. Vamos al hueco que nos indica la cabeza
    page_id, slot_id = free_list_head
    offset = (page_id * PAGE_SIZE) + (slot_id * RECORD_SIZE)

    with open(FILE_NAME, "r+") as file:
        file.seek(offset)
        tombstone = file.read(RECORD_SIZE)

        # 2. Parseamos la lapida para saber cual es el siguiente hueco
        if "NONE" in tombstone:
            free_list_head = None
        else:
            p_str = tombstone[7:11]
            s_str = tombstone[12:16]
            free_list_head = (int(p_str), int(s_str))

        # 3. Sobrescribimos el hueco con los datos del nuevo empleado
        file.seek(offset)
        new_record_str = format_record(emp_id, last_name, first_name, age, salary)
        file.write(new_record_str)

    print(f"  [INSERT] {first_name} {last_name} -> reciclado en RID({page_id}, {slot_id})")
    if free_list_head:
        print(f"           Free List head -> RID{free_list_head} (siguiente hueco disponible)")
    else:
        print(f"           Free List vacia -- proximo INSERT expandira el archivo")
    return True

# ============================================================================
# BLOQUE PRINCIPAL (Pruebas de Escritorio)
# ============================================================================
if __name__ == "__main__":
    print("--- Laboratorio: Free List en Heap Files ---")
    print(f"Tamano de Pagina  : {PAGE_SIZE} bytes")
    print(f"Tamano de Registro: {RECORD_SIZE} bytes")
    print(f"Registros por Pagina: {RECORDS_PER_PAGE}")
    print()

    simpsons_data = [
        (123, "Simpson",  "Homer",   31, "$400"),  # Page 0, Slot 0
        (443, "Simpson",  "Marge",   32, "$140"),  # Page 0, Slot 1
        (244, "Flanders", "Ned",     55, "$300"),  # Page 1, Slot 0
        (134, "Skinner",  "Seymour", 55, "$400")   # Page 1, Slot 1
    ]

    print("--- Poblando el Heap File ---")
    bulk_insert_in_pages(simpsons_data)
    print("Base de datos inicial creada.\n")

    print("--- 1. Generando huecos (Deletes) ---")
    # Borramos a Marge (Primera en salir -> fondo de la pila LIFO)
    delete_record_and_link(0, 1)
    # Borramos a Ned  (Ultimo en salir  -> cabeza de la pila LIFO)
    delete_record_and_link(1, 0)
    print()
    print(">>> Inspecciona 'my_database_v3.dat' ahora para ver las lapidas.")
    print(">>> Busca cadenas como '*FREE*P0000S0001' o '*FREE*NONE' en los slots borrados.")
    print()

    # --- INICIO BLOQUE RECICLAJE (comentar hasta FIN BLOQUE para la Parte A) ---
    print("--- 2. Insertando nuevos registros (Reciclaje) ---")
    print("Insertando a Lisa Simpson...")
    insert_recycled_record(999, "Simpson", "Lisa", 8, "$10")

    print()
    print("Insertando a Milhouse Van Houten...")
    insert_recycled_record(888, "Van Houten", "Milhouse", 10, "$5")
    # --- FIN BLOQUE RECICLAJE ---

    print("\n--- Fin del Laboratorio ---")