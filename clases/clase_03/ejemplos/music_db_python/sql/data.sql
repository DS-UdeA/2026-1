-- ======================================================
-- SCRIPT 2: INSERTAR DATOS (POBLACIÓN)
-- ======================================================
-- Se ejecuta DESPUÉS de crear tablas.
-- ======================================================

-- 1) Insertar artistas
INSERT INTO Artist (id, name, debut_year, country) VALUES
(101, 'Billie Holiday', 1933, 'USA'),
(102, 'Ella Fitzgerald', 1917, 'USA'),
(103, 'Louis Armstrong', 1922, 'USA');

-- 2) Insertar álbumes
INSERT INTO Album (id, name, release_year) VALUES
(11, 'Lady in Satin', 1958),
(22, 'Body and Soul', 1957),
(33, 'What a Wonderful World', 1967);

-- 3) Relacionar artistas con álbumes (tabla puente)
-- Lee cada fila como: (artista, álbum)
INSERT INTO Artist_Album (artist_id, album_id) VALUES
(101, 11),  -- Billie Holiday -> Lady in Satin
(102, 22),  -- Ella Fitzgerald -> Body and Soul
(103, 22),  -- Louis Armstrong -> Body and Soul (ejemplo de relación)
(103, 33);  -- Louis Armstrong -> What a Wonderful World