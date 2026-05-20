# Tema 12: Replicación en Bases de Datos

## Descripción

Este tema explica la replicación en bases de datos y cómo ayuda a mantener la disponibilidad y la tolerancia a fallos. Se cubren definiciones básicas, modelos de replicación, el papel del nodo líder y los seguidores, fallos de líder y failover, diferencias entre replicación síncrona y asíncrona, y los problemas de latencia y consistencia que surgen en sistemas distribuidos.

## Integrantes

| Nombre | Correo |
|--------|--------|
| Juan Daniel Atencia Pahuana | - |
| Juan Daniel Rincón Bedoya | - |

## Referencias

- Designing Data-Intensive Applications (base del contenido presentado).
- https://severalnines.com/case-studies/instant-gaming-case-study/
- https://about.gitlab.com/blog/postmortem-of-database-outage-of-january-31/
- https://severalnines.com/case-studies/knorr-bremse-case-study
- https://netflixtechblog.com/dynomite-with-redis-on-aws-benchmarks-5c942fc7ca38
- https://dev.to/vivian-voss/the-backup-that-wasnt-20gi

### Artículos y Documentación

- Definición de replicación: mantener copias de los mismos datos en varias máquinas.
- Problemas de una sola máquina: fallo de hardware, lentitud bajo carga y mantenimiento.
- Arquitectura líder-seguidor: el líder procesa escrituras y los seguidores replican datos para lecturas.
- Fallos de líder y split brain: promoción de seguidores y riesgos de múltiples líderes.
- Replicación síncrona vs asíncrona: seguridad frente a velocidad.
- Modelos de replicación: líder único, multi-líder y sin líder.
- Aplicaciones de replicación para sistemas distribuidos, alta disponibilidad y escalabilidad de lecturas.
