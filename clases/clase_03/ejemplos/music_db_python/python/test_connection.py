import psycopg2

def main():
    try:
        conn = psycopg2.connect(
            host="localhost",               # Reemplaza con la dirección de tu servidor PostgreSQL
            port=5433,                      # Reemplaza con el puerto correcto (5432 es el puerto por defecto de PostgreSQL)
            dbname="music_db",              # Reemplaza con el nombre de tu base de datos
            user="postgres",                # Reemplaza con tu usuario correcto
            password="PASSWORD"             # Reemplaza con tu contraseña correcta
        )
        print("[OK] Conexión exitosa a PostgreSQL.")

        # Prueba mínima: preguntar versión del servidor
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            print("Versión del servidor:")
            print(cur.fetchone()[0])

        conn.close()

    except Exception as e:
        print("[ERROR] Error de conexión.")
        print("Detalle:", e)

if __name__ == "__main__":
    main()