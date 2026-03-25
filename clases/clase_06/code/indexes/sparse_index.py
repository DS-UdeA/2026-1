# ============================================================================
# Laboratorio de Estructuras de Datos - UdeA
# Topic  : Ordered Indexes — Phase 2: Sparse Index
# Module : sparse_index.py
# ============================================================================
#
# A sparse index stores ONE entry per disk block (not per record).
# Each entry holds the FIRST (minimum) search key found in that block.
#
# Lookup strategy:
#   1. Binary search to find the entry with the largest key ≤ target key.
#   2. Read that block from disk          (1 disk I/O).
#   3. Scan linearly within the block until the target record is found.
#
# Requirements:
#   - The data file MUST be physically sorted by the search key.
#     (Without ordering, the floor-key logic does not guarantee correctness.)
#
# Trade-off vs. dense index:
#   + Smaller index (one entry per block instead of one per record).
#   + Lower maintenance cost on insertions/deletions.
#   - Slower per lookup: requires an intra-block linear scan.
#   - Cannot be used on unsorted files.
#
# Slides reference: "Índice disperso (Sparse index)" — Clase 6, slides 29–30
# Textbook: Silberschatz et al., §14.2
# ============================================================================

import bisect
import math
from typing import Optional

from index_utils import (
    INSTRUCTOR_TABLE,
    N_RECORDS_DEMO, N_BLOCKS_DEMO,
    N_RECORDS_SCALE, N_BLOCKS_SCALE,
    INDEX_ENTRIES_PER_BLOCK,
    F_ID,
    block_of, binary_search_ios, io_cost_ms, full_scan_cost,
    print_section, print_subsection,
    print_index_entries, print_cost_table, print_data_file,
)


# ============================================================================
# SPARSE INDEX CLASS
# ============================================================================

class SparseIndex:
    """
    Sparse ordered index over a physically sorted list of records.

    Stores one (search_key, block_number) entry per block.
    The search key stored is the MINIMUM key value in that block.

    Attributes:
        key_field (int)        : field index used as the search key.
        entries   (list[tuple]): one (min_key, block_number) entry per block.

    Usage example:
        >>> idx = SparseIndex(INSTRUCTOR_TABLE)
        >>> idx.lookup(45565)   # returns block to scan, not exact record
        1
    """

    def __init__(self, records: list[tuple], key_field: int = F_ID):
        """
        Builds the sparse index: one entry per block.

        Iterates through all records and emits an index entry only when
        the block number changes (i.e. for the first record of each block).

        Args:
            records   : instructor tuples sorted by key_field.
            key_field : field index used as the search key (default: ID).
        """
        self.key_field = key_field
        self.entries: list[tuple] = []

        current_block = -1
        for i, rec in enumerate(records):
            b = block_of(i)
            if b != current_block:
                # First record in this block → emit one index entry
                self.entries.append((rec[key_field], b))
                current_block = b

        # Parallel key list for bisect
        self._keys: list = [e[0] for e in self.entries]

    # ------------------------------------------------------------------
    # Lookup operations
    # ------------------------------------------------------------------

    def lookup(self, key) -> Optional[int]:
        """
        Returns the block that MAY contain the record with the given key.

        Uses a floor lookup: finds the entry with the largest key ≤ target.
        The engine then reads that block and scans it linearly for the key.

        Args:
            key: search key value to locate (exact match target).

        Returns:
            Block number to scan, or None if key is below all index entries.
        """
        pos = bisect.bisect_right(self._keys, key) - 1
        if pos < 0:
            return None
        return self.entries[pos][1]

    # ------------------------------------------------------------------
    # I/O cost model
    # ------------------------------------------------------------------

    def io_cost(self, n_blocks: Optional[int] = None) -> dict:
        """
        Returns the I/O breakdown for a single-key point lookup.

        Formula:
            index_entries = n_blocks          (one per block)
            index_blocks  = ceil(n_blocks / INDEX_ENTRIES_PER_BLOCK)
            index_ios     = ceil(log2(index_blocks))
            data_ios      = 1                 (one block read + linear scan)
            total_ios     = index_ios + 1

        Args:
            n_blocks: optional data-file block count override for scale
                      simulations. Pass None to use the actual index size.

        Returns:
            Dict with keys: index_entries, index_blocks, index_ios,
            data_ios, total_ios, total_ms.
        """
        n  = n_blocks if n_blocks else len(self.entries)
        nb = math.ceil(n / INDEX_ENTRIES_PER_BLOCK)
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
        return (f"SparseIndex(entries={len(self.entries)}, "
                f"key_field={self.key_field})")


