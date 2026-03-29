# ============================================================================
# Laboratorio de Estructuras de Datos - UdeA
# Topic  : Ordered Indexes — Phase 4: Secondary Index
# Module : secondary_index.py
# ============================================================================
#
# A secondary index (also called non-clustering index) is built on a file
# that is NOT physically ordered by the search key.
#
# Because records with the same key value are scattered across different
# blocks, the engine may need one disk I/O PER MATCHING RECORD in the
# worst case (one random seek per block).
#
# Key trade-off — selectivity:
#   High selectivity (rare key value, few matches):
#       → few scattered I/Os → secondary index is very fast.
#   Low selectivity (common key value, many matches):
#       → many scattered I/Os → secondary index can be SLOWER
#         than a full sequential scan.
#
# This module reproduces the slide Example 4 exactly:
#   Table  : instructor, 1M records, file ordered by ID.
#   Index  : dense secondary index on salary.
#   Query  : WHERE salary = 80,000  (25% of records match → low selectivity)
#   Result : 250,014 I/Os ≈ 41.7 min  vs  200,000 I/Os ≈ 33.3 min (full scan)
#
# Slides reference: "Índice secundario (Secondary index)"
#                   Clase 6, slides 47–48, Example 4
# Textbook: Silberschatz et al., §14.3
# ============================================================================

import bisect
import math
from typing import Optional

from index_utils import (
    INSTRUCTOR_TABLE,
    N_RECORDS_DEMO,
    N_RECORDS_SCALE, N_BLOCKS_SCALE,
    INDEX_ENTRIES_PER_BLOCK,
    F_ID, F_SALARY,
    block_of, binary_search_ios, io_cost_ms, full_scan_cost,
    print_section, print_subsection,
    print_index_entries, print_cost_table, print_data_file,
)


# ============================================================================
# SECONDARY INDEX CLASS
# ============================================================================

class SecondaryIndex:
    """
    Dense secondary (non-clustering) index over an unordered file.

    The index is sorted by the search key value.  Each entry holds a pointer
    to the physical block where the record resides in the original file
    (ordered by a DIFFERENT key, e.g. ID).

    Because the file is not ordered by this key, matching records may be
    in any block → each pointer may require a separate random disk I/O.

    Attributes:
        key_field (int)        : field index used as the search key.
        entries   (list[tuple]): sorted list of (key, block_number) pairs,
                                 one entry per record.

    Usage example:
        >>> idx = SecondaryIndex(INSTRUCTOR_TABLE, key_field=F_SALARY)
        >>> idx.lookup(80000)
        [1, 2]   # two matching records in different blocks
    """

    def __init__(self, records: list[tuple], key_field: int = F_SALARY):
        """
        Builds the dense secondary index sorted by key_field.

        The original file order (by ID) is used to assign block numbers,
        so that scattered access patterns are correctly reflected.

        Args:
            records   : instructor tuples in original file order (by ID).
            key_field : field index used as the search key (default: salary).
        """
        self.key_field = key_field

        # Sort by search key; preserve original position for block mapping
        indexed = sorted(enumerate(records), key=lambda x: x[1][key_field])
        self.entries: list[tuple] = [
            (rec[key_field], block_of(orig_i))
            for orig_i, rec in indexed
        ]

        self._keys: list = [e[0] for e in self.entries]

    # ------------------------------------------------------------------
    # Lookup operations
    # ------------------------------------------------------------------

    def lookup(self, key) -> list[int]:
        """
        Returns all distinct block numbers containing records with key == salary.

        Each block number in the result may require a separate disk I/O
        because the file is not ordered by this key.

        Args:
            key: salary value to look up (exact match).

        Returns:
            Sorted list of distinct block numbers (may be non-contiguous).
        """
        start = bisect.bisect_left(self._keys, key)
        end   = bisect.bisect_right(self._keys, key)
        return sorted({self.entries[i][1] for i in range(start, end)})

    def matching_count(self, key) -> int:
        """
        Returns the number of index entries that match the given key.

        This is equal to the number of records with that key value.

        Args:
            key: salary value to count.

        Returns:
            Count of matching records.
        """
        start = bisect.bisect_left(self._keys, key)
        end   = bisect.bisect_right(self._keys, key)
        return end - start

    # ------------------------------------------------------------------
    # I/O cost model
    # ------------------------------------------------------------------

    def io_cost(self, key,
                n_records: Optional[int] = None,
                n_matching: Optional[int] = None) -> dict:
        """
        Returns the I/O breakdown for an equality lookup on the given key.

        Worst-case assumption: each matching record is in a different block
        (fully scattered).  This is the assumption used in the slide examples.

        Args:
            key       : salary value being searched.
            n_records : optional override for total record count
                        (for textbook-scale calculations).
            n_matching: optional override for matching record count
                        (for textbook-scale calculations).

        Returns:
            Dict with keys: index_entries, index_blocks, index_ios,
            data_ios, total_ios, total_ms.
        """
        n_entries    = n_records if n_records else len(self.entries)
        n_idx_blocks = math.ceil(n_entries / INDEX_ENTRIES_PER_BLOCK)
        idx_ios      = binary_search_ios(n_idx_blocks)

        # Worst case: each matching record is in a different block
        if n_matching:
            data_ios = n_matching
        else:
            data_ios = len(self.lookup(key))

        return {
            "index_entries" : n_entries,
            "index_blocks"  : n_idx_blocks,
            "index_ios"     : idx_ios,
            "data_ios"      : data_ios,
            "total_ios"     : idx_ios + data_ios,
            "total_ms"      : io_cost_ms(idx_ios + data_ios),
        }

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self.entries)

    def __repr__(self) -> str:
        return (f"SecondaryIndex(entries={len(self.entries)}, "
                f"key_field={self.key_field})")


