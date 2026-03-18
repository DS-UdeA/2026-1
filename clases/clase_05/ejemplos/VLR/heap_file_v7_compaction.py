# ============================================================================
# Laboratorio de Estructuras de Datos - UdeA
# Tema: Slotted Page — Reorganización y Estabilidad del RID
# Versión: v7 — Compactación intra-página (desfragmentación)
# ============================================================================
#
# Extends v6 with page-level compaction.
#
# KEY CONCEPT (slides 37–38):
#   After several insert/delete cycles the record area becomes fragmented —
#   small gaps of unusable space appear between records. A new insertion that
#   is larger than any single gap may fail even though the TOTAL free bytes
#   are sufficient.
#
#   compact_page() solves this by sliding all valid records to the right end
#   of the page and updating the offset values in the slot directory. The
#   slot_ids themselves NEVER change, so every RID held by an index or by
#   the application layer remains valid after compaction.
#
#   Before compaction:
#     [ HEADER | slots | free | rec3 | ??? | rec1 | ??? | rec0 ]
#                              ↑gap (rec2 deleted)    ↑gap (rec4 deleted)
#
#   After compaction:
#     [ HEADER | slots |       free (consolidated)    | rec3 | rec1 | rec0 ]
#
#   External view: RID(0,0), RID(0,1), RID(0,3) still point to the same
#   logical records — only the (offset) field inside the slot directory
#   entry was updated. The (page_id, slot_id) pair is unchanged.
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
    emp_id, name, dept_name, salary = record
    varchar_vals = [str(emp_id), name, dept_name]
    var_data = b''; pairs = []; cur = FIXED_SECTION
    for i, val in enumerate(varchar_vals):
        if null_mask & (1 << i):
            pairs.append((0, 0))
        else:
            enc = val.encode('utf-8')
            pairs.append((cur, len(enc))); var_data += enc; cur += len(enc)
    fixed = b''
    for (off, ln) in pairs:
        fixed += struct.pack('>HH', off, ln)
    sal_val = 0 if (null_mask & NULL_SALARY) else int((salary or 0) * 100)
    fixed  += struct.pack('>q', sal_val)
    fixed  += struct.pack('B', null_mask)
    return fixed + var_data


def deserialize_offset_array(data: bytes) -> tuple:
    pairs = [struct.unpack_from('>HH', data, i * 4) for i in range(N_VAR_FIELDS)]
    salary_raw = struct.unpack_from('>q', data, N_VAR_FIELDS * 4)[0]
    null_mask  = struct.unpack_from('B',  data, N_VAR_FIELDS * 4 + SALARY_BYTES)[0]
    vvals = []
    for i, (off, ln) in enumerate(pairs):
        if null_mask & (1 << i): vvals.append(None)
        elif ln == 0:             vvals.append('')
        else:                     vvals.append(data[off:off + ln].decode('utf-8'))
    salary = None if (null_mask & NULL_SALARY) else salary_raw / 100.0
    return (
        int(vvals[0]) if vvals[0] is not None else None,
        vvals[1], vvals[2], salary,
    )


# ---------------------------------------------------------------------------
# PAGE ARCHITECTURE CONSTANTS
# ---------------------------------------------------------------------------

PAGE_SIZE        = 256
PAGE_HEADER_SIZE = 8
SLOT_SIZE        = 4
SLOT_DELETED     = 0xFFFF

FILE_NAME = "my_database_v7.dat"


# ---------------------------------------------------------------------------
# PAGE-LEVEL HELPERS  (identical to v6)
# ---------------------------------------------------------------------------

def create_empty_page(page_id: int) -> bytearray:
    page = bytearray(PAGE_SIZE)
    struct.pack_into('>HHHH', page, 0, 0, PAGE_HEADER_SIZE, PAGE_SIZE, page_id)
    return page


def _read_header(page: bytearray) -> tuple:
    return struct.unpack_from('>HHHH', page, 0)


