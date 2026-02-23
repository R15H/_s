# Code Review: `psw___()` in `bin/python_parserFTW.py` (lines 3546–3796)

**Purpose:** Reads synthetic weight experiment files, extracts per-instruction
weight fields for two instruction addresses, and plots weight ratios.

---

## Coding Mistakes (Bugs)

### 1. Custom legend is immediately overwritten (HIGH — lines 3785, 3789)

```python
plt.legend(all_handles, all_labels, loc='upper right', framealpha=0.9)  # line 3785
# ...
plt.legend()  # line 3789 — OVERWRITES the custom legend
```

The carefully constructed multi-section custom legend (Access Pattern, Metric,
Measurement) is immediately replaced by a bare `plt.legend()` call. All
legend construction work (lines 3716–3785) is wasted.

**Fix:** Remove the `plt.legend()` call at line 3789.

### 2. Dead-code block overwrites `df_inst1` (HIGH — line 3635)

```python
for df_inst1 in [_, df_inst2]:
```

This loop variable rebinds `df_inst1` to `df_inst2` on the second iteration.
If this block were ever re-enabled (`impo` set to even), the active plotting
block below would use `df_inst2` for both numerator and denominator, plotting
ratios of 1.0.

**Fix:** Use a different loop variable name (e.g., `df_curr`).

### 3. Duplicate legend entries in active scatter loop (MEDIUM — lines 3663, 3668)

Both scatter calls use `label=weight`, producing each metric twice in the
legend with no distinction between raw ratio and delta ratio.

**Fix:** Use `label=weight` for the first scatter and `label="_nolegend_"` (or
a different label like `weight + " Δ"`) for the second.

### 4. Legend labels don't match `FIELDSSS` (MEDIUM — line 3723)

Custom legend hardcodes `'MLP_BY_MEAN'` as the blue metric, but `FIELDSSS`
uses `"AVG_INST_COST_160"` as its first (blue) field.

**Fix:** Keep legend labels in sync with `FIELDSSS`.

### 5. `wc` color index is fragile (LOW — line 3622)

`wc` is shared state between the dead block and the active block. Works by
accident because the dead block never runs. Enabling it would corrupt `wc`.

**Fix:** Reset `wc = 0` immediately before each plotting loop.

---

## Logical Errors

### 1. Positional division assumes aligned DataFrames (HIGH — line 3661)

```python
df_inst1[str(weight)] / df_inst2[str(weight)]
```

After `reset_index`, integer indices only align if both DataFrames have the
same `(arand, aptr)` pairs in the same order. If any file is missing one
instruction address, the division produces wrong results or NaN silently.

**Fix:** Merge `df_inst1` and `df_inst2` on `["arand", "aptr"]` before
computing ratios.

### 2. `startswith` address matching can over-match (MEDIUM — line 3566)

```python
if not l.startswith(str(aptr_inst)) and not l.startswith(str(arand_inst)):
```

If address `14416` exists and a line starts with `144160`, the prefix check
matches incorrectly.

**Fix:** Split the line and compare the first field exactly:
`l.split(" ")[0] == str(aptr_inst)`.

### 3. `climb` mask alignment assumption (MEDIUM — line 3619)

`climb` is computed from `df_inst1` and used to index into both `df_inst1`
(safe) and implicitly against `df_inst2` data in ratio calculations. If the
two DataFrames have different lengths, boolean indexing will fail or silently
produce wrong slices.

### 4. Large dead-code blocks (LOW — lines 3631, 3675)

- `impo = 1; if impo % 2 == 0:` — always False
- `if False and True:` — always False

These blocks contain bugs of their own and make the function hard to read.

---

## Data Column Correspondence

### Correct:
- `WEIGHT_FIELD` enum maps indices 0–15 to base fields and 16–31 to `"80"`
  variants via `get_name()`. This is consistent with how columns like
  `"TOTAL_TIME80"` are later accessed.
- `arand` and `aptr` are correctly parsed from the filename and added to each
  row from that file.
- The `pd.concat` is inside the line loop (line 3576), so multiple rows per
  file are captured correctly.

### Incorrect:
- The ADDR column (index 0 in each line) is matched via string prefix, not
  exact equality — potential for false matches.
- Ratio computations between `df_inst1` and `df_inst2` assume positional
  alignment without an explicit join on the experiment parameters.

---

## Summary

| # | Severity | Lines | Issue |
|---|----------|-------|-------|
| 1 | HIGH | 3789 | `plt.legend()` overwrites custom legend |
| 2 | HIGH | 3635 | Dead block overwrites `df_inst1` |
| 3 | HIGH | 3661 | Positional division without merge/join |
| 4 | MEDIUM | 3723 | Legend label mismatch with FIELDSSS |
| 5 | MEDIUM | 3663,3668 | Duplicate legend labels |
| 6 | MEDIUM | 3566 | `startswith` over-matching addresses |
| 7 | LOW | 3631,3675 | Dead code blocks |
