# ============================================================================
# Laboratorio de Estructuras de Datos - UdeA
# Tema: Registros de Longitud Variable (VLR) — Los Tres Formatos
# Versión: v5 — Serialización a nivel de registro (sin páginas todavía)
# ============================================================================
#
# This file demonstrates the three VLR storage formats from the slides:
#
#   Format 1 — Delimiter-based      : fields separated by a sentinel byte ('$')
#   Format 2 — Length prefix        : each field prefixed with its byte length
#   Format 3 — Offset array         : header holds (offset, length) pairs + null bitmap
#
# Schema: instructor(ID varchar(5), name varchar(20),
#                    dept_name varchar(20), salary numeric(8,2))
#
# Key contrast with v4: there is NO padding. Records that store shorter strings
# ("Wu" vs "Srinivasan") genuinely occupy fewer bytes on disk.
# ============================================================================

import struct

# ---------------------------------------------------------------------------
# SCHEMA CONSTANTS
# ---------------------------------------------------------------------------
DELIMITER     = b'$'        # sentinel used by Format 1
N_VAR_FIELDS  = 3           # ID, name, dept_name are variable-length fields
SALARY_BYTES  = 8           # salary stored as big-endian int64 (in cents)
NULL_BYTES    = 1           # null bitmap: 1 byte covers up to 8 nullable fields

# The fixed section of a Format-3 record consists of:
#   N_VAR_FIELDS × 4 bytes  (one (offset, length) pair per varchar field)
#   + SALARY_BYTES          (salary, fixed numeric)
#   + NULL_BYTES            (null bitmap)
FIXED_SECTION = N_VAR_FIELDS * 4 + SALARY_BYTES + NULL_BYTES   # = 21 bytes

# Null bitmap bit masks — one bit per field
NULL_ID       = 0b00000001  # bit 0 → ID is NULL
NULL_NAME     = 0b00000010  # bit 1 → name is NULL
NULL_DEPTNAME = 0b00000100  # bit 2 → dept_name is NULL
NULL_SALARY   = 0b00001000  # bit 3 → salary is NULL


# ============================================================================
# FORMAT 1: DELIMITER-BASED (CSV-style)
# ============================================================================

def serialize_delimited(record: tuple) -> bytes:
    """
    Joins all field values with a '$' delimiter byte.

    Layout:  field1 $ field2 $ field3 $ field4

    Pro  : trivially simple to produce.
    Con  : O(n) field access — the engine must scan every byte from the start
           of the record to locate any specific field.
    """
    emp_id, name, dept_name, salary = record
    parts = [str(emp_id), name, dept_name, f"{salary:.2f}"]
    return DELIMITER.join(p.encode('utf-8') for p in parts)


def deserialize_delimited(data: bytes) -> tuple:
    """Splits on '$' and casts each field to its expected Python type."""
    parts = data.split(DELIMITER)
    return (
        int(parts[0]),
        parts[1].decode('utf-8'),
        parts[2].decode('utf-8'),
        float(parts[3]),
    )


# ============================================================================
# FORMAT 2: LENGTH PREFIX
# ============================================================================

def serialize_length_prefix(record: tuple) -> bytes:
    """
    Prefixes the entire record with a field count (2 bytes), then prefixes
    each individual field with its byte length (2 bytes).

    Layout:  [N fields (2B)] | [len1 (2B)] [data1] | [len2 (2B)] [data2] | ...

    Pro  : knowing a field's length allows skipping it in one seek rather than
           scanning byte-by-byte — better than pure delimiters.
    Con  : field access is still sequential; finding field k requires reading
           the length prefixes of fields 0 … k−1.
    """
    emp_id, name, dept_name, salary = record
    fields = [str(emp_id), name, dept_name, f"{salary:.2f}"]

    buf = struct.pack('>H', len(fields))           # 2-byte field count (big-endian)
    for f in fields:
        enc = f.encode('utf-8')
        buf += struct.pack('>H', len(enc)) + enc   # 2-byte length + raw bytes
    return buf


def deserialize_length_prefix(data: bytes) -> tuple:
    """Reads the field count, then iterates over length-prefixed fields."""
    pos = 0
    n_fields = struct.unpack_from('>H', data, pos)[0];  pos += 2
    fields = []
    for _ in range(n_fields):
        flen = struct.unpack_from('>H', data, pos)[0];  pos += 2
        fields.append(data[pos:pos + flen].decode('utf-8'));    pos += flen
    return (int(fields[0]), fields[1], fields[2], float(fields[3]))


