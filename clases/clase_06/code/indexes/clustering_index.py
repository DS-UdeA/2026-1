# ============================================================================
# Laboratorio de Estructuras de Datos - UdeA
# Topic  : Ordered Indexes — Phase 3: Clustering Index
# Module : clustering_index.py
# ============================================================================
#
# A clustering index (also called primary index) is built on a file that is
# physically ordered by the search key.  One entry is stored per UNIQUE
# search-key value, pointing to the first block that contains records with
# that value.
#
# Key advantage — range queries:
#   Because records with the same key value (or consecutive key values) are
#   stored in physically adjacent blocks, a range query reads a contiguous
#   sequence of blocks.  This is the best-case disk access pattern.
#
# Contrast with secondary index (Phase 4):
#   A secondary index on the same data would scatter reads across many
#   non-contiguous blocks → much higher I/O cost for range queries.
#
# Constraint:
#   A table can have AT MOST ONE clustering index (there is only one
#   physical ordering of the file on disk).
#
# Slides reference: "Índice de agrupamiento (Clustering index)"
#                   Clase 6, slides 43–46, Example 3
# Textbook: Silberschatz et al., §14.3
# ============================================================================

import bisect
import math
from typing import Optional

from index_utils import (
    INSTRUCTOR_TABLE,
    N_RECORDS_DEMO, N_BLOCKS_DEMO,
    N_RECORDS_SCALE, N_BLOCKS_SCALE,
    INDEX_ENTRIES_PER_BLOCK, RECORDS_PER_BLOCK,
    F_ID, F_DEPT,
    block_of, binary_search_ios, io_cost_ms, full_scan_cost,
    print_section, print_subsection,
    print_index_entries, print_cost_table, print_data_file,
)


# ============================================================================
# CLUSTERING INDEX CLASS
# ============================================================================

class ClusteringIndex:
    """
    Clustering (primary) index over a file sorted by the search key.

    One entry per unique search-key value, pointing to the first block
    that contains records with that value.

    Because the file is physically ordered, a range query on [lo, hi]
    returns a contiguous sequence of blocks — sequential I/O.

    Attributes:
        key_field (int)        : field index used as the search key.
        entries   (list[tuple]): one (key, first_block) entry per unique key.

    Usage example:
        >>> records = sorted(INSTRUCTOR_TABLE, key=lambda r: r[F_DEPT])
        >>> idx = ClusteringIndex(records, key_field=F_DEPT)
        >>> idx.lookup("History")
        1
    """

    def __init__(self, records: list[tuple], key_field: int = F_DEPT):
        """
        Builds the clustering index over records sorted by key_field.

        Emits one entry per unique search-key value, storing the block
        number of the first occurrence of that key.

        Args:
            records   : instructor tuples sorted by key_field.
            key_field : field index used as the search key (default: dept_name).
        """
        self.key_field = key_field
        self.entries: list[tuple] = []

        seen: set = set()
        for i, rec in enumerate(records):
            k = rec[key_field]
            if k not in seen:
                seen.add(k)
                self.entries.append((k, block_of(i)))

        self._keys: list = [e[0] for e in self.entries]

    # ------------------------------------------------------------------
    # Lookup operations
    # ------------------------------------------------------------------

    def lookup(self, key) -> Optional[int]:
        """
        Returns the first block containing records with the given key.

        The engine then reads subsequent consecutive blocks until the
        search-key value changes (exploiting physical ordering).

        Args:
            key: search key value (exact match).

        Returns:
            First block number, or None if the key is not in the index.
        """
        pos = bisect.bisect_left(self._keys, key)
        if pos < len(self.entries) and self.entries[pos][0] == key:
            return self.entries[pos][1]
        return None

    def range_lookup(self, lo, hi) -> list[int]:
        """
        Returns all distinct blocks with records whose key is in [lo, hi].

        Because the file is clustered, the result is always a contiguous
        sequence of blocks — the engine reads them with a single pass.

        Args:
            lo: lower bound key (inclusive).
            hi: upper bound key (inclusive).

        Returns:
            Sorted list of distinct block numbers (always contiguous).
        """
        start = bisect.bisect_left(self._keys, lo)
        end   = bisect.bisect_right(self._keys, hi)
        return sorted({self.entries[i][1] for i in range(start, end)})

    def range_io_cost(self, lo, hi,
                      n_records_per_key: Optional[int] = None) -> dict:
        """
        Returns the I/O breakdown for a range query on [lo, hi].

        For clustered files, data blocks in the range are read sequentially
        (contiguous) — no random I/O overhead.

        Args:
            lo               : lower bound key (inclusive).
            hi               : upper bound key (inclusive).
            n_records_per_key: optional override for records per key value
                               (used for textbook-scale calculations).

        Returns:
            Dict with keys: index_ios, data_blocks, data_ios,
            total_ios, total_ms.
        """
        demo_blocks = self.range_lookup(lo, hi)
        if n_records_per_key:
            # Textbook-scale: count keys in range and multiply
            start = bisect.bisect_left(self._keys, lo)
            end   = bisect.bisect_right(self._keys, hi)
            n_keys_in_range = end - start
            data_blocks = math.ceil(
                n_keys_in_range * n_records_per_key / RECORDS_PER_BLOCK
            )
        else:
            data_blocks = len(demo_blocks)

        return {
            "index_ios"   : 1,            # one lookup to find start block
            "data_blocks" : data_blocks,
            "data_ios"    : data_blocks,   # sequential — one I/O per block
            "total_ios"   : 1 + data_blocks,
            "total_ms"    : io_cost_ms(1 + data_blocks),
        }

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self.entries)

    def __repr__(self) -> str:
        return (f"ClusteringIndex(entries={len(self.entries)}, "
                f"key_field={self.key_field})")


