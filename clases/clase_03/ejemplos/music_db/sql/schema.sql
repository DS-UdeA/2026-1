-- ======================================================
-- SCRIPT 1: CREAR LAS TABLAS (ESTRUCTURA)
-- ======================================================
-- Idea clave:
--   Una base de datos no es un “proyecto” como Java.
--   Aquí el “proyecto” son estos scripts: definen y documentan la BD.
--
-- Este archivo se ejecuta UNA VEZ al iniciar (o cuando quieras reiniciar el ejercicio).
-- ======================================================

-- (Opcional para clase) Si ya habías creado tablas antes, bórralas para empezar limpio.
-- Importante: borramos primero la tabla puente (Artist_Album) porque depende de las otras.
DROP TABLE IF EXISTS Artist_Album;
DROP TABLE IF EXISTS Album;
DROP TABLE IF EXISTS Artist;

-- ======================================================
-- TABLA 1: Artist (artistas)
-- ======================================================
-- Columnas:
--   id: identificador único del artista (no se repite)
--   name: nombre del artista (obligatorio)
--   debut_year: año aproximado de inicio/carrera (dato informativo)
--   country: país (dato informativo)
CREATE TABLE Artist (
  id INT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  debut_year INT,
  country VARCHAR(50)
);

-- ======================================================
-- TABLA 2: Album (álbumes)
-- ======================================================
-- Columnas:
--   id: identificador único del álbum
--   name: nombre del álbum (obligatorio)
--   release_year: año de publicación (dato informativo)
CREATE TABLE Album (
  id INT PRIMARY KEY,
  name VARCHAR(150) NOT NULL,
  release_year INT
);

-- ======================================================
-- TABLA 3: Artist_Album (relación muchos-a-muchos)
-- ======================================================
-- ¿Por qué existe esta tabla?
--   Un artista puede tener muchos álbumes,
--   y un álbum puede estar asociado a varios artistas (colaboraciones).
--
-- Esta tabla guarda PARES (artist_id, album_id).
CREATE TABLE Artist_Album (
  artist_id INT NOT NULL,
  album_id INT NOT NULL,

  -- Clave primaria compuesta:
  --   evita duplicados del mismo par (artista, álbum)
  PRIMARY KEY (artist_id, album_id),

  -- Claves foráneas:
  --   obligan a que el artista y el álbum EXISTAN antes de relacionarlos
  FOREIGN KEY (artist_id) REFERENCES Artist(id),
  FOREIGN KEY (album_id) REFERENCES Album(id)
);