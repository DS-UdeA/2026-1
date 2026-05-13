# Tema 5: B+Tree inserción y split

## Descripción

Este tema explora el proceso de inserción en árboles B+ y el manejo de splits cuando ocurre overflow en nodos, asegurando el mantenimiento de las propiedades del árbol. Se incluyen ejemplos prácticos y una implementación en Python.

- Introducción a B+ Trees: estructura, propiedades y diferencias con B-Trees
- Inserción básica en hojas
- Concepto de overflow y capacidad máxima de nodos (2d claves)
- Split de hojas: división en dos, clave mediana se copia al padre
- Split de nodos internos: clave mediana sube al padre
- Split de la raíz: crecimiento en altura del árbol
- Implementación en Python: clases Nodo y BPlusTree
- Demostración con secuencia de inserciones que provocan splits
- Lista enlazada de hojas para recorridos secuenciales

## Integrantes

| Nombre | Correo |
|--------|--------|
| Juan José Gomez Castaño | - |
| Jose Manuel Londoño Castaño | - |
| Mateo Upegui Borja | - |

## Referencias

- Bayer, R., & McCreight, E. (1972). Organization and maintenance of large ordered indexes. Acta Informatica, 1(3), 173-189.
- Comer, D. (1979). The ubiquitous B-tree. ACM Computing Surveys, 11(2), 121-137.
- Silberschatz, A., Korth, H. F., & Sudarshan, S. (2020). Database System Concepts (7th ed.). McGraw-Hill.
- Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2009). Introduction to Algorithms (3rd ed.). MIT Press.

### Artículos y Documentación

- Documentación oficial de Python: https://docs.python.org/3/
- Jupyter Notebook: https://jupyter.org/
- Repositorio del curso: https://github.com/DS-UdeA/2026-1

