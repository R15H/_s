import os
import re
from dataclasses import dataclass, field
from typing import Optional
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

METRICS = ["promotions", "demotions", "stalls", "access_ratio", "time"]


@dataclass
class BenchmarkConfig:
    # Human-readable name used in plot titles.
    display_name: str
    # DRAM configs to include; None means all available.
    dram_configs: Optional[list] = field(default=None)


# Registry: benchmark identifier (as it appears in all_results) → config.
BENCHMARK_CONFIGS: dict[str, BenchmarkConfig] = {
    "bcuuu": BenchmarkConfig(
        display_name="BCU (Block Compression Unit)",
        dram_configs=[1, 2, 4, 8],
    ),
}


# ── Helpers ────────────────────────────────────────────────────────────────────

def _normalize_base(base_str: str) -> str:
    """Collapse repeated trailing number segments: FOO-299-299-299 → FOO-299."""
    return re.sub(r"(-\d+)\1+$", r"\1", str(base_str))


def _extract_config_type(base_str: str) -> str:
    """Strip system prefix to get the shared config type.

    ASMEM-<config>          → <config>
    MEMTIS-<digits>-<config> → <config>   (version number stripped too)
    MEMTIS-<config>         → <config>
    """
    return re.sub(r"(?i)^(asmem|memtis(-\d+)?)-", "", str(base_str))


def _extract_system(base_str: str) -> str:
    """Detects 'asmem' or 'memtis' substring in BASE field."""
    s = str(base_str).lower()
    if "asmem" in s:
        return "asmem"
    if "memtis" in s:
        return "memtis"
    return "unknown"



def _compute_ratios(df: pd.DataFrame) -> pd.DataFrame:
    """
    For every (dram_config, benchmark) pair, computes asmem/memtis ratio
    for each metric. Uses merge — assumes one run per (system, dram, benchmark).
    """
    group_keys = ["dram_config", "benchmark"]

    asmem  = df[df["system"] == "asmem" ][group_keys + METRICS]
    memtis = df[df["system"] == "memtis"][group_keys + METRICS]
    print(f"  [ratios] asmem rows={len(asmem)}, memtis rows={len(memtis)}")
    print(f"  [ratios] asmem dram_configs:  {sorted(asmem['dram_config'].unique())}")
    print(f"  [ratios] memtis dram_configs: {sorted(memtis['dram_config'].unique())}")
    print(f"  [ratios] asmem benchmarks:    {sorted(asmem['benchmark'].unique())}")
    print(f"  [ratios] memtis benchmarks:   {sorted(memtis['benchmark'].unique())}")

    ratio_df = pd.merge(asmem, memtis, on=group_keys, suffixes=("_asmem", "_memtis"))
    print(f"  [ratios] after merge: {len(ratio_df)} rows")

    for m in METRICS:
        ratio_df[f"ratio_{m}"] = ratio_df[f"{m}_asmem"] / ratio_df[f"{m}_memtis"]

    ratio_cols = [f"ratio_{m}" for m in METRICS]
    ratio_df = ratio_df[group_keys + ratio_cols]
    before = len(ratio_df)
    ratio_df = ratio_df.dropna(subset=ratio_cols, how="all")
    print(f"  [ratios] dropped {before - len(ratio_df)} all-NaN ratio rows, {len(ratio_df)} remain")
    return ratio_df