def _write_header(page: bytearray, num_slots, free_ptr, data_ptr, page_id):
    struct.pack_into('>HHHH', page, 0, num_slots, free_ptr, data_ptr, page_id)


def _read_slot(page: bytearray, slot_id: int) -> tuple:
    pos = PAGE_HEADER_SIZE + slot_id * SLOT_SIZE
    return struct.unpack_from('>HH', page, pos)


def _write_slot(page: bytearray, slot_id: int, offset: int, length: int):
    pos = PAGE_HEADER_SIZE + slot_id * SLOT_SIZE
    struct.pack_into('>HH', page, pos, offset, length)


def get_free_space(page: bytearray) -> int:
    _, free_ptr, data_ptr, _ = _read_header(page)
    return data_ptr - free_ptr


def insert_into_page(page: bytearray, record_bytes: bytes) -> int:
    num_slots, free_ptr, data_ptr, page_id = _read_header(page)
    rec_len = len(record_bytes)
    reuse_slot = next(
        (i for i in range(num_slots) if _read_slot(page, i)[0] == SLOT_DELETED),
        None,
    )
    dir_overhead = 0 if reuse_slot is not None else SLOT_SIZE
    if get_free_space(page) < rec_len + dir_overhead:
        return -1
    data_ptr -= rec_len
    page[data_ptr:data_ptr + rec_len] = record_bytes
    if reuse_slot is not None:
        slot_id = reuse_slot
    else:
        slot_id = num_slots; num_slots += 1; free_ptr += SLOT_SIZE
    _write_slot(page, slot_id, data_ptr, rec_len)
    _write_header(page, num_slots, free_ptr, data_ptr, page_id)
    return slot_id


def delete_from_page(page: bytearray, slot_id: int) -> bool:
    num_slots, *_ = _read_header(page)
    if slot_id >= num_slots: return False
    off, _ = _read_slot(page, slot_id)
    if off == SLOT_DELETED: return False
    _write_slot(page, slot_id, SLOT_DELETED, 0)
    return True


def read_from_page(page: bytearray, slot_id: int):
    num_slots, *_ = _read_header(page)
    if slot_id >= num_slots: return None
    off, ln = _read_slot(page, slot_id)
    if off == SLOT_DELETED: return None
    return bytes(page[off:off + ln])


# ---------------------------------------------------------------------------
# FILE I/O  (identical to v6)
# ---------------------------------------------------------------------------

def _load_page(page_id: int):
    if not os.path.exists(FILE_NAME): return None
    if page_id * PAGE_SIZE >= os.path.getsize(FILE_NAME): return None
    with open(FILE_NAME, 'rb') as f:
        f.seek(page_id * PAGE_SIZE)
        return bytearray(f.read(PAGE_SIZE))


def _save_page(page_id: int, page: bytearray):
    with open(FILE_NAME, 'r+b') as f:
        f.seek(page_id * PAGE_SIZE); f.write(bytes(page))


def _page_count() -> int:
    if not os.path.exists(FILE_NAME): return 0
    return os.path.getsize(FILE_NAME) // PAGE_SIZE


def _append_page(page: bytearray):
    with open(FILE_NAME, 'ab') as f: f.write(bytes(page))


# ---------------------------------------------------------------------------
# HIGH-LEVEL DML  (identical to v6)
# ---------------------------------------------------------------------------

def insert_record(record: tuple, null_mask: int = 0) -> tuple:
    rb = serialize_offset_array(record, null_mask)
    for pid in range(_page_count()):
        pg  = _load_page(pid)
        sid = insert_into_page(pg, rb)
        if sid >= 0:
            _save_page(pid, pg)
            print(f"[INSERT] '{record[1]}' → RID({pid},{sid})  [{len(rb)}B]")
            return (pid, sid)
    pid = _page_count()
    _append_page(create_empty_page(pid))
    pg  = _load_page(pid)
    sid = insert_into_page(pg, rb)
    _save_page(pid, pg)
    print(f"[INSERT] '{record[1]}' → RID({pid},{sid})  [{len(rb)}B]  ← new page")
    return (pid, sid)


