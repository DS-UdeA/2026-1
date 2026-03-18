# ============================================================================
# Laboratorio de Estructuras de Datos - UdeA
# Tema: Slotted Page — Página Ranurada para Registros de Longitud Variable
# Versión: v6 — Implementación completa de la Slotted Page con I/O a disco
# ============================================================================
#
# Builds on the offset-array format from v5.
#
# Slotted Page anatomy (slides 31–33):
#
#   Byte 0                                               Byte PAGE_SIZE-1
#   ┌─────────┬────────────────────────┬──────────────────────────────────┐
#   │ HEADER  │  SLOT DIRECTORY  →→→   │  ←←←  RECORD AREA               │
#   │  8 B    │  grows rightward       │  grows leftward                  │
#   └─────────┴────────────────────────┴──────────────────────────────────┘
#                                      ↑                ↑
#                                  free_ptr          data_ptr
#                                  (end of          (start of
#                                 slot dir)         record area)
#
# Page Header (8 bytes, fixed):
#   num_slots (2B) — total slot entries in the directory
#   free_ptr  (2B) — byte offset where free space begins (= end of slot dir)
#   data_ptr  (2B) — byte offset where record area begins (= start of records)
#   page_id   (2B) — logical identifier of this page
#
# Slot Entry (4 bytes each):
#   offset (2B) — byte offset of the record within the page; 0xFFFF = deleted
#   length (2B) — byte length of the record; 0 when deleted
#
# RID = (page_id, slot_id) — stable across internal reorganizations because
# external references point to the SLOT, not the physical byte position.
# ============================================================================

import struct
import os

# ---------------------------------------------------------------------------
# VLR SERIALIZATION (self-contained copy from v5)
# ---------------------------------------------------------------------------

N_VAR_FIELDS  = 3
SALARY_BYTES  = 8
NULL_BYTES    = 1
FIXED_SECTION = N_VAR_FIELDS * 4 + SALARY_BYTES + NULL_BYTES   # 21 bytes

NULL_ID       = 0b00000001
NULL_NAME     = 0b00000010
NULL_DEPTNAME = 0b00000100
NULL_SALARY   = 0b00001000


def serialize_offset_array(record: tuple, null_mask: int = 0) -> bytes:
    """
    Serializes an instructor record using the offset-array format.
    See heap_file_v5_vlr_formats.py for the full layout description.
    """
    emp_id, name, dept_name, salary = record
    varchar_vals = [str(emp_id), name, dept_name]

    var_data = b''
    pairs    = []
    cur      = FIXED_SECTION

    for i, val in enumerate(varchar_vals):
        if null_mask & (1 << i):
            pairs.append((0, 0))
        else:
            enc = val.encode('utf-8')
            pairs.append((cur, len(enc)))
            var_data += enc
            cur      += len(enc)

    fixed = b''
    for (off, ln) in pairs:
        fixed += struct.pack('>HH', off, ln)

    sal_val = 0 if (null_mask & NULL_SALARY) else int((salary or 0) * 100)
    fixed  += struct.pack('>q', sal_val)
    fixed  += struct.pack('B',  null_mask)

    return fixed + var_data


def deserialize_offset_array(data: bytes) -> tuple:
    """Recovers an instructor record from the offset-array format."""
    pairs = []
    for i in range(N_VAR_FIELDS):
        off, ln = struct.unpack_from('>HH', data, i * 4)
        pairs.append((off, ln))

    salary_raw = struct.unpack_from('>q', data, N_VAR_FIELDS * 4)[0]
    null_mask  = struct.unpack_from('B',  data, N_VAR_FIELDS * 4 + SALARY_BYTES)[0]

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
        varchar_vals[1], varchar_vals[2], salary,
    )


# ---------------------------------------------------------------------------
# PAGE ARCHITECTURE CONSTANTS
# ---------------------------------------------------------------------------

PAGE_SIZE        = 256      # bytes per page — small for classroom visibility
PAGE_HEADER_SIZE = 8        # num_slots(2) + free_ptr(2) + data_ptr(2) + page_id(2)
SLOT_SIZE        = 4        # offset(2) + length(2) per slot directory entry
SLOT_DELETED     = 0xFFFF   # sentinel: a slot with offset=0xFFFF is marked deleted

