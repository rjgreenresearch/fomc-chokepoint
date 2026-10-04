#!/usr/bin/env python3
"""
fetch_brent.py
Download daily Brent front-month futures closes (Yahoo symbol BZ=F) to data/brent.csv.
Pure stdlib. If your existing Yahoo fetcher already writes date,close CSVs, use that instead
and point event_window_test.py --brent at its output.

Usage: python fetch_brent.py [--start 2026-01-01] [--end 2026-11-06] [--symbol BZ=F]
Note: front-month futures roll monthly; an 8-day window can straddle a roll.
The protocol treats this as a known limitation (see PREREGISTRATION.md, section 7).
"""
import argparse
import csv
import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent


def to_epoch(s):
    return int(datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2026-01-01")
    ap.add_argument("--end", default=datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    ap.add_argument("--symbol", default="BZ=F")
    ap.add_argument("--out", default=str(HERE / "data" / "brent.csv"))
    a = ap.parse_args()

    url = ("https://query1.finance.yahoo.com/v8/finance/chart/"
           f"{urllib.parse.quote(a.symbol)}?period1={to_epoch(a.start)}"
           f"&period2={to_epoch(a.end) + 86400}&interval=1d")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read().decode("utf-8"))
    res = data["chart"]["result"][0]
    ts = res["timestamp"]
    closes = res["indicators"]["quote"][0]["close"]
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "close"])
        for t, c in zip(ts, closes):
            if c is None:
                continue
            w.writerow([datetime.fromtimestamp(t, tz=timezone.utc).strftime("%Y-%m-%d"), f"{c:.4f}"])
            n += 1
    print(f"Wrote {n} rows to {out}")


if __name__ == "__main__":
    main()
