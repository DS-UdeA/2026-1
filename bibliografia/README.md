# Referencias y Recursos Académicos del Curso

Este documento reúne la bibliografía oficial, los materiales de estudio y las herramientas digitales esenciales para su proceso de aprendizaje en **Estructuras de Datos y Persistencia**.

---

## Fundamentación Teórica

*Lecturas obligatorias para comprender los conceptos clave, independientemente del lenguaje de programación que decida utilizar.*

1.  **Petrov, A. (2019).** *Database Internals: A Deep Dive into How Distributed Data Systems Work*. O'Reilly Media.
    * **Enfoque:** Explica cómo funcionan los motores de base de datos modernos "bajo el capó".
2.  **Silberschatz, A., Korth, H. F., & Sudarshan, S. (2019).** *Database System Concepts* (7th Edition). McGraw-Hill.
    * **Enfoque:** El texto clásico para entender la teoría general de bases de datos.
3.  **Kleppmann, M. (2017).** *Designing Data-Intensive Applications*. O'Reilly Media.
    * **Enfoque:** Ideal para entender sistemas distribuidos y manejo de grandes volúmenes de datos.
4.  **Knuth, D. E. (1998).** *The Art of Computer Programming, Vol. 3: Sorting and Searching*. Addison-Wesley.
    * **Enfoque:** Referencia avanzada para el análisis matemático de algoritmos.
5.  **Folk, M. J., Zoellick, B., & Riccardi, G. (1998).** *File Structures: An Object-Oriented Approach with C++*. Addison-Wesley.
    * **Enfoque:** Fundamental para entender cómo gestionar archivos byte a byte en el disco.
6. **Ramakrishnan, R., & Gehrke, J. (2003).** *Database Management Systems* (3rd Edition). McGraw-Hill.
    * **Enfoque:** Conocido como el "Cow Book", es una referencia estándar por su claridad al explicar la implementación de índices (B+ Trees, Hashing) y el optimizador de consultas.

---

## Guías de Implementación (Por Lenguaje)

Seleccione los recursos correspondientes al lenguaje de programación.

### Java

* **Sciore, E. (2020).** *Database Design and Implementation: Second Edition*. Springer.
    * *Utilidad:* Guía paso a paso para construir un motor de base de datos en Java.
* **Goodrich, M. T., & Tamassia, R. (2014).** *Data Structures and Algorithms in Java*. Wiley.
    * *Utilidad:* Referencia para escribir código eficiente y limpio en Java.
