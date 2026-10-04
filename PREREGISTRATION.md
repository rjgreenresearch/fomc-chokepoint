# Pre-Registration: Do Chokepoint Attacks Cluster Before FOMC Decisions?

Robert J. Green, Independent Economics and National Security Researcher
ORCID 0009-0002-9097-1021 | robert@rjgreenresearch.org
Protocol version 1.0, drafted October 4, 2026. Frozen on the date recorded in MANIFEST.sha256.

## 1. The claim under test

On September 16, 2026, hours before the Federal Reserve raised the federal funds target range to 3.75 to 4.00 percent, Iranian Parliament Speaker Mohammad Bagher Ghalibaf posted a "Straits Taylor Rule" that added Strait of Hormuz (SOH) and Bab el-Mandeb (BEM) risk terms to the Taylor rule. A widely shared commentary on the post argued that attacks on shipping and energy infrastructure intensify before FOMC meetings, citing the September and July meetings, and predicted the same pattern before the October 28 decision.

That is a testable timing claim. This protocol tests it once, with rules fixed in advance.

## 2. Hypotheses

**H1 (attack timing).** The daily rate of confirmed attacks on merchant shipping in the Middle East maritime region is higher in the eight days ending on an FOMC decision day than on other days.

**H2 (price timing).** The Brent log return over the same pre-decision windows is higher than over equally long windows placed elsewhere in the sample.

**OOS (out-of-sample prediction).** The attack count in the window October 21 to October 28, 2026 meets or exceeds a threshold set in Section 5.3.

The null in each case is no association with FOMC timing. All tests are one-sided in the direction the claim predicts.

## 3. Data and coding rules

**3.1 Attack series.** The authoritative source is the UK Maritime Trade Operations (UKMTO) numbered WARNING series for 2026 (reference format NNN-26), cross-checked against Joint Maritime Information Center (JMIC) advisory notes. UKMTO and JMIC compile incidents for mariners, without reference to monetary policy, which makes them independent of this hypothesis.

An incident counts if all of the following hold:

1. UKMTO classifies it as an ATTACK (not a hijack, boarding, suspicious approach, or advisory).
2. It occurs in the Arabian Gulf, Strait of Hormuz, Gulf of Oman, Southern Red Sea, Bab el-Mandeb, or Gulf of Aden.
3. It is attributed to Iran or an Iran-aligned group, or left unattributed. Incidents attributed to U.S. or coalition enforcement are excluded. Piracy is excluded.

Each struck vessel counts once. The date is the event date in UTC; where UKMTO gives only a report date, the report date is used and the row is flagged.

**3.2 Infrastructure strikes** (pipelines, refineries, LNG trains) are logged separately and reported descriptively. They are too few for a timing test.

**3.3 Prices.** Daily settlement of front-month Brent futures (Yahoo Finance symbol BZ=F). The pre-decision return runs from the last close on or before D minus 8 to the last close on or before D minus 1, so the decision itself is excluded.

**3.4 FOMC dates.** Decision days from the Federal Reserve Board's 2026 calendar: March 18, April 29, June 17, July 29, September 16 (in-sample) and October 28 (out-of-sample). January 28 precedes the war and is excluded.

## 4. Sample and windows

The in-sample period runs from March 1 to October 3, 2026 (217 days), starting the day after the February 28 strikes. The primary window covers D minus 7 through D, eight calendar days per meeting and 40 days in total.

## 5. Tests and decision rules

**5.1 H1 primary.** The statistic is the rate ratio: attacks per day inside the windows divided by attacks per day outside. Significance comes from a circular-shift permutation. All five decision dates move together by k days (modulo the sample length) for every k from 1 to 216. This keeps the number, length, and spacing of windows fixed while breaking their alignment with the FOMC calendar. The p-value is (1 + the number of shifts with a ratio at or above the observed one) divided by (1 + the number of valid shifts). H0 is rejected at alpha 0.05, one-sided.

An exact binomial test is also reported. It assumes attacks arrive independently, which clustering violates, so it is secondary.

**5.2 H2.** The statistic is the mean pre-decision Brent log return across the five meetings, tested with the same circular-shift permutation, alpha 0.05, one-sided.

**5.3 OOS.** The expected attack count for October 21 to 28 equals eight times a daily rate built as an equal-weight blend of two rates: the trailing 28-day rate (September 23 to October 20) and the full in-sample rate. The blend keeps one quiet month from making a single attack look anomalous. The threshold is the 95th percentile of a Poisson distribution with that expected count, with a floor of one attack. The claim is scored as consistent if the observed count meets or exceeds the threshold.

The threshold will be computed and published on October 21, before the window opens, using the code in this package unchanged.

## 6. Pre-specified robustness checks

These are reported in full whatever they show. None of them overrides the primary decision.

1. Attack-days in place of attack counts, which damps same-day clusters.
2. Windows of D minus 3 and D minus 14.
3. Excluding March. The opening weeks of the war had the highest attack rate, and the March 18 window falls inside them.
4. Iran and unattributed attacks only, excluding Houthi attacks.

## 7. Known limitations

- **Small n.** Five meetings give limited power. A null result means no detectable effect, not proof of no effect.
- **Regime shifts.** The attack rate changed with the April ceasefire, the U.S. escort operation from May, the July 20 Houthi blockade of Saudi-linked shipping, and the late-July Iran-Oman talks. The circular shift keeps the overall rate but not the timing of these regimes.
- **Coincident calendars.** CPI releases and the FOMC communications blackout both fall in the days before most decisions. A positive H1 result could reflect either rather than deliberate targeting of the Fed.
- **Futures rolls.** A front-month Brent window can straddle a contract roll. This is noted; it is not corrected.
- **Reporting lags.** UKMTO sometimes issues late warnings. Event dates are used where given.

## 8. Disclosure of prior exposure

Before freezing this protocol, the author saw a partial set of incidents while checking the commentary's claims, including a cluster of attacks from July 17 to 24 ahead of the July 29 decision. That seed log is included in this package and labeled incomplete. The windows, tests, thresholds, and coding rules above were set without computing any statistic on a complete incident series.

## 9. Freeze procedure

1. Compute SHA-256 hashes of this file, event_window_test.py, fetch_brent.py, and data/fomc_calendar_2026.csv, and record them in MANIFEST.sha256.
2. Commit the package to github.com/rjgreenresearch and publish the commit hash in the companion Substack article before October 21, 2026.
3. Compile the full UKMTO attack series into data/incidents_full.csv under Section 3.1. Run the in-sample test and publish the result as computed.
4. On October 21, publish the OOS threshold. After October 28, run the OOS test and publish the result.

Any deviation from this protocol will be disclosed alongside the result it affects.

## 10. What each outcome means

- **H1 rejected and OOS consistent:** the timing claim survives a test it could have failed. The question becomes mechanism, whether that is targeting of the Fed, the CPI calendar, or something else.
- **H1 not rejected and OOS not consistent:** the pre-FOMC pattern is anecdote. The chokepoint premium still feeds inflation, but there is no evidence it is timed to monetary policy.
- **Mixed results:** these are reported as mixed, with no post hoc re-specification.