def select_by_rid(page_id: int, slot_id: int):
    pg = _load_page(page_id)
    if pg is None: return None
    raw = read_from_page(pg, slot_id)
    return deserialize_offset_array(raw) if raw else None


def delete_by_rid(page_id: int, slot_id: int) -> bool:
    pg = _load_page(page_id)
    if pg is None: return False
    ok = delete_from_page(pg, slot_id)
    if ok:
        _save_page(page_id, pg)
        print(f"[DELETE] RID({page_id},{slot_id}) marked as deleted")
    return ok


def scan_all():
    print("\n[SCAN] Full table scan:")
    found = False
    for pid in range(_page_count()):
        pg = _load_page(pid)
        num_slots, *_ = _read_header(pg)
        for sid in range(num_slots):
            rec = select_by_rid(pid, sid)
            if rec:
                print(f"  RID({pid},{sid}) → {rec}")
                found = True
    if not found:
        print("  (no records found)")


# ============================================================================
# v7 NEW: COMPACTION
# ============================================================================

def compact_page(page: bytearray):
    """
    Eliminates internal fragmentation within a page (slide 37).

    Algorithm:
      1. Snapshot all valid (slot_id, record_bytes) pairs in order.
         Deleted slots are skipped — they will be marked as reusable.
      2. Reset data_ptr to PAGE_SIZE (the full right side is now free).
      3. Rewrite each valid record from right to left, in the same relative
         order, updating the slot directory entry (offset, length) for each.
      4. Update the page header with the new data_ptr.

    The slot_ids are NOT changed in any way.  An external reference such as
    RID(0, 2) that pointed to record 'Katz' before compaction still points
    to the same logical record after compaction — the SLOT entry for slot 2
    now contains a new physical offset, but the (page_id=0, slot_id=2)
    tuple the caller holds remains correct.

    This is the invariant that makes the Slotted Page safe to compact at any
    time without invalidating indices or cursors that hold RIDs.
    """
    num_slots, free_ptr, _, page_id = _read_header(page)

    # Step 1: collect valid records preserving their slot association
    valid = []
    for i in range(num_slots):
        off, ln = _read_slot(page, i)
        if off != SLOT_DELETED and ln > 0:
            valid.append((i, bytes(page[off:off + ln])))

    # Step 2 & 3: rewrite records compactly at the right end of the page
    new_data_ptr = PAGE_SIZE
    for slot_id, rec_bytes in valid:
        new_data_ptr -= len(rec_bytes)
        page[new_data_ptr:new_data_ptr + len(rec_bytes)] = rec_bytes
        _write_slot(page, slot_id, new_data_ptr, len(rec_bytes))

    # Step 4: update header — only data_ptr changes
    _write_header(page, num_slots, free_ptr, new_data_ptr, page_id)


def compact_page_by_id(page_id: int):
    """Loads a page, runs compaction, measures reclaimed space, saves to disk."""
    page = _load_page(page_id)
    if page is None:
        print(f"[COMPACT] Page {page_id} not found.")
        return

    _, _, before_data_ptr, _ = _read_header(page)
    before_free = get_free_space(page)

    compact_page(page)

    _, _, after_data_ptr, _ = _read_header(page)
    after_free = get_free_space(page)

    _save_page(page_id, page)
    reclaimed = after_free - before_free
    print(f"[COMPACT] Page {page_id}:")
    print(f"          Free space  : {before_free} B  →  {after_free} B"
          f"  (+{reclaimed} B recovered)")
    print(f"          data_ptr    : {before_data_ptr}  →  {after_data_ptr}")


# ============================================================================
# DEBUG / INSPECTION
# ============================================================================

