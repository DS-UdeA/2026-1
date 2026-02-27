A continuación se propone un **README** (lenguaje formal pero amigable, semestre 5) que conecta el trabajo previo en PostgreSQL/pgAdmin con una implementación equivalente desde **Python**, incluyendo los espacios para figuras.

---

# Implementación en Python: Conexión y operaciones sobre PostgreSQL

## 1. Propósito

Este material muestra cómo una aplicación en **Python** puede conectarse a una base de datos **PostgreSQL** y ejecutar operaciones SQL (consultas y modificaciones). La intención es evidenciar que, en escenarios reales, la interacción con bases de datos suele realizarse **desde aplicaciones** y no únicamente desde herramientas gráficas como pgAdmin.

---

## 2. Requerimientos

Antes de iniciar, la máquina debe contar con lo siguiente:

### 2.1. Software y configuración mínima

* **PostgreSQL instalado** y en ejecución.
* **Base de datos creada** (por ejemplo: `music_db`).
* Scripts del proyecto ejecutados previamente en el orden:

  1. `schema.sql`
  2. `data.sql`
  3. `querys.sql`
* **Python 3.10+** instalado (se recomienda 3.11 o superior).
* Acceso a un editor o IDE (por ejemplo: VS Code, PyCharm o similar).

> **Figura (opcional):** Captura de PostgreSQL activo y la base de datos `music_db` visible en pgAdmin.
> **[FIGURA AQUI: “PostgreSQL/pgAdmin listo”]**

---

### 2.2. Instalación de la librería de conexión (driver)

Para conectar Python con PostgreSQL se utilizará un *driver* (controlador) que implementa el protocolo de conexión.

Se recomienda instalar **psycopg2** (opción ampliamente usada en cursos):

```bash
pip install psycopg2-binary
```

> Alternativa (más moderna, opcional): `psycopg`
> `pip install psycopg`

---

### 2.3. Verificación de instalación de la librería

Para comprobar que la librería quedó instalada correctamente, ejecutar en terminal:

```bash
python -c "import psycopg2; print('psycopg2 instalado correctamente')"
```

Si aparece el mensaje, la instalación fue exitosa.

> **Figura (opcional):** Captura de terminal mostrando el mensaje de verificación.
> **[FIGURA AQUI: “Verificación de psycopg2”]**

---

## 3. Antes de empezar: verificación de conexión desde Python

En esta sección se valida que Python logra conectarse al servidor PostgreSQL.
Esto permite detectar temprano problemas típicos: usuario/contraseña incorrectos, puerto, servidor apagado, base inexistente, etc.

### 3.1. Parámetros requeridos

En el siguiente script deberán ajustarse estos datos según el entorno local:

* `host` (usualmente `localhost`)
* `port` (por defecto `5432`)
* `dbname` (por ejemplo `music_db`)
* `user` (por ejemplo `postgres`)
* `password` (definida durante la instalación)

---

### 3.2. Script de prueba de conexión

Crear un archivo llamado `test_connection.py` con el siguiente contenido:

```python
import psycopg2

def main():
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            dbname="music_db",
            user="postgres",
            password="CAMBIAR_AQUI"
        )
        print("✅ Conexión exitosa a PostgreSQL.")

        # Prueba mínima: preguntar versión del servidor
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            print("Versión del servidor:")
            print(cur.fetchone()[0])

        conn.close()

    except Exception as e:
        print("❌ Error de conexión.")
        print("Detalle:", e)

if __name__ == "__main__":
    main()
```

Ejecutar:

```bash
python test_connection.py
```

Si la conexión es correcta, se mostrará el mensaje de éxito y la versión de PostgreSQL.

> **Figura (obligatoria sugerida):** Captura del resultado exitoso en consola.
> **[FIGURA AQUI: “Conexión exitosa desde Python”]**

---

## 4. Ejemplo: reproducir desde Python el flujo realizado en pgAdmin

### 4.1. Objetivo del ejemplo

En el trabajo previo con pgAdmin se siguió un flujo típico:

1. Consultar tablas existentes.
2. Insertar un nuevo artista.
3. Insertar un nuevo álbum.
4. Crear la relación artista–álbum.
5. Ejecutar una consulta con `JOIN` para verificar.
6. Realizar una actualización y comprobar el resultado.
7. (Opcional) Probar eliminación y observar integridad referencial.

En esta sección se construye una aplicación Python que ejecuta el mismo proceso, de manera programática.

---

### 4.2. Estructura recomendada

Se sugiere crear una carpeta con:

```
python_app/
├── app.py
└── test_connection.py
```

