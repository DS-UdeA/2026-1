# ============================================================================
# Laboratorio de Estructuras de Datos - UdeA
# Topic  : Ordered Indexes — Shared Utilities
# Module : index_utils.py
# ============================================================================
#
# Shared constants, data, and helpers used by all index modules:
#
#   dense_index.py       — Phase 1: Dense index
#   sparse_index.py      — Phase 2: Sparse index
#   clustering_index.py  — Phase 3: Clustering index
#   secondary_index.py   — Phase 4: Secondary index
#   multilevel_index.py  — Phase 5: Multilevel index
#   cost_comparison.py   — Final I/O cost summary
#
# Data source:
#   Silberschatz, A., Korth, H. F., & Sudarshan, S.
#   "Database System Concepts", 7th ed.
#   Table: instructor(ID, name, dept_name, salary)
# ============================================================================

import math

# ---------------------------------------------------------------------------
# SCHEMA FIELD INDICES — instructor(ID, name, dept_name, salary)
# ---------------------------------------------------------------------------

F_ID     = 0   # instructor ID  (primary key, integer)
F_NAME   = 1   # instructor name
F_DEPT   = 2   # department name
F_SALARY = 3   # annual salary  (integer, dollars)

# ---------------------------------------------------------------------------
# INSTRUCTOR TABLE
# Source: Silberschatz et al., "Database System Concepts", 7th ed.
# Physical order: sorted by ID (clustering key used in Phases 1, 2, 5).
# ---------------------------------------------------------------------------

INSTRUCTOR_TABLE: list[tuple] = [
    (10101, "Srinivasan", "Comp. Sci.", 65000),
    (12121, "Wu",         "Finance",    90000),
    (15151, "Mozart",     "Music",      40000),
    (22222, "Einstein",   "Physics",    95000),
    (32343, "El Said",    "History",    60000),
    (33456, "Gold",       "Physics",    87000),
    (45565, "Katz",       "Comp. Sci.", 75000),
    (58583, "Califieri",  "History",    62000),
    (76543, "Singh",      "Finance",    80000),
    (76766, "Crick",      "Biology",    72000),
    (83821, "Brandt",     "Comp. Sci.", 92000),
    (98345, "Kim",        "Elec. Eng.", 80000),
]

# ---------------------------------------------------------------------------
# DISK MODEL CONSTANTS
# Values match the textbook examples used throughout the slide deck.
# ---------------------------------------------------------------------------

RECORDS_PER_BLOCK       = 5    # records that fit in one disk block
INDEX_ENTRIES_PER_BLOCK = 100  # index entries per index block
MS_PER_BLOCK            = 10   # milliseconds per disk I/O

# Derived — demo table (12 records)
N_RECORDS_DEMO = len(INSTRUCTOR_TABLE)
N_BLOCKS_DEMO  = math.ceil(N_RECORDS_DEMO / RECORDS_PER_BLOCK)

# Derived — textbook scale (matches slide examples exactly)
N_RECORDS_SCALE = 1_000_000
N_BLOCKS_SCALE  = N_RECORDS_SCALE // RECORDS_PER_BLOCK   # 200,000


# ============================================================================
# DISK MODEL HELPERS
# ============================================================================

def block_of(record_index: int) -> int:
    """
    Returns the block number that contains the record at position record_index.

    Assumes records are stored sequentially, RECORDS_PER_BLOCK per block.

    Args:
        record_index: zero-based position of the record in the sorted file.

    Returns:
        Block number (zero-based).

    Example:
        >>> block_of(0)   # records 0-4 → block 0
        0
        >>> block_of(5)   # records 5-9 → block 1
        1
    """
    return record_index // RECORDS_PER_BLOCK


def binary_search_ios(n_blocks: int) -> int:
    """
    Returns the number of I/Os needed to binary-search through n_blocks.

    Formula: ceil(log2(n_blocks)), minimum 1.
    This matches the textbook cost model for sorted index lookups.

    Args:
        n_blocks: number of index blocks to search.

    Returns:
        Number of disk I/O operations required.

    Example:
        >>> binary_search_ios(10000)   # dense index at scale
        14
        >>> binary_search_ios(2000)    # sparse index at scale
        11
    """
    if n_blocks <= 1:
        return 1
    return math.ceil(math.log2(n_blocks))


def io_cost_ms(n_ios: int) -> float:
    """
    Converts a count of I/O operations to milliseconds.

    Args:
        n_ios: number of disk block reads.

    Returns:
        Total time in milliseconds.

    Example:
        >>> io_cost_ms(15)
        150.0
    """
    return n_ios * MS_PER_BLOCK