# ============================================================================
# FORMAT 3: OFFSET ARRAY  (standard in PostgreSQL, SQLite, etc.)
# ============================================================================

def serialize_offset_array(record: tuple, null_mask: int = 0) -> bytes:
    """
    Packs a record using the offset-array format — the industry standard for
    variable-length records in production disk-based DBMSes.

    Fixed section layout (bytes 0–20, total 21 bytes):
      Bytes  0– 3  : (offset_id,        length_id)        — 2 B each
      Bytes  4– 7  : (offset_name,      length_name)
      Bytes  8–11  : (offset_dept_name, length_dept_name)
      Bytes 12–19  : salary stored as big-endian int64 in cents (fixed width)
      Byte   20    : null bitmap  (bit i = 1  →  field i is NULL)

    Variable section (starts at byte 21):
      Concatenated UTF-8 bytes of ID, name, dept_name in field order.
      NULL fields contribute ZERO bytes to this section.

    null_mask : use NULL_ID | NULL_NAME | NULL_DEPTNAME | NULL_SALARY constants.

    Pro  : O(1) field access — the engine reads the (offset, length) pair and
           jumps directly to the field's bytes with a single seek.
           NULL values consume zero storage in the variable section.
    """
    emp_id, name, dept_name, salary = record
    varchar_vals = [str(emp_id), name, dept_name]

    # --- Build variable data section and compute offset-length pairs ---
    var_data = b''
    pairs    = []
    cur      = FIXED_SECTION       # variable data begins right after the fixed section

    for i, val in enumerate(varchar_vals):
        if null_mask & (1 << i):   # field is NULL — no bytes emitted
            pairs.append((0, 0))
        else:
            enc = val.encode('utf-8')
            pairs.append((cur, len(enc)))
            var_data += enc
            cur      += len(enc)

    # --- Assemble fixed section ---
    fixed = b''
    for (off, ln) in pairs:
        fixed += struct.pack('>HH', off, ln)       # 4 bytes per (offset, length) pair

    sal_val = 0 if (null_mask & NULL_SALARY) else int((salary or 0) * 100)
    fixed  += struct.pack('>q', sal_val)            # 8 bytes — salary as cents
    fixed  += struct.pack('B',  null_mask)          # 1 byte  — null bitmap

    return fixed + var_data


def deserialize_offset_array(data: bytes) -> tuple:
    """
    Recovers a record from the offset-array format.
    Each varchar field is located in O(1) via its (offset, length) pair.
    """
    # Read (offset, length) pairs from the fixed section
    pairs = []
    for i in range(N_VAR_FIELDS):
        off, ln = struct.unpack_from('>HH', data, i * 4)
        pairs.append((off, ln))

    # Read salary (big-endian int64 starting at byte N_VAR_FIELDS * 4 = 12)
    salary_raw = struct.unpack_from('>q', data, N_VAR_FIELDS * 4)[0]

    # Read null bitmap (1 byte immediately after salary)
    null_mask = struct.unpack_from('B', data, N_VAR_FIELDS * 4 + SALARY_BYTES)[0]

    # Decode each varchar field using its (offset, length) pair
    varchar_vals = []
    for i, (off, ln) in enumerate(pairs):
        if null_mask & (1 << i):
            varchar_vals.append(None)
        elif ln == 0:
            varchar_vals.append('')
        else:
            varchar_vals.append(data[off:off + ln].decode('utf-8'))

    salary = None if (null_mask & NULL_SALARY) else salary_raw / 100.0

    return (
        int(varchar_vals[0]) if varchar_vals[0] is not None else None,
        varchar_vals[1],
        varchar_vals[2],
        salary,
    )


# ============================================================================
# HELPERS
# ============================================================================

def _hexdump(label: str, data: bytes):
    """Prints a compact annotated hex view of a serialized record."""
    hex_str = ' '.join(f'{b:02x}' for b in data)
    print(f"  [{label}]")
    print(f"    Size : {len(data)} bytes")
    print(f"    Hex  : {hex_str}")


