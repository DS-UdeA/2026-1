# ============================================================================
# Laboratorio de Estructuras de Datos - UdeA
# Topic  : Ordered Indexes — Phase 1: Dense Index
# Module : dense_index.py
# ============================================================================
#
# A dense index stores ONE entry per record in the data file.
# Each entry is a (search_key, block_number) pair.
#
# Properties:
#   - Applicable to any file ordering (does NOT require a sorted file).
#   - O(log n) binary search over the index → exactly 1 data I/O.
#   - Largest space footprint: one entry per record.
#   - If the file IS sorted, a dense index on a unique key gives direct
#     record-level access (no intra-block scan needed).
#
# Slides reference: "Índice denso (Dense index)"  — Clase 6, slides 24–27
# Textbook: Silberschatz et al., §14.2
# ============================================================================

import bisect
import math
from typing import Optional

from index_utils import (
    INSTRUCTOR_TABLE,
    N_RECORDS_DEMO, N_RECORDS_SCALE,
    RECORDS_PER_BLOCK, INDEX_ENTRIES_PER_BLOCK,
    F_ID,
    block_of, binary_search_ios, io_cost_ms, full_scan_cost,
    print_section, print_subsection,
    print_index_entries, print_cost_table, print_data_file,
)


# ============================================================================
# DENSE INDEX CLASS
# ============================================================================

class DenseIndex:
    """
    Dense ordered index over a sorted list of records.

    Builds one (search_key, block_number) entry per record and keeps
    a parallel sorted key list for O(log n) binary search via bisect.

    Attributes:
        key_field (int)        : field index used as the search key.
        entries   (list[tuple]): sorted list of (key, block_number) pairs.

    Usage example:
        >>> idx = DenseIndex(INSTRUCTOR_TABLE)
        >>> idx.lookup(45565)
        1
    """

    def __init__(self, records: list[tuple], key_field: int = F_ID,
                 records_per_block: int = RECORDS_PER_BLOCK,
                 index_entries_per_block: int = INDEX_ENTRIES_PER_BLOCK):
        """
        Builds the dense index from a list of records.

        Records should be sorted by key_field; the resulting entries list
        will be in the same order.

        Args:
            records                : instructor tuples sorted by key_field.
            key_field              : field index to use as search key (default: ID).
            records_per_block      : number of data records per disk block (default: RECORDS_PER_BLOCK).
            index_entries_per_block: number of index entries per index block (default: INDEX_ENTRIES_PER_BLOCK).
        """
        self.key_field               = key_field
        self.records_per_block       = records_per_block
        self.index_entries_per_block = index_entries_per_block

        # One (search_key, block_number) entry per record
        self.entries: list[tuple] = [
            (rec[key_field], i // records_per_block)
            for i, rec in enumerate(records)
        ]

        # Parallel key list used by bisect for binary search
        self._keys: list = [e[0] for e in self.entries]

    # ------------------------------------------------------------------
    # Lookup operations
    # ------------------------------------------------------------------

    def lookup(self, key) -> Optional[int]:
        """
        Returns the block number containing the record with the given key.

        Uses binary search (bisect_left) — O(log n) steps over the index,
        then the caller issues exactly 1 disk I/O to fetch the block.

        Args:
            key: search key value (exact match).

        Returns:
            Block number if the key exists, None otherwise.
        """
        pos = bisect.bisect_left(self._keys, key)
        if pos < len(self.entries) and self.entries[pos][0] == key:
            return self.entries[pos][1]
        return None

    def range_lookup(self, lo, hi) -> list[int]:
        """
        Returns all distinct block numbers with records in key range [lo, hi].

        Args:
            lo: lower bound of the range (inclusive).
            hi: upper bound of the range (inclusive).

        Returns:
            Sorted list of distinct block numbers.
        """
        start = bisect.bisect_left(self._keys, lo)
        end   = bisect.bisect_right(self._keys, hi)
        return sorted({self.entries[i][1] for i in range(start, end)})

    # ------------------------------------------------------------------
    # I/O cost model
    # ------------------------------------------------------------------

    def io_cost(self, n_records: Optional[int] = None) -> dict:
        """
        Returns the I/O breakdown for a single-key point lookup.

        Formula:
            index_ios = ceil(log2(index_blocks))   [binary search]
            data_ios  = 1                           [one ReadBlock()]
            total_ios = index_ios + data_ios

        Args:
            n_records: optional record count override for scale simulations.
                       Pass None to use the actual index size.

        Returns:
            Dict with keys: index_entries, index_blocks, index_ios,
            data_ios, total_ios, total_ms.
        """
        n  = n_records if n_records else len(self.entries)
        nb = math.ceil(n / self.index_entries_per_block)
        ii = binary_search_ios(nb)
        return {
            "index_entries" : n,
            "index_blocks"  : nb,
            "index_ios"     : ii,
            "data_ios"      : 1,
            "total_ios"     : ii + 1,
            "total_ms"      : io_cost_ms(ii + 1),
        }

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self.entries)

    def __repr__(self) -> str:
        return (f"DenseIndex(entries={len(self.entries)}, "
                f"key_field={self.key_field})")


