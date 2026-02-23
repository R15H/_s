# Bug Report: python_parserFTW.py & python_parser.py

Analysis of `mago()`, `simple_weight()`, `valo()`, and functions that depend on them.

---

## BUG 1 — `_m()` called with list instead of unpacked args (python_parserFTW.py)

**File:** `bin/python_parserFTW.py`
**Lines:** 1591–1592

```python
def _m(*args):
    return np.mean(np.array(args))
```

Called as:
```python
'all_fast' : _m([77.81]),
'all_slow': _m([213.11]),
```

`_m` uses `*args`, so `_m([77.81])` results in `args = ([77.81],)`, and `np.array(args)` creates a 2D array `array([[77.81]])` instead of `array([77.81])`. While `np.mean` still returns the correct scalar here by coincidence, the semantics are wrong — compare with line 1596 where `_m(139.37, 132.70, 141.23)` is called correctly with unpacked values. The inconsistency means `_m` was designed for unpacked args but is being called with a list in some places.

**Severity:** Low (works by accident, but inconsistent and fragile)

---

## BUG 2 — `mago()`: Syntax error creating a set literal instead of dict value (python_parser.py)

**File:** `bin/python_parser.py`
**Lines:** 762–765

```python
'3000': {
    np.mean(np.array([84.06, 78.30, ...]))
    # stable all good!
}
```

The `'3000'` key in `params['mg.C']['TPP']` uses curly braces `{}` instead of parentheses. This creates a **set** containing the float value, not the float itself. So `params['mg.C']['TPP']['3000']` is `{80.xxx}` (a set) rather than `80.xxx` (a float). Any downstream arithmetic on this value will fail or produce wrong results.

In `python_parserFTW.py` (line 1638), this is fixed — the value is correctly written as a bare expression without braces.

**Severity:** High — produces a set where a float is expected; will cause type errors in arithmetic operations.

---

## BUG 3 — `mago()`: Duplicate dict keys silently override values (python_parserFTW.py)

**File:** `bin/python_parserFTW.py`
**Lines:** 1689–1703 (`bcu` params block)

```python
'bcu': {
    'RSS': 22000,                          # line 1690 — FIRST definition
    'OBJ_DRAMS': [0, 512, ...],            # line 1691 — FIRST definition
    'soargrep': 'urand.sg',               # line 1693 — FIRST definition
    'SYSTEM_COL': "5",                     # line 1695 — FIRST definition
    'RSS': 22000,                          # line 1697 — DUPLICATE (overwrites)
    ...
    'OBJ_DRAMS': [0, 512, ...],            # line 1701 — DUPLICATE (overwrites)
    'SYSTEM_COL': "5",                     # line 1702 — DUPLICATE (overwrites)
    'soargrep': 'kron.sg',                # line 1703 — DUPLICATE, DIFFERENT VALUE!
```

`'soargrep'` is defined twice with different values: first `'urand.sg'` (line 1693), then overwritten by `'kron.sg'` (line 1703). Since Python uses the last value, `soargrep` will be `'kron.sg'` — but the original intent appears to have been `'urand.sg'` based on the `bcu` benchmark name (which stands for "bc urand"). This will cause `mago()` to grep for the wrong benchmark when processing `bcu`.

Similarly, `'RSS'`, `'OBJ_DRAMS'`, and `'SYSTEM_COL'` are all defined twice (though with the same values — wasteful but harmless).

**Severity:** High — `soargrep` silently uses the wrong value, which corrupts data selection for the `bcu` benchmark.

---

## BUG 4 — `mago()`: `ax` used before definition (python_parser.py)

**File:** `bin/python_parser.py`
**Line:** 900

```python
plt.figure()
ax.axhline(y=params[bench]['all_slow']/norm, color='blue', ...)
```

`plt.figure()` is called but its return value is not assigned. Then `ax.axhline(...)` references `ax` which was never defined in this scope. This will raise a `NameError` at runtime. Should be `fig, ax = plt.subplots()` or `ax = plt.gca()`.

**Severity:** High — guaranteed crash (`NameError`).

---