def load_and_join_metrico(benchmark=None, n_recent=None):
    """
    Reads super_desired and all_results, joining on:
      super_desired['BASE'] (col 0) == all_results[col 4]
    Returns a merged DataFrame.

    benchmark : if given, keep only rows where the last column (ar_col6) equals this value.
    n_recent  : if given, after the benchmark filter keep only the N rows with the
                highest ar_col5 (run timestamp).
    """
    SUPER_DESIRED_PATH = "/mnt/nas/inesc/ist196723/osdi26/super_desired"
    ALL_RESULTS_PATH   = "/mnt/nas/inesc/ist196723/all_results"

    # --- Load super_desired ---
    super_desired_cols = ["BASE", "runID", "promotions", "demotions",
                          "stalls", "access_ratio", "time"]
    df_super = pd.read_csv(
        SUPER_DESIRED_PATH,
        sep=r"\s+",          # whitespace-separated (space-delimited echo output)
        header=None,
        names=super_desired_cols
    )
    df_super["BASE"] = df_super["BASE"].apply(_normalize_base)
    print(f"[load] super_desired: {len(df_super)} rows")
    print(f"[load] super_desired BASE sample (first 5): {df_super['BASE'].unique()[:5].tolist()}")
    mask = df_super["BASE"].str.lower().str.contains("asmem|memtis", na=False)
    df_super = df_super[mask]
    print(f"[load] super_desired after system filter: {len(df_super)} rows")
    print(f"[load] super_desired runID dtype={df_super['runID'].dtype}, sample={df_super['runID'].unique()[:5].tolist()}")

    # --- Load all_results ---
    # Two row formats exist in this file:
    #   7-col: time  0  dram  0  SYSTEM  runID  bench
    #   8-col: time  extra_metric  0  dram  0  SYSTEM  runID  bench
    # The 8-col format (used by mg.C and cg.D) has an extra metric at position 1.
    _ar_names = [f"ar_col{i}" for i in range(9)]
    df_all = pd.read_csv(
        ALL_RESULTS_PATH,
        sep=r"\s+",
        header=None,
        names=_ar_names,
        index_col=False,
        on_bad_lines='skip'
    )
    print(f"[load] all_results raw: {len(df_all)} rows total")
    _nf = df_all.notna().sum(axis=1)
    print(f"[load] column-count distribution: { {k: int(v) for k, v in _nf.value_counts().sort_index().items()} }")

    # Detect 8-col rows: SYSTEM token falls at ar_col5 instead of ar_col4.
    _sys_pat = r"(?i)asmem|memtis"
    _is8 = df_all["ar_col5"].astype(str).str.contains(_sys_pat, na=False)
    _is7 = df_all["ar_col4"].astype(str).str.contains(_sys_pat, na=False)
    print(f"[load] format detection: 7-col={_is7.sum()}, 8-col={_is8.sum()}, neither={( ~_is7 & ~_is8).sum()}")
    print(f"[load] 8-col sample row: { df_all[_is8][['ar_col0','ar_col1','ar_col2','ar_col3','ar_col4','ar_col5','ar_col6','ar_col7']].head(2).to_dict('records') }")

    # Normalise runID, benchmark, and dram_raw into consistent columns.
    df_all["runID"]    = df_all["ar_col6"].where(_is8, df_all["ar_col5"])
    df_all["benchmark"]= df_all["ar_col7"].where(_is8, df_all["ar_col6"])
    df_all["dram_raw"] = df_all["ar_col3"].where(_is8, df_all["ar_col2"])

    # Keep only rows that matched either format.
    df_all = df_all[_is7 | _is8].copy()
    df_all = df_all.dropna(subset=["benchmark"])
    print(f"[load] all_results after format detection: {len(df_all)} rows")
    print(f"[load] all_results benchmarks: {sorted(df_all['benchmark'].dropna().unique().tolist())}")
    print(f"[load] all_results runID dtype={df_all['runID'].dtype}, sample={df_all['runID'].unique()[:5].tolist()}")

    # Check runID type match before join
    df_super["runID"] = pd.to_numeric(df_super["runID"], errors="coerce")
    df_all["runID"]   = pd.to_numeric(df_all["runID"],   errors="coerce")
    print(f"[load] after coercion — super runID dtype={df_super['runID'].dtype}, all runID dtype={df_all['runID'].dtype}")
    _common = set(df_super["runID"].dropna()) & set(df_all["runID"].dropna())
    print(f"[load] runIDs in common: {len(_common)}  (super has {df_super['runID'].nunique()}, all_results has {df_all['runID'].nunique()})")
    if _common:
        _sample_id = next(iter(_common))
        print(f"[load] sample common runID={_sample_id} → bench={df_all.loc[df_all['runID']==_sample_id,'benchmark'].tolist()}")

    if benchmark is not None:
        df_all = df_all[df_all["benchmark"] == benchmark]
        print(f"[load] after benchmark filter ({benchmark!r}): {len(df_all)} rows")

    if n_recent is not None:
        df_all = df_all.nlargest(n_recent, "runID")
        print(f"[load] after n_recent={n_recent}: {len(df_all)} rows")

    # --- Join on runID ---
    merged = pd.merge(df_super, df_all, on="runID", how="inner")
    print(f"[load] after inner join: {len(merged)} rows")
    print(f"[load] merged benchmarks: {sorted(merged['benchmark'].dropna().unique().tolist()) if 'benchmark' in merged.columns else 'NO benchmark col'}")
    if merged.empty:
        print(f"[load]   super_desired runID sample:  {df_super['runID'].dropna().unique()[:5].tolist()}")
        print(f"[load]   all_results runID sample:    {df_all['runID'].dropna().unique()[:5].tolist()}")

    return merged


def _apply_benchmark_config(ratio_df: pd.DataFrame) -> pd.DataFrame:
    """
    For each benchmark that has an entry in BENCHMARK_CONFIGS:
      - restrict the rows to the declared dram_configs (if set)
      - replace the benchmark id with its display_name for labelling
    Benchmarks absent from the registry are left untouched.
    """
    if ratio_df.empty:
        return ratio_df

    frames = []
    for bench, group in ratio_df.groupby("benchmark", sort=False):
        cfg = BENCHMARK_CONFIGS.get(str(bench))
        if cfg is not None:
            if cfg.dram_configs is not None:
                group = group[group["dram_config"].isin(cfg.dram_configs)]
            group = group.copy()
            group["benchmark"] = cfg.display_name
        frames.append(group)

    return pd.concat(frames, ignore_index=True) if frames else ratio_df.iloc[0:0]


