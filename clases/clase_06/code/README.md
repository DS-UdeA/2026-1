![Built with AI](https://img.shields.io/badge/Built%20with-AI-blue.svg)

# Índices Ordenados — Acceso Eficiente a Datos en Disco

* **Laboratorio de Estructuras de Datos · Universidad de Antioquia**
* **Módulos:** `index_utils.py` · `dense_index.py` · `sparse_index.py` · `clustering_index.py` · `secondary_index.py` · `multilevel_index.py` · `cost_comparison.py`
* **Prerrequisito recomendado:** Haber revisado las entregas de Heap Files (v5–v7) para tener contexto sobre cómo se almacenan los registros en disco.

---

> [!warning]
> Este material es un **apoyo al contenido de las diapositivas**, no un reemplazo. Se recomienda revisar primero las láminas de la Clase 6 (Indexación) antes de ejecutar los scripts, ya que el código implementa directamente los conceptos allí presentados.

---

## Tabla de Contenido

- [Índices Ordenados — Acceso Eficiente a Datos en Disco](#índices-ordenados--acceso-eficiente-a-datos-en-disco)
  - [Tabla de Contenido](#tabla-de-contenido)
  - [0. Conceptos Previos: Búsqueda Binaria y el módulo `bisect`](#0-conceptos-previos-búsqueda-binaria-y-el-módulo-bisect)
    - [0.1 ¿Qué es la búsqueda binaria y por qué importa en indexación?](#01-qué-es-la-búsqueda-binaria-y-por-qué-importa-en-indexación)
    - [0.2 El módulo `bisect` de Python](#02-el-módulo-bisect-de-python)
    - [0.3 Comparación con Java (`Collections.binarySearch`)](#03-comparación-con-java-collectionsbinarysearch)
    - [0.4 Ejemplo práctico sobre `bisect`](#04-ejemplo-práctico-sobre-bisect)
    - [0.5 Recursos para profundizar](#05-recursos-para-profundizar)
  - [1. Punto de Partida: ¿Por qué esta entrega existe?](#1-punto-de-partida-por-qué-esta-entrega-existe)
  - [2. Repaso Teórico](#2-repaso-teórico)
    - [2.1 Jerarquía de almacenamiento y capas del DBMS](#21-jerarquía-de-almacenamiento-y-capas-del-dbms)
    - [2.2 Organización de archivos: Heap, Sorted, Hash](#22-organización-de-archivos-heap-sorted-hash)
    - [2.3 Conceptos básicos de indexación](#23-conceptos-básicos-de-indexación)
    - [2.4 La tabla `instructor` de Silberschatz](#24-la-tabla-instructor-de-silberschatz)
    - [2.5 Densidad del índice](#25-densidad-del-índice)
      - [Índice denso (Dense index)](#índice-denso-dense-index)
      - [Índice disperso (Sparse index)](#índice-disperso-sparse-index)
      - [Trade-off: ¿cuándo usar cada uno?](#trade-off-cuándo-usar-cada-uno)
    - [2.6 Agrupamiento del índice](#26-agrupamiento-del-índice)
      - [Índice de agrupamiento (Clustering index)](#índice-de-agrupamiento-clustering-index)
      - [Índice secundario (Secondary index)](#índice-secundario-secondary-index)
      - [Comparación: clustering vs. secondary](#comparación-clustering-vs-secondary)
    - [2.7 Índice multinivel (Multilevel index)](#27-índice-multinivel-multilevel-index)
    - [2.8 Actualización de índices](#28-actualización-de-índices)
  - [3. Descripción del Módulo](#3-descripción-del-módulo)
    - [3.1 Qué simula este código y qué no](#31-qué-simula-este-código-y-qué-no)
    - [3.2 Organización de archivos](#32-organización-de-archivos)
    - [3.3 Clases y funciones principales](#33-clases-y-funciones-principales)
    - [3.4 Diagrama de clases](#34-diagrama-de-clases)
  - [4. Guía de Ejecución y Validación](#4-guía-de-ejecución-y-validación)
    - [4.1 Preparación del entorno](#41-preparación-del-entorno)
    - [4.2 Fase 1 — Índice denso sobre ID (`dense_index.py`)](#42-fase-1--índice-denso-sobre-id-dense_indexpy)
      - [Punto 1 — Una entrada por cada registro de la tabla](#punto-1--una-entrada-por-cada-registro-de-la-tabla)
      - [Punto 2 — La búsqueda binaria reduce drásticamente los I/Os](#punto-2--la-búsqueda-binaria-reduce-drásticamente-los-ios)
      - [Punto 3 — El índice denso es mucho más rápido que el full scan](#punto-3--el-índice-denso-es-mucho-más-rápido-que-el-full-scan)
    - [4.3 Fase 2 — Índice disperso sobre ID (`sparse_index.py`)](#43-fase-2--índice-disperso-sobre-id-sparse_indexpy)
      - [Punto 4 — Una entrada por bloque, no por registro](#punto-4--una-entrada-por-bloque-no-por-registro)
      - [Punto 5 — La búsqueda usa floor lookup más scan lineal](#punto-5--la-búsqueda-usa-floor-lookup-más-scan-lineal)
      - [Punto 6 — El disperso ocupa 5x menos espacio que el denso](#punto-6--el-disperso-ocupa-5x-menos-espacio-que-el-denso)
    - [4.4 Fase 3 — Clustering index sobre dept\_name (`clustering_index.py`)](#44-fase-3--clustering-index-sobre-dept_name-clustering_indexpy)
      - [Punto 7 — El orden del índice coincide con el orden físico](#punto-7--el-orden-del-índice-coincide-con-el-orden-físico)
      - [Punto 8 — Consulta de rango: bloques consecutivos = mínimo I/O](#punto-8--consulta-de-rango-bloques-consecutivos--mínimo-io)
    - [4.5 Fase 4 — Secondary index sobre salary (`secondary_index.py`)](#45-fase-4--secondary-index-sobre-salary-secondary_indexpy)
      - [Punto 9 — El orden del índice difiere del orden físico](#punto-9--el-orden-del-índice-difiere-del-orden-físico)
      - [Punto 10 — Baja selectividad: el índice secundario es más lento que el full scan](#punto-10--baja-selectividad-el-índice-secundario-es-más-lento-que-el-full-scan)
    - [4.6 Fase 5 — Índice multinivel (`multilevel_index.py`)](#46-fase-5--índice-multinivel-multilevel_indexpy)
      - [Punto 11 — El outer index en memoria elimina I/Os de búsqueda](#punto-11--el-outer-index-en-memoria-elimina-ios-de-búsqueda)
      - [Punto 12 — Costo total: exactamente 2 I/Os independiente del tamaño](#punto-12--costo-total-exactamente-2-ios-independiente-del-tamaño)
  - [5. Comparativa Final de Costos I/O (`cost_comparison.py`)](#5-comparativa-final-de-costos-io-cost_comparisonpy)
  - [6. Referencias y Material de Profundización](#6-referencias-y-material-de-profundización)

---

## 0. Conceptos Previos: Búsqueda Binaria y el módulo `bisect`

A diferencia de las entregas anteriores (v5–v7), estos scripts no manipulan bytes binarios con `struct`. El concepto técnico clave aquí es más simple pero igual de fundamental: la **búsqueda binaria** como mecanismo central para localizar claves en un índice ordenado de forma eficiente.

---

### 0.1 ¿Qué es la búsqueda binaria y por qué importa en indexación?

Un índice ordenado es esencialmente una lista de pares `(search_key, block_number)` mantenida en orden por `search_key`. Cuando el motor necesita localizar un valor específico, tiene dos opciones:

- **Búsqueda lineal:** revisar entrada por entrada desde el inicio — O(n) pasos.
- **Búsqueda binaria:** dividir repetidamente la lista por la mitad — O(log₂ n) pasos.

<!-- 🖼️ PENDIENTE: diagrama comparativo búsqueda lineal vs binaria sobre una lista de 12 elementos -->
<!-- Ruta sugerida: ./images/diagram_linear_vs_binary_search.svg -->

La diferencia es dramática a escala. Para un índice de 10.000 bloques (caso del índice denso con 1M de registros), la búsqueda lineal requeriría hasta 10.000 comparaciones; la búsqueda binaria necesita como máximo ⌈log₂(10.000)⌉ = **14**. Eso se traduce directamente en 14 I/Os de disco vs. 10.000 — la búsqueda binaria es la razón por la que los índices funcionan.

> [!note]
> La fórmula que usan las diapositivas para calcular el costo de búsqueda en un índice es exactamente esta: **I/O_search = ⌈log₂(B_índice)⌉**, donde B_índice es el número de bloques del índice. Todos los ejemplos numéricos de la Clase 6 usan esta fórmula.

---

### 0.2 El módulo `bisect` de Python

`bisect` es el módulo de la biblioteca estándar de Python que implementa búsqueda binaria sobre listas ordenadas. Sus dos funciones principales son:

| Función | Comportamiento | Uso en este laboratorio |
|---|---|---|
| `bisect.bisect_left(a, x)` | Retorna la posición más a la izquierda donde insertar `x` manteniendo el orden. Si `x` ya existe, retorna su posición. | Búsqueda exacta (`DenseIndex.lookup`) |
| `bisect.bisect_right(a, x)` | Retorna la posición más a la derecha donde insertar `x`. Si `x` ya existe, retorna la posición *después* de él. | Límite superior en búsquedas de rango |

La combinación de ambas permite implementar todos los patrones de acceso que aparecen en las diapositivas:

| Patrón de acceso | Implementación con `bisect` |
|---|---|
| Búsqueda exacta (`WHERE ID = k`) | `bisect_left` para encontrar la posición, luego verificar si `a[pos] == k` |
| Floor lookup (`mayor clave ≤ k`) | `bisect_right(a, k) - 1` — usado en `SparseIndex` y `ClusteringIndex` |
| Rango `[lo, hi]` | `bisect_left(a, lo)` como inicio, `bisect_right(a, hi)` como fin |

---

### 0.3 Comparación con Java (`Collections.binarySearch`)

Si ha usado `java.util.Collections.binarySearch()` en Java, `bisect` de Python es conceptualmente equivalente pero más flexible:

| Operación | Java | Python (`bisect`) |
|---|---|---|
| Búsqueda exacta en lista ordenada | `Collections.binarySearch(list, key)` | `bisect.bisect_left(a, key)` + verificación |
| Insertar manteniendo orden | `list.add(pos, value)` tras `binarySearch` | `bisect.insort(a, value)` |
| Límite inferior de un rango | No disponible directamente | `bisect.bisect_left(a, lo)` |
| Límite superior de un rango | No disponible directamente | `bisect.bisect_right(a, hi)` |

> [!note]
> `Collections.binarySearch` en Java retorna un índice negativo si el elemento no existe. `bisect_left` siempre retorna una posición válida (dónde estaría el elemento), lo que resulta más natural para construir índices de base de datos.

---

### 0.4 Ejemplo práctico sobre `bisect`

```python
import bisect

# Imagine this is our sparse index: [(min_key_in_block, block_number)]
index = [(10101, 0), (33456, 1), (83821, 2)]
keys  = [entry[0] for entry in index]   # [10101, 33456, 83821]

# Floor lookup: find the block that MAY contain ID = 45565
# bisect_right returns the insertion point AFTER any existing 45565
# subtract 1 → the last entry with key ≤ 45565
pos   = bisect.bisect_right(keys, 45565) - 1   # pos = 1
block = index[pos][1]                           # block = 1
print(f"ID=45565 → scan Block {block}")         # Block 1 ✓

# Range lookup: all entries with key in [22222, 76766]
lo = bisect.bisect_left(keys, 22222)    # lo = 1 (first key ≥ 22222)
hi = bisect.bisect_right(keys, 76766)   # hi = 2 (first key > 76766)
matching = index[lo:hi]                 # [(33456, 1)]
```

---

### 0.5 Recursos para profundizar

- **Python docs — `bisect`:** [https://docs.python.org/3/library/bisect.html](https://docs.python.org/3/library/bisect.html)
- **Visualización interactiva de búsqueda binaria:** [https://visualgo.net/en/bst](https://visualgo.net/en/bst)
- **CS186 Berkeley — Storage & Indexes:** [https://cs186berkeley.net/notes/note17/](https://cs186berkeley.net/notes/note17/)

---

## 1. Punto de Partida: ¿Por qué esta entrega existe?

Las entregas anteriores (v5–v7) resolvieron el problema de **cómo almacenar registros** en disco: formatos de longitud variable, slotted pages, compactación. Pero resolver el almacenamiento deja abierta una pregunta igual de importante: ¿cómo encontrar un registro específico una vez que está almacenado?

La respuesta más simple — recorrer el archivo completo desde el primer bloque hasta el último — se llama **full scan** o escaneo completo. Funciona, pero su costo es proporcional al tamaño del archivo. Las diapositivas de la Clase 6 plantean el caso de una tabla con 1.000.000 de registros almacenados en 200.000 bloques de disco:

```
T_full_scan = 200.000 bloques × 10 ms/bloque = 2.000.000 ms ≈ 33 minutos
```

Treinta y tres minutos para encontrar un solo registro es inaceptable en cualquier sistema real. Los **índices ordenados** son la solución: estructuras auxiliares que mapean un valor de clave de búsqueda directamente al bloque de disco donde se encuentran los registros con ese valor, reduciendo el costo de una búsqueda puntual a decenas de milisegundos.

<!-- 🖼️ PENDIENTE: diagrama motivacional — full scan vs index lookup -->
<!-- Ruta sugerida: ./images/diagram_fullscan_vs_index.svg -->

> [!note]
> Este módulo es **completamente independiente** de las entregas v5–v7. La capa de datos es una lista Python simple (`INSTRUCTOR_TABLE` en `index_utils.py`) para que el foco sea 100% en las estructuras de índice. En un DBMS real, el índice se construiría sobre un heap file con slotted pages como los implementados en v6–v7 — pero mezclar ambas capas en un solo script haría más difícil entender cualquiera de las dos.

---

## 2. Repaso Teórico

### 2.1 Jerarquía de almacenamiento y capas del DBMS

Un DBMS se organiza en capas funcionales que van desde el almacenamiento físico hasta la planificación de consultas. Los índices viven en la capa de **Access Methods**, que es la responsable de leer y escribir datos eficientemente desde las páginas almacenadas por capas inferiores.

<!-- 🖼️ PENDIENTE: diagrama de capas del DBMS con Access Methods resaltado -->
<!-- Sugerencia: usar directamente la diapositiva 8 de clase6.pdf -->
<!-- Ruta sugerida: ./images/diagram_dbms_layers.png -->

La indexación es el mecanismo fundamental de esta capa: permite acceder a los datos **sin recorrer el archivo completo**, respondiendo a la pregunta "¿en qué bloque de disco está el registro que busco?" antes de emitir una sola operación de I/O sobre el archivo de datos.

---

### 2.2 Organización de archivos: Heap, Sorted, Hash

Antes de hablar de índices, es útil recordar que los archivos de datos pueden estar organizados de tres maneras principales, cada una adecuada para patrones de acceso distintos:

**Archivos heap (Heap files):** los registros se insertan en cualquier posición con espacio disponible, sin orden garantizado. Son ideales cuando el acceso típico es un escaneo completo del archivo. Son los que implementamos en v5–v7.

**Archivos ordenados (Sorted files):** los registros están físicamente ordenados por una clave de búsqueda. Permiten búsquedas eficientes por esa clave y consultas de rango, pero las inserciones son costosas porque pueden requerir reorganización.

**Índices (Indexes):** estructuras de datos auxiliares — basadas en árboles o hashing — que aceleran las búsquedas sin modificar el orden físico del archivo de datos. Las actualizaciones son mucho más rápidas que en archivos ordenados.

---

### 2.3 Conceptos básicos de indexación

El **indexado** es una técnica que consiste en utilizar estructuras de datos auxiliares para permitir que un DBMS localice registros de forma eficiente sin tener que escanear toda una tabla en cada acceso.

Los tres conceptos centrales son:

- **Clave de búsqueda (Search Key):** atributo o conjunto de atributos sobre cuyos valores se construye el índice. No tiene que ser la clave primaria de la tabla; puede ser cualquier campo de interés para las consultas.
- **Archivo de índice (Index file):** archivo auxiliar que contiene las entradas del índice, ordenadas por la clave de búsqueda.
- **Entrada de índice (Index entry):** par `(search_key, data_reference)` donde la referencia apunta al bloque de disco que contiene los registros con ese valor de clave.

<!-- 🖼️ PENDIENTE: diagrama value → index → blocks → matching records -->
<!-- Sugerencia: usar directamente las diapositivas 11–13 de clase6.pdf -->
<!-- Ruta sugerida: ./images/diagram_index_concept.png -->

Un índice acelera las consultas pero agrega costo a las operaciones de escritura: toda inserción, eliminación o actualización sobre la tabla debe reflejarse también en todos sus índices. Este es el **trade-off** central que los diseñadores de bases de datos deben evaluar.

---

### 2.4 La tabla `instructor` de Silberschatz

Todos los ejemplos de código de este módulo usan la relación `instructor` que aparece en el libro de texto estándar del curso:

> Silberschatz, A., Korth, H. F., & Sudarshan, S. *Database System Concepts*, 7th ed. McGraw-Hill.

El esquema es `instructor(ID, name, dept_name, salary)`:

| ID | Name | Dept Name | Salary |
|---:|---|---|---:|
| 10101 | Srinivasan | Comp. Sci. | 65,000 |
| 12121 | Wu | Finance | 90,000 |
| 15151 | Mozart | Music | 40,000 |
| 22222 | Einstein | Physics | 95,000 |
| 32343 | El Said | History | 60,000 |
| 33456 | Gold | Physics | 87,000 |
| 45565 | Katz | Comp. Sci. | 75,000 |
| 58583 | Califieri | History | 62,000 |
| 76543 | Singh | Finance | 80,000 |
| 76766 | Crick | Biology | 72,000 |
| 83821 | Brandt | Comp. Sci. | 92,000 |
| 98345 | Kim | Elec. Eng. | 80,000 |

Esta es la misma tabla que se usa en las diapositivas de la Clase 6 para todos los ejemplos de índices ordenados (denso, disperso, clustering, secondary, multinivel). Usarla aquí permite que el estudiante reconozca los mismos datos en el código, en el README y en las slides.

En el código, la tabla se almacena como una lista de tuplas en `index_utils.py` y se importa en todos los demás módulos.

---

### 2.5 Densidad del índice

Cuando se construye un índice, una decisión fundamental es cuántas entradas tendrá. A esta característica se le denomina **densidad del índice**.

#### Índice denso (Dense index)

En un índice denso existe **una entrada por cada registro** del archivo de datos. Cada entrada contiene el valor de la clave y un puntero al bloque que contiene ese registro.

<!-- 🖼️ PENDIENTE: diagrama índice denso — una flecha por registro -->
<!-- Sugerencia: usar directamente la diapositiva 24 de clase6.pdf -->
<!-- Ruta sugerida: ./images/diagram_dense_index.png -->

Propiedades clave:
- Permite localizar **directamente** cualquier registro con una búsqueda binaria sobre el índice.
- Si la clave de búsqueda **no es única**, el índice mantiene una entrada por cada registro con ese valor — el acceso a los demás ocurre secuencialmente siguiendo los punteros del archivo.
- Ocupa **más espacio** que el disperso: tantas entradas como registros tenga la tabla.

#### Índice disperso (Sparse index)

En un índice disperso existe **una entrada por cada bloque** del archivo de datos, no por cada registro. La entrada almacena el valor de la clave mínima en ese bloque.

<!-- 🖼️ PENDIENTE: diagrama índice disperso — una flecha por bloque -->
<!-- Sugerencia: usar directamente la diapositiva 29 de clase6.pdf -->
<!-- Ruta sugerida: ./images/diagram_sparse_index.png -->

El proceso de búsqueda tiene dos pasos: primero se localiza la entrada con la **clave más grande ≤ clave buscada** (floor lookup), y luego se lee ese bloque y se escanea linealmente hasta encontrar el registro.

Propiedades clave:
- **Solo es aplicable** cuando el archivo está físicamente ordenado por la clave de búsqueda.
- Ocupa mucho **menos espacio**: tantas entradas como bloques tenga el archivo.
- Es ligeramente **más lento** por requerir el scan intra-bloque final.

#### Trade-off: ¿cuándo usar cada uno?

| | Índice denso | Índice disperso |
|---|---|---|
| **Entradas** | Una por registro | Una por bloque |
| **Velocidad de búsqueda** | Más rápido | Más lento |
| **Espacio ocupado** | Mayor | Menor |
| **Costo de actualización** | Mayor | Menor |
| **Requisito** | Ninguno | Archivo ordenado |
| **Uso típico** | Índices secundarios | Índices de agrupamiento |

La regla práctica del libro (Silberschatz): para un índice de agrupamiento (*clustered*) usar disperso con una entrada por bloque; para un índice no agrupado (*unclustered*) usar disperso sobre índice denso (multinivel).

---

### 2.6 Agrupamiento del índice

La segunda dimensión fundamental de los índices ordenados es su relación con el **orden físico del archivo**: ¿el orden de las entradas del índice coincide con el orden en que los registros están almacenados físicamente en disco?

#### Índice de agrupamiento (Clustering index)

En un índice de agrupamiento, el orden del índice **coincide con el orden físico** del archivo. También se llama índice primario (*primary index*).

<!-- 🖼️ PENDIENTE: diagrama clustering index — registros físicamente contiguos -->
<!-- Sugerencia: usar directamente la diapositiva 45 de clase6.pdf -->
<!-- Ruta sugerida: ./images/diagram_clustering_index.png -->

La ventaja principal aparece en las **consultas de rango**: como los registros con valores de clave contiguos están almacenados en bloques adyacentes, el motor puede leerlos en una única pasada secuencial — el patrón de acceso más eficiente posible en disco.

```sql
-- BETWEEN aprovecha el orden físico: el DBMS entra por 22222 y lee
-- bloques consecutivos hasta llegar al último registro ≤ 45565
SELECT * FROM instructor WHERE ID BETWEEN 22222 AND 45565;
```

#### Índice secundario (Secondary index)

En un índice secundario, el orden del índice es **diferente al orden físico** del archivo. También se llama índice no agrupado (*non-clustering index*).

<!-- 🖼️ PENDIENTE: diagrama secondary index — registros dispersos -->
<!-- Sugerencia: usar directamente la diapositiva 47 de clase6.pdf -->
<!-- Ruta sugerida: ./images/diagram_secondary_index.png -->

Los índices secundarios deben ser **densos**: como el archivo no está ordenado por esta clave, no hay garantía de que registros con el mismo valor estén juntos — se necesita un puntero por cada registro individual.

Cada puntero puede apuntar a un bloque diferente → cada acceso puede requerir una operación de disco independiente. Esto hace que los índices secundarios sean costosos cuando **muchos registros coinciden** con la consulta.

#### Comparación: clustering vs. secondary

| | Clustering index | Secondary index |
|---|---|---|
| **Orden** | Coincide con el archivo físico | Diferente al archivo físico |
| **Densidad** | Puede ser disperso | Debe ser denso |
| **Acceso a rangos** | Muy eficiente | Costoso |
| **Acceso por igualdad** | Eficiente | Eficiente (alta selectividad) |
| **Cantidad por tabla** | Solo uno | Puede haber varios |
| **Operaciones de disco** | Mínimas (registros contiguos) | Puede ser una por registro |

Una tabla solo puede tener **un índice de agrupamiento**, ya que los registros solo pueden estar físicamente ordenados de una manera. Sin embargo, puede tener **múltiples índices secundarios**.

---

### 2.7 Índice multinivel (Multilevel index)

Hasta ahora se ha asumido que el índice cabe completamente en memoria. Pero si el índice crece demasiado, la búsqueda binaria sobre él mismo requiere múltiples I/Os de disco.

La solución es aplicar el mismo principio de indexación **sobre el propio índice**: construir un índice sobre el índice. A esta estructura se le denomina **índice multinivel**.

<!-- 🖼️ PENDIENTE: diagrama outer index → inner index → data -->
<!-- Sugerencia: usar directamente la diapositiva 63 de clase6.pdf -->
<!-- Ruta sugerida: ./images/diagram_multilevel_index.png -->

Se organiza en dos capas:
- **Índice interno (inner index):** el archivo de índice básico, almacenado en disco. Puede ser un índice denso completo.
- **Índice externo (outer index):** un índice disperso construido sobre los **bloques** del índice interno. Suficientemente pequeño para mantenerse en memoria principal.

Cuando el outer index cabe en memoria, buscarlo cuesta **0 I/Os de disco**. Solo se necesita un I/O para leer el bloque del inner index relevante, y otro para leer el bloque de datos: total **2 I/Os** independientemente del tamaño del dataset.

Este principio de construir índices sobre índices es exactamente la idea detrás de los **árboles B⁺**, que lo generalizan de forma dinámica y balanceada.

---

### 2.8 Actualización de índices

Sin importar el tipo de índice, los índices deben actualizarse siempre que se inserte, modifique o elimine un registro. Una actualización de datos se modela como: eliminación del registro antiguo + inserción del nuevo valor, lo que significa que solo es necesario definir las operaciones de inserción y eliminación sobre el índice.

**Eliminación en índice denso:** si el registro eliminado era el único con ese valor de clave, se elimina la entrada del índice. Si existían más registros con esa clave, se elimina el puntero al registro borrado de la entrada existente.

**Eliminación en índice disperso:** si el índice no contiene una entrada para la clave del registro eliminado, no hay nada que hacer. Si sí la contiene, se actualiza la entrada para apuntar al siguiente registro válido en el bloque.

**Inserción en índice denso:** si la clave no existe en el índice, se inserta una nueva entrada en la posición correcta. Si ya existe, se agrega un puntero al nuevo registro.

**Inserción en índice disperso:** solo se emite una nueva entrada si se crea un nuevo bloque (el nuevo registro es el primero de ese bloque) o si el nuevo registro tiene el menor valor de clave en su bloque.

---

## 3. Descripción del Módulo

### 3.1 Qué simula este código y qué no

Este módulo simula la **capa de índice** de un DBMS ordenado, con foco total en las estructuras de acceso y su costo I/O.

**Lo que sí simula:**
- Construcción de índices densos, dispersos, clustering, secondary y multinivel.
- Operaciones de lookup puntual y de rango.
- Modelo de costo I/O a dos escalas: demo (12 registros) y textbook (1M registros).
- Los números de I/O y tiempo coinciden exactamente con los ejemplos 1–5 de las diapositivas.

**Lo que NO simula:**
- Escritura/lectura de bytes binarios a disco (eso lo hacen v6–v7).
- Gestión de páginas (slotted pages, buffer pool).
- Operaciones de actualización del índice ante inserciones/eliminaciones.

> [!note]
> En un DBMS real, la capa de índice se construye sobre un heap file con slotted pages como las implementadas en v6–v7. Aquí la capa de datos es una lista Python simple para que el estudiante pueda concentrarse 100% en entender las estructuras de índice sin distracciones de bajo nivel.

---

### 3.2 Organización de archivos

```
indexes/
├── index_utils.py          # tabla instructor + constantes + helpers compartidos
├── dense_index.py          # Phase 1: DenseIndex
├── sparse_index.py         # Phase 2: SparseIndex
├── clustering_index.py     # Phase 3: ClusteringIndex
├── secondary_index.py      # Phase 4: SecondaryIndex
├── multilevel_index.py     # Phase 5: MultilevelIndex
└── cost_comparison.py      # tabla resumen final — importa todos los módulos
```

Todos los módulos importan de `index_utils.py`. El orden recomendado de ejecución es `index_utils` → `dense` → `sparse` → `clustering` → `secondary` → `multilevel` → `cost_comparison`.

---

### 3.3 Clases y funciones principales

**`index_utils.py` — Utilidades compartidas**

| Función / Constante | Descripción |
|---|---|
| `INSTRUCTOR_TABLE` | Lista de 12 tuplas con la tabla `instructor` de Silberschatz |
| `block_of(record_index)` | Retorna el número de bloque que contiene el registro en la posición dada |
| `binary_search_ios(n_blocks)` | Retorna ⌈log₂(n_blocks)⌉ — I/Os para búsqueda binaria |
| `io_cost_ms(n_ios)` | Convierte número de I/Os a milisegundos |
| `full_scan_cost(n_blocks)` | Retorna costo de un escaneo completo como dict |
| `print_section(title)` | Imprime separador de sección con título |
| `print_index_entries(entries, label)` | Imprime tabla de entradas del índice |
| `print_cost_table(rows)` | Imprime tabla comparativa de costos I/O |
| `print_data_file(records, ordered_by)` | Imprime layout del archivo de datos por bloques |

**`dense_index.py` — `DenseIndex`**

| Método | Descripción |
|---|---|
| `__init__(records, key_field)` | Construye el índice: una entrada `(key, block)` por registro |
| `lookup(key)` | Búsqueda exacta — retorna número de bloque o `None` |
| `range_lookup(lo, hi)` | Retorna lista de bloques con registros en el rango `[lo, hi]` |
| `io_cost(n_records)` | Retorna dict con desglose de I/Os para una búsqueda puntual |

**`sparse_index.py` — `SparseIndex`**

| Método | Descripción |
|---|---|
| `__init__(records, key_field)` | Construye el índice: una entrada `(min_key, block)` por bloque |
| `lookup(key)` | Floor lookup — retorna bloque a escanear linealmente |
| `io_cost(n_blocks)` | Retorna dict con desglose de I/Os para una búsqueda puntual |

**`clustering_index.py` — `ClusteringIndex`**

| Método | Descripción |
|---|---|
| `__init__(records, key_field)` | Construye el índice: una entrada por valor único de clave |
| `lookup(key)` | Retorna primer bloque con registros de ese valor de clave |
| `range_lookup(lo, hi)` | Retorna lista de bloques contiguos para el rango `[lo, hi]` |
| `range_io_cost(lo, hi, n_records_per_key)` | Retorna dict con costo I/O de una consulta de rango |

**`secondary_index.py` — `SecondaryIndex`**

| Método | Descripción |
|---|---|
| `__init__(records, key_field)` | Construye índice denso ordenado por `key_field` (salario) |
| `lookup(key)` | Retorna lista de bloques distintos con registros que coinciden |
| `matching_count(key)` | Retorna número de registros que coinciden con la clave |
| `io_cost(key, n_records, n_matching)` | Retorna dict con costo I/O, incluyendo peor caso para datos dispersos |

**`multilevel_index.py` — `MultilevelIndex`**

| Método | Descripción |
|---|---|
| `__init__(records, key_field)` | Construye inner `DenseIndex` + outer sparse index sobre sus bloques |
| `lookup(key)` | Búsqueda en dos niveles: outer en memoria (0 I/Os) + inner en disco (1 I/O) |
| `io_cost(n_records)` | Retorna dict con desglose por nivel: outer_ios=0, inner_ios=1, data_ios=1 |

**`cost_comparison.py`**

| Función | Descripción |
|---|---|
| `run_comparison()` | Construye todos los índices y genera el reporte consolidado de costos I/O |

---

### 3.4 Diagrama de clases

<!-- 📐 PENDIENTE: diagrama PlantUML de clases -->
<!-- Ruta sugerida: ./images/class_diagram.puml -->

```plantuml
@startuml
' Placeholder — completar con diagrama real
' Clases: DenseIndex, SparseIndex, ClusteringIndex,
'         SecondaryIndex, MultilevelIndex
' Relaciones: MultilevelIndex *-- DenseIndex (composición)
' Dependencias: todos dependen de index_utils
@enduml
```

---

## 4. Guía de Ejecución y Validación

### 4.1 Preparación del entorno

Los módulos usan únicamente la biblioteca estándar de Python — no se requiere instalar dependencias externas.

```bash
# Clonar o descargar los archivos en una carpeta local
cd indexes/

# Verificar que Python 3.9+ esté disponible
python --version

# Ejecutar el módulo de utilidades como self-test
python index_utils.py
```

**Salida esperada del self-test:**

```
==============================================================
  index_utils.py — Self-test
==============================================================

  Instructor table:

  Records : 12
  Blocks  : 3  (5 records/block, 10 ms/I/O)
  Ordered by: ID

   Blk      ID  Name          Dept            Salary
  ────  ──────  ────────────  ────────────  ────────
     0   10101  Srinivasan    Comp. Sci.      65,000
     ...
     2   98345  Kim           Elec. Eng.      80,000

  binary_search_ios(10000) = 14   (dense index, 1M records)
  binary_search_ios(2000)  = 11   (sparse index, 1M records)

  Full scan (200,000 blocks):
    200,000 I/Os → 33.33 min
```

**Lista de verificación — Preparación:**

- [ ] `python --version` muestra Python 3.9 o superior
- [ ] `python index_utils.py` termina sin errores
- [ ] La tabla impresa tiene 12 registros distribuidos en 3 bloques
- [ ] `binary_search_ios(10000)` retorna 14

---

### 4.2 Fase 1 — Índice denso sobre ID (`dense_index.py`)

```bash
python dense_index.py
```

#### Punto 1 — Una entrada por cada registro de la tabla

El índice denso construido sobre los 12 registros de `INSTRUCTOR_TABLE` produce exactamente 12 entradas — una por registro, en el mismo orden de la tabla (ordenada por ID):

```
  [Dense index on ID] — 12 entries total
     #      Search Key  Block #
  ────  ──────────────  ───────
     0           10101        0
     1           12121        0
     ...
     6           45565        1
     ...
    11           98345        2
```

**Lista de verificación — Punto 1:**

- [ ] El índice imprime exactamente 12 entradas
- [ ] Los primeros 5 registros (IDs 10101–32343) están en Block 0
- [ ] Los siguientes 5 registros (IDs 33456–76766) están en Block 1
- [ ] Los últimos 2 registros (IDs 83821–98345) están en Block 2

---

#### Punto 2 — La búsqueda binaria reduce drásticamente los I/Os

Al buscar `ID = 45565`, el script reporta el bloque encontrado y el número de pasos de búsqueda binaria:

```
  Found ID=45565 → Block 1
  Binary search steps: ceil(log2(12)) = 4 index reads + 1 data read
```

A escala textbook (1M registros → 10.000 bloques de índice):

```
  Textbook scale (   1,000,000 records):
    Index blocks  : 10,000
    Index I/Os    : 14  (ceil(log2(10,000)))
    Data  I/Os    : 1
    Total         : 15 I/Os → 150 ms
```

**Lista de verificación — Punto 2:**

- [ ] `lookup(45565)` retorna Block 1
- [ ] A escala textbook, `index_blocks = 10,000`
- [ ] `index_ios = 14` = ⌈log₂(10.000)⌉
- [ ] `total_ios = 15`, `total_ms = 150`

---

#### Punto 3 — El índice denso es mucho más rápido que el full scan

La tabla comparativa al final de la salida muestra el contraste:

```
  Strategy                             I/Os          Time
  ──────────────────────────────── ────────  ────────────
  No index (full scan)              200,000     33.33 min
  Dense index                            15        150 ms

  Speedup: 13,333× fewer I/Os with a dense index.
```

**Lista de verificación — Punto 3:**

- [ ] Full scan: 200,000 I/Os → ~33 min
- [ ] Dense index: 15 I/Os → 150 ms
- [ ] El speedup reportado es ~13,333×

---

### 4.3 Fase 2 — Índice disperso sobre ID (`sparse_index.py`)

```bash
python sparse_index.py
```

#### Punto 4 — Una entrada por bloque, no por registro

El índice disperso sobre los mismos 12 registros (3 bloques) produce solo **3 entradas** — una por bloque, almacenando la clave mínima de cada uno:

```
  [Sparse index on ID] — 3 entries total
     #      Search Key  Block #
  ────  ──────────────  ───────
     0           10101        0
     1           33456        1
     2           83821        2
```

**Lista de verificación — Punto 4:**

- [ ] El índice disperso tiene exactamente 3 entradas (vs 12 del denso)
- [ ] Las claves son los primeros IDs de cada bloque: 10101, 33456, 83821

---

#### Punto 5 — La búsqueda usa floor lookup más scan lineal

Al buscar `ID = 45565`, el floor lookup identifica que debe buscar en Block 1 (el bloque cuya clave mínima es 33456, el mayor valor ≤ 45565):

```
  Floor lookup → scan Block 1 linearly for ID=45565
  (Entry with largest key ≤ 45565 is 33456 → Block 1)
```

**Lista de verificación — Punto 5:**

- [ ] `lookup(45565)` retorna Block 1 (no Block 0)
- [ ] El mensaje impreso menciona la clave de entrada 33456

---

#### Punto 6 — El disperso ocupa 5x menos espacio que el denso

La comparación de espacio a escala textbook:

```
  Dense  :  1,000,000 entries → 10,000 index blocks
  Sparse :    200,000 entries →  2,000 index blocks
  Ratio  : sparse uses 5× fewer index entries.
```

Y el disperso es también ligeramente más rápido: 12 I/Os vs 15, porque su índice tiene menos bloques y la búsqueda binaria requiere menos pasos.

**Lista de verificación — Punto 6:**

- [ ] Dense: 10,000 index blocks
- [ ] Sparse: 2,000 index blocks (5× menos)
- [ ] Sparse total: 12 I/Os → 120 ms

---

### 4.4 Fase 3 — Clustering index sobre dept\_name (`clustering_index.py`)

```bash
python clustering_index.py
```

#### Punto 7 — El orden del índice coincide con el orden físico

El script re-ordena la tabla por `dept_name` para simular un archivo físicamente agrupado, y el índice construido sobre ese archivo refleja ese orden:

```
  File physically ordered by dept_name:

   Blk  Dept          Name
  ────  ────────────  ────────────
     0  Biology       Crick
     0  Comp. Sci.    Srinivasan
     ...
     1  Finance       Wu
     1  History       El Said
     ...
     2  Physics       Einstein
```

```
  [Clustering index on dept_name] — 7 entries total
     0         Biology        0
     1      Comp. Sci.        0
     ...
     6         Physics        2
```

**Lista de verificación — Punto 7:**

- [ ] El archivo tiene registros agrupados por departamento en bloques consecutivos
- [ ] El índice tiene 7 entradas (una por cada departamento único)
- [ ] `lookup("History")` retorna Block 1

---

#### Punto 8 — Consulta de rango: bloques consecutivos = mínimo I/O

La consulta de rango entre `'Comp. Sci.'` y `'History'` accede únicamente a los bloques que contienen esos departamentos — que son físicamente contiguos:

```
  Blocks in range (demo): [0, 1]
  All blocks are CONTIGUOUS → sequential I/O, no random seeks.

  Cost breakdown:
    Index I/Os : 1  (find entry for 'Comp. Sci.')
    Data  I/Os : 2  (2 consecutive blocks)
    Total      : 3 I/Os → 30 ms
```

**Lista de verificación — Punto 8:**

- [ ] `range_lookup("Comp. Sci.", "History")` retorna `[0, 1]`
- [ ] Total: 3 I/Os → 30 ms
- [ ] El mensaje confirma que los bloques son CONTIGUOUS

---

### 4.5 Fase 4 — Secondary index sobre salary (`secondary_index.py`)

```bash
python secondary_index.py
```

#### Punto 9 — El orden del índice difiere del orden físico

El archivo sigue ordenado por ID. El índice secundario sobre `salary` tiene sus entradas ordenadas por salario, pero los punteros apuntan a bloques no contiguos:

```
  [Secondary index on salary (sorted by salary)] — 12 entries total
     0           40000        0
     1           60000        0
     2           62000        1
     ...
     6           80000        1
     7           80000        2     ← mismo salary, bloque diferente
     ...
```

**Lista de verificación — Punto 9:**

- [ ] Los 12 registros aparecen ordenados por salary (40000 → 95000)
- [ ] `lookup(80000)` retorna `[1, 2]` — dos bloques distintos

---

#### Punto 10 — Baja selectividad: el índice secundario es más lento que el full scan

Este es el resultado más contraintuitivo del módulo y uno de los más importantes del curso. Con el 25% de los registros coincidiendo con la consulta, el índice secundario es **más lento** que un full scan:

```
  Textbook scale (1,000,000 records) — low selectivity:
    Matching records   : 250,000  (25% of 1,000,000)
    Data  I/Os (worst) : 250,000  (one per matching record)
    Total              : 250,014 I/Os → 41.7 min
    Full scan          : 200,000 I/Os → 33.3 min

  ⚠  Secondary index is SLOWER than full scan in this scenario.
```

En contraste, para `salary = 95,000` (solo 1 registro), el índice secundario tarda solo 2 I/Os.

**Lista de verificación — Punto 10:**

- [ ] Low selectivity: 250,014 I/Os → 41.7 min
- [ ] Full scan: 200,000 I/Os → 33.3 min
- [ ] High selectivity (`salary = 95,000`): 2 I/Os

---

### 4.6 Fase 5 — Índice multinivel (`multilevel_index.py`)

```bash
python multilevel_index.py
```

#### Punto 11 — El outer index en memoria elimina I/Os de búsqueda

El outer index es un índice disperso sobre los bloques del inner index. A escala textbook cabe completamente en memoria (100 bloques), lo que hace que buscarlo cueste **0 I/Os**:

```
  Textbook scale (1,000,000 records):
    Inner index : 1,000,000 entries → 10,000 blocks  (on disk)
    Outer index : 10,000 entries    →    100 blocks  (in memory → 0 I/Os)
```

**Lista de verificación — Punto 11:**

- [ ] `inner_blocks = 10,000` (en disco)
- [ ] `outer_blocks = 100` (en memoria)
- [ ] `outer_ios = 0`

---

#### Punto 12 — Costo total: exactamente 2 I/Os independiente del tamaño

El lookup de tres pasos resulta en exactamente 2 I/Os:

```
  Step 1 — search outer index (in memory) : 0 I/Os
  Step 2 — read inner index block          : 1 I/O
  Step 3 — linear scan inner block         : (in memory, no I/O)
  Step 4 — read data block                 : 1 I/O
  Found ID=45565 → Block 1

  Total : 2 I/Os → 20 ms
```

**Lista de verificación — Punto 12:**

- [ ] `lookup(45565)` retorna Block 1
- [ ] `total_ios = 2`, `total_ms = 20`
- [ ] El desglose muestra `outer_ios=0`, `inner_ios=1`, `data_ios=1`

---

## 5. Comparativa Final de Costos I/O (`cost_comparison.py`)

```bash
python cost_comparison.py
```

Este módulo importa todos los índices y produce el reporte consolidado. La tabla de punto lookup a escala textbook reproduce exactamente la comparación final de las diapositivas de la Clase 6:

```
  Strategy                             I/Os          Time
  ──────────────────────────────── ────────  ────────────
  No index (full scan)              200,000     33.33 min
  Dense index (1 level)                  15        150 ms
  Sparse index (1 level)                 12        120 ms
  Multilevel index (2 levels)             2         20 ms
```

El módulo también incluye:
- Comparativa de consultas de rango (clustering vs secondary vs full scan)
- Comparativa de selectividad baja (secondary index vs full scan)
- Tabla de espacio ocupado por tipo de índice
- Guía de decisión: cuándo usar cada tipo

<!-- 🖼️ PENDIENTE: gráfico de barras comparativo de I/Os por estrategia -->
<!-- Ruta sugerida: ./images/chart_io_comparison.svg -->

---

## 6. Referencias y Material de Profundización

Los conceptos implementados en este módulo corresponden directamente al capítulo de indexación de la literatura estándar de sistemas de bases de datos.

- **Silberschatz, A., Korth, H. F., & Sudarshan, S.** *Database System Concepts*, 7th ed. McGraw-Hill.
  Capítulo 14: Indexing. La tabla `instructor` usada en todos los ejemplos de este módulo proviene de este libro.

- **Ramakrishnan, R., & Gehrke, J.** *Database Management Systems*, 3rd ed.
  Capítulo sobre organización de archivos e índices ordenados.

- **UC Berkeley — CS 186:** *Course Notes, Note 17: Indexes*.
  Disponible en: [https://cs186berkeley.net/notes/note17/](https://cs186berkeley.net/notes/note17/)

- **Carnegie Mellon University — CMU 15-445/645:** *Intro to Database Systems — Tree Indexes*.
  Disponible en: [https://15445.courses.cs.cmu.edu](https://15445.courses.cs.cmu.edu)

- **Python docs — `bisect`:** Documentación oficial del módulo de búsqueda binaria.
  Disponible en: [https://docs.python.org/3/library/bisect.html](https://docs.python.org/3/library/bisect.html)

---

> [!important]
> Este material fue desarrollado con apoyo de herramientas de IA como asistente de redacción y estructuración. El contenido ha sido supervisado, validado y refinado por intervención humana para garantizar su precisión técnica y coherencia pedagógica. No obstante, pueden haber errores.