def full_scan_cost(n_blocks: int) -> dict:
    """
    Returns the I/O cost of a full sequential table scan.

    This is the baseline cost against which all index strategies are compared.
    A full scan reads every block in the file exactly once.

    Args:
        n_blocks: total number of data blocks in the file.

    Returns:
        Dict with keys:
            total_ios  (int)   — number of block reads.
            total_ms   (float) — total time in milliseconds.
            total_min  (float) — total time in minutes.
    """
    total_ms = io_cost_ms(n_blocks)
    return {
        "total_ios" : n_blocks,
        "total_ms"  : total_ms,
        "total_min" : total_ms / 60_000,
    }


# ============================================================================
# DISPLAY HELPERS
# ============================================================================

def print_section(title: str, width: int = 62):
    """Prints a titled section separator."""
    print(f"\n{'=' * width}")
    print(f"  {title}")
    print(f"{'=' * width}")


def print_subsection(title: str, width: int = 62):
    """Prints a subsection separator."""
    print(f"\n{'─' * 3} {title} {'─' * max(0, width - len(title) - 5)}")


def print_index_entries(entries: list, label: str, max_rows: int = 20):
    """
    Prints a compact table of index entries.

    Args:
        entries : list of (search_key, block_number) tuples.
        label   : header label for the table.
        max_rows: maximum rows to display before truncating.
    """
    print(f"\n  [{label}] — {len(entries)} entries total")
    print(f"  {'#':>4}  {'Search Key':>14}  {'Block #':>7}")
    print(f"  {'─'*4}  {'─'*14}  {'─'*7}")
    for i, (key, blk) in enumerate(entries[:max_rows]):
        print(f"  {i:>4}  {str(key):>14}  {blk:>7}")
    if len(entries) > max_rows:
        print(f"  ... ({len(entries) - max_rows} more entries not shown)")


def print_cost_table(rows: list[dict]):
    """
    Prints a formatted I/O cost comparison table.

    Args:
        rows: list of dicts, each with keys:
              'label' (str), 'ios' (int), 'ms' (float).
    """
    print(f"\n  {'Strategy':<32} {'I/Os':>8}  {'Time':>12}")
    print(f"  {'─'*32} {'─'*8}  {'─'*12}")
    for r in rows:
        ms = r["ms"]
        if ms < 1000:
            time_str = f"{ms:.0f} ms"
        elif ms < 60_000:
            time_str = f"{ms/1000:.1f} s"
        else:
            time_str = f"{ms/60_000:.2f} min"
        print(f"  {r['label']:<32} {r['ios']:>8}  {time_str:>12}")


def print_data_file(records: list[tuple], ordered_by: str = "ID"):
    """
    Prints the data file layout showing which records land in each block.

    Args:
        records   : list of instructor tuples to display.
        ordered_by: label for the ordering key (used in the header).
    """
    print(f"\n  Records : {len(records)}")
    print(f"  Blocks  : {math.ceil(len(records)/RECORDS_PER_BLOCK)}"
          f"  ({RECORDS_PER_BLOCK} records/block, {MS_PER_BLOCK} ms/I/O)")
    print(f"  Ordered by: {ordered_by}\n")
    print(f"  {'Blk':>4}  {'ID':>6}  {'Name':<12}  {'Dept':<12}  {'Salary':>8}")
    print(f"  {'─'*4}  {'─'*6}  {'─'*12}  {'─'*12}  {'─'*8}")
    for i, rec in enumerate(records):
        new_block = block_of(i) != block_of(i - 1) and i > 0
        marker = "← new block" if new_block else ""
        print(f"  {block_of(i):>4}  {rec[F_ID]:>6}  {rec[F_NAME]:<12}  "
              f"{rec[F_DEPT]:<12}  {rec[F_SALARY]:>8}  {marker}")


# ============================================================================
# SELF-TEST
# ============================================================================

if __name__ == "__main__":
    print_section("index_utils.py — Self-test")

    print("\n  Instructor table:")
    print_data_file(INSTRUCTOR_TABLE)

    print(f"\n  block_of(0)  = {block_of(0)}   (records 0–4  → block 0)")
    print(f"  block_of(5)  = {block_of(5)}   (records 5–9  → block 1)")
    print(f"  block_of(10) = {block_of(10)}   (records 10–11 → block 2)")

    print(f"\n  binary_search_ios(10000) = {binary_search_ios(10000)}"
          f"   (dense index, 1M records)")
    print(f"  binary_search_ios(2000)  = {binary_search_ios(2000)}"
          f"   (sparse index, 1M records)")
    print(f"  binary_search_ios(100)   = {binary_search_ios(100)}"
          f"   (outer multilevel, 1M records)")

    fs = full_scan_cost(N_BLOCKS_SCALE)
    print(f"\n  Full scan ({N_BLOCKS_SCALE:} blocks):")
    print(f"    {fs['total_ios']:} I/Os → {fs['total_min']:.2f} min")
