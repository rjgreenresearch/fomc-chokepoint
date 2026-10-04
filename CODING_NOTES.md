# Coding Notes: incidents_full.csv (built October 4, 2026)

Source: user-supplied archive of UKMTO 2026 WARNING PDFs (149 files) and ADVISORY PDFs (22 files). Text was extracted with pdftotext; one corrupt file (WARNING 113-26) was read with pypdf.

## Counts
- Unique WARNING numbers found: 002 through 150, minus advisories and gaps.
- Final category after updates: 88 ATTACK. Updates that reclassified a warning were applied (092-26 from suspicious activity to attack; 023-26 and 026-26 from attack to suspicious activity; 077-26 and 090-26 to boarding and hijack).
- Rows in incidents_full.csv: 90 (two warnings report two struck vessels: 021-26 and 133-26).
- Included under protocol Section 3.1: 83. In-sample (March 1 to October 3): 82.

## Exclusions (7 rows)
- 002-26: before the war (February 17).
- 036-26: Arabian Sea, 112NM southeast of Ras Al Hadd. Outside the protocol's listed regions.
- 119-26: central Red Sea, 63NM west of Yanbu. Outside the protocol's listed regions (the protocol names the Southern Red Sea).
- 065-26, 069-26, 070-26, 071-26: armed skiffs firing on and trying to board vessels in the Gulf of Aden. Coded as piracy.

## Date rules
- Event date is the UKMTO report date unless the body gives a different event date.
- 139-26: issued September 18 as a time-late report; the body dates the attack to September 16. Coded September 16.
- Other time-late reports with no event date in the body keep the report date and carry date_confidence = medium.

## Actor rules
- UKMTO does not attribute most attacks. Red Sea and Gulf of Aden attacks are labeled houthi for the Iran-only robustness check, based on the July 20 Houthi blockade context. Persian Gulf, Strait of Hormuz, and Gulf of Oman attacks are labeled iran_or_unattributed.

## Gaps
Warning numbers missing from the archive: 027, 033, 040, 042, 058, 075, 099, 100. If any were attacks, they are absent from the series. A worst-case bound (all eight treated as attacks, each placed inside a pre-FOMC window wherever its neighbors' dates allow) is reported in RESULTS_2026-10-04.md.