---

### 4.3. Aplicación `app.py`

Crear `app.py` con el siguiente contenido (ajustando credenciales):

```python
import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "music_db",
    "user": "postgres",
    "password": "CAMBIAR_AQUI"
}

def run_query(conn, query, params=None, fetch=False):
    """Ejecuta una consulta SQL. Si fetch=True, retorna resultados."""
    with conn.cursor() as cur:
        cur.execute(query, params)
        if fetch:
            return cur.fetchall()

def main():
    conn = psycopg2.connect(**DB_CONFIG)
    print("✅ Conectado a PostgreSQL.")

    try:
        # 1) Leer artistas existentes
        print("\n1) Artistas actuales:")
        rows = run_query(conn, "SELECT id, name, debut_year, country FROM Artist ORDER BY id;", fetch=True)
        for r in rows:
            print(r)

        # 2) Insertar nuevo artista (Lucho Bermúdez)
        print("\n2) Insertando artista...")
        run_query(conn,
            "INSERT INTO Artist (id, name, debut_year, country) VALUES (%s, %s, %s, %s);",
            (200, "Lucho Bermúdez", 1940, "Colombia")
        )

        # 3) Insertar nuevo álbum
        print("3) Insertando álbum...")
        run_query(conn,
            "INSERT INTO Album (id, name, release_year) VALUES (%s, %s, %s);",
            (90, "Colombia Tierra Querida", 1950)
        )

        # 4) Relacionar artista con álbum
        print("4) Creando relación artista–álbum...")
        run_query(conn,
            "INSERT INTO Artist_Album (artist_id, album_id) VALUES (%s, %s);",
            (200, 90)
        )

        # 5) Verificar con JOIN
        print("\n5) Verificación (JOIN):")
        join_rows = run_query(conn, """
            SELECT a.name AS artist, al.name AS album, al.release_year
            FROM Artist a
            JOIN Artist_Album aa ON aa.artist_id = a.id
            JOIN Album al ON al.id = aa.album_id
            WHERE a.id = %s;
        """, (200,), fetch=True)

        for r in join_rows:
            print(r)

        # 6) Actualizar país (ejemplo de UPDATE)
        print("\n6) Actualizando país a 'CO'...")
        run_query(conn,
            "UPDATE Artist SET country = %s WHERE id = %s;",
            ("CO", 200)
        )

        # 7) Confirmar actualización
        print("7) Confirmación del UPDATE:")
        updated = run_query(conn, "SELECT id, name, country FROM Artist WHERE id = %s;", (200,), fetch=True)
        print(updated[0])

        # Confirmar cambios (COMMIT)
        conn.commit()
        print("\n✅ Cambios confirmados (COMMIT).")

    except Exception as e:
        # Si ocurre un error, se revierten cambios para no dejar la BD a medias
        conn.rollback()
        print("\n❌ Ocurrió un error. Se ejecutó ROLLBACK.")
        print("Detalle:", e)

    finally:
        conn.close()
        print("\n🔒 Conexión cerrada.")

if __name__ == "__main__":
    main()
```

Ejecutar:

```bash
python app.py
```

> **Figura (obligatoria sugerida):** Captura del output de `app.py` mostrando inserciones, JOIN y UPDATE.
> **[FIGURA AQUI: “Ejecución de app.py”]**

---

## 5. Observación conceptual

* **pgAdmin** facilita pruebas manuales y administración.
* **Python** (o Java) permite que la interacción sea parte de un sistema real: aplicaciones, servicios web, APIs, automatización, etc.

En la práctica profesional, lo usual es:

* Guardar la estructura y datos de ejemplo en scripts `.sql` (versionables con Git).
* Usar un lenguaje (Python/Java) para interactuar con la base de datos desde la lógica de negocio.

---

## 6. Actividad sugerida

Se recomienda que, tras ejecutar el ejemplo, se realicen pequeñas modificaciones:

* Cambiar el artista y el álbum por otros valores.
* Insertar una segunda relación en `Artist_Album`.
* Consultar todos los álbumes asociados a un artista.
* Intentar eliminar un álbum y observar qué ocurre si existe una relación activa en la tabla puente.

> **Figura (opcional):** Evidencia de un error por integridad referencial al intentar eliminar un álbum relacionado.
> **[FIGURA AQUI: “Error por integridad referencial”]**

---

Si desea, puedo ayudarte a mejorar este README en el estilo de laboratorio (con checkpoints y preguntas de reflexión) o añadir una sección corta de “Errores comunes y solución” orientada a estudiantes.



