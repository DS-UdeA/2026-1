-- ======================================================
-- SCRIPT 3: CONSULTAS DE PRÁCTICA (VERIFICACIÓN + CRUD)
-- ======================================================
-- Se ejecuta al final para comprobar que todo quedó bien.
-- ======================================================

-- A) Ver tablas completas (lectura básica)
SELECT * FROM Artist;
SELECT * FROM Album;
SELECT * FROM Artist_Album;

-- B) Consulta más “real”: artista con sus álbumes
-- JOIN = “unir tablas” usando columnas relacionadas
SELECT
  a.name AS artist,
  al.name AS album,
  al.release_year
FROM Artist a
JOIN Artist_Album aa ON aa.artist_id = a.id
JOIN Album al ON al.id = aa.album_id
ORDER BY a.name;

-- C) CRUD guiado (ejecuta uno por uno en clase)

-- CREATE: crear un artista nuevo
-- INSERT INTO Artist (id, name, debut_year, country)
-- VALUES (104, 'New Artist', 2020, 'CO');

-- READ: buscar artistas por país
-- SELECT * FROM Artist WHERE country = 'USA';

-- UPDATE: actualizar el país de un artista
-- UPDATE Artist
-- SET country = 'United States'
-- WHERE country = 'USA';

-- DELETE: borrar un artista (si no está referenciado en Artist_Album)
-- DELETE FROM Artist WHERE id = 104;