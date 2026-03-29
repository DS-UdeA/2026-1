# ============================================================================
# Laboratorio de Estructuras de Datos - UdeA
# Topic  : Ordered Indexes — Phase 5: Multilevel Index
# Module : multilevel_index.py
# ============================================================================
#
# When an index grows too large to fit in main memory, binary search over
# it still requires multiple disk I/Os.  The solution is to apply the same
# indexing principle to the index itself: build an index OVER the index.
#
# Two-level structure:
#   Inner index (level 1): dense index over all records — stored on disk.
#   Outer index (level 2): sparse index over the inner index blocks
#                          — small enough to keep in memory.
#
# Lookup cost:
#   Step 1 — search outer index (in memory)    : 0 disk I/Os
#   Step 2 — read one inner index block        : 1 disk I/O
#   Step 3 — read one data block               : 1 disk I/O
#   Total                                      : 2 disk I/Os
#
# This matches the textbook Example 5 (slide deck) exactly:
#   1M records → inner: 10,000 blocks → outer: 100 blocks (fits in RAM)
#   Result: 2 I/Os → 20 ms  vs  200,000 I/Os ≈ 33 min (full scan)
#
# The same principle generalizes to 3+ levels (the foundation of B+-trees).
#
# Slides reference: "Índice multinivel (Multilevel index)"
#                   Clase 6, slides 63–70, Example 5
# Textbook: Silberschatz et al., §14.4
# ============================================================================

import bisect
import math
from typing import Optional

from index_utils import (
    INSTRUCTOR_TABLE,
    N_RECORDS_DEMO,
    N_RECORDS_SCALE, N_BLOCKS_SCALE,
    INDEX_ENTRIES_PER_BLOCK,
    F_ID,
    block_of, binary_search_ios, io_cost_ms, full_scan_cost,
    print_section, print_subsection,
    print_index_entries, print_cost_table, print_data_file,
)
from dense_index import DenseIndex


# ============================================================================
# MULTILEVEL INDEX CLASS
# ============================================================================

class MultilevelIndex:
    """
    Two-level ordered index: sparse outer index in memory + dense inner index.

    The inner index is a standard DenseIndex over all records.
    The outer index is a sparse index over the inner index blocks — one
    entry per inner block, keeping the smallest key of each inner block.

    When the outer index fits entirely in main memory, binary search over
    it costs zero disk I/Os, reducing the total lookup cost to exactly 2 I/Os
    regardless of how large the dataset is.

    Attributes:
        key_field     (int)        : field index used as the search key.
        outer_entries (list[tuple]): sparse entries over inner index blocks.

    Usage example:
        >>> idx = MultilevelIndex(INSTRUCTOR_TABLE)
        >>> idx.lookup(45565)
        1
    """

    def __init__(self, records: list[tuple], key_field: int = F_ID):
        """
        Builds the two-level index.

        Inner level — DenseIndex over all records (may be large, on disk).
        Outer level — sparse index over inner index blocks (small, in memory).
                      One entry per inner block: stores (min_key, inner_block_id).

        Args:
            records   : instructor tuples sorted by key_field.
            key_field : field index used as the search key (default: ID).
        """
        self.key_field = key_field

        # Inner index — dense, one entry per record
        self._inner = DenseIndex(records, key_field)

        # Outer index — sparse, one entry per inner index block
        self.outer_entries: list[tuple] = []
        prev_inner_block = -1
        for i, (key, _) in enumerate(self._inner.entries):
            inner_block_id = i // INDEX_ENTRIES_PER_BLOCK
            if inner_block_id != prev_inner_block:
                # First entry in a new inner block → emit outer entry
                self.outer_entries.append((key, inner_block_id))
                prev_inner_block = inner_block_id

        self._outer_keys: list = [e[0] for e in self.outer_entries]

    # ------------------------------------------------------------------
    # Lookup operations
    # ------------------------------------------------------------------

    def lookup(self, key) -> Optional[int]:
        """
        Two-level lookup returning the data block number for the given key.

        Step 1 — Binary search over outer index (in memory → 0 disk I/Os).
        Step 2 — Read the relevant inner index block from disk (1 I/O).
        Step 3 — Linear scan within that inner block for the exact key.
        Step 4 — Return the data block pointer (caller issues 1 more I/O).

        Args:
            key: search key value (exact match).

        Returns:
            Data block number, or None if the key does not exist.
        """
        # Step 1: floor lookup on outer index (in memory — no I/O)
        outer_pos = bisect.bisect_right(self._outer_keys, key) - 1
        if outer_pos < 0:
            return None

        # Step 2: identify inner block (simulate 1 I/O)
        inner_block_id = self.outer_entries[outer_pos][1]
        inner_start    = inner_block_id * INDEX_ENTRIES_PER_BLOCK
        inner_end      = min(inner_start + INDEX_ENTRIES_PER_BLOCK,
                             len(self._inner.entries))

        # Step 3: linear scan within inner block (in memory after I/O)
        for i in range(inner_start, inner_end):
            if self._inner.entries[i][0] == key:
                return self._inner.entries[i][1]   # data block number

        return None

    # ------------------------------------------------------------------
    # I/O cost model
    # ------------------------------------------------------------------

    def io_cost(self, n_records: Optional[int] = None) -> dict:
        """
        Returns the I/O breakdown for a single-key point lookup.

        The outer index is assumed to fit in memory → 0 outer I/Os.
        Only one inner block and one data block need to be read from disk.

        Args:
            n_records: optional record count override for scale simulations.

        Returns:
            Dict with keys: inner_entries, inner_blocks, outer_entries,
            outer_blocks, outer_ios, inner_ios, data_ios, total_ios, total_ms.
        """
        n_inner      = n_records if n_records else len(self._inner.entries)
        n_inner_blk  = math.ceil(n_inner / INDEX_ENTRIES_PER_BLOCK)
        n_outer      = n_inner_blk   # one outer entry per inner block
        n_outer_blk  = math.ceil(n_outer / INDEX_ENTRIES_PER_BLOCK)

        return {
            "inner_entries" : n_inner,
            "inner_blocks"  : n_inner_blk,
            "outer_entries" : n_outer,
            "outer_blocks"  : n_outer_blk,
            "outer_ios"     : 0,   # outer fits in memory → 0 disk I/Os
            "inner_ios"     : 1,   # read one inner index block
            "data_ios"      : 1,   # read one data block
            "total_ios"     : 2,
            "total_ms"      : io_cost_ms(2),
        }

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (f"MultilevelIndex("
                f"inner_entries={len(self._inner)}, "
                f"outer_entries={len(self.outer_entries)})")