def _compare_formats(record: tuple):
    """Serializes one record in all three formats and prints a comparison."""
    d1 = serialize_delimited(record)
    d2 = serialize_length_prefix(record)
    d3 = serialize_offset_array(record)
    print(f"  Delimiter  : {len(d1):3d} bytes")
    print(f"  Len-prefix : {len(d2):3d} bytes")
    print(f"  Offset arr : {len(d3):3d} bytes")


# ============================================================================
# MAIN — classroom demo
# ============================================================================
if __name__ == "__main__":
    print("=" * 62)
    print("  Heap Files v5 — VLR Record Formats")
    print("=" * 62)

    # Instructor records from the slides
    RECORDS = [
        (22222, "Einstein",   "Physics",    95000.00),
        (12121, "Wu",         "Finance",    90000.00),
        (10101, "Srinivasan", "Comp. Sci.", 65000.00),
        (45565, "Katz",       "Comp. Sci.", 75000.00),
    ]

    # ------------------------------------------------------------------
    # FORMAT 1: DELIMITER-BASED
    # ------------------------------------------------------------------
    print("\n=== FORMAT 1 — Delimiter-based ===")
    for rec in RECORDS:
        raw       = serialize_delimited(rec)
        recovered = deserialize_delimited(raw)
        _hexdump(rec[1], raw)
        assert recovered == rec, "Round-trip failed!"
        print(f"    Decoded: {recovered}")

    # ------------------------------------------------------------------
    # FORMAT 2: LENGTH PREFIX
    # ------------------------------------------------------------------
    print("\n=== FORMAT 2 — Length Prefix ===")
    for rec in RECORDS:
        raw       = serialize_length_prefix(rec)
        recovered = deserialize_length_prefix(raw)
        _hexdump(rec[1], raw)
        assert recovered == rec, "Round-trip failed!"
        print(f"    Decoded: {recovered}")

    # ------------------------------------------------------------------
    # FORMAT 3: OFFSET ARRAY
    # ------------------------------------------------------------------
    print("\n=== FORMAT 3 — Offset Array ===")
    for rec in RECORDS:
        raw       = serialize_offset_array(rec)
        recovered = deserialize_offset_array(raw)
        _hexdump(rec[1], raw)
        assert recovered == rec, "Round-trip failed!"
        print(f"    Decoded: {recovered}")

    # ------------------------------------------------------------------
    # NULL BITMAP DEMO (Format 3 only)
    # ------------------------------------------------------------------
    print("\n=== FORMAT 3 — Null Bitmap Demo ===")

    # Case A: salary is NULL
    crick = (76766, "Crick", "Biology", None)
    raw_a = serialize_offset_array(crick, null_mask=NULL_SALARY)
    _hexdump("Crick — salary=NULL", raw_a)
    rec_a = deserialize_offset_array(raw_a)
    print(f"    Decoded: {rec_a}")
    print(f"    salary field → {rec_a[3]}")

    # Case B: dept_name is NULL
    kim = (98345, "Kim", None, 80000.00)
    raw_b = serialize_offset_array(kim, null_mask=NULL_DEPTNAME)
    _hexdump("Kim — dept_name=NULL", raw_b)
    rec_b = deserialize_offset_array(raw_b)
    print(f"    Decoded: {rec_b}")

    # ------------------------------------------------------------------
    # SIZE COMPARISON — same record, three formats
    # ------------------------------------------------------------------
    print("\n=== Size comparison (same record each time) ===")
    for rec in RECORDS:
        print(f"\n  Record: {rec[1]}")
        _compare_formats(rec)

    print("\n  Observation:")
    wu_d1 = len(serialize_delimited((12121, "Wu", "Finance", 90000.00)))
    wu_d3 = len(serialize_offset_array((12121, "Wu", "Finance", 90000.00)))
    sr_d1 = len(serialize_delimited((10101, "Srinivasan", "Comp. Sci.", 65000.00)))
    sr_d3 = len(serialize_offset_array((10101, "Srinivasan", "Comp. Sci.", 65000.00)))
    print(f"  'Wu'         → offset-array: {wu_d3} bytes (delimiter: {wu_d1})")
    print(f"  'Srinivasan' → offset-array: {sr_d3} bytes (delimiter: {sr_d1})")
    print(f"  Difference   : {sr_d3 - wu_d3} bytes — only the actual data, no padding")
    print()