def print_page_layout(page: bytearray, label: str = ""):
    """Prints a compact layout summary of a page for classroom inspection."""
    num_slots, free_ptr, data_ptr, page_id = _read_header(page)
    tag = f" [{label}]" if label else ""
    print(f"\n  ── Page {page_id}{tag} ──────────────────────────────────")
    print(f"  Free space  : {get_free_space(page):3d} B"
          f"  (bytes {free_ptr} – {data_ptr - 1})")
    for i in range(num_slots):
        off, ln = _read_slot(page, i)
        if off == SLOT_DELETED:
            print(f"  Slot [{i}] : DELETED  (bytes not yet reclaimed)")
        else:
            rec = deserialize_offset_array(bytes(page[off:off + ln]))
            print(f"  Slot [{i}] : offset={off:3d}, len={ln:2d}"
                  f"  →  '{rec[1]}' / '{rec[2]}'")


# ============================================================================
# MAIN — classroom demo
# ============================================================================
if __name__ == "__main__":
    if os.path.exists(FILE_NAME):
        os.remove(FILE_NAME)

    print("=" * 62)
    print("  Heap Files v7 — Compaction & RID Stability")
    print("=" * 62)

    # ------------------------------------------------------------------
    # Phase 1: Insert several records to partially fill a page
    # ------------------------------------------------------------------
    print("\n[Phase 1] Inserting records to fill a page")
    rid_einstein = insert_record((22222, "Einstein",   "Physics",    95000.00))
    rid_wu       = insert_record((12121, "Wu",         "Finance",    90000.00))
    rid_el_said  = insert_record((32343, "El Said",    "History",    60000.00))
    rid_katz     = insert_record((45565, "Katz",       "Comp. Sci.", 75000.00))

    print_page_layout(_load_page(0), label="after 4 inserts")

    # ------------------------------------------------------------------
    # Phase 2: Delete two records to create internal fragmentation
    # ------------------------------------------------------------------
    print("\n[Phase 2] Deleting Wu and El Said — creating fragmentation")
    delete_by_rid(*rid_wu)
    delete_by_rid(*rid_el_said)

    print_page_layout(_load_page(0), label="after 2 deletes — fragmented")

    # The surviving RIDs should still resolve correctly
    print(f"\n  RID{rid_einstein} → {select_by_rid(*rid_einstein)}")
    print(f"  RID{rid_katz}     → {select_by_rid(*rid_katz)}")

    # ------------------------------------------------------------------
    # Phase 3: Run compaction
    # ------------------------------------------------------------------
    print("\n[Phase 3] compact_page_by_id(0) — consolidate free space")
    compact_page_by_id(0)
    print_page_layout(_load_page(0), label="after compaction")

    # ------------------------------------------------------------------
    # Phase 4: Verify RID stability
    # The (page_id, slot_id) pairs for Einstein and Katz have NOT changed,
    # but their internal offsets in the slot directory have been updated.
    # ------------------------------------------------------------------
    print("\n[Phase 4] RID stability check")
    rec_e = select_by_rid(*rid_einstein)
    rec_k = select_by_rid(*rid_katz)
    print(f"  RID{rid_einstein} → {rec_e}   ← SAME RID as before compaction")
    print(f"  RID{rid_katz}     → {rec_k}   ← SAME RID as before compaction")
    assert rec_e is not None and rec_e[1] == "Einstein", "RID stability broken!"
    assert rec_k is not None and rec_k[1] == "Katz",     "RID stability broken!"
    print("  [OK] All RIDs remain valid after compaction.")

    # ------------------------------------------------------------------
    # Phase 5: Insert into the now-consolidated free space
    # ------------------------------------------------------------------
    print("\n[Phase 5] Inserting Mozart into the recovered space")
    rid_mozart = insert_record((15151, "Mozart", "Music",   40000.00))
    rid_brandt = insert_record((83821, "Brandt", "Comp. Sci.", 92000.00))

    print_page_layout(_load_page(0), label="final state")
    scan_all()

    print()
    print("  Summary of RID assignments:")
    for name, rid in [("Einstein", rid_einstein), ("Katz",    rid_katz),
                      ("Mozart",   rid_mozart),   ("Brandt",  rid_brandt)]:
        print(f"    {name:12s} → RID{rid}")
