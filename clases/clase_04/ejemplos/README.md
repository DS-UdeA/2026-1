# DBFiles — Representación física de datos en un DBMS


Este ejercicio estudia cómo un sistema gestor de bases de datos representa los datos en disco.

El objetivo es entender la estructura fundamental que usan los DBMS modernos:

Database → File → Page → Record

---

## 1. Contexto teórico

En un DBMS relacional los datos no se almacenan como tablas directamente.

En el disco la estructura es:

```
File
├── Page 0
├── Page 1
├── Page 2
└── Page N
```

Cada página contiene registros.

```
Page
├── Header
├── Record 0
├── Record 1
└── Record N
```

Cada registro se identifica mediante un identificador interno del DBMS:

```
RID = (page_id, slot)
```

Este identificador permite localizar rápidamente un registro dentro del archivo.

---

## 2. Arquitectura del ejemplo

Para entender estos conceptos implementaremos una versión simplificada de un **Heap File**.

Componentes:

```
HeapFile
│
├── Page
│     ├── bitmap
│     └── slots
│
├── Record
│
└── RID
```

---

## 3. Diagrama UML

```
@startuml

class HeapFile {
insert(record)
get(rid)
delete(rid)
scan()
}

class Page {
pageId
slots
bitmap
insert(record)
get(slot)
delete(slot)
}

class Record {
data
}

class RID {
pageId
slot
}

HeapFile --> Page
Page --> Record
HeapFile --> RID

@enduml
```

---

## 4. Organización del repositorio

```
ejemplos/dbfiles/

architecture/
requirements.md
uml/

python/
heap_file.py
page.py
record.py
rid.py

tests/
test_heap_file.py
test_page.py

java/
src/dbfiles/
HeapFile.java
Page.java
Record.java
RID.java

test/
HeapFileTest.java
````
---

## 5. Implementación Python

### Record

```python
class Record:
    def __init__(self, values):
        self.values = values
````

---

### RID

```python
class RID:

    def __init__(self, page_id, slot):
        self.page_id = page_id
        self.slot = slot
```

---

### Page

La página contiene slots para registros y un bitmap que indica qué slots están ocupados.

```python
class Page:

    def __init__(self, page_id, capacity):
        self.page_id = page_id
        self.capacity = capacity
        self.slots = [None] * capacity
        self.bitmap = [0] * capacity

    def insert(self, record):

        for i in range(self.capacity):

            if self.bitmap[i] == 0:

                self.slots[i] = record
                self.bitmap[i] = 1

                return i

        raise Exception("Page full")

    def get(self, slot):

        if self.bitmap[slot] == 1:
            return self.slots[slot]

        return None

    def delete(self, slot):

        if self.bitmap[slot] == 1:

            self.bitmap[slot] = 0
            self.slots[slot] = None
```

---

### HeapFile

```python
from page import Page
from rid import RID

class HeapFile:

    def __init__(self, page_capacity=4):

        self.pages = []
        self.page_capacity = page_capacity

    def insert(self, record):

        for page in self.pages:

            try:
                slot = page.insert(record)

                return RID(page.page_id, slot)

            except:
                continue

        new_page = Page(len(self.pages), self.page_capacity)

        self.pages.append(new_page)

        slot = new_page.insert(record)

        return RID(new_page.page_id, slot)

    def get(self, rid):

        page = self.pages[rid.page_id]

        return page.get(rid.slot)

    def delete(self, rid):

        page = self.pages[rid.page_id]

        page.delete(rid.slot)
```

---

## 6. Pruebas unitarias

### Test Page

```python
import unittest
from page import Page
from record import Record

class TestPage(unittest.TestCase):

    def test_insert(self):

        page = Page(0, 2)

        r1 = Record(["Homer"])
        r2 = Record(["Marge"])

        s1 = page.insert(r1)
        s2 = page.insert(r2)

        self.assertEqual(s1, 0)
        self.assertEqual(s2, 1)
```

---

### Test HeapFile

```python
import unittest

from heap_file import HeapFile
from record import Record

class TestHeapFile(unittest.TestCase):

    def test_insert_get(self):

        heap = HeapFile()

        rid = heap.insert(Record(["Homer"]))

        rec = heap.get(rid)

        self.assertEqual(rec.values[0], "Homer")

    def test_delete(self):

        heap = HeapFile()

        rid = heap.insert(Record(["Lisa"]))

        heap.delete(rid)

        rec = heap.get(rid)

        self.assertIsNone(rec)
```

---

# 7. Experimento para ejecutar en clase

Ejecutar:

```
python -m unittest discover tests
```

Luego modificar:

```
page_capacity = 4
page_capacity = 100
page_capacity = 1
```

y observar cómo cambia la cantidad de páginas creadas.

---

## 8. Conexión con SimpleDB

| Concepto | SimpleDB | Este ejemplo |
| -------- | -------- | ------------ |
| Registro | Tuple    | Record       |
| Página   | HeapPage | Page         |
| Archivo  | HeapFile | HeapFile     |
| RID      | RecordId | RID          |

---

## 9. Preguntas de reflexión

1. ¿Por qué los DBMS trabajan con **páginas** en lugar de registros individuales?

2. ¿Qué ventajas tiene usar un identificador:

   ```
   RID = (page_id, slot)
   ```

   en lugar de usar direcciones físicas?

3. ¿Qué ocurre si eliminamos registros sin usar bitmap?

4. ¿Qué problema aparece si los registros cruzan el límite de página?

5. ¿Qué estructura adicional permitiría encontrar páginas con espacio libre más rápido?

---

## 10. Conceptos clave aprendidos

Después de esta sesión deberías entender:

```
DBMS Storage Hierarchy

Database
↓
File
↓
Page
↓
Record
```

y cómo el DBMS usa el identificador:

```
RID = (page_id, slot)
```

para localizar registros de manera eficiente.

---

## Resultado pedagógico

Con este README los estudiantes ven **la conexión directa con la teoría**:

Diapositivas →  
- páginas  
- registros  
- RID  
- heap file  

Código →  
- Page  
- Record  
- RID  
- HeapFile  

Pruebas →  
- inserción  
- eliminación  
- acceso por RID  