# ============================================================================
# MAIN — classroom demo
# ============================================================================

if __name__ == "__main__":

    print_section("Phase 3 — Clustering Index  (search key: dept_name)")

    # ----------------------------------------------------------------
    # Re-sort by dept_name to simulate a physically clustered file
    # ----------------------------------------------------------------
    clustered = sorted(INSTRUCTOR_TABLE, key=lambda r: r[F_DEPT])
    print_data_file(clustered, ordered_by="dept_name")

    clustering = ClusteringIndex(clustered, key_field=F_DEPT)
    print(f"\n  {clustering}")
    print_index_entries(clustering.entries, "Clustering index on dept_name")

    # ----------------------------------------------------------------
    # Point lookup — History department
    # ----------------------------------------------------------------
    target_dept = "History"
    blk = clustering.lookup(target_dept)

    print_subsection(f"Lookup: SELECT * FROM instructor WHERE dept_name = '{target_dept}'")
    print(f"\n  Index entry → Block {blk}")
    print(f"  Engine reads Block {blk} sequentially until dept_name ≠ '{target_dept}'")

    # ----------------------------------------------------------------
    # Range query — Comp. Sci. to History  (matches slide Example 3)
    # ----------------------------------------------------------------
    lo_dept, hi_dept = "Comp. Sci.", "History"
    blocks_cl = clustering.range_lookup(lo_dept, hi_dept)
    cost_range = clustering.range_io_cost(lo_dept, hi_dept)

    print_subsection(
        f"Range: SELECT * FROM instructor "
        f"WHERE dept_name BETWEEN '{lo_dept}' AND '{hi_dept}'"
    )
    print(f"\n  Blocks in range (demo): {blocks_cl}")
    print(f"  All blocks are CONTIGUOUS → sequential I/O, no random seeks.")
    print(f"\n  Cost breakdown:")
    print(f"    Index I/Os : {cost_range['index_ios']}"
          f"  (find entry for '{lo_dept}')")
    print(f"    Data  I/Os : {cost_range['data_ios']}"
          f"  ({cost_range['data_blocks']} consecutive blocks)")
    print(f"    Total      : {cost_range['total_ios']} I/Os"
          f" → {cost_range['total_ms']:.0f} ms")

    # ----------------------------------------------------------------
    # Textbook-scale range query  (matches slide Example 3 numbers)
    # ----------------------------------------------------------------
    # 1M records, 5 rec/block, 4 depts with equal distribution
    # → 1M/4 = 250,000 records per dept
    # For a range covering 4 depts: 4 * (250,000 / 5) = 200,000 blocks
    cost_scale_range = clustering.range_io_cost(
        lo_dept, hi_dept,
        n_records_per_key=N_RECORDS_SCALE // 4,
    )
    fs = full_scan_cost(N_BLOCKS_SCALE)

    print(f"\n  Textbook scale — same range query ({N_RECORDS_SCALE:,} records):")
    print(f"    Index I/Os : {cost_scale_range['index_ios']}")
    print(f"    Data  I/Os : {cost_scale_range['data_ios']:,}"
          f"  ({cost_scale_range['data_blocks']:,} consecutive blocks)")
    print(f"    Total      : {cost_scale_range['total_ios']:,} I/Os"
          f" → {io_cost_ms(cost_scale_range['total_ios'])/60000:.1f} min")

    # ----------------------------------------------------------------
    # Why clustering matters for range queries
    # ----------------------------------------------------------------
    print_subsection("Key insight: Clustering vs Secondary for range queries")
    print(f"\n  Clustering index → {cost_scale_range['total_ios']:,} I/Os"
          f"  (contiguous blocks, sequential read)")
    print(f"  Secondary index  → up to {N_RECORDS_SCALE//4:,} I/Os"
          f"  (scattered blocks, random reads)")
    print(f"  Full scan        → {fs['total_ios']:,} I/Os"
          f"  ({fs['total_min']:.1f} min)")
    print(f"\n  A clustering index is always preferred for range queries")
    print(f"  because it eliminates random I/O completely.\n")