* **Proyecto SimpleDB (MIT/Boston College)**
    * Código fuente de referencia académica.
    * [🔗 Ver Repositorio en GitHub](https://github.com/MIT-DB-Class/simple-db-hw)
* **Data Structures & Algorithm Analysis - Clifford A. Shaffer**
  * [🌐 Sitio Web](https://people.cs.vt.edu/~shaffer/Book/)
  
### Python

* **Goodrich, M. T., Tamassia, R., & Goldwasser, M. H. (2013).** *Data Structures and Algorithms in Python*. Wiley.
    * *Utilidad:* Algoritmos clásicos adaptados a la sintaxis de Python.
* **Documentación Oficial de Python 3**
    * Módulos de bajo nivel requeridos para el curso: `struct`, `io`, `mmap`.
    * [🔗 Ver Documentación](https://docs.python.org/3/)
* **DBDB: Dog Bed Database**
    * Tutorial sobre cómo crear una base de datos transaccional clave-valor desde cero.
    * [🔗 Leer Tutorial](https://aosabook.org/en/500L/dbdb-dog-bed-database.html)
* **BPlusTree (Implementación de Referencia)**
    * Código educativo de un Árbol B+ persistente en disco.
    * [🔗 Ver en GitHub](https://github.com/NicolasLM/bplustree)

---

## Clases en Video (Cursos Complementarios)
*Material audiovisual de universidades internacionales para reforzar lo visto en clase.*

### CMU 15-445/645: Database Systems (Carnegie Mellon)
* [🌐 Sitio Web del Curso](https://15445.courses.cs.cmu.edu/)
* [▶️ Canal de YouTube](https://www.youtube.com/playlist?list=PLSE8ODhjZXjbohkNBWQs_otTrBTrjyohi)

### Intro to Database Systems (Carnegie Mellon)
* [🌐 Sitio Web del Curso](https://15445.courses.cs.cmu.edu/spring2025/)

### CSE444: Database Systems Internals
* [🌐 Sitio Web del Curso](https://courses.cs.washington.edu/courses/cse444/)

### CS186: Introduction to Database Systems (UC Berkeley)
* [🌐 Sitio Web del Curso](https://cs186berkeley.net/)
* [▶️ Canal de YouTube](https://www.youtube.com/@cs186berkeley)

### Data Management and Data Systems
* [🌐 Sitio Web del Curso](https://cs145-fa20.github.io/)

### Intro to Big Data Systems
* [🌐 Sitio Web del Curso](https://cs145-bigdata.web.app/)

### Readings in Database Systems
* [🌐 Sitio Web del Curso](http://www.redbook.io/)

### Introduction to Databases - Columbia University
* [🌐 Sitio Web del Curso](https://w4111.github.io/)

### CS50's Introduction to Databases with SQL
* [🌐 Sitio Web del Curso](https://cs50.harvard.edu/sql/)

### CSE444: Database Systems Internals
* [🌐 Sitio Web del Curso](https://courses.cs.washington.edu/courses/cse444/)

---

## Bases de datos


A continuación se listan algunos sistemas de bases de datos académicos utilizados en cursos universitarios para estudiar la arquitectura interna de un DBMS.

### Java

- **SimpleDB (MIT)**  
  Implementación educativa usada en cursos del MIT para enseñar los componentes básicos de un DBMS.  
  - https://github.com/MIT-DB-Class/simple-db-hw
  - https://github.com/awelm/simpledb

---

### C++

- **BusTub (Carnegie Mellon University)**  
  DBMS educativo utilizado en el curso CMU 15-445/645 para estudiar almacenamiento, índices y ejecución de consultas.  
  https://github.com/cmu-db/bustub

- **Minibase**  
  Motor de base de datos educativo asociado al libro *Database Management Systems* de Ramakrishnan & Gehrke.  
  https://github.com/zhangzhiyi/minibase

---

### Python

- **SimpleDB (Python)**  
  Implementación ligera de un DBMS en Python diseñada para explorar conceptos básicos de almacenamiento y manejo de registros.  
  - https://github.com/coleifer/simpledb
  

- **TinyDB**  
  Base de datos ligera escrita en Python que almacena datos en archivos JSON, útil para estudiar bases de datos embebidas.  
  https://github.com/msiemens/tinydb

---

### Sistemas reales (para estudiar arquitectura)

- **SQLite**  
  Motor de base de datos embebido ampliamente utilizado y muy estudiado en cursos de bases de datos.  
  https://github.com/sqlite/sqlite

- **DuckDB**  
  Sistema analítico moderno diseñado para procesamiento eficiente de datos en columnas.  
  https://github.com/duckdb/duckdb

## Simuladores y Visualización
*Herramientas obligatorias para realizar pruebas de escritorio antes de programar.*

### Data Structure Visualizations (USFCA)

Permite ver paso a paso cómo se comportan las estructuras al insertar o borrar datos.
* [Ir a Algorithms](https://www.cs.usfca.edu/~galles/visualization/Algorithms.html)
  * [Árboles B-Tree](https://www.cs.usfca.edu/~galles/visualization/BTree.html)
  * [Árboles B+ Tree](https://www.cs.usfca.edu/~galles/visualization/BPlusTree.html)
  * [Hashing](https://www.cs.usfca.edu/~galles/visualization/OpenHash.html)

### VisuAlgo (National University of Singapore)
Muestra la ejecución del algoritmo visualmente junto con su pseudocódigo.
* [Ir a VisuAlgo.net](https://visualgo.net/en)