![Built with AI](https://img.shields.io/badge/Built%20with-AI-blue.svg)

# Procesamiento de Archivos en C++

## Objetivos de Aprendizaje

Al completar esta serie de ejemplos, los estudiantes serán capaces de:

- **Comprender** los conceptos fundamentales de entrada/salida de archivos en C++
- **Utilizar** las clases `fstream`, `ifstream` y `ofstream` para leer y escribir archivos
- **Implementar** manejo de errores al abrir y procesar archivos
- **Aplicar** patrones comunes como lectura línea por línea, carácter por carácter y procesamiento de datos estructurados
- **Resolver** problemas prácticos que involucran manipulación de archivos de texto

---

## Descripción General

Este directorio contiene una colección progresiva de **22 ejemplos** que ilustran diferentes aspectos del procesamiento de archivos en C++. Los ejemplos abarcan desde operaciones básicas de lectura y escritura hasta técnicas avanzadas como paso de flujos a funciones y procesamiento de datos con formato.

---

## Estructura del Proyecto

```
cpp/
├── README.md                    # Este archivo
├── makefile                     # Script de compilación automatizada
├── src/                         # Código fuente (23 archivos .cpp)
│   ├── ejemplo1.cpp  - ejemplo22.cpp
│   ├── list.cpp
│   └── listcpp.cpp
└── data/                        # Archivos de datos para pruebas
    ├── demofile.txt
    ├── hownow.txt
    ├── letters.txt
    ├── murphy.txt
    ├── names2.txt
    ├── numfile.txt
    ├── sentence.txt
    ├── table.txt
    └── out.txt
```

---

## Requisitos Previos

- **Compilador**: GCC/G++ (mínimo versión C++17)
- **Sistema operativo**: Linux, macOS o Windows (con herramientas POSIX)
- **Herramientas**: `make` y terminal/línea de comandos

### Verificar instalación

```bash
g++ --version
make --version
```

---

## Guía de Uso: Paso a Paso

### 1. Compilar Todos los Ejemplos

En la carpeta `cpp/`, ejecuta:

```bash
make
```

Este comando:
- Compila automáticamente todos los archivos `.cpp` en la carpeta `src/`
- Crea ejecutables en la carpeta `bin/`
- Copia todos los archivos de datos a `bin/` (necesarios para que los programas funcionen)

**Resultado esperado**: Se crearán ejecutables compilados sin errores.

### 2. Listar Archivos Generados

Para ver qué se compiló:

```bash
make list
```

Muestra:
- Archivos fuente en `src/`
- Ejecutables generados en `bin/`
- Archivos de datos copiados a `bin/`

### 3. Ejecutar un Ejemplo Específico

Navega a la carpeta `bin/`:

```bash
cd bin
```

Ejecuta el ejemplo deseado:

```bash
./ejemplo1
./ejemplo5
./ejemplo10
```

**Windows (PowerShell)**:
```powershell
.\ejemplo1.exe
.\ejemplo5.exe
.\ejemplo10.exe
```

### 4. Entender la Salida

Cada programa imprime en pantalla:
- Mensajes de estado (apertura de archivo, lectura, escritura)
- Contenido del archivo procesado
- Confirmación de finalización

**Ejemplo de salida típica**:
```
File opened successfully.
Now writing information to the file.
Done.
```

### 5. Limpiar Archivos Compilados

Para eliminar todos los ejecutables y archivos de datos en `bin/`:

```bash
make clean
```

---

## Descripción de Ejemplos por Categoría

### Escritura Básica en Archivos
- **ejemplo1.cpp**: Escritura simple con el operador `<<`
- **ejemplo2.cpp**: Sobrescritura de archivos existentes
- **ejemplo3.cpp**: Apertura segura de archivos

### Lectura Básica de Archivos
- **ejemplo4.cpp**: Lectura línea por línea con `getline()`
- **ejemplo5.cpp**: Paso de flujos a funciones
- **ejemplo6.cpp**: Lectura de archivos con manejo de errores

### Lectura Avanzada
- **ejemplo7.cpp**: Lectura carácter por carácter con `get()`
- **ejemplo8.cpp**: Procesamiento de archivos con múltiples líneas
- **ejemplo9.cpp**: Verificación de fin de archivo (EOF)
- **ejemplo10.cpp**: Lectura con entrada del usuario

### Procesamiento de Datos Estructurados
- **ejemplo11.cpp** - **ejemplo22.cpp**: Procesamiento de datos con formato, estructuras, validación y operaciones complejas

### Utilidades
- **list.cpp** / **listcpp.cpp**: Programas complementarios para exploración

---

## Archivos de Datos Disponibles

Los archivos en `data/` contienen diferentes tipos de datos para las pruebas:

| Archivo | Contenido | Uso Típico |
|---------|-----------|-----------|
| `demofile.txt` | Lista de nombres | Lectura/escritura básica |
| `hownow.txt` | Texto de pradera | Procesamiento de líneas |
| `letters.txt` | Caracteres individuales | Lectura carácter por carácter |
| `murphy.txt` | Párrafo narrativo | Lectura continua |
| `names2.txt` | Lista de nombres | Validación de datos |
| `numfile.txt` | Números | Conversión y procesamiento numérico |
| `sentence.txt` | Oración simple | Análisis de palabras |
| `table.txt` | Datos tabulares | Procesamiento de estructura |

---

## Flujo de Trabajo Recomendado

```
1. Compilar todos los ejemplos
   └─ make

2. Listar qué se compiló
   └─ make list

3. Ejecutar ejemplos progresivamente
   └─ cd bin && ./ejemplo1, ./ejemplo2, etc.

4. Estudiar el código fuente
   └─ Abrir src/ejemplo1.cpp en el editor

5. Modificar y experimentar
   └─ Cambiar ejemplo1.cpp y recompilar

6. Limpiar después de terminar
   └─ make clean
```

---

## Recursos Complementarios

### Diapositivas
- Conceptos teóricos sobre streams y archivos en C++
- Modelos de apertura y modos de acceso
- Manejo de excepciones

### Cheat Sheet
- Sintaxis rápida de `fstream`, `ifstream`, `ofstream`
- Funciones comunes: `open()`, `close()`, `getline()`, `get()`, `put()`
- Manejo de errores: `is_open()`, verificación de EOF

---

## Preguntas Frecuentes

**P: ¿Por qué me sale "File not found"?**
A: Asegúrate de compilar con `make` primero. Los archivos de datos deben estar en `bin/`.

**P: ¿Puedo modificar los ejemplos?**
A: Sí, modifica los archivos `.cpp` en `src/` y recompila con `make`.

**P: ¿Cómo paso archivos como argumentos?**
A: En ejemplo10, se solicita el nombre del archivo interactivamente. Puedes modificar otros ejemplos para hacer lo mismo.

**P: ¿Qué pasa si no tengo `make`?**
A: Compila manualmente: `g++ -std=c++17 -O2 src/ejemplo1.cpp -o bin/ejemplo1`

---

## Notas Importantes

- Siempre **verifica que el archivo se abrió correctamente** antes de operarlo
- Los programas **sobrescriben archivos existentes** sin advertencia (ve el modo `ios::out`)
- Para **leer datos**, asegúrate de que el archivo exista y esté en `bin/`
- Los datos generados se guardan en `bin/` (revisar `out.txt` después de ejecutar)

---

## Próximos Pasos

Después de completar estos ejemplos, podrás:

1. **Integrar** manejo de archivos en proyectos más complejos
2. **Implementar** parsers y procesadores de datos
3. **Desarrollar** aplicaciones que persistan información en disco
4. **Optimizar** entrada/salida para archivos grandes

> [!Note]
> **AI Disclosure:** This document was created with the assistance of Artificial Intelligence language models. The content has been reviewed, edited, and validated by a human author to ensure accuracy and quality.