# ============================================================================
# MAIN — classroom demo
# ============================================================================

if __name__ == "__main__":

    print_section("Phase 1 — Dense Index  (search key: ID)")

    # ----------------------------------------------------------------
    # Build the index and display the data file layout
    # ----------------------------------------------------------------
    print_data_file(INSTRUCTOR_TABLE, ordered_by="ID")

    dense = DenseIndex(INSTRUCTOR_TABLE)
    print(f"\n  {dense}")
    print_index_entries(dense.entries, "Dense index on ID")

    # ----------------------------------------------------------------
    # Point lookup — Katz (ID = 45565)
    # ----------------------------------------------------------------
    target_id = 45565
    blk = dense.lookup(target_id)

    print_subsection(f"Lookup: SELECT * FROM instructor WHERE ID = {target_id}")
    print(f"\n  Found ID={target_id} → Block {blk}")
    print(f"  Binary search steps: ceil(log2({len(dense)})) "
          f"= {math.ceil(math.log2(len(dense)))} index reads + 1 data read")

    # ----------------------------------------------------------------
    # I/O cost — demo scale
    # ----------------------------------------------------------------
    cost_demo = dense.io_cost()
    print(f"\n  Demo scale  ({N_RECORDS_DEMO:>12,} records):")
    print(f"    Index entries : {cost_demo['index_entries']:}")
    print(f"    Index blocks  : {cost_demo['index_blocks']:}")
    print(f"    Index I/Os    : {cost_demo['index_ios']}  (binary search)")
    print(f"    Data  I/Os    : {cost_demo['data_ios']}")
    print(f"    Total         : {cost_demo['total_ios']} I/Os"
          f" → {cost_demo['total_ms']:.0f} ms")

    # ----------------------------------------------------------------
    # I/O cost — textbook scale  (matches slide Example 2 exactly)
    # ----------------------------------------------------------------
    cost_scale = dense.io_cost(n_records=N_RECORDS_SCALE)
    fs          = full_scan_cost(200_000)

    print(f"\n  Textbook scale ({N_RECORDS_SCALE:>12,} records):")
    print(f"    Index entries : {cost_scale['index_entries']:}")
    print(f"    Index blocks  : {cost_scale['index_blocks']:}")
    print(f"    Index I/Os    : {cost_scale['index_ios']}"
          f"  (ceil(log2({cost_scale['index_blocks']:})))")
    print(f"    Data  I/Os    : {cost_scale['data_ios']}")
    print(f"    Total         : {cost_scale['total_ios']} I/Os"
          f" → {cost_scale['total_ms']:.0f} ms")

    # ----------------------------------------------------------------
    # Comparison vs full scan
    # ----------------------------------------------------------------
    print_subsection("Comparison: Dense index vs full scan")
    print_cost_table([
        {"label": "No index (full scan)",
         "ios": fs["total_ios"],   "ms": fs["total_ms"]},
        {"label": "Dense index",
         "ios": cost_scale["total_ios"], "ms": cost_scale["total_ms"]},
    ])
    speedup = fs["total_ios"] / cost_scale["total_ios"]
    print(f"\n  Speedup: {speedup:.0f}× fewer I/Os with a dense index.")
    print(f"  Trade-off: requires {cost_scale['index_blocks']:} extra"
          f" blocks of storage for the index.\n")
