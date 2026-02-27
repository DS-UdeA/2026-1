import sys
import os

# --- PREPARACIÓN DEL ENTORNO DE IMPORTACIÓN ---

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
src_path = os.path.join(project_root, 'src')
sys.path.append(src_path)

# --- IMPORTS ---
# Nota importante: Como agregamos 'src' al path, ahora importamos DIRECTAMENTE
# sin poner 'src.' al principio.
from db_manager import FileManager
from main import get_student_name, get_course_data

def run_tests():
    """
    Ejecuta una batería de pruebas automáticas sobre la lógica del sistema.
    No requiere interacción del usuario.
    """
    print("\n" + "="*60)
    print(" --- INICIANDO SUITE DE PRUEBAS (Backend Logic Test) ---")
    print(f" Ejecutando desde: {current_dir}")
    print("="*60)

    # Instanciamos el gestor (Automáticamente buscará data/ en la raíz)
    db = FileManager()

    # --- TEST 1: Verificar Integridad de Datos Maestros ---
    print("\n[TEST 1] Integridad de Archivos Maestros (Estudiantes/Cursos)")
    
    students = db.read_all("estudiantes")
    courses = db.read_all("cursos")

    if not students:
        print("   [X] FAIL: No se encontraron estudiantes. Revise data/estudiantes.csv")
        return
    if not courses:
        print("   [X] FAIL: No se encontraron cursos. Revise data/cursos.csv")
        return

    # Probamos buscar un dato conocido (Hardcoded para el test)
    # Asumimos que el ID 1001 existe en el CSV inicial
    test_id = 1001
    name = get_student_name(test_id, students)
    
    if name:
        print(f"   [OK] PASS: Búsqueda correcta. ID {test_id} corresponde a '{name}'.")
    else:
        print(f"   [X] FAIL: No se encontró al estudiante {test_id}.")

    # --- TEST 2: Simulación de Matrícula (Escritura) ---
    print("\n[TEST 2] Persistencia de Datos (Matricular)")
    
    # Datos de prueba
    test_course = "ING101"
    test_semester = "TEST-2025"
    
    # Validamos que el curso exista antes de intentar
    course_obj = get_course_data(test_course, courses)
    if not course_obj:
        print(f"    [X] SKIP: No se puede probar matrícula, el curso {test_course} no existe.")
        return

    new_enrollment = {
        "id_matricula": 9999, # ID alto para diferenciarlo
        "estudiante_id": test_id,
        "curso_codigo": test_course,
        "semestre": test_semester,
        "nota_final": 5.0
    }

    if db.append_record("matriculas", new_enrollment):
        print(f"   [OK] PASS: El sistema reportó éxito al guardar la matrícula.")
    else:
        print("   [X] FAIL: El sistema falló al escribir en el archivo.")

    # --- TEST 3: Verificación de Lectura (Read-After-Write) ---
    print("\n[TEST 3] Consistencia (Leer lo que acabamos de escribir)")
    
    # Recargamos desde el disco para asegurar que no está solo en memoria
    enrollments_reloaded = db.read_all("matriculas")
    
    found = False
    for record in enrollments_reloaded:
        # Convertimos a str para comparar seguramente
        if str(record['id_matricula']) == "9999" and record['semestre'] == test_semester:
            found = True
            break
            
    if found:
        print("   [OK] PASS: El registro se recuperó exitosamente del disco.")
    else:
        print("   [X] CRITICAL FAIL: El registro se perdió. Problema de persistencia.")

    print("\n" + "="*60)
    print(" --- FIN DE LAS PRUEBAS ---")

if __name__ == "__main__":
    run_tests()