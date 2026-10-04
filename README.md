# FOMC Chokepoint Event-Window Test (v1.0)

Pre-registered test of whether Middle East shipping attacks and Brent moves cluster before FOMC decisions. Protocol: PREREGISTRATION.md.

## Files
- `PREREGISTRATION.md`: hypotheses, coding rules, tests, decision rules, limitations
- `event_window_test.py`: in-sample test (H1, H2, robustness) and out-of-sample test (`--oos`)
- `fetch_brent.py`: daily Brent (BZ=F) closes to `data/brent.csv` (stdlib; not run in the build sandbox, so test it on Termux first)
- `data/fomc_calendar_2026.csv`: Federal Reserve Board 2026 decision dates
- `data/incidents_seed.csv`: 27 sourced rows (25 included). INCOMPLETE. For harness testing only.
- `data/infrastructure_seed.csv`: infrastructure strikes, descriptive only
- `MANIFEST.sha256`: hashes for the freeze

## Run
    python fetch_brent.py --start 2026-01-01
    python event_window_test.py --incidents data/incidents_full.csv
    python event_window_test.py --incidents data/incidents_full.csv --oos

Each run writes `runs/run-YYYYMMDD-HHMMSS-mmm.log` and a matching `.json`.

## Before the test counts
`incidents_full.csv` must be compiled from the UKMTO WARNING series (001-26 onward) using the Section 3.1 rules, with the same columns as the seed file. JMIC reported 94 incidents of all types between March 1 and August 20, so the full attack series will run to roughly 100 or more rows.