FILE_NAME = "my_database_v6.dat"


# ============================================================================
# PAGE-LEVEL OPERATIONS  (operate on an in-memory bytearray)
# ============================================================================

def create_empty_page(page_id: int) -> bytearray:
    """
    Allocates PAGE_SIZE bytes and initializes the page header.

    Initial state:
      num_slots = 0           (no slots in directory yet)
      free_ptr  = PAGE_HEADER_SIZE   (slot dir starts right after header)
      data_ptr  = PAGE_SIZE          (record area starts at the very end)
    The entire data region is zeroed — no records, no slot entries.
    """
    page = bytearray(PAGE_SIZE)
    struct.pack_into('>HHHH', page, 0,
                     0,                # num_slots
                     PAGE_HEADER_SIZE, # free_ptr  (= end of header = start of slot dir)
                     PAGE_SIZE,        # data_ptr  (= start of record area)
                     page_id)          # page_id
    return page


def _read_header(page: bytearray) -> tuple:
    """Returns (num_slots, free_ptr, data_ptr, page_id) from the page header."""
    return struct.unpack_from('>HHHH', page, 0)


def _write_header(page: bytearray,
                  num_slots: int, free_ptr: int, data_ptr: int, page_id: int):
    struct.pack_into('>HHHH', page, 0, num_slots, free_ptr, data_ptr, page_id)


def _read_slot(page: bytearray, slot_id: int) -> tuple:
    """Returns (offset, length) for a given slot index."""
    pos = PAGE_HEADER_SIZE + slot_id * SLOT_SIZE
    return struct.unpack_from('>HH', page, pos)


def _write_slot(page: bytearray, slot_id: int, offset: int, length: int):
    pos = PAGE_HEADER_SIZE + slot_id * SLOT_SIZE
    struct.pack_into('>HH', page, pos, offset, length)


def get_free_space(page: bytearray) -> int:
    """Returns the number of bytes available in the free-space gap."""
    _, free_ptr, data_ptr, _ = _read_header(page)
    return data_ptr - free_ptr


def insert_into_page(page: bytearray, record_bytes: bytes) -> int:
    """
    Inserts a variable-length record into the slotted page.

    Protocol (slide 35):
      1. Find the first deleted slot to reuse (avoids growing the directory).
         If none exists, a new slot entry will be appended.
      2. Check that the free-space gap is large enough for:
            record data  +  (SLOT_SIZE if no deleted slot to reuse, else 0)
      3. Write the record bytes at the new data_ptr position (growing left).
      4. Write / update the slot entry.
      5. Update the page header.

    Returns the assigned slot_id, or -1 if the page has insufficient space.
    """
    num_slots, free_ptr, data_ptr, page_id = _read_header(page)
    rec_len = len(record_bytes)

    # Look for a reusable deleted slot
    reuse_slot = None
    for i in range(num_slots):
        off, _ = _read_slot(page, i)
        if off == SLOT_DELETED:
            reuse_slot = i
            break

    # Determine how much space is actually needed
    dir_overhead = 0 if reuse_slot is not None else SLOT_SIZE
    if get_free_space(page) < rec_len + dir_overhead:
        return -1   # page is full

    # Place the record at the new data_ptr (grows toward lower addresses)
    data_ptr -= rec_len
    page[data_ptr:data_ptr + rec_len] = record_bytes

    # Assign slot_id: reuse a deleted entry or create a new one
    if reuse_slot is not None:
        slot_id = reuse_slot
        # free_ptr and num_slots remain unchanged — directory size does not grow
    else:
        slot_id   = num_slots
        num_slots += 1
        free_ptr  += SLOT_SIZE   # slot directory expanded by one entry

    _write_slot(page, slot_id, data_ptr, rec_len)
    _write_header(page, num_slots, free_ptr, data_ptr, page_id)
    return slot_id


def delete_from_page(page: bytearray, slot_id: int) -> bool:
    """
    Logical delete (slide 36): marks the slot entry as deleted by writing
    SLOT_DELETED (0xFFFF) in the offset field.

    The record bytes in the data area are NOT overwritten — the physical
    space is reclaimed lazily (during compaction in v7, or by reuse).
    """
    num_slots, *_ = _read_header(page)
    if slot_id >= num_slots:
        return False
    off, _ = _read_slot(page, slot_id)
    if off == SLOT_DELETED:
        return False    # already deleted
    _write_slot(page, slot_id, SLOT_DELETED, 0)
    return True


