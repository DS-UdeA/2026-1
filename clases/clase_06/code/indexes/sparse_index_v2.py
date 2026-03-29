# ============================================================================
# Laboratorio de Estructuras de Datos - UdeA
# Topic  : Ordered Indexes — Phase 2: Sparse Index (v2 — realistic I/O model)
# Module : sparse_index_v2.py
# ============================================================================
#
# Extends SparseIndex with two improvements over v1:
#
#   1. Block-level binary search — same as DenseIndexV2: each iteration reads
#      ONE index block from disk instead of running bisect over all entries
#      in RAM. Total index I/Os = ceil(log2(B)) where B = index blocks.
#
#   2. Generic constructor — accepts records_per_block as a parameter so the
#      index can be built over files with any block size, not just the global
#      RECORDS_PER_BLOCK constant.
#
# Key difference vs. DenseIndexV2:
#   The block-level search here is a FLOOR lookup, not an exact match.
#   It finds the index block whose last key ≤ target, then returns the
#   data block to scan linearly — the engine never knows the exact record
#   position until it reads and scans the data block.
#
# Textbook: Silberschatz et al., §14.2
# ============================================================================

import math
from typing import Optional

from sparse_index import SparseIndex
from index_utils import (
    INSTRUCTOR_TABLE,
    N_RECORDS_SCALE, N_BLOCKS_SCALE,
    RECORDS_PER_BLOCK, INDEX_ENTRIES_PER_BLOCK,
    binary_search_ios, io_cost_ms, full_scan_cost,
    print_section, print_subsection, print_cost_table, print_data_file,
    print_index_entries,
)
from dense_index import DenseIndex


# ============================================================================
# SPARSE INDEX V2 — block-level floor lookup + generic constructor
# ============================================================================

