Aquí tienes el enunciado del proyecto reescrito y adaptado para el uso de archivos CSV, listo para copiar y pegar en tu archivo README.md o en la guía del laboratorio.

Markdown
# Laboratorio: Implementación de Persistencia de Datos (Mini-SIA)

## 1. Contexto del Problema

En el desarrollo de software, la gestión de datos es fundamental. Antes de la existencia de los Sistemas Gestores de Bases de Datos (DBMS) modernos como PostgreSQL o MySQL, los sistemas almacenaban información en "archivos planos" (flat files).

Este proyecto busca simular un **Sistema de Información Académica (SIA)** básico utilizando archivos **CSV** y **Python**. El objetivo es comprender los desafíos de la persistencia manual: integridad referencial, consistencia de datos y complejidad algorítmica al relacionar información.

## 2. Objetivos de Aprendizaje
* Manipulación de archivos de texto (Lectura/Escritura) en Python.
* **Parsing manual:** Conversión de tipos de datos (String a Int/Float) desde CSV.
* Implementación lógica de operaciones **CRUD** (Create, Read, Update, Delete).
* Simulación algorítmica de **JOINs** (relacionar datos de dos archivos distintos).
* Validación manual de integridad referencial (Foreign Keys).

## 3. Estructura de Datos (Archivos CSV)
El sistema se basará en tres archivos CSV ubicados en la carpeta `/data`.

### A. `estudiantes.csv` (Entidad Maestra)
Almacena la información de los alumnos.
* **Columnas:** `id, nombre, email, carrera, semestre`
* **Llave Primaria:** `id`
* **Tipos de datos esperados:** `id` (int), `semestre` (int), resto (string).

### B. `cursos.csv` (Entidad Maestra)
Almacena la oferta académica disponible.
* **Columnas:** `codigo, nombre, creditos, profesor`
* **Llave Primaria:** `codigo`
* **Tipos de datos esperados:** `creditos` (int), resto (string).

### C. `matriculas.csv` (Entidad Relacional)
Vincula estudiantes con cursos (Relación Muchos a Muchos).
* **Columnas:** `id_matricula, estudiante_id, curso_codigo, semestre, nota_final`
* **Llave Primaria:** `id_matricula`
* **Llaves Foráneas:**
    * `estudiante_id` -> debe existir en `estudiantes.csv`
    * `curso_codigo` -> debe existir en `cursos.csv`
* **Nota:** `nota_final` puede estar vacía (null) si el curso no ha terminado.

## 4. Requerimientos Funcionales

### Módulo 1: Gestión de Archivos (`db_manager.py`)
Desarrollar una clase que permita:
1.  Leer un archivo CSV y retornarlo como una lista de diccionarios.
2.  **Conversión de Tipos:** Detectar y convertir números (que el CSV lee como strings `"100"`) a sus tipos reales (`100` o `4.5`).
3.  Escribir una lista de diccionarios de vuelta al archivo CSV (guardar cambios).

### Módulo 2: Lógica de Negocio (`main.py`)
Implementar las siguientes funcionalidades en la consola:

1.  **Matricular Estudiante:**
    * Solicitar ID de estudiante y Código de curso.
    * **Validación (Integridad):** Verificar que ambos existan en sus respectivos archivos maestros *antes* de guardar.
    * Generar un nuevo registro en `matriculas.csv`.

2.  **Reporte de Notas (Simulación de JOIN):**
    * Dado un ID de estudiante, listar sus materias matriculadas.
    * El sistema debe mostrar el *Nombre de la Materia* (obtenido de `cursos.csv`), no solo el código.
    * Calcular el promedio acumulado del estudiante (ignorando materias sin nota).

## 5. Estructura del Proyecto Sugerida

```text
proyecto_sia/
│
├── data/
│   ├── estudiantes.csv
│   ├── cursos.csv
│   └── matriculas.csv
│
├── src/
│   ├── db_manager.py   # Lógica de lectura/escritura CSV
│   └── main.py         # Menú e interacción con usuario
│
└── README.md
```

### 6. Preguntas de Reflexión (Para el informe)

* ¿Qué sucede si borro un estudiante de estudiantes.csv pero dejo sus registros en matriculas.csv?
* ¿Cuál es la complejidad computacional ($O(?)$) de buscar el nombre de un curso para cada matrícula de un estudiante?
* ¿Cómo se maneja el problema de que nota_final sea un string vacío `""` al calcular el promedio?