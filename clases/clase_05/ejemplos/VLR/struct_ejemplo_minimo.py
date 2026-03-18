# =============================================================================
# Laboratorio de Estructuras de Datos - UdeA
# Tema: Conceptos Previos — Ejemplo mínimo del módulo struct
# Sección: 0.4 del README de la carpeta VLR
# =============================================================================
#
# Este script ilustra el ciclo completo de uso de struct:
#   1. Empaquetar valores Python en bytes binarios (pack)
#   2. Inspeccionar los bytes resultantes uno a uno
#   3. Recuperar los valores originales (unpack) — round-trip
#   4. Leer y escribir sobre un bytearray que simula una página de disco
#
# No requiere dependencias externas. Solo biblioteca estándar de Python.
# Ejecutar con:
#   python struct_ejemplo_minimo.py
# =============================================================================

import struct

print("=" * 60)
print("  Ejemplo mínimo — módulo struct de Python")
print("=" * 60)

# -----------------------------------------------------------------------------
# PASO 1 — Empaquetar
# -----------------------------------------------------------------------------
# Una entrada del slot directory ocupa 4 bytes:
#   offset (2B, uint16 big-endian) + length (2B, uint16 big-endian)
#
# Format string '>HH':
#   '>'  → big-endian
#   'H'  → unsigned short (uint16, 2 bytes)
#   'H'  → unsigned short (uint16, 2 bytes)

offset = 215   # el registro comienza en el byte 215 de la página
length = 41    # el registro ocupa 41 bytes

packed = struct.pack('>HH', offset, length)

print("\n── Paso 1: empaquetar ──────────────────────────────────")
print(f"  offset = {offset}  →  hex: 0x{offset:04X}")
print(f"  length = {length}   →  hex: 0x{length:04X}")
print(f"  struct.pack('>HH', {offset}, {length})")
print(f"  Resultado  : {packed.hex(' ')}")   # 00 d7 00 29
print(f"  Tamaño     : {len(packed)} bytes")
print(f"  Calculado  : {struct.calcsize('>HH')} bytes  (struct.calcsize)")

# -----------------------------------------------------------------------------
# PASO 2 — Inspección byte a byte
# -----------------------------------------------------------------------------
# 215 decimal = 0x00D7
#   Big-endian:    byte[0]=0x00, byte[1]=0xD7   ← MSB primero
#   Little-endian: byte[0]=0xD7, byte[1]=0x00   ← LSB primero
#
# 41 decimal = 0x0029
#   Big-endian:    byte[2]=0x00, byte[3]=0x29

print("\n── Paso 2: inspección byte a byte ─────────────────────")
for i, b in enumerate(packed):
    print(f"  byte[{i}] = 0x{b:02X}  ({b:3d} decimal)")

print()
print("  Nota: 0xD7 = 215. Big-endian escribe 0x00 (MSB) antes")
print("  que 0xD7 (LSB). En little-endian sería al revés: D7 00.")

# -----------------------------------------------------------------------------
# PASO 3 — Desempaquetar (round-trip)
# -----------------------------------------------------------------------------

print("\n── Paso 3: desempaquetar ───────────────────────────────")
recovered_offset, recovered_length = struct.unpack('>HH', packed)

print(f"  struct.unpack('>HH', packed)")
print(f"  offset recuperado : {recovered_offset}")
print(f"  length recuperado : {recovered_length}")

assert recovered_offset == offset, "¡El offset no coincide!"
assert recovered_length == length, "¡El length no coincide!"
print("  Round-trip OK ✓")

# -----------------------------------------------------------------------------
# PASO 4 — pack_into / unpack_from sobre un bytearray (simula una página)
# -----------------------------------------------------------------------------
# En los scripts v6 y v7, la página en memoria es un bytearray de 256 bytes.
# pack_into escribe directamente en una posición del bytearray sin crear
# un objeto bytes intermedio — esto es más eficiente para páginas grandes.

print("\n── Paso 4: pack_into / unpack_from sobre bytearray ────")
page = bytearray(256)    # página de 256 bytes, toda en ceros

SLOT_0_POS = 8           # el primer slot empieza en el byte 8 (tras el header)

print(f"  page antes  : {page[8:12].hex(' ')}  (bytes 8-11, todos en 0x00)")

struct.pack_into('>HH', page, SLOT_0_POS, offset, length)

print(f"  page después: {page[8:12].hex(' ')}  (bytes 8-11 tras pack_into)")

read_back = struct.unpack_from('>HH', page, SLOT_0_POS)
print(f"  unpack_from → offset={read_back[0]}, length={read_back[1]}")

assert read_back[0] == offset
assert read_back[1] == length
print("  Round-trip sobre bytearray OK ✓")

# -----------------------------------------------------------------------------
# EXTRA — comparación big-endian vs little-endian para el mismo par
# -----------------------------------------------------------------------------

print("\n── Extra: big-endian vs little-endian ─────────────────")
be = struct.pack('>HH', offset, length)
le = struct.pack('<HH', offset, length)

print(f"  Big-endian    '>HH': {be.hex(' ')}   ← 0x00 primero (MSB)")
print(f"  Little-endian '<HH': {le.hex(' ')}   ← 0xD7 primero (LSB)")
print()
print("  Mismo número, mismo tamaño, distinto orden de bytes.")
print("  El motor debe usar siempre el mismo orden al leer y escribir.")

print("\n" + "=" * 60)
print("  Fin del ejemplo. Sin errores.")
print("=" * 60)