# ============================================================================
# MAIN — classroom demo
# ============================================================================

if __name__ == "__main__":

    print_section("Phase 4 — Secondary Index  (search key: salary)")

    # ----------------------------------------------------------------
    # Build the index — file is ordered by ID (not salary)
    # ----------------------------------------------------------------
    print_data_file(INSTRUCTOR_TABLE, ordered_by="ID  (salary is NOT the ordering key)")

    secondary = SecondaryIndex(INSTRUCTOR_TABLE, key_field=F_SALARY)
    print(f"\n  {secondary}")
    print_index_entries(secondary.entries, "Secondary index on salary (sorted by salary)")

    # ----------------------------------------------------------------
    # Point lookup — salary = 80,000
    # ----------------------------------------------------------------
    target_salary = 80_000
    scattered_blocks = secondary.lookup(target_salary)
    n_matching_demo  = secondary.matching_count(target_salary)

    print_subsection(
        f"Lookup: SELECT * FROM instructor WHERE salary = {target_salary:}"
    )
    print(f"\n  Matching records (demo): {n_matching_demo}")
    print(f"  Block numbers accessed : {scattered_blocks}")
    print(f"  Blocks are NON-CONTIGUOUS → each = a separate random disk I/O.")

    cost_demo = secondary.io_cost(target_salary)
    print(f"\n  Demo scale  ({N_RECORDS_DEMO:>12,} records):")
    print(f"    Index I/Os : {cost_demo['index_ios']}")
    print(f"    Data  I/Os : {cost_demo['data_ios']}"
          f"  ({len(scattered_blocks)} distinct blocks)")
    print(f"    Total      : {cost_demo['total_ios']} I/Os"
          f" → {cost_demo['total_ms']:.0f} ms")

    # ----------------------------------------------------------------
    # Textbook-scale — low selectivity scenario (matches slide Example 4)
    # 4 equal-distribution departments → 25% of 1M records = 250,000
    # ----------------------------------------------------------------
    n_matching_scale = N_RECORDS_SCALE // 4    # 250,000 matching records
    cost_scale = secondary.io_cost(
        target_salary,
        n_records=N_RECORDS_SCALE,
        n_matching=n_matching_scale,
    )
    fs = full_scan_cost(N_BLOCKS_SCALE)

    print(f"\n  Textbook scale ({N_RECORDS_SCALE:} records) — low selectivity:")
    print(f"    Matching records   : {n_matching_scale:}"
          f"  (25% of {N_RECORDS_SCALE:})")
    print(f"    Index entries      : {cost_scale['index_entries']:}")
    print(f"    Index blocks       : {cost_scale['index_blocks']:}")
    print(f"    Index I/Os         : {cost_scale['index_ios']}"
          f"  (binary search)")
    print(f"    Data  I/Os (worst) : {cost_scale['data_ios']:}"
          f"  (one per matching record)")
    print(f"    Total              : {cost_scale['total_ios']:} I/Os"
          f" → {cost_scale['total_ms']/60_000:.1f} min")

    # ----------------------------------------------------------------
    # Comparison vs full scan
    # ----------------------------------------------------------------
    print_subsection("Comparison: Secondary index vs full scan")
    print_cost_table([
        {"label": "Secondary index (low selectivity)",
         "ios": cost_scale["total_ios"], "ms": cost_scale["total_ms"]},
        {"label": "No index (full scan)",
         "ios": fs["total_ios"],         "ms": fs["total_ms"]},
    ])

    print(f"\n  ⚠  Secondary index is SLOWER than full scan in this scenario.")
    print(f"  Root cause: {n_matching_scale:} matching records are scattered"
          f" across up to {n_matching_scale:} blocks.")
    print(f"  Full scan reads only {N_BLOCKS_SCALE:} blocks sequentially.")

    # ----------------------------------------------------------------
    # High-selectivity contrast
    # ----------------------------------------------------------------
    print_subsection("Contrast: high-selectivity query (salary = 95,000)")
    target_high = 95_000
    blocks_high = secondary.lookup(target_high)
    cost_high   = secondary.io_cost(target_high)
    print(f"\n  Matching records (demo) : {secondary.matching_count(target_high)}")
    print(f"  Blocks accessed         : {blocks_high}")
    print(f"  Total I/Os              : {cost_high['total_ios']}")
    print(f"\n  High selectivity → very few matches → secondary index wins.\n")
