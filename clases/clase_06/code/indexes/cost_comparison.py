# ============================================================================
# Laboratorio de Estructuras de Datos - UdeA
# Topic  : Ordered Indexes — Final I/O Cost Summary
# Module : cost_comparison.py
# ============================================================================
#
# Imports all five index types and produces a consolidated comparison of
# their I/O costs at both demo scale (12 records) and textbook scale (1M).
#
# Run this module last, after reviewing each individual index module.
#
# Slides reference: summary tables from Clase 6, Examples 1–5
# Textbook: Silberschatz et al., §14.2–14.4
# ============================================================================

from index_utils import (
    INSTRUCTOR_TABLE,
    N_RECORDS_SCALE, N_BLOCKS_SCALE,
    print_section, print_subsection, print_cost_table,
    full_scan_cost,
)
from dense_index       import DenseIndex
from sparse_index      import SparseIndex
from clustering_index  import ClusteringIndex
from secondary_index   import SecondaryIndex
from multilevel_index  import MultilevelIndex


def run_comparison():
    """
    Builds all five index types and prints a consolidated I/O cost report.

    Covers:
        1. Single-key point lookup     (all index types, textbook scale)
        2. Range query                 (clustering vs secondary vs full scan)
        3. Low-selectivity equality    (secondary index vs full scan)
        4. Space overhead summary      (index blocks per strategy)
    """

    # ----------------------------------------------------------------
    # Build all indexes
    # ----------------------------------------------------------------
    clustered    = sorted(INSTRUCTOR_TABLE, key=lambda r: r[2])   # by dept_name
    dense        = DenseIndex(INSTRUCTOR_TABLE)
    sparse       = SparseIndex(INSTRUCTOR_TABLE)
    clustering   = ClusteringIndex(clustered)
    secondary    = SecondaryIndex(INSTRUCTOR_TABLE)
    multilevel   = MultilevelIndex(INSTRUCTOR_TABLE)

    fs = full_scan_cost(N_BLOCKS_SCALE)

    # ----------------------------------------------------------------
    # 1. Single-key point lookup  (textbook scale)
    # ----------------------------------------------------------------
    print_section("I/O Cost — Single-Key Point Lookup  (1M records, 10 ms/I/O)")

    cost_d  = dense.io_cost(n_records=N_RECORDS_SCALE)
    cost_s  = sparse.io_cost(n_blocks=N_BLOCKS_SCALE)
    cost_ml = multilevel.io_cost(n_records=N_RECORDS_SCALE)

    print_cost_table([
        {"label": "No index (full scan)",
         "ios": fs["total_ios"],       "ms": fs["total_ms"]},
        {"label": "Dense index (1 level)",
         "ios": cost_d["total_ios"],   "ms": cost_d["total_ms"]},
        {"label": "Sparse index (1 level)",
         "ios": cost_s["total_ios"],   "ms": cost_s["total_ms"]},
        {"label": "Multilevel index (2 levels)",
         "ios": cost_ml["total_ios"],  "ms": cost_ml["total_ms"]},
    ])

    # ----------------------------------------------------------------
    # 2. Range query — clustering vs secondary
    # ----------------------------------------------------------------
    print_subsection(
        "Range Query: dept_name BETWEEN 'Comp. Sci.' AND 'History'"
    )

    lo, hi = "Comp. Sci.", "History"
    n_records_per_key = N_RECORDS_SCALE // 4   # 250,000 (equal distribution)
    cost_cl_range = clustering.range_io_cost(lo, hi,
                                              n_records_per_key=n_records_per_key)
    cost_sec_range_ios = n_records_per_key * 4  # 4 depts × 250k records
    cost_sec_range_ms  = cost_sec_range_ios * 10

    print_cost_table([
        {"label": "No index (full scan)",
         "ios": fs["total_ios"],          "ms": fs["total_ms"]},
        {"label": "Clustering index",
         "ios": cost_cl_range["total_ios"],"ms": cost_cl_range["total_ms"]},
        {"label": "Secondary index (worst case)",
         "ios": cost_sec_range_ios,        "ms": cost_sec_range_ms},
    ])

    print(f"\n  Clustering index: reads {cost_cl_range['data_blocks']:,}"
          f" CONSECUTIVE blocks — sequential I/O.")
    print(f"  Secondary index : up to {cost_sec_range_ios:,} SCATTERED blocks"
          f" — random I/O per record.")

    # ----------------------------------------------------------------
    # 3. Low-selectivity equality  (secondary index vs full scan)
    # ----------------------------------------------------------------
    print_subsection(
        "Equality Query — Low Selectivity: salary = 80,000  (25% match)"
    )

    n_matching = N_RECORDS_SCALE // 4   # 250,000
    cost_sec   = secondary.io_cost(80_000,
                                   n_records=N_RECORDS_SCALE,
                                   n_matching=n_matching)
    print_cost_table([
        {"label": "Secondary index (salary)",
         "ios": cost_sec["total_ios"],  "ms": cost_sec["total_ms"]},
        {"label": "No index (full scan)",
         "ios": fs["total_ios"],        "ms": fs["total_ms"]},
    ])
    print(f"\n  ⚠  Secondary index is SLOWER than full scan here.")
    print(f"  Reason: {n_matching:,} matching records × 1 random I/O each"
          f" > {N_BLOCKS_SCALE:,} sequential I/Os.")

    # ----------------------------------------------------------------
    # 4. Space overhead
    # ----------------------------------------------------------------
    print_subsection("Index Space Overhead  (textbook scale: 1M records)")

    print(f"\n  {'Strategy':<32} {'Index entries':>16}  {'Index blocks':>14}")
    print(f"  {'─'*32} {'─'*16}  {'─'*14}")

    rows = [
        ("No index",          0,                    0),
        ("Dense index",       N_RECORDS_SCALE,      cost_d["index_blocks"]),
        ("Sparse index",      N_BLOCKS_SCALE,       cost_s["index_blocks"]),
        ("Multilevel outer",  cost_ml["outer_entries"], cost_ml["outer_blocks"]),
        ("Multilevel inner",  cost_ml["inner_entries"], cost_ml["inner_blocks"]),
    ]
    for label, entries, blocks in rows:
        print(f"  {label:<32} {entries:>16,}  {blocks:>14,}")

    # ----------------------------------------------------------------
    # 5. Design guidelines summary
    # ----------------------------------------------------------------
    print_section("Design Guidelines — When to Use Each Index Type")
    guidelines = [
        ("Dense index",
         "Need direct record access; file may not be sorted; "
         "fast point lookups."),
        ("Sparse index",
         "File is sorted; space is a concern; acceptable for "
         "one-per-block lookup + intra-block scan."),
        ("Clustering index",
         "Frequent range queries on a key; records physically "
         "ordered by that key."),
        ("Secondary index",
         "Point queries on non-ordering attribute; HIGH selectivity "
         "(few matching records)."),
        ("Multilevel index",
         "Index itself is too large for RAM; want minimum disk I/Os "
         "(exactly 2) for point lookups."),
    ]
    print()
    for name, guideline in guidelines:
        print(f"  {name:<24} — {guideline}")
    print()


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    run_comparison()
