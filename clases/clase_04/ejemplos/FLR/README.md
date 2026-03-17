# Laboratorio: Almacenamiento Físico en Bases de Datos

**Laboratorio de Estructuras de Datos · Universidad de Antioquia**

> [!warning]
> Este material ha sido diseñado como apoyo directo a las diapositivas presentadas
> en las sesiones magistrales sobre **Almacenamiento Físico y Organización de Archivos**.
> Se sugiere tener dichas presentaciones a la mano para correlacionar la teoría
> con el código aquí desarrollado.

---

## Tabla de Contenido

1. [¿Qué se construye en este laboratorio?](#1-qué-se-construye-en-este-laboratorio)
2. [Estructura del repositorio](#2-estructura-del-repositorio)
3. [Contenido de cada carpeta](#3-contenido-de-cada-carpeta)
   - [3.1 packet — Registros de Longitud Fija](#31-packet--registros-de-longitud-fija)
   - [3.2 bitmap — Encabezados y Mapas de Bits](#32-bitmap--encabezados-y-mapas-de-bits)
4. [¿Qué se espera que el estudiante comprenda?](#4-qué-se-espera-que-el-estudiante-comprenda)
5. [Para ir más allá](#5-para-ir-más-allá)

---

## 1. ¿Qué se construye en este laboratorio?

Este laboratorio implementa la capa más baja de un Sistema Gestor de Bases de
Datos (DBMS): el **Disk Manager**. Es la capa responsable de leer y escribir
datos organizados en archivos, páginas y registros directamente sobre el disco.

El recorrido es incremental: cada carpeta y cada archivo dentro de ella resuelve
una limitación concreta de la versión anterior, reflejando exactamente la
evolución histórica que llevó a los motores modernos a su arquitectura actual.

```
Aplicación SQL
      ↓
Query Planning
      ↓
Operator Execution
      ↓
Access Methods
      ↓
Buffer Pool Manager
      ↓
  Disk Manager        ← Este laboratorio implementa esta capa
```

> [!important]
> Este laboratorio implementa exclusivamente *Unordered Heap Files* con
> registros de longitud fija. Sorted Files, Clustered Heap Files e Index
> Files (B+, Hashing) se abordan en sesiones posteriores.

---

## 2. Estructura del repositorio

```
laboratorio-almacenamiento/
│
├── README.md                  ← Este archivo
│
├── packet/                    ← Parte I: Registros empaquetados (v1 → v3)
│   ├── README.md
│   ├── heap_file_fixed_init.py
│   ├── heap_file_fixed.py
│   ├── heap_file_v2_pages.py
│   ├── heap_file_v3_freemospace.py
│   └── images/
│
└── bitmap/                    ← Parte II: Bitmaps y Page Headers (v4)
    ├── README.md
    ├── heap_file_v4_bitmap.py
    └── images/
```

> [!note]
> Cada carpeta contiene su propio `README.md` con la teoría, el código
> anotado, la guía de ejecución y los puntos de control correspondientes
> a esa etapa. Este archivo raíz es el punto de entrada — los READMEs
> internos son los guías de cada sesión.

---

## 3. Contenido de cada carpeta

### 3.1 [`packet/`](packet/) — Registros de Longitud Fija

**Prerrequisito:** Ninguno. Este es el punto de partida.

Esta carpeta implementa la evolución desde un archivo de texto plano hasta
un heap file paginado con reciclaje de espacio. Se trabajan cuatro versiones
del motor, cada una construida sobre la anterior:

| Versión | Archivo | Concepto central |
|:---:|---|---|
| Plantilla | `heap_file_fixed_init.py` | Esqueleto para completar en clase |
| v1 | `heap_file_fixed.py` | Serialización, padding, seek O(1) |
| v2 | `heap_file_v2_pages.py` | Páginas, RID = (page\_id, slot\_id), tombstones |
| v3 | `heap_file_v3_freemospace.py` | Free List encadenada, reciclaje de espacio |

Al finalizar esta carpeta, el motor es funcional pero presenta una limitación
crítica: el estado de la Free List vive únicamente en la memoria RAM. Si el
proceso termina inesperadamente, esa información se pierde. Esta limitación
es la motivación directa para la carpeta `bitmap/`.

---

### 3.2 [`bitmap/`](bitmap/) — Encabezados y Mapas de Bits

**Prerrequisito:** Haber completado la carpeta `packet/`.

Esta carpeta introduce la versión `v4` del motor, que resuelve el problema
de persistencia de la `v3` mediante dos innovaciones arquitectónicas: el
**Page Header** y el **Bitmap**.

| Concepto | Descripción |
|---|---|
| Page Header | Región de bytes al inicio de cada página que almacena metadatos en disco |
| Bitmap | Arreglo de bits dentro del header — cada bit indica si un slot está libre u ocupado |
| Borrado lógico optimizado | Ya no requiere sobrescribir el registro con asteriscos — basta con cambiar un bit |
| Early exit en SELECT | Si el bitmap indica slot libre, el motor retorna sin leer el área de datos |

La fórmula de acceso evoluciona respecto a la `v3`:

```
v3:  offset = (page_id × PAGE_SIZE) + (slot_id × RECORD_SIZE)
v4:  offset = (page_id × PAGE_SIZE) + HEADER_SIZE + (slot_id × RECORD_SIZE)
```

---

## 4. ¿Qué se espera que el estudiante comprenda?

Al completar ambas carpetas y correlacionar el código con la teoría de clase,
se espera que el estudiante sea capaz de responder con claridad las siguientes
preguntas:

**Sobre la representación física de los datos:**
- ¿Por qué un DBMS no delega al sistema operativo la gestión de sus archivos?
- ¿Cuál es la diferencia entre un archivo visto por el SO y un archivo visto
  por el DBMS?
- ¿Por qué la unidad mínima de transferencia entre disco y RAM es la página
  completa, aunque solo se necesite modificar un campo de 50 bytes?

**Sobre los registros de longitud fija:**
- ¿Cómo se logra acceso O(1) a cualquier registro sin índices ni búsqueda
  secuencial?
- ¿Qué implica el padding interno y qué trade-off introduce respecto al
  espacio en disco?
- ¿Por qué al borrar un registro no se desplazan los demás?

**Sobre páginas y RID:**
- ¿Qué información codifica un RID y por qué es suficiente para localizar
  cualquier registro en O(1)?
- ¿Qué ocurre con los RIDs existentes si se mueve un registro dentro de su
  página?

**Sobre la gestión de espacio libre:**
- ¿Cuál es la diferencia entre un borrado físico y un borrado lógico?
- ¿Qué problema resuelve la Free List y qué problema nuevo introduce (v3)?
- ¿Por qué el Bitmap soluciona el problema de persistencia que la Free List
  no podía resolver?
- ¿Qué ventaja ofrece el early exit en SELECT cuando se usa un Bitmap?

---

## 5. Para ir más allá

El motor construido en este laboratorio es una base sólida. Los siguientes
son caminos naturales de extensión, ordenados de menor a mayor complejidad,
que pueden explorarse como trabajo independiente o en sesiones futuras:

- **Registros de longitud variable (VLR):** Implementar soporte para campos
  `varchar` reales usando el formato de arreglo de desplazamientos (*offset array*),
  tal como lo hace PostgreSQL internamente con su *Slotted Page*.

- **Slotted Page completa:** Extender el Page Header para incluir el directorio
  de slots con pares `(offset, longitud)`, permitiendo que los registros se
  muevan físicamente dentro de la página sin invalidar sus RIDs externos.

- **Buffer Pool básico:** Implementar una caché en RAM de páginas leídas del
  disco, con una política de reemplazo simple (LRU) y soporte para *dirty pages*.

- **Page Directory persistente:** Reemplazar el escaneo lineal de bitmaps por
  un directorio de páginas almacenado en una Header Page dedicada (Página 0),
  tal como lo describe la arquitectura de lista enlazada vs. directorio vista
  en clase.

- **Sorted Heap File:** Mantener las páginas ordenadas por una clave de búsqueda,
  explorar el costo de inserción y la ganancia en búsquedas de rango respecto
  al Unordered Heap File.

- **Índice primario (B+ Tree):** Construir una estructura de índice separada
  que almacene pares `(clave, RID)`, permitiendo localizar cualquier registro
  por valor de clave sin un Full Table Scan.

- **Write-Ahead Log (WAL) básico:** Agregar un archivo de log que registre
  cada operación antes de aplicarla al archivo de datos, como primer paso
  hacia la recuperación ante fallos (*crash recovery*).

---

> [!important]
> Este material fue desarrollado con apoyo de herramientas de IA como asistente
> de redacción y estructuración. El contenido ha sido supervisado, validado y
> refinado por intervención humana para garantizar su precisión técnica y
> coherencia pedagógica. No obstante, pueden existir errores.
