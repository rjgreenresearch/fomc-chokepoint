#!/usr/bin/env python3
"""
event_window_test.py
Pre-registered event-window test of the claim that chokepoint attacks and
Brent price moves cluster in the days before FOMC rate decisions.

Pure Python stdlib. Runs on Termux (aarch64) and Windows (Python 3.9+).
Protocol: PREREGISTRATION.md (frozen before the 28 Oct 2026 decision).

Usage:
  python event_window_test.py                          # primary analysis, in-sample
  python event_window_test.py --incidents data/incidents_full.csv --brent data/brent.csv
  python event_window_test.py --oos                    # out-of-sample test, Oct 28 meeting
"""
import argparse
import csv
import json
import math
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent

# ---- Frozen protocol parameters (do not edit after registration) ----
SAMPLE_START = date(2026, 3, 1)
SAMPLE_END = date(2026, 10, 3)
PRIMARY_WINDOW = (7, 0)            # D-7 through D, inclusive (8 days)
SENSITIVITY_WINDOWS = [(3, 0), (14, 0)]
ALPHA = 0.05                       # one-sided
OOS_DECISION = date(2026, 10, 28)
OOS_BASELINE_DAYS = 28             # trailing days ending the day before the OOS window
OOS_QUANTILE = 0.95
# ---------------------------------------------------------------------


