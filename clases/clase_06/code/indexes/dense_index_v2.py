# ============================================================================
# Laboratorio de Estructuras de Datos - UdeA
# Topic  : Ordered Indexes — Phase 1: Dense Index (v2 — realistic I/O model)
# Module : dense_index_v2.py
# ============================================================================
#
# Extends DenseIndex with a block-level binary search that simulates realistic
# disk access: instead of running bisect over all entries in memory, each
# iteration reads exactly ONE index block and adjusts the search window based
# on the block's boundary keys — exactly as described in Silberschatz §14.2.
#
# Key difference vs. v1:
#   v1 — bisect.bisect_left over self._keys (all entries in RAM, 0 I/Os)
#   v2 — block-level loop: each iteration issues 1 simulated disk I/O and
#        loads only that block into the buffer; total index I/Os = ceil(log2(B))
#        where B = number of index blocks.
#
# ============================================================================

import math
from typing import Optional

from dense_index import DenseIndex
from index_utils import (
    INSTRUCTOR_TABLE,
    N_RECORDS_SCALE,
    RECORDS_PER_BLOCK, INDEX_ENTRIES_PER_BLOCK,
    F_ID,
    binary_search_ios, io_cost_ms, full_scan_cost,
    print_section, print_subsection, print_cost_table, print_data_file,
)


# ============================================================================
# DENSE INDEX V2 — block-level binary search
# ============================================================================

class DenseIndexV2(DenseIndex):
    """
    Dense index with a realistic block-level binary search.

    Inherits index construction from DenseIndex. Overrides lookup with a
    loop that reads one index block per iteration, mirroring what a real
    buffer pool manager would do on disk.

    New public method:
        lookup_v2(key) -> dict
            Returns data_block, ios breakdown, and a per-step I/O trace.
    """

    # ------------------------------------------------------------------
    # Private — simulated disk read
    # ------------------------------------------------------------------

    def _read_index_block(self, block_num: int) -> list[tuple]:
        """
        Simulates reading index block `block_num` from disk into the buffer.

        In a real system this would be a ReadBlock() call; here it slices
        self.entries, which represents the full index file on disk.

        Args:
            block_num: zero-based index block number.

        Returns:
            List of (search_key, data_block_number) entries in that block.
        """
        start = block_num * self.index_entries_per_block
        end   = start + self.index_entries_per_block
        return self.entries[start:end]

    # ------------------------------------------------------------------
    # Public — block-level lookup
    # ------------------------------------------------------------------

    def lookup_v2(self, key) -> dict:
        """
        Searches for `key` using block-level binary search.

        Algorithm:
            1. Compute bounds over index block numbers: low=0, high=B-1.
            2. Each iteration:
               a. mid = (low + high) // 2
               b. ReadBlock(mid) — 1 simulated I/O.
               c. Compare key against block's first and last entry:
                  - key < first_key  →  high = mid - 1
                  - key > last_key   →  low  = mid + 1
                  - otherwise        →  linear scan within block → done.
            3. After finding the entry, 1 more I/O to read the data block.

        Args:
            key: search key value (exact match).

        Returns:
            Dict with keys:
                data_block  (int|None) : data block containing the record.
                index_ios   (int)      : I/Os used to search the index.
                data_ios    (int)      : I/Os to fetch the data block (0 or 1).
                total_ios   (int)      : index_ios + data_ios.
                total_ms    (float)    : estimated time in milliseconds.
                trace       (list)     : one entry per I/O with step details.
        """
        n_index_blocks = math.ceil(len(self.entries) / self.index_entries_per_block)
        low   = 0
        high  = n_index_blocks - 1
        ios   = 0
        trace = []

        while low <= high:
            mid   = (low + high) // 2
            block = self._read_index_block(mid)   # <-- simulated disk I/O
            ios  += 1

            first_key = block[0][0]
            last_key  = block[-1][0]

            if key < first_key:
                decision = f"key {key} < first_key {first_key} → high = {mid - 1}"
                high = mid - 1
                trace.append(_step(ios, mid, first_key, last_key, decision))

            elif key > last_key:
                decision = f"key {key} > last_key {last_key} → low = {mid + 1}"
                low = mid + 1
                trace.append(_step(ios, mid, first_key, last_key, decision))

            else:
                # key falls within this block — linear scan (in-memory, no extra I/O)
                found_block = None
                for entry in block:
                    if entry[0] == key:
                        found_block = entry[1]
                        break

                if found_block is not None:
                    decision = f"key {key} in [{first_key}, {last_key}] → found, data block = {found_block}"
                    trace.append(_step(ios, mid, first_key, last_key, decision))
                    return {
                        "data_block" : found_block,
                        "index_ios"  : ios,
                        "data_ios"   : 1,
                        "total_ios"  : ios + 1,
                        "total_ms"   : io_cost_ms(ios + 1),
                        "trace"      : trace,
                    }
                else:
                    decision = f"key {key} in [{first_key}, {last_key}] → not found in block"
                    trace.append(_step(ios, mid, first_key, last_key, decision))
                    break

        return {
            "data_block" : None,
            "index_ios"  : ios,
            "data_ios"   : 0,
            "total_ios"  : ios,
            "total_ms"   : io_cost_ms(ios),
            "trace"      : trace,
        }


