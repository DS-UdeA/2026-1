-- ======================================================
-- 1. DEFINICIÓN DE ESTRUCTURA (DDL)
-- ======================================================

CREATE TABLE Artist (
    id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    year INT,
    country VARCHAR(50)
);

CREATE TABLE Album (
    id INT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    year INT
);

CREATE TABLE Artist_Album (
    artist_id INT NOT NULL,
    album_id INT NOT NULL,
    PRIMARY KEY (artist_id, album_id),
    FOREIGN KEY (artist_id) REFERENCES Artist(id),
    FOREIGN KEY (album_id) REFERENCES Album(id)
);

-- ======================================================
-- 2. CARGA DE DATOS (DML)
-- ======================================================

INSERT INTO Artist (id, name, year, country) VALUES
(101, 'Billie Holiday', 1933, 'USA'),
(102, 'Ella Fitzgerald', 1917, 'USA'),
(103, 'Louis Armstrong', 1922, 'USA');

INSERT INTO Album (id, name, year) VALUES
(11, 'Lady in Satin', 1958),
(22, 'Body and Soul', 1957),
(33, 'what a wonderful world', 1922);

INSERT INTO Artist_Album (artist_id, album_id) VALUES
(101, 11),
(102, 22),
(103, 22),
(103, 33);