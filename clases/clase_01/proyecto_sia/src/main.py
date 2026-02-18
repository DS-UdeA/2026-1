import os
from db_manager import FileManager

def get_student_name(student_id, students_list):
    """
    Simula una búsqueda simple: SELECT nombre FROM estudiantes WHERE id = ...
    Complejidad: O(n) - Búsqueda Lineal (Ineficiente comparado con un Index)
    """
    for student in students_list:
        if str(student['id']) == str(student_id):
            return student['nombre']
    return None

def get_course_data(course_code, courses_list):
    """
    Busca los detalles de un curso dado su código.
    """
    for course in courses_list:
        if course['codigo'] == course_code:
            return course
    return None

def enroll_student(db):
    """
    Caso de Uso: Matricular un estudiante.
    Conceptos: Validación de Foreign Keys (Integridad Referencial).
    """
    print("\n--- NUEVA MATRÍCULA ---")
    
    # 1. Solicitar datos de entrada
    student_id = input("Ingrese ID del Estudiante: ")
    course_code = input("Ingrese Código del Curso (ej. ING101): ")
    semester = input("Ingrese Semestre (ej. 2024-1): ")

    # 2. Cargar 'tablas' maestras para validar (Integridad Referencial)
    students = db.read_all("estudiantes")
    courses = db.read_all("cursos")

    # 3. Validar existencia (Simulación de Foreign Key Constraint)
    student_exists = get_student_name(student_id, students)
    course_data = get_course_data(course_code, courses)

    if not student_exists:
        print(f"ERROR: El estudiante con ID {student_id} no existe.")
        return

    if not course_data:
        print(f"ERROR: El curso {course_code} no existe.")
        return

    # 4. Generar ID autoincremental (Simulación de SEQUENCE o AUTO_INCREMENT)
    current_enrollments = db.read_all("matriculas")
    new_id = len(current_enrollments) + 1

    # 5. Crear el registro
    new_enrollment = {
        "id_matricula": new_id,
        "estudiante_id": int(student_id),
        "curso_codigo": course_code,
        "semestre": semester,
        "nota_final": ""  # Inicialmente vacío (NULL)
    }

    # 6. Guardar (Commit)
    if db.append_record("matriculas", new_enrollment):
        print(f"EXITO: {student_exists} matriculado en {course_data['nombre']}.")

def generate_report_card(db):
    """
    Caso de Uso: Reporte de Notas.
    Conceptos: INNER JOIN manual y Agregación (Promedio).
    """
    print("\n--- REPORTE DE NOTAS ---")
    student_id = input("Ingrese ID del Estudiante a consultar: ")

    # 1. Cargar datos (Full Table Scan)
    # En SQL esto sería optimizado por el motor, aquí lo hacemos manual.
    students = db.read_all("estudiantes")
    enrollments = db.read_all("matriculas")
    courses = db.read_all("cursos")

    # 2. Obtener datos del encabezado
    student_name = get_student_name(student_id, students)
    
    if not student_name:
        print("ERROR: Estudiante no encontrado.")
        return

    print(f"\n BOLETÍN DE CALIFICACIONES: {student_name} (ID: {student_id})")
    print("-" * 60)
    print(f"{'CÓDIGO':<10} | {'MATERIA':<25} | {'SEMESTRE':<10} | {'NOTA':<5}")
    print("-" * 60)

    # Variables para cálculo de promedio
    sum_grades = 0
    count_grades = 0

    # 3. Algoritmo de JOIN (Nested Loop Join manual)
    # Recorremos la tabla intermedia 'matriculas' filtrando por el estudiante
    found_records = False
    
    for record in enrollments:
        # Filtro: WHERE estudiante_id = ...
        if str(record['estudiante_id']) == str(student_id):
            found_records = True
            
            # JOIN con cursos: Buscamos el nombre de la materia
            course_info = get_course_data(record['curso_codigo'], courses)
            course_name = course_info['nombre'] if course_info else "Desconocido"

            # Formateo de nota (manejo de NULL)
            grade = record['nota_final']
            grade_display = str(grade) if grade is not None else "Pend."

            print(f"{record['curso_codigo']:<10} | {course_name:<25} | {record['semestre']:<10} | {grade_display:<5}")

            # Acumular para promedio (solo si tiene nota numérica)
            if grade is not None:
                sum_grades += grade
                count_grades += 1

    print("-" * 60)
    
    if not found_records:
        print("WARNING: Este estudiante no tiene matrículas registradas.")
    elif count_grades > 0:
        average = sum_grades / count_grades
        print(f"Promedio Acumulado: {average:.2f}")
    else:
        print("Promedio: N/A (Sin notas registradas)")

def main():
    # Instanciar el gestor de base de datos
    db = FileManager()

    while True:
        print("\n" + "="*40)
        print("   SISTEMA DE GESTIÓN ACADÉMICA (CSV)   ")
        print("="*40)
        print("1. Ver Estudiantes")
        print("2. Matricular Estudiante (INSERT + FK)")
        print("3. Ver Reporte de Notas (JOIN)")
        print("4. Salir")
        
        option = input("\nSeleccione una opción: ")

        if option == "1":
            students = db.read_all("estudiantes")
            print("\n--- LISTA DE ESTUDIANTES ---")
            for s in students:
                print(f"{s['id']}: {s['nombre']} ({s['carrera']})")
                
        elif option == "2":
            enroll_student(db)
            
        elif option == "3":
            generate_report_card(db)
            
        elif option == "4":
            print("Saliendo del sistema...")
            break
        else:
            print("Opción no válida.")

if __name__ == "__main__":
    main()