# ============================================================================
# MAIN — classroom demo
# ============================================================================

if __name__ == "__main__":

    print_section("Phase 5 — Multilevel Index  (outer in memory + dense inner)")

    # ----------------------------------------------------------------
    # Build the index
    # ----------------------------------------------------------------
    print_data_file(INSTRUCTOR_TABLE, ordered_by="ID")

    multilevel = MultilevelIndex(INSTRUCTOR_TABLE)
    print(f"\n  {multilevel}")

    print_index_entries(
        multilevel._inner.entries, "Inner index (dense, on disk)"
    )
    print_index_entries(
        multilevel.outer_entries, "Outer index (sparse, in memory)"
    )

    # ----------------------------------------------------------------
    # Point lookup — Katz (ID = 45565)
    # ----------------------------------------------------------------
    target_id = 45565
    blk = multilevel.lookup(target_id)

    print_subsection(f"Lookup: SELECT * FROM instructor WHERE ID = {target_id}")
    print(f"\n  Step 1 — search outer index (in memory) : 0 I/Os")
    print(f"  Step 2 — read inner index block          : 1 I/O")
    print(f"  Step 3 — linear scan inner block         : (in memory, no I/O)")
    print(f"  Step 4 — read data block                 : 1 I/O")
    print(f"  Found ID={target_id} → Block {blk}")

    # ----------------------------------------------------------------
    # I/O cost — demo scale
    # ----------------------------------------------------------------
    cost_demo = multilevel.io_cost()
    print(f"\n  Demo scale  ({N_RECORDS_DEMO:>12,} records):")
    print(f"    Inner entries : {cost_demo['inner_entries']}")
    print(f"    Inner blocks  : {cost_demo['inner_blocks']}")
    print(f"    Outer entries : {cost_demo['outer_entries']}")
    print(f"    Outer blocks  : {cost_demo['outer_blocks']} (in memory)")
    print(f"    Total         : {cost_demo['total_ios']} I/Os"
          f" → {cost_demo['total_ms']:.0f} ms")

    # ----------------------------------------------------------------
    # I/O cost — textbook scale  (matches slide Example 5 exactly)
    # ----------------------------------------------------------------
    cost_scale = multilevel.io_cost(n_records=N_RECORDS_SCALE)
    fs          = full_scan_cost(N_BLOCKS_SCALE)

    print(f"\n  Textbook scale ({N_RECORDS_SCALE:} records):")
    print(f"    Inner entries : {cost_scale['inner_entries']:}")
    print(f"    Inner blocks  : {cost_scale['inner_blocks']:}  (on disk)")
    print(f"    Outer entries : {cost_scale['outer_entries']:}")
    print(f"    Outer blocks  : {cost_scale['outer_blocks']:}  (in memory → 0 I/Os)")
    print(f"    Total         : {cost_scale['total_ios']} I/Os"
          f" → {cost_scale['total_ms']:.0f} ms")

    # ----------------------------------------------------------------
    # Final comparison table  (matches slide Example 5 summary)
    # ----------------------------------------------------------------
    from sparse_index import SparseIndex
    sparse     = SparseIndex(INSTRUCTOR_TABLE)
    cost_dense_scale  = DenseIndex(INSTRUCTOR_TABLE).io_cost(n_records=N_RECORDS_SCALE)
    cost_sparse_scale = sparse.io_cost(n_blocks=N_BLOCKS_SCALE)

    print_subsection("Final comparison  (textbook scale: 1M records)")
    print_cost_table([
        {"label": "No index (full scan)",
         "ios": fs["total_ios"],           "ms": fs["total_ms"]},
        {"label": "Dense index (1 level)",
         "ios": cost_dense_scale["total_ios"],  "ms": cost_dense_scale["total_ms"]},
        {"label": "Sparse index (1 level)",
         "ios": cost_sparse_scale["total_ios"], "ms": cost_sparse_scale["total_ms"]},
        {"label": "Multilevel index (2 levels)",
         "ios": cost_scale["total_ios"],    "ms": cost_scale["total_ms"]},
    ])

    print(f"\n  Key insight: the multilevel index achieves the minimum possible")
    print(f"  cost — 2 I/Os — by keeping the outer index in memory, completely")
    print(f"  eliminating binary search over disk blocks.")
    print(f"\n  This is the core idea behind B+-trees, which generalize the")
    print(f"  multilevel structure dynamically to support inserts and deletes.\n")
