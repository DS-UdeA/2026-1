import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "music_db",
    "user": "postgres",
    "password": "PASSWORD"
}

def run_query(conn, query, params=None, fetch=False):
    """Ejecuta una consulta SQL. Si fetch=True, retorna resultados."""
    with conn.cursor() as cur:
        cur.execute(query, params)
        if fetch:
            return cur.fetchall()

def main():
    conn = psycopg2.connect(**DB_CONFIG)
    print("Conectado a PostgreSQL.")

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
        
        """
        # 8) Intento de eliminación indebida
        print("\n8) Intentando eliminar un álbum relacionado...")
        run_query(conn, "DELETE FROM Album WHERE id = %s;", (90,)) 
        """

        # Confirmar cambios (COMMIT)
        conn.commit()
        print("\n[OK] Cambios confirmados (COMMIT).")

    except Exception as e:
        # Si ocurre un error, se revierten cambios para no dejar la BD a medias
        conn.rollback()
        print("\n[ERROR] Ocurrió un error. Se ejecutó ROLLBACK.")
        print("Detalle:", e)

    finally:
        conn.close()
        print("\nConexión cerrada.")

if __name__ == "__main__":
    main()