def read_from_page(page: bytearray, slot_id: int):
    """
    Retrieves a record by its slot_id.

    Indirection layer (slide 32): the engine reads the (offset, length) pair
    from the slot directory and then jumps to the record's physical position.
    External references never need to know where the record physically is.

    Returns raw bytes, or None if the slot is deleted or out of range.
    """
    num_slots, *_ = _read_header(page)
    if slot_id >= num_slots:
        return None
    off, ln = _read_slot(page, slot_id)
    if off == SLOT_DELETED:
        return None
    return bytes(page[off:off + ln])


# ============================================================================
# FILE-LEVEL I/O
# ============================================================================

def _load_page(page_id: int):
    """Reads one PAGE_SIZE block from disk. Returns a bytearray or None."""
    if not os.path.exists(FILE_NAME):
        return None
    if page_id * PAGE_SIZE >= os.path.getsize(FILE_NAME):
        return None
    with open(FILE_NAME, 'rb') as f:
        f.seek(page_id * PAGE_SIZE)
        return bytearray(f.read(PAGE_SIZE))


def _save_page(page_id: int, page: bytearray):
    """Writes a page bytearray back to its exact position on disk."""
    with open(FILE_NAME, 'r+b') as f:
        f.seek(page_id * PAGE_SIZE)
        f.write(bytes(page))


def _page_count() -> int:
    """Returns the number of pages currently stored in the file."""
    if not os.path.exists(FILE_NAME):
        return 0
    return os.path.getsize(FILE_NAME) // PAGE_SIZE


def _append_page(page: bytearray):
    """Appends a new page to the end of the database file."""
    with open(FILE_NAME, 'ab') as f:
        f.write(bytes(page))


# ============================================================================
# HIGH-LEVEL DML OPERATIONS
# ============================================================================

def insert_record(record: tuple, null_mask: int = 0) -> tuple:
    """
    Serializes the record and finds the first page with sufficient free space.
    Creates a new page if no existing page can accommodate the record.
    Returns the assigned RID = (page_id, slot_id).
    """
    record_bytes = serialize_offset_array(record, null_mask)

    # Scan existing pages for space (first-fit strategy)
    for page_id in range(_page_count()):
        page    = _load_page(page_id)
        slot_id = insert_into_page(page, record_bytes)
        if slot_id >= 0:
            _save_page(page_id, page)
            print(f"[INSERT] '{record[1]}' "
                  f"→ RID({page_id},{slot_id})  [{len(record_bytes)} bytes]")
            return (page_id, slot_id)

    # No existing page has enough space — allocate a new one
    page_id  = _page_count()
    new_page = create_empty_page(page_id)
    _append_page(new_page)

    page    = _load_page(page_id)
    slot_id = insert_into_page(page, record_bytes)
    _save_page(page_id, page)
    print(f"[INSERT] '{record[1]}' "
          f"→ RID({page_id},{slot_id})  [{len(record_bytes)} bytes]  ← new page")
    return (page_id, slot_id)


def select_by_rid(page_id: int, slot_id: int):
    """
    Retrieves a record using its RID = (page_id, slot_id).
    Uses the slot directory for O(1) indirection to the physical position.
    Returns the deserialized record tuple or None.
    """
    page = _load_page(page_id)
    if page is None:
        return None
    raw = read_from_page(page, slot_id)
    return deserialize_offset_array(raw) if raw else None


def delete_by_rid(page_id: int, slot_id: int) -> bool:
    """
    Marks a record as logically deleted by setting its slot entry to SLOT_DELETED.
    The record bytes remain on disk until compaction (v7) reclaims the space.
    """
    page = _load_page(page_id)
    if page is None:
        return False
    result = delete_from_page(page, slot_id)
    if result:
        _save_page(page_id, page)
        print(f"[DELETE] RID({page_id},{slot_id}) marked as deleted")
    return result


