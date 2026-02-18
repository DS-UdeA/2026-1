# Clase 1

**Fecha**: 18/02/2026

## Resumen

En esta sección se introdujo el concepto de bases de datos y su relacion con los archivos. Además, de hablo, de los **sistemas basados en archivos** como antes del auge de los motores de bases de datos los aplicaciones gestionaban la información empleando archivos. Posteriormente se hablo sobre los **Motores de bases de datos (DBMS)**, sus ventajas y componentes principales. 

Como ejemplo de apoyo se introduce un caso de uso simple de sistemas basados en archivos, mas especificamente un **Sistema de Administración academica (SIA)**. Con este se pretende explicar los problemas a los que nos podemos enfrentar cuando almacenamos información en disco.

## Agenda

- [x] Conceptos teoricos (Diapositivas).
- [ ] Analisis y ejecución del ejemplo de clase.

## Recursos

### Diapositivas y manuscritos

A contiación se listan los recursos de esta clase:
- Diapositivas rayadas [[link]](clase1_annotated.pdf)
- Apuntes de la clase [[link]](DS_clase01_18-02-2026.pdf.pdf)

### Caso de aplicación: Mini SIA

El ejemplo se encuentra en el directorio [proyecto_sia](proyecto_sia/), sin embargo para ejecutarlo puede descargar el archivo comprimido y siguiendo las instrucciones dadas en el siguiente [link](proyecto_sia/README.md) ejecutarlo en su maquina.

En resumen, el proyecto contiene:
- **Base de datos (muy simplre)**: Archivos en formato CSV (cursos, estudiantes, matrículas):
  - [cursos.csv](proyecto_sia/data/cursos.csv)
  - [estudiantes.csv](proyecto_sia/data/estudiantes.csv)
  - [matriculas.csv](proyecto_sia/data/matriculas.csv)
- **Código fuente**: Backend para gestión de la base de datos y lógica de la aplicación.
  - [db_manager.py](proyecto_sia/src/db_manager.py)
  - [main.py](proyecto_sia/src/main.py)
- **Pruebas unitarias**: Pruebas basica para garantizar el correcto funcionamiento del backend.
  - [test_backend.py](proyecto_sia/tests/test_backend.py)