def log_setup():
    runs = HERE / "runs"
    runs.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-") + f"{datetime.now().microsecond // 1000:03d}"
    path = runs / f"run-{stamp}.log"
    fh = open(path, "w", encoding="utf-8")

    def log(msg=""):
        print(msg)
        fh.write(msg + "\n")
        fh.flush()

    return log, fh, path, stamp


def parse_date(s):
    return datetime.strptime(s.strip(), "%Y-%m-%d").date()


def load_calendar(path):
    rows = []
    with open(path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            rows.append((parse_date(r["decision_date"]), int(r["in_sample"])))
    return rows


def load_incidents(path, include_houthi=True):
    counts = {}
    n_in = n_ex = 0
    with open(path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            keep = r.get("include", "1").strip() == "1" and r.get("event_class", "").strip() == "attack"
            if not include_houthi and r.get("actor_class", "").strip() == "houthi":
                keep = False
            if not keep:
                n_ex += 1
                continue
            d = parse_date(r["event_date"])
            counts[d] = counts.get(d, 0) + 1
            n_in += 1
    return counts, n_in, n_ex


def load_prices(path):
    px = {}
    with open(path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            c = r.get("close", "").strip()
            if c and c.lower() != "null":
                px[parse_date(r["date"])] = float(c)
    return px


def day_range(a, b):
    d = a
    while d <= b:
        yield d
        d += timedelta(days=1)


def window_days(decisions, win, start, end):
    pre, post = win
    s = set()
    for D in decisions:
        for d in day_range(D - timedelta(days=pre), D + timedelta(days=post)):
            if start <= d <= end:
                s.add(d)
    return s


def rate_ratio(counts, wdays, start, end, binary=False):
    n_days = (end - start).days + 1
    win_n = out_n = 0
    for d in day_range(start, end):
        c = counts.get(d, 0)
        if binary:
            c = 1 if c > 0 else 0
        if d in wdays:
            win_n += c
        else:
            out_n += c
    wd = len(wdays)
    od = n_days - wd
    rw = win_n / wd if wd else float("nan")
    ro = out_n / od if od else float("nan")
    rr = rw / ro if ro > 0 else (float("inf") if rw > 0 else float("nan"))
    return rr, win_n, out_n, wd, od


def circular_shift_p(counts, decisions, win, start, end, binary=False):
    """Shift all decision dates by k days (mod sample length) for every k != 0.
    Preserves window count, length, and spacing; breaks alignment with FOMC dates."""
    n_days = (end - start).days + 1
    obs, *_ = rate_ratio(counts, window_days(decisions, win, start, end), start, end, binary)
    ge = 0
    k_total = 0
    for k in range(1, n_days):
        shifted = [start + timedelta(days=((D - start).days + k) % n_days) for D in decisions]
        rr, *_ = rate_ratio(counts, window_days(shifted, win, start, end), start, end, binary)
        if not math.isnan(rr):
            k_total += 1
            if rr >= obs:
                ge += 1
    return obs, (1 + ge) / (1 + k_total), k_total


def binom_sf(k, n, p):
    """P(X >= k), X ~ Binomial(n, p)."""
    if k <= 0:
        return 1.0
    total = 0.0
    for i in range(k, n + 1):
        total += math.comb(n, i) * (p ** i) * ((1 - p) ** (n - i))
    return min(1.0, total)


def poisson_quantile(lam, q):
    k, cdf = 0, math.exp(-lam)
    while cdf < q:
        k += 1
        cdf += math.exp(-lam) * lam ** k / math.factorial(k)
    return k


def close_on_or_before(px, d, max_back=7):
    for i in range(max_back + 1):
        dd = d - timedelta(days=i)
        if dd in px:
            return dd, px[dd]
    return None, None


def window_return(px, D, win):
    pre, _ = win
    d0, p0 = close_on_or_before(px, D - timedelta(days=pre + 1))
    d1, p1 = close_on_or_before(px, D - timedelta(days=1))
    if p0 is None or p1 is None or d0 >= d1:
        return None
    return math.log(p1 / p0)


def brent_test(px, decisions, win, start, end):
    obs_vals = [window_return(px, D, win) for D in decisions]
    if any(v is None for v in obs_vals):
        return None
    obs = sum(obs_vals) / len(obs_vals)
    n_days = (end - start).days + 1
    ge = k_total = 0
    for k in range(1, n_days):
        shifted = [start + timedelta(days=((D - start).days + k) % n_days) for D in decisions]
        vals = [window_return(px, S, win) for S in shifted]
        if any(v is None for v in vals):
            continue
        k_total += 1
        if sum(vals) / len(vals) >= obs:
            ge += 1
    return obs, obs_vals, (1 + ge) / (1 + k_total), k_total


def in_sample(args, log):
    cal = load_calendar(args.calendar)
    decisions = [d for d, flag in cal if flag == 1 and SAMPLE_START <= d <= SAMPLE_END]
    counts, n_in, n_ex = load_incidents(args.incidents)
    results = {"decisions": [d.isoformat() for d in decisions],
               "incidents_file": str(args.incidents),
               "incidents_included": n_in, "incidents_excluded": n_ex}
    log(f"Sample: {SAMPLE_START} to {SAMPLE_END} ({(SAMPLE_END - SAMPLE_START).days + 1} days)")
    log(f"FOMC decisions in sample: {', '.join(results['decisions'])}")
    log(f"Incidents included: {n_in}  excluded: {n_ex}  file: {args.incidents}")
    log("")

    def run(label, win, cts, start=SAMPLE_START, decs=decisions, binary=False):
        wd = window_days(decs, win, start, SAMPLE_END)
        rr, wn, on, wdn, odn = rate_ratio(cts, wd, start, SAMPLE_END, binary)
        _, p_perm, k = circular_shift_p(cts, decs, win, start, SAMPLE_END, binary)
        total = wn + on
        p_bin = binom_sf(wn, total, wdn / (wdn + odn)) if total else float("nan")
        log(f"[{label}] window D-{win[0]}..D+{win[1]}  "
            f"in-window {wn}/{wdn}d  outside {on}/{odn}d  RR={rr:.3f}  "
            f"p_perm={p_perm:.4f} (K={k})  p_binom={p_bin:.4f}")
        return {"window": list(win), "rr": rr, "in_window": wn, "window_days": wdn,
                "outside": on, "outside_days": odn, "p_perm": p_perm, "K": k, "p_binom": p_bin}

    results["H1_primary"] = run("H1 primary, counts", PRIMARY_WINDOW, counts)
    results["H1_binary_days"] = run("H1 robustness, attack-days", PRIMARY_WINDOW, counts, binary=True)
    for w in SENSITIVITY_WINDOWS:
        results[f"H1_sens_{w[0]}"] = run(f"H1 sensitivity", w, counts)
    apr1 = date(2026, 4, 1)
    results["H1_ex_march"] = run("H1 excluding war-onset March", PRIMARY_WINDOW, counts,
                                 start=apr1, decs=[d for d in decisions if d >= apr1])
    hc, _, _ = load_incidents(args.incidents, include_houthi=False)
    results["H1_iran_only"] = run("H1 Iran/unattributed only", PRIMARY_WINDOW, hc)

    log("")
    if args.brent and Path(args.brent).exists():
        px = load_prices(args.brent)
        bt = brent_test(px, decisions, PRIMARY_WINDOW, SAMPLE_START, SAMPLE_END)
        if bt:
            obs, vals, p, k = bt
            log(f"[H2 Brent] mean pre-window log return {obs:+.4f}  "
                f"per meeting {', '.join(f'{v:+.4f}' for v in vals)}  p_perm={p:.4f} (K={k})")
            results["H2_brent"] = {"mean_logret": obs, "per_meeting": vals, "p_perm": p, "K": k}
        else:
            log("[H2 Brent] insufficient price coverage; run fetch_brent.py first")
    else:
        log("[H2 Brent] skipped: no price file (run fetch_brent.py)")

    p = results["H1_primary"]["p_perm"]
    verdict = ("REJECT H0: attacks cluster before FOMC decisions" if p < ALPHA
               else "FAIL TO REJECT H0: no detectable pre-FOMC clustering")
    log("")
    log(f"Primary decision (alpha={ALPHA}, one-sided, circular-shift permutation): {verdict}")
    results["verdict"] = verdict
    return results


def oos(args, log):
    counts, n_in, _ = load_incidents(args.incidents)
    pre, post = PRIMARY_WINDOW
    w_start = OOS_DECISION - timedelta(days=pre)
    w_end = OOS_DECISION + timedelta(days=post)
    b_end = w_start - timedelta(days=1)
    b_start = b_end - timedelta(days=OOS_BASELINE_DAYS - 1)
    base_n = sum(counts.get(d, 0) for d in day_range(b_start, b_end))
    w_len = (w_end - w_start).days + 1
    full_days = (SAMPLE_END - SAMPLE_START).days + 1
    full_n = sum(counts.get(d, 0) for d in day_range(SAMPLE_START, SAMPLE_END))
    # Frozen rule: equal-weight blend of trailing 28-day rate and full in-sample rate,
    # so a quiet baseline month cannot make a single attack look anomalous.
    rate = 0.5 * (base_n / OOS_BASELINE_DAYS) + 0.5 * (full_n / full_days)
    lam = rate * w_len
    thresh = max(1, poisson_quantile(lam, OOS_QUANTILE))
    obs = sum(counts.get(d, 0) for d in day_range(w_start, w_end))
    log(f"OOS meeting {OOS_DECISION}: window {w_start}..{w_end}")
    log(f"Trailing baseline {b_start}..{b_end}: {base_n} attacks; full sample: {full_n} attacks / {full_days} days")
    log(f"Blended expected count in window: {lam:.2f}")
    log(f"Pre-registered threshold (Poisson {OOS_QUANTILE:.0%} quantile): >= {thresh} attacks")
    log(f"Observed in window: {obs}")
    if obs >= thresh:
        v = "CONSISTENT with pre-FOMC escalation claim"
    else:
        v = "NOT CONSISTENT with pre-FOMC escalation claim"
    log(f"OOS outcome: {v}")
    return {"oos_decision": OOS_DECISION.isoformat(), "window": [w_start.isoformat(), w_end.isoformat()],
            "baseline": [b_start.isoformat(), b_end.isoformat()], "baseline_attacks": base_n, "full_sample_attacks": full_n,
            "expected": lam, "threshold": thresh, "observed": obs, "outcome": v}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--calendar", default=str(HERE / "data" / "fomc_calendar_2026.csv"))
    ap.add_argument("--incidents", default=str(HERE / "data" / "incidents_seed.csv"))
    ap.add_argument("--brent", default=str(HERE / "data" / "brent.csv"))
    ap.add_argument("--oos", action="store_true", help="run the out-of-sample Oct 28 test")
    args = ap.parse_args()

    log, fh, path, stamp = log_setup()
    log(f"event_window_test run {stamp}")
    if "seed" in Path(args.incidents).name:
        log("WARNING: running on the SEED log. Seed is incomplete; results are not the registered test.")
    log("")
    res = oos(args, log) if args.oos else in_sample(args, log)
    out = path.with_suffix(".json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2, default=str)
    log("")
    log(f"Log: {path}")
    log(f"JSON: {out}")
    fh.close()


if __name__ == "__main__":
    sys.exit(main())