def scan_all():
    """Full sequential scan across all pages and all valid slots."""
    print("\n[SCAN] Full table scan:")
    found = False
    for page_id in range(_page_count()):
        page = _load_page(page_id)
        num_slots, *_ = _read_header(page)
        for slot_id in range(num_slots):
            rec = select_by_rid(page_id, slot_id)
            if rec:
                print(f"  RID({page_id},{slot_id}) → {rec}")
                found = True
    if not found:
        print("  (no records found)")


# ============================================================================
# DEBUG / INSPECTION
# ============================================================================

def print_page_layout(page: bytearray):
    """Prints a human-readable summary of a page's memory layout."""
    num_slots, free_ptr, data_ptr, page_id = _read_header(page)
    print(f"\n  ── Page {page_id} Layout ──────────────────────────────")
    print(f"  Header     : bytes   0 – {PAGE_HEADER_SIZE - 1}")
    print(f"  Slot dir   : bytes {PAGE_HEADER_SIZE:3d} – {free_ptr - 1:3d}"
          f"   ({num_slots} slot{'s' if num_slots != 1 else ''},"
          f" {num_slots * SLOT_SIZE} bytes)")
    print(f"  Free space : bytes {free_ptr:3d} – {data_ptr - 1:3d}"
          f"   ({get_free_space(page)} bytes available)")
    print(f"  Record area: bytes {data_ptr:3d} – {PAGE_SIZE - 1:3d}")
    print(f"  Slots:")
    for i in range(num_slots):
        off, ln = _read_slot(page, i)
        if off == SLOT_DELETED:
            print(f"    [{i}] DELETED")
        else:
            rec = deserialize_offset_array(bytes(page[off:off + ln]))
            print(f"    [{i}] offset={off:3d}, len={ln:2d}"
                  f"  →  id={rec[0]}, name='{rec[1]}', dept='{rec[2]}', salary={rec[3]}")


# ============================================================================
# MAIN — classroom demo
# ============================================================================
if __name__ == "__main__":
    if os.path.exists(FILE_NAME):
        os.remove(FILE_NAME)

    print("=" * 62)
    print("  Heap Files v6 — Slotted Page")
    print("=" * 62)

    # ------------------------------------------------------------------
    # Phase 1: Initial inserts
    # ------------------------------------------------------------------
    print("\n[Phase 1] Inserting records")
    rid_einstein   = insert_record((22222, "Einstein",   "Physics",    95000.00))
    rid_wu         = insert_record((12121, "Wu",         "Finance",    90000.00))
    rid_el_said    = insert_record((32343, "El Said",    "History",    60000.00))
    rid_katz       = insert_record((45565, "Katz",       "Comp. Sci.", 75000.00))
    rid_srinivasan = insert_record((10101, "Srinivasan", "Comp. Sci.", 65000.00))

    scan_all()

    # Inspect page layouts
    for pid in range(_page_count()):
        print_page_layout(_load_page(pid))

    # ------------------------------------------------------------------
    # Phase 2: Logical delete
    # ------------------------------------------------------------------
    print("\n[Phase 2] Deleting El Said:", rid_el_said)
    delete_by_rid(*rid_el_said)

    rec_after = select_by_rid(*rid_el_said)
    print(f"[SELECT] RID{rid_el_said} after delete → {rec_after}")

    # ------------------------------------------------------------------
    # Phase 3: Slot reuse — the deleted slot should be recycled
    # ------------------------------------------------------------------
    print("\n[Phase 3] Inserting Mozart — expect slot reuse")
    rid_mozart = insert_record((15151, "Mozart", "Music", 40000.00))
    print(f"  El Said was at {rid_el_said}, Mozart landed at {rid_mozart}")

    scan_all()

    # ------------------------------------------------------------------
    # Phase 4: NULL field demo
    # ------------------------------------------------------------------
    print("\n[Phase 4] Inserting Crick with salary=NULL")
    rid_crick = insert_record((76766, "Crick", "Biology", None),
                               null_mask=NULL_SALARY)
    rec_crick = select_by_rid(*rid_crick)
    print(f"[SELECT] RID{rid_crick} → {rec_crick}")
    print(f"  salary field is: {rec_crick[3]}")

    # ------------------------------------------------------------------
    # Phase 5: Final layout inspection
    # ------------------------------------------------------------------
    print("\n[Phase 5] Final page layout inspection")
    for pid in range(_page_count()):
        print_page_layout(_load_page(pid))