# ============================================================================
# MAIN — classroom demo
# ============================================================================

if __name__ == "__main__":

    print_section("Phase 2 — Sparse Index  (search key: ID)")

    # ----------------------------------------------------------------
    # Build the index and display the data file layout
    # ----------------------------------------------------------------
    print_data_file(INSTRUCTOR_TABLE, ordered_by="ID")

    sparse = SparseIndex(INSTRUCTOR_TABLE)
    print(f"\n  {sparse}")
    print_index_entries(sparse.entries, "Sparse index on ID")

    # ----------------------------------------------------------------
    # Point lookup — Katz (ID = 45565)
    # ----------------------------------------------------------------
    target_id = 45565
    blk = sparse.lookup(target_id)

    print_subsection(f"Lookup: SELECT * FROM instructor WHERE ID = {target_id}")
    print(f"\n  Floor lookup → scan Block {blk} linearly for ID={target_id}")
    print(f"  (Entry with largest key ≤ {target_id} is "
          f"{sparse.entries[blk][0]} → Block {blk})")

    # ----------------------------------------------------------------
    # I/O cost — demo scale
    # ----------------------------------------------------------------
    cost_demo = sparse.io_cost()
    print(f"\n  Demo scale  ({N_RECORDS_DEMO:>12,} records, "
          f"{N_BLOCKS_DEMO} blocks):")
    print(f"    Index entries : {cost_demo['index_entries']}"
          f"  (one per block)")
    print(f"    Index blocks  : {cost_demo['index_blocks']}")
    print(f"    Total         : {cost_demo['total_ios']} I/Os"
          f" → {cost_demo['total_ms']:.0f} ms")

    # ----------------------------------------------------------------
    # I/O cost — textbook scale  (matches slide Example 3 exactly)
    # ----------------------------------------------------------------
    cost_scale = sparse.io_cost(n_blocks=N_BLOCKS_SCALE)
    fs          = full_scan_cost(N_BLOCKS_SCALE)

    print(f"\n  Textbook scale ({N_RECORDS_SCALE:>12,} records):")
    print(f"    Index entries : {cost_scale['index_entries']:,}"
          f"  (one per block, {N_BLOCKS_SCALE:,} blocks)")
    print(f"    Index blocks  : {cost_scale['index_blocks']:,}")
    print(f"    Index I/Os    : {cost_scale['index_ios']}"
          f"  (ceil(log2({cost_scale['index_blocks']:,})))")
    print(f"    Data  I/Os    : {cost_scale['data_ios']}")
    print(f"    Total         : {cost_scale['total_ios']} I/Os"
          f" → {cost_scale['total_ms']:.0f} ms")

    # ----------------------------------------------------------------
    # Space comparison: dense vs sparse  (matches slide conclusion)
    # ----------------------------------------------------------------
    from dense_index import DenseIndex
    dense      = DenseIndex(INSTRUCTOR_TABLE)
    cost_dense = dense.io_cost(n_records=N_RECORDS_SCALE)

    print_subsection("Space comparison: Dense vs Sparse  (textbook scale)")
    print(f"\n  Dense  : {N_RECORDS_SCALE:>10,} entries"
          f" → {cost_dense['index_blocks']:>6,} index blocks")
    print(f"  Sparse : {N_BLOCKS_SCALE:>10,} entries"
          f" → {cost_scale['index_blocks']:>6,} index blocks")
    ratio = N_RECORDS_SCALE // N_BLOCKS_SCALE
    print(f"  Ratio  : sparse uses {ratio}× fewer index entries.")

    # ----------------------------------------------------------------
    # Full comparison table
    # ----------------------------------------------------------------
    print_subsection("Comparison: Dense vs Sparse vs full scan")
    print_cost_table([
        {"label": "No index (full scan)",
         "ios": fs["total_ios"],        "ms": fs["total_ms"]},
        {"label": "Dense index (1 level)",
         "ios": cost_dense["total_ios"],"ms": cost_dense["total_ms"]},
        {"label": "Sparse index (1 level)",
         "ios": cost_scale["total_ios"],"ms": cost_scale["total_ms"]},
    ])

    print(f"\n  Key trade-off:")
    print(f"    Sparse is faster than dense here because its smaller index")
    print(f"    requires fewer binary-search I/Os ({cost_scale['index_ios']}"
          f" vs {cost_dense['index_ios']}).")
    print(f"    However, sparse requires an intra-block linear scan — extra")
    print(f"    CPU cost that does not add disk I/Os in this model.\n")