## BUG 5 — `mago()`: `SOAR_DRAMS` length mismatch with `SOAR_TIMES` for `mg.C` (python_parser.py)

**File:** `bin/python_parser.py`
**Lines:** 918–919

```python
if bench == "mg.C":
    SOAR_TIMES = [212.86, 147.36]       # 2 elements
    SOAR_DRAMS = DRAMS_BY_OBJ           # 4 elements: [1186, 2372, 3458, 3570]
```

`SOAR_TIMES` has 2 elements but `SOAR_DRAMS` has 4 (it's set to the full `DRAMS_BY_OBJ`). When these are used together (e.g., `plt.bar(x + i*width, ...)`), the dimension mismatch will cause an error or silently misalign data.

**Severity:** High — data dimension mismatch.

---

## BUG 6 — `mago()`: Mixed dict key types — string integers vs quoted integers (python_parserFTW.py)

**File:** `bin/python_parserFTW.py`
**Lines:** 1606–1622, 1625–1652

In the `SOAR` sub-dict:
```python
'SOAR' : {
    '1186' :  np.mean(np.array([150.35])),
    "2372":   np.mean(np.array([77.53])),
}
```

And in the `STOCK` sub-dict:
```python
'STOCK': {
    '1': _m(139.37, 132.70, 141.23),
    '2': 87.705,
    '3': 20  # FILL
}
```

The keys switch between representing DRAM sizes (`'1186'`, `"2372"`) and ordinal indices (`'1'`, `'2'`, `'3'`), and between single-quoted and double-quoted strings inconsistently. When accessed downstream by the `manual()` function (line 930+), iteration over `sorted(list(s.keys()))` will yield lexicographic ordering (`'1186'` before `'2372'`), not numeric. This is a latent correctness problem if any code depends on numeric key ordering.

**Severity:** Medium — inconsistent key schemes risk incorrect data alignment.

---

## BUG 7 — `simple_weight()`: `header` computed from `uniq_add+1` does element-wise add, not length+1 (python_parser.py)

**File:** `bin/python_parser.py`
**Line:** 2172

```python
header = (str(len(uniq_add+1)) + " ") * 10 + "\n"
```

`uniq_add` is a numpy array. `uniq_add+1` adds 1 to every element (element-wise), not to the length. `len(uniq_add+1)` equals `len(uniq_add)`, so the `+1` is a no-op. The intended code was almost certainly:

```python
header = (str(len(uniq_add) + 1) + " ") * 10 + "\n"
```

In `python_parserFTW.py` (line 4161), the FTW version correctly uses `actually_added+1` — confirming the parser.py version is buggy.

**Severity:** High — the header count is always off by 1 compared to intent, corrupting the output format.

---

## BUG 8 — `simple_weight()`: `break` after first iteration of `agg_keys` loop (python_parserFTW.py)

**File:** `bin/python_parserFTW.py`
**Lines:** 3922–3925

```python
for k in agg_keys:
    v = np.concatenate((agg[k], load_aggregate_fields(data, r)[k]))
    agg[k] = v
    break
```

The `break` causes only the first key in `agg_keys` (`'count'`) to be concatenated. The remaining keys (`'address'`, `'accessBracket'`, `'stallCyclesMLPLoad'`) are never appended when aggregating runs. This means the aggregate data arrays become misaligned — `agg['count']` grows with each merged run, but the other arrays don't.

**Severity:** Critical — silently corrupts aggregate data alignment, producing incorrect weight computations.

---

## BUG 9 — `simple_weight()`: Aggregate concatenation uses `r` instead of `ru` (python_parserFTW.py)

**File:** `bin/python_parserFTW.py`
**Line:** 3923

```python
for ru in data:
    ...
    if binary == this_binary:
        ...
        for k in agg_keys:
            v = np.concatenate((agg[k], load_aggregate_fields(data, r)[k]))  # <-- uses r, not ru!
            agg[k] = v
            break
```

The loop iterates over `ru` but loads aggregate fields for `r` (the original run, not the current `ru`). This means it concatenates the *same* run's aggregate data repeatedly instead of the matching run's data. The `keys_used` loop on line 3916 correctly uses `ru` for instruction fields, but the aggregate loop does not.

Same bug exists in `python_parser.py` at line 2251 in the equivalent section — wait, let me verify.

Actually in `python_parser.py`, the aggregate loop doesn't exist at all in `simple_weight()` — the parser.py version doesn't aggregate `agg_keys` in the MULTI loop.

**Severity:** Critical — aggregate data is always from the same run repeated N times, not from the N different runs.

---

## BUG 10 — `simple_weight()`: `agg` is re-loaded from scratch after the MULTI merge, discarding all concatenated data (python_parserFTW.py)

**File:** `bin/python_parserFTW.py`
**Line:** 3955

```python
# After the MULTI block merges agg data (lines 3922-3924):
agg = load_aggregate_fields(data, r)   # completely overwrites the merged agg!
```

All the aggregate concatenation work done in the MULTI block is thrown away because `agg` is reassigned by loading fresh data from just run `r`. This means the multiprocessing merge of aggregate fields has zero effect.

**Severity:** Critical — silently discards all merged aggregate data.

---

## BUG 11 — `simple_weight()`: Unreachable code after `return` in FTW version (python_parserFTW.py)

**File:** `bin/python_parserFTW.py`
**Lines:** 4175–4204

```python
        return
        if "syn" in benchset:      # UNREACHABLE
            ...
        def do_compressed(...):    # UNREACHABLE
            ...
        with open(...) as f:       # UNREACHABLE
            f.write(do_compressed(ints_1, uniq_add))
```

The `return` at line 4175 makes all subsequent code dead — the synthetic benchset handling and `do_compressed` output files are never written. The `python_parser.py` version does NOT have this early return, so these outputs are generated there but not in FTW.

**Severity:** High — compressed output files and synthetic benchset handling are silently disabled.

---

## BUG 12 — `simple_weight()`: `exit(0)` in `_proccess_inst` kills the whole process on a non-fatal condition (python_parserFTW.py)

**File:** `bin/python_parserFTW.py`
**Line:** 4071

```python
if not OLD_V4 and not ignore_inst:
    exit(0)
    mlpWeighted /= 1024     # DEAD CODE after exit
    mlp_by_mean = ...        # DEAD CODE
```

When `OLD_V4` is False and `ignore_inst` is False, the program terminates immediately. The code after `exit(0)` is dead. Since `OLD_V4` is set to `False` (line 3808) and `ignore_inst` is `True` (line 3844), this path is currently avoided only because `ignore_inst = True`. If `ignore_inst` were ever changed to `False`, this would crash.

**Severity:** Medium — latent crash behind a flag; dead code after `exit(0)`.

---

## BUG 13 — `simple_weight()`: `exit(0)` in error handler in python_parser.py

**File:** `bin/python_parser.py`
**Lines:** 2108–2110, 2145–2148

```python
if(len(load_inst_fields(data, r)['totalTime']) != len(load_inst_fields(data, r)['address'])):
    print("big mistake!!")
    exit(0)
```

And:
```python
except:
    print("FAILED??")
    exit(0)
    break    # unreachable
```

Using `exit(0)` in error handling terminates the entire process instead of skipping the problematic run. The FTW version (line 3901) improved this to `raise Exception(...)` for the first case, but the second case (line 3921) still has `exit(0)`.

**Severity:** Medium — crashes the entire analysis pipeline instead of skipping a single bad run.

---

## BUG 14 — `simple_weight()` (python_parser.py): `else: return` followed by `pass` makes non-MULTI path dead

**File:** `bin/python_parser.py`
**Lines:** 2153–2156

```python
        else:
            return
            pass
            #return
```

When `MULTI` is False, the function always returns early, making the rest of `simp()` unreachable in non-MULTI mode. The `pass` after `return` is dead code. Combined with `MULTI=True` (line 2070) this is currently inert, but the code structure suggests this was not always intended — someone tried to disable/enable the return via comments.

**Severity:** Low — dead code; confusing intent.

---

## BUG 15 — `valo()`: `benchset` vs `benchsett` variable name mismatch (python_parserFTW.py)

**File:** `bin/python_parserFTW.py`
**Line:** 8706

```python
def valo(data, r):
    ...
    benchsett = data[r]['0']['benchset']   # 'benchsett' with double t
    ...
    if "80" not in data[r]:
        print("No 80 run", benchset, data[r]['0']['bench'])  # uses 'benchset' (no double t)!
```

The function defines `benchsett` (with double t) on line 8682, but line 8706 references `benchset` (single t) — a different variable from an outer scope. This will either use a stale value from a previous iteration or raise a `NameError`.

Same bug in `python_parser.py` line 6068.

**Severity:** High — references wrong variable; will print/use incorrect benchset value.

---

## BUG 16 — `valo()`: Swapped labels for "Active cycles fast" and "Active cycles slow" (python_parser.py)

**File:** `bin/python_parser.py`
**Lines:** 6142–6143

```python
'Active cycles fast': (getSLOW('currentCycle') - getSLOW('stalledCycles'))/norm,
'Active cycles slow': (get('currentCycle') - get('stalledCycles'))/norm,
```

`getSLOW` reads from `glob_80` (the slow tier data) and `get` reads from `glob_0` (the fast tier data). So `'Active cycles fast'` is computed from the **slow** data and `'Active cycles slow'` is computed from the **fast** data — the labels are swapped.

In `python_parserFTW.py` (lines 8846–8847), the labels are correct:
```python
'Active cycles slow': (getSLOW('currentCycle') - getSLOW('stalledCycles'))/norm,
'Active cycles fast': (get('currentCycle') - get('stalledCycles'))/norm,
```

**Severity:** High — metrics are labeled backwards, producing misleading analysis results.

---

## BUG 17 — `valo()`: Operator precedence error in `∆ Squashed` computation (both files)

**File:** `bin/python_parserFTW.py` line 8908, `bin/python_parser.py` line 6208

```python
globy['∆ Squashed'] = getSLOW('totalSquashed') - get('totalSquashed') / norm
```

Due to operator precedence, this computes `getSLOW('totalSquashed') - (get('totalSquashed') / norm)` instead of the intended `(getSLOW('totalSquashed') - get('totalSquashed')) / norm`. The delta should be normalized, but instead only the fast-tier value is divided by `norm` before subtraction.

Compare with `'Squashed instructions'` on the line above it, which does `aggregate_op(...) / norm` — consistent normalization of a single value, not a delta.

**Severity:** High — produces mathematically wrong metric in both files.

---

## BUG 18 — `valo()`: `norm_function()` missing `"active"` case (python_parser.py)

**File:** `bin/python_parser.py`
**Lines:** 6112–6127

```python
def norm_function():
    if NORM == "fast_cycles":
        ...
    if NORM == "NONE":
        ...
    if NORM == "STALL":
        ...
    if NORM == "TPP":
        ...
    if NORM == "PEBS":
        ...
    if NORM == "user":
        ...
    else:
        exit("Unknown norm: " + NORM)
```

The python_parser.py version is missing the `"active"` case that exists in python_parserFTW.py (line 8792). Also missing the `"stores"` case (FTW line 8807). If `NORM` is set to `"active"` or `"stores"`, this function will fall through to the `else` branch and terminate.

Additionally, the chain of `if` statements (not `elif`) means the `else` is only paired with the *last* `if NORM == "user"`. If `NORM` is any value other than `"user"`, the `else` branch executes `exit(...)` even for valid norms — this is the pattern in parser.py. In FTW, the same structural issue exists.

**Severity:** High — incorrect `if/elif` chain means `exit()` fires for any valid NORM except `"user"`.

---

## BUG 19 — `iterate_over_benches()`: Missing `continue` when keys '0' or '80' are absent (both files)

**File:** `bin/python_parserFTW.py` lines 4279–4283, `bin/python_parser.py` lines 2318–2322

```python
for r in data:
    if '0' not in data[r].keys() or '80' not in data[r].keys():
        pass           # should be 'continue'!
```

When a run is missing the `'0'` or `'80'` key, the code does `pass` and falls through to access `data[r]['0']['benchnr']` on the next line, which will raise a `KeyError`. The comment `# <---------` suggests this was noticed before. The `continue` is commented out.

**Severity:** High — every run missing a key will crash with `KeyError` (caught by the outer try/except, but inflates `bad_runs` count and hides the real error).

---

## BUG 20 — `valo()`: Dead code after `raise Exception(...)` (both files)

**File:** `bin/python_parserFTW.py` lines 8680–8681, 8685–8686, 8714–8715, 8736–8737
**File:** `bin/python_parser.py` lines 6050–6051, 6055–6056, 6076–6077, 6098–6099

```python
raise Exception("Unaligned execution detected!!")
return   # DEAD CODE — never reached
```

Multiple locations have `return` statements immediately after `raise Exception(...)`. The `return` is unreachable because the exception is always thrown first. This is not functionally a bug (the exception is the intended behavior) but indicates confused control flow — perhaps the intent was to `return` (skip the run) rather than raise an exception (which might also terminate if not caught).

**Severity:** Low — dead code; misleading intent.

---

## BUG 21 — `valo()`: Incorrect epoch timestamp for December 7, 2025 (both files)

**File:** `bin/python_parserFTW.py` line 8724, `bin/python_parser.py` line 6086

```python
december_day_7_2025_mid_night = 1765065600
```

Unix timestamp `1765065600` corresponds to **December 7, 2025 00:00:00 UTC+1** (actually `1733529600` is Dec 7 2024 midnight UTC). The value `1765065600` is actually **late 2025 / early 2026**. While the date filtering is currently disabled (the `pass` path), if ever re-enabled, the wrong epoch will filter incorrectly.

**Severity:** Low — currently disabled; incorrect constant if ever re-enabled.

---

## BUG 22 — `simple_weight()` FTW: `process_inst` uses closure variables `i`, `ignore_inst` inside multiprocessing Pool

**File:** `bin/python_parserFTW.py`
**Lines:** 3978, 4148–4151

```python
def process_inst(addr):
    ...
    sel = ...   # uses 'i' from closure
    mlpWeighted = 0 if ignore_inst else ...  # uses 'ignore_inst' from closure
    ...

from pathos.multiprocessing import Pool
with Pool(30) as p:
    results = p.map(process_inst, uniq_add)
```

`process_inst` references `i` (instruction data dict), `ignore_inst`, `OLD_V4`, and other closure variables from `simp()`. When using `pathos.multiprocessing.Pool`, these get serialized/pickled. Numpy arrays inside `i` are large, and pickling them 30 times is very expensive. More importantly, `load_aggregate_fields` inside `_proccess_inst` (line 4128) re-loads data from disk inside each worker — which is redundant and slow, and also means the aggregate data `agg` accumulated in the MULTI loop is not used by the workers.

**Severity:** Medium — performance issue and potential correctness issue with stale data in workers.

---

## BUG 23 — `simple_weight()` FTW: `process_inst` → `_proccess_inst` may fail silently and `zero` may be unbound

**File:** `bin/python_parserFTW.py`
**Lines:** 4133–4142

```python
try:
    zero = _proccess_inst(addr, agg)
    eighty = _proccess_inst(addr, agg80)
except Exception as e:
    print(e)
    import traceback
    traceback.print_exc()

if not zero:       # <-- if the try block raised, 'zero' is UNBOUND
    return ""
return zero[:-2] + " " + eighty
```

If `_proccess_inst` raises an exception for the `agg` call, `zero` is never assigned, and the subsequent `if not zero` raises an `UnboundLocalError`. If only the `agg80` call fails, `eighty` is unbound and `zero[:-2] + " " + eighty` raises `UnboundLocalError`.

**Severity:** High — unhandled exception path leads to `UnboundLocalError`.

---

## BUG 24 — `overloaded_cost()`: `n_hidden` computed identically to `n_llc_misses` (python_parserFTW.py)

**File:** `bin/python_parserFTW.py`
**Lines:** 4002–4009

```python
def overloaded_cost(bracket):
    hidden_cost = (aggi['address'] == addr) & (aggi['accessBracket'] <= bracket)
    llc_misses  = (aggi['address'] == addr) & (aggi['accessBracket'] > bracket)
    n_llc_misses = np.sum(aggi['count'][llc_misses])
    n_llc_misses = n_llc_misses if n_llc_misses != 0 else 1
    n_hidden = np.sum(aggi['count'][llc_misses])     # BUG: should be hidden_cost, not llc_misses
    n_hidden = n_hidden if n_hidden != 0 else 1
    return (np.sum(aggi['stallCyclesMLPLoad'][hidden_cost])/n_llc_misses) + ...
```

`n_hidden` is computed as `np.sum(aggi['count'][llc_misses])` — the same as `n_llc_misses`. It should be `np.sum(aggi['count'][hidden_cost])`. The `hidden_cost` mask is intended to select the hidden (low-latency) accesses, and `n_hidden` should count those. Same bug in `inst_cost()` at line 4015.

Additionally, `n_hidden` is computed but never used — the return statement divides by `n_llc_misses` for both terms.

**Severity:** High — wrong denominator / unused variable; the cost calculation for hidden accesses is incorrect.

---

## BUG 25 — `mago()` FTW: `Alto` dict has trailing comma after `0` creating a valid but wrong entry

**File:** `bin/python_parserFTW.py`
**Line:** 1652

```python
'Alto' : {
    '1186' : np.mean(np.array([5330.72, 5299.27])),
    "2372": np.mean(np.array([169.63, 204.03, 226.90, 210.53])),
    '4000' : 0  # FAILS, catastrophic migration overhead
},
```

The key `'4000' : 0` with comment "FAILS" is included in the dict. When `manual()` iterates over `sorted(list(s.keys()))`, it will include this zero-value entry, which could distort plots or averages. This is data that the comment says should not be used.

**Severity:** Low — the 0 value should probably be removed or the entry commented out.

---

## Summary Table

| # | Bug | File(s) | Severity | Function |
|---|-----|---------|----------|----------|
| 1 | `_m()` called with list arg | FTW | Low | mago |
| 2 | Set literal `{}` instead of float value | parser.py | **High** | mago |
| 3 | Duplicate dict keys, `soargrep` overwritten | FTW | **High** | mago |
| 4 | `ax` undefined (NameError) | parser.py | **High** | mago |
| 5 | SOAR_DRAMS/SOAR_TIMES length mismatch | parser.py | **High** | mago |
| 6 | Mixed key types (string ints) | FTW | Medium | mago |
| 7 | `len(uniq_add+1)` element-wise, not length+1 | parser.py | **High** | simple_weight |
| 8 | `break` after first agg_key iteration | FTW | **Critical** | simple_weight |
| 9 | Aggregate uses `r` instead of `ru` | FTW | **Critical** | simple_weight |
| 10 | `agg` re-loaded, discarding merge | FTW | **Critical** | simple_weight |
| 11 | Unreachable code after `return` | FTW | **High** | simple_weight |
| 12 | `exit(0)` kills process in non-fatal path | FTW | Medium | simple_weight |
| 13 | `exit(0)` in error handlers | parser.py | Medium | simple_weight |
| 14 | `else: return` makes non-MULTI dead | parser.py | Low | simple_weight |
| 15 | `benchset` vs `benchsett` name mismatch | Both | **High** | valo |
| 16 | Swapped "fast"/"slow" labels | parser.py | **High** | valo |
| 17 | Operator precedence in `∆ Squashed` | Both | **High** | valo |
| 18 | Missing norm cases + bad if/elif chain | parser.py | **High** | valo |
| 19 | Missing `continue` in iterate_over_benches | Both | **High** | iterate_over_benches |
| 20 | Dead code after `raise` | Both | Low | valo |
| 21 | Wrong epoch timestamp | Both | Low | valo |
| 22 | Closure vars in multiprocessing Pool | FTW | Medium | simple_weight |
| 23 | Unbound `zero`/`eighty` after exception | FTW | **High** | simple_weight |
| 24 | `n_hidden` uses wrong mask | FTW | **High** | simple_weight |
| 25 | Failed data point included in dict | FTW | Low | mago |

**Critical:** 3 | **High:** 13 | **Medium:** 4 | **Low:** 5