def _plot_set(ratio_df: pd.DataFrame,
              facet_col: str,
              bar_col: str,
              title_prefix: str,
              filename_prefix: str,
              output_dir: str = ".") -> list[str]:
    """
    Generates one figure per unique value of `facet_col`.
      X axis  → metrics
      Y axis  → asmem / memtis ratio
      Bars    → unique values of `bar_col`
    Saves each figure as a PNG. Returns list of saved file paths.
    """
    created = []
    facets = sorted(ratio_df[facet_col].dropna().unique())
    if not facets:
        print(f"[SKIP] {filename_prefix}: no data")
        return created
    x      = np.arange(len(METRICS))
    colors = plt.cm.tab10.colors

    for facet in facets:
        fig, ax = plt.subplots(figsize=(max(8, len(METRICS) * 1.8), 5))
        subset   = ratio_df[ratio_df[facet_col] == facet]
        bar_vals = sorted(subset[bar_col].dropna().unique())
        if not bar_vals:
            print(f"[SKIP] {filename_prefix} facet={facet}: no bars")
            plt.close(fig)
            continue
        n_bars = len(bar_vals)
        width  = 0.75 / n_bars

        for i, bar_val in enumerate(bar_vals):
            row = subset[subset[bar_col] == bar_val]
            ratios = [
                float(row[f"ratio_{m}"].iloc[0])
                if len(row) > 0 and not pd.isna(row[f"ratio_{m}"].iloc[0])
                else np.nan
                for m in METRICS
            ]
            offset = (i - n_bars / 2 + 0.5) * width
            ax.bar(
                x + offset, ratios, width,
                label=str(bar_val),
                color=colors[i % len(colors)],
                edgecolor="white", linewidth=0.6
            )

        # Reference line: ratio = 1 means both systems are equal
        ax.axhline(1.0, color="black", linestyle="--", linewidth=1.1,
                   alpha=0.75, label="ratio = 1  (asmem ≡ memtis)")

        ax.set_xticks(x)
        ax.set_xticklabels(METRICS, rotation=20, ha="right", fontsize=10)
        ax.set_ylabel("asmem / memtis  (ratio)", fontsize=11)
        ax.set_title(f"{title_prefix}: {facet}", fontsize=13, fontweight="bold")
        ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2fx"))
        ax.legend(title=bar_col, bbox_to_anchor=(1.01, 1), loc="upper left",
                  fontsize=9, title_fontsize=10)
        ax.grid(axis="y", alpha=0.3, linestyle=":")
        ax.set_axisbelow(True)

        plt.tight_layout()
        safe_name = re.sub(r"[^\w\-]", "_", str(facet))
        fname = os.path.join(output_dir, f"{filename_prefix}_{safe_name}.png")
        fig.savefig(fname, dpi=150, bbox_inches="tight")
        print("Saved to", fname)
        created.append(fname)
        plt.show()
        plt.close(fig)
    return created


# ── Main ───────────────────────────────────────────────────────────────────────

def plot_reality_show(benchmark=None, n_recent=None):
    df = load_and_join_metrico(benchmark=benchmark, n_recent=n_recent)

    # ── Parse system, config type, and DRAM config from BASE ──────────────────
    df["system"]      = df["BASE"].apply(_extract_system)
    df["config_type"] = df["BASE"].apply(_extract_config_type)
    df["dram_config"] = pd.to_numeric(df["dram_raw"], errors="coerce").astype("Int64")

    # ── Coerce metrics to numeric ──────────────────────────────────────────────
    for m in METRICS:
        df[m] = pd.to_numeric(df[m], errors="coerce")

    unknown_mask = df["system"] == "unknown"
    if unknown_mask.any():
        print(f"[drop] {unknown_mask.sum()} rows with unrecognised system type dropped. "
              f"Sample BASE values: {df.loc[unknown_mask, 'BASE'].unique()[:5]}")
    df = df[~unknown_mask]

    config_types = sorted(df["config_type"].dropna().unique())
    print(f"[plot] {len(config_types)} config type(s): {config_types}")

    all_created = []

    for ctype in config_types:
        sub = df[df["config_type"] == ctype]
        print(f"\n[config] === {ctype} === ({len(sub)} rows, "
              f"systems={sub['system'].value_counts().to_dict()}, "
              f"benchmarks={sorted(sub['benchmark'].dropna().unique().tolist())})")

        ratio_df = _compute_ratios(sub)
        if ratio_df.empty:
            print(f"[config] no ratios for {ctype!r}, skipping")
            continue

        ratio_df = _apply_benchmark_config(ratio_df)

        out_dir = re.sub(r"[^\w\-]", "_", ctype)
        os.makedirs(out_dir, exist_ok=True)
        print(f"[config] output folder: {out_dir}/")

        all_created += _plot_set(
            ratio_df,
            facet_col="dram_config",
            bar_col="benchmark",
            title_prefix=f"[{ctype}] DRAM config",
            filename_prefix="plot_by_dram",
            output_dir=out_dir,
        )
        all_created += _plot_set(
            ratio_df,
            facet_col="benchmark",
            bar_col="dram_config",
            title_prefix=f"[{ctype}] Benchmark",
            filename_prefix="plot_by_benchmark",
            output_dir=out_dir,
        )

    print(f"\n{'─'*60}")
    print(f"Created {len(all_created)} file(s):")
    for f in all_created:
        print(f"  {f}")

plot_reality_show()