# ============================================================================
# HELPERS
# ============================================================================

def _step(io_num: int, block: int, first_key, last_key, decision: str) -> dict:
    """Builds a single trace entry for one I/O step."""
    return {
        "io"        : io_num,
        "block_read": block,
        "first_key" : first_key,
        "last_key"  : last_key,
        "decision"  : decision,
    }


def print_trace(result: dict):
    """Prints the per-step I/O trace returned by lookup_v2."""
    trace = result["trace"]
    print(f"\n  {'I/O':>4}  {'Block read':>10}  {'First key':>12}  {'Last key':>12}  Decision")
    print(f"  {'─'*4}  {'─'*10}  {'─'*12}  {'─'*12}  {'─'*42}")
    for s in trace:
        print(f"  {s['io']:>4}  {s['block_read']:>10}  {str(s['first_key']):>12}  "
              f"{str(s['last_key']):>12}  {s['decision']}")
    found = result["data_block"]
    if found is not None:
        print(f"\n  → 1 additional I/O to fetch data block {found}")
    print(f"\n  Total: {result['index_ios']} index I/O(s) + {result['data_ios']} data I/O"
          f" = {result['total_ios']} I/O(s)  ({result['total_ms']:.0f} ms)")


# ============================================================================
# MAIN — classroom demo
# ============================================================================

if __name__ == "__main__":

    print_section("Phase 1 — Dense Index v2  (block-level binary search)")

    print_data_file(INSTRUCTOR_TABLE, ordered_by="ID")

    idx = DenseIndexV2(INSTRUCTOR_TABLE)
    print(f"\n  {idx}")
    print(f"  Index entries per block : {idx.index_entries_per_block}")
    n_idx_blocks = math.ceil(len(idx) / idx.index_entries_per_block)
    print(f"  Index blocks            : {n_idx_blocks}")

    # ----------------------------------------------------------------
    # Demo: trace a lookup step by step — Katz (ID = 45565)
    # ----------------------------------------------------------------
    target_id = 45565
    print_subsection(f"Lookup v2: SELECT * FROM instructor WHERE ID = {target_id}")

    result = idx.lookup_v2(target_id)
    print_trace(result)

    # ----------------------------------------------------------------
    # Demo: key not present
    # ----------------------------------------------------------------
    missing_id = 99999
    print_subsection(f"Lookup v2: SELECT * FROM instructor WHERE ID = {missing_id} (not found)")

    result_miss = idx.lookup_v2(missing_id)
    print_trace(result_miss)

    # ----------------------------------------------------------------
    # Scale comparison: v1 (bisect) vs v2 (block-level) — same I/O count
    # ----------------------------------------------------------------
    print_subsection("I/O cost at textbook scale (1000000 records)")

    n          = N_RECORDS_SCALE
    n_i_blocks = math.ceil(n / INDEX_ENTRIES_PER_BLOCK)
    index_ios  = binary_search_ios(n_i_blocks)
    total_ios  = index_ios + 1
    fs         = full_scan_cost(200_000)

    print(f"\n  Index entries           : {n}")
    print(f"  Index blocks            : {n_i_blocks}")
    print(f"  Index I/Os (log2)       : {index_ios}")
    print(f"  Data  I/Os              : 1")
    print(f"  Total                   : {total_ios} I/Os  ({io_cost_ms(total_ios):.0f} ms)")

    print_subsection("Comparison: Dense index v2 vs full scan")
    print_cost_table([
        {"label": "No index (full scan)",
         "ios": fs["total_ios"], "ms": fs["total_ms"]},
        {"label": "Dense index v2 (block-level)",
         "ios": total_ios, "ms": io_cost_ms(total_ios)},
    ])
    print(f"\n  Speedup: {fs['total_ios'] // total_ios}x fewer I/Os with dense index v2.\n")
