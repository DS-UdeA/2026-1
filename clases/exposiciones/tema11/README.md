# Tema 11: LSM Trees

## Descripción

Este tema trata la arquitectura y los casos reales de los Log-Structured Merge Trees (LSM Trees). Se explica qué es un LSM Tree, su importancia para escrituras intensivas, las diferencias con los B-Trees, la arquitectura general con MemTable, Write-Ahead Log (WAL) y SSTables, su ciclo de vida y mantenimiento, así como sus ventajas, desventajas y aplicaciones en sistemas de bases de datos modernas.

## Integrantes

| Nombre | Correo |
|--------|--------|
| Juan Andrés Ramírez Patiño | - |
| Julián Esteban Hurtado Serna | - |
| Juan Pablo Ocampo Soto | - |

## Referencias

- LSM: qué es y por qué es importante para las bases de datos. (28 de agosto de 2025). InnovaciónDigital360. https://www.innovaciondigital360.com/big-data/lsm-para-empresas-beneficios-clave-y-aplicaciones/
- Fiona. (2026). Estructuras de datos en disco: árboles B y LSM. Beefed.ai. https://beefed.ai/es/on-disk-data-structures-btrees-lsms

### Artículos y Documentación

- Definición de LSM Trees y su operación como estructura de datos clave-valor.
- Importancia de los LSM Trees para escrituras masivas y aplicaciones de datos en tiempo real.
- Diferencias entre LSM Trees y B-Trees.
- Arquitectura de LSM Trees: MemTable, WAL, SSTables y Bloom Filters.
- Ciclo de vida del dato: escritura en memoria, flush a disco y uso de compaction.
- Pros y contras: alta velocidad de escritura, amplificación de lectura/escritura y latencia por compactación.
- Casos de uso reales: RocksDB, Apache Cassandra, ScyllaDB, Bigtable, IoT, mensajería, telemetría, logs y blockchain.