class SparseIndexV2(SparseIndex):
    """
    Sparse index with block-level floor lookup and generic block size.

    Improvements over SparseIndex (v1):
        - Constructor accepts records_per_block as a parameter.
        - lookup_v2() reads one index block per iteration (simulated I/O)
          instead of running bisect over all entries in RAM.
        - Returns a detailed trace showing each I/O step and the floor
          decision — making explicit that the result is a block to SCAN,
          not an exact record pointer.

    New public method:
        lookup_v2(key) -> dict
    """

    def __init__(self, records: list[tuple],
                 key_field: int = 0,
                 records_per_block: int = RECORDS_PER_BLOCK,
                 index_entries_per_block: int = INDEX_ENTRIES_PER_BLOCK):
        """
        Builds the sparse index: one entry per block.

        Args:
            records               : tuples sorted by key_field.
            key_field             : field index used as search key.
            records_per_block     : number of data records per disk block.
            index_entries_per_block: number of index entries per index block.
        """
        self.key_field               = key_field
        self.records_per_block       = records_per_block
        self.index_entries_per_block = index_entries_per_block
        self.entries: list[tuple]    = []

        current_block = -1
        for i, rec in enumerate(records):
            b = i // records_per_block          # generic, not block_of()
            if b != current_block:
                self.entries.append((rec[key_field], b))
                current_block = b

        self._keys: list = [e[0] for e in self.entries]

    # ------------------------------------------------------------------
    # Private — simulated disk read
    # ------------------------------------------------------------------

    def _read_index_block(self, block_num: int) -> list[tuple]:
        """
        Simulates reading index block `block_num` from disk into the buffer.

        Args:
            block_num: zero-based index block number.

        Returns:
            List of (min_key, data_block_number) entries in that block.
        """
        start = block_num * self.index_entries_per_block
        end   = start + self.index_entries_per_block
        return self.entries[start:end]

    # ------------------------------------------------------------------
    # Public — block-level floor lookup
    # ------------------------------------------------------------------

    def lookup_v2(self, key) -> dict:
        """
        Searches for the data block that MAY contain `key` using a
        block-level floor lookup.

        Algorithm:
            1. Compute bounds: low=0, high=B-1 (B = index blocks).
            2. Each iteration:
               a. mid = (low + high) // 2
               b. ReadBlock(mid) — 1 simulated I/O.
               c. Examine first and last keys of the block:
                  - key < first_key of block 0  →  key not in file, stop.
                  - key < first_key             →  high = mid - 1
                  - key >= first_key of next block (or mid is last block
                    and key >= first_key)        →  low  = mid + 1
                  - otherwise                   →  floor is in this block.
            3. Within the found block, scan linearly for the entry with
               the largest key ≤ target (floor entry).
            4. Return that entry's data block number — caller must issue
               1 more I/O and scan the data block linearly.

        Args:
            key: search key value to locate.

        Returns:
            Dict with keys:
                data_block      (int|None) : data block to scan linearly.
                floor_key       (any|None) : index entry key used as floor.
                index_ios       (int)      : I/Os used to search the index.
                data_ios        (int)      : 1 if block found, 0 otherwise.
                total_ios       (int)      : index_ios + data_ios.
                total_ms        (float)    : estimated time in milliseconds.
                requires_scan   (bool)     : always True when data_block found.
                trace           (list)     : one entry per I/O step.
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

            # Is the key below everything in the index?
            if mid == 0 and key < first_key:
                decision = f"key {key} < first index entry {first_key} → not in file"
                trace.append(_step(ios, mid, first_key, last_key, decision))
                return _not_found(ios, trace)

            # Is the floor definitely in a later block?
            next_block_first = _peek_next_block_first(self.entries,
                                                       mid, self.index_entries_per_block)
            if next_block_first is not None and key >= next_block_first:
                decision = (f"key {key} >= first key of next block "
                            f"({next_block_first}) → low = {mid + 1}")
                trace.append(_step(ios, mid, first_key, last_key, decision))
                low = mid + 1

            elif key < first_key:
                decision = f"key {key} < first_key {first_key} → high = {mid - 1}"
                trace.append(_step(ios, mid, first_key, last_key, decision))
                high = mid - 1

            else:
                # Floor is within this block — linear scan for largest key ≤ target
                floor_entry = None
                for entry in block:
                    if entry[0] <= key:
                        floor_entry = entry
                    else:
                        break

                if floor_entry is not None:
                    decision = (f"floor found: key {floor_entry[0]} ≤ {key} "
                                f"→ scan data block {floor_entry[1]} linearly")
                    trace.append(_step(ios, mid, first_key, last_key, decision))
                    return {
                        "data_block"   : floor_entry[1],
                        "floor_key"    : floor_entry[0],
                        "index_ios"    : ios,
                        "data_ios"     : 1,
                        "total_ios"    : ios + 1,
                        "total_ms"     : io_cost_ms(ios + 1),
                        "requires_scan": True,
                        "trace"        : trace,
                    }
                else:
                    decision = f"no floor entry found in block {mid}"
                    trace.append(_step(ios, mid, first_key, last_key, decision))
                    return _not_found(ios, trace)

        return _not_found(ios, trace)


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


def _not_found(ios: int, trace: list) -> dict:
    """Returns a standard not-found result dict."""
    return {
        "data_block"   : None,
        "floor_key"    : None,
        "index_ios"    : ios,
        "data_ios"     : 0,
        "total_ios"    : ios,
        "total_ms"     : io_cost_ms(ios),
        "requires_scan": False,
        "trace"        : trace,
    }


def _peek_next_block_first(entries: list, current_block: int,
                            entries_per_block: int) -> Optional[object]:
    """
    Returns the first key of the index block immediately after current_block,
    or None if current_block is the last block.
    """
    next_start = (current_block + 1) * entries_per_block
    if next_start < len(entries):
        return entries[next_start][0]
    return None


def print_trace(result: dict):
    """Prints the per-step I/O trace returned by lookup_v2."""
    trace = result["trace"]
    print(f"\n  {'I/O':>4}  {'Block read':>10}  {'First key':>12}  {'Last key':>12}  Decision")
    print(f"  {'─'*4}  {'─'*10}  {'─'*12}  {'─'*12}  {'─'*48}")
    for s in trace:
        print(f"  {s['io']:>4}  {s['block_read']:>10}  {str(s['first_key']):>12}  "
              f"{str(s['last_key']):>12}  {s['decision']}")
    found = result["data_block"]
    if found is not None:
        print(f"\n  → data block {found} found (floor key = {result['floor_key']})")
        print(f"  → 1 additional I/O + linear scan within block required")
    else:
        print(f"\n  → key not found in index")
    print(f"\n  Total: {result['index_ios']} index I/O(s) + {result['data_ios']} data I/O"
          f" = {result['total_ios']} I/O(s)  ({result['total_ms']:.0f} ms)")


# ============================================================================
# MAIN — classroom demo
# ============================================================================

if __name__ == "__main__":

    print_section("Phase 2 — Sparse Index v2  (block-level floor lookup)")

    print_data_file(INSTRUCTOR_TABLE, ordered_by="ID")

    idx = SparseIndexV2(INSTRUCTOR_TABLE)
    print(f"\n  {idx}")
    print(f"  Index entries per block : {idx.index_entries_per_block}")
    n_idx_blocks = math.ceil(len(idx) / idx.index_entries_per_block)
    print(f"  Index blocks            : {n_idx_blocks}")
    print_index_entries(idx.entries, "Sparse index on ID")

    # ----------------------------------------------------------------
    # Demo: trace a floor lookup — Katz (ID = 45565)
    # ----------------------------------------------------------------
    target_id = 45565
    print_subsection(f"Lookup v2: SELECT * FROM instructor WHERE ID = {target_id}")

    result = idx.lookup_v2(target_id)
    print_trace(result)

    # ----------------------------------------------------------------
    # Demo: key not present (but floor exists)
    # ----------------------------------------------------------------
    missing_id = 50000
    print_subsection(f"Lookup v2: SELECT * FROM instructor WHERE ID = {missing_id} (not in table)")

    result_miss = idx.lookup_v2(missing_id)
    print_trace(result_miss)
    print(f"  Note: block {result_miss['data_block']} is returned because"
          f" floor key {result_miss['floor_key']} ≤ {missing_id}.")
    print(f"  The linear scan within block {result_miss['data_block']}"
          f" will confirm the record does not exist.")

    # ----------------------------------------------------------------
    # Demo: key below all index entries
    # ----------------------------------------------------------------
    below_id = 5000
    print_subsection(f"Lookup v2: SELECT * FROM instructor WHERE ID = {below_id} (below all keys)")

    result_below = idx.lookup_v2(below_id)
    print_trace(result_below)

    # ----------------------------------------------------------------
    # Demo: reduced parameters (records_per_block=2, index_entries_per_block=4)
    # ----------------------------------------------------------------
    print_subsection("Reduced parameters: records_per_block=2, index_entries_per_block=4")

    idx_small = SparseIndexV2(INSTRUCTOR_TABLE,
                               records_per_block=2,
                               index_entries_per_block=4)
    print_index_entries(idx_small.entries, "Sparse index — reduced params")

    result_small = idx_small.lookup_v2(45565)
    print_subsection("Lookup v2 with reduced params: ID = 45565")
    print_trace(result_small)

    # ----------------------------------------------------------------
    # Scale comparison
    # ----------------------------------------------------------------
    print_subsection("I/O cost at textbook scale (1000000 records, 200000 blocks)")

    cost = idx.io_cost(n_blocks=N_BLOCKS_SCALE)
    fs   = full_scan_cost(N_BLOCKS_SCALE)

    dense     = DenseIndex(INSTRUCTOR_TABLE)
    cost_dense = dense.io_cost(n_records=N_RECORDS_SCALE)

    print(f"\n  Index entries           : {cost['index_entries']}"
          f"  (one per data block)")
    print(f"  Index blocks            : {cost['index_blocks']}")
    print(f"  Index I/Os (log2)       : {cost['index_ios']}")
    print(f"  Data  I/Os              : 1  (+ linear scan, no extra I/O)")
    print(f"  Total                   : {cost['total_ios']} I/Os"
          f"  ({cost['total_ms']:.0f} ms)")

    print_subsection("Comparison: Sparse v2 vs Dense vs full scan")
    print_cost_table([
        {"label": "No index (full scan)",
         "ios": fs["total_ios"],         "ms": fs["total_ms"]},
        {"label": "Dense index v2",
         "ios": cost_dense["total_ios"], "ms": cost_dense["total_ms"]},
        {"label": "Sparse index v2",
         "ios": cost["total_ios"],       "ms": cost["total_ms"]},
    ])

    ratio = N_RECORDS_SCALE // N_BLOCKS_SCALE
    print(f"\n  Space trade-off: sparse uses {ratio}x fewer index entries than dense.")
    print(f"  I/O trade-off  : sparse needs {cost['index_ios']} index I/Os vs"
          f" {cost_dense['index_ios']} for dense — smaller index = fewer search steps.")
    print(f"  Hidden cost    : sparse requires intra-block linear scan (CPU,"
          f" no extra disk I/O).\n")
