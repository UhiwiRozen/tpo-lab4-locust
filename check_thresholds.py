"""Проверка критериев TC-01..TC-03 по load_report_stats.csv (падает с кодом 1 при нарушении)."""
import csv
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "load_report_stats.csv"
rows = {(r["Type"], r["Name"]): r for r in csv.DictReader(open(path, encoding="utf-8"))}

checks = [
    ("TC-01", "GET /api/users avg < 200 ms",
     float(rows[("GET", "/api/users")]["Average Response Time"]) < 200),
    ("TC-02", "POST /api/users avg < 300 ms",
     float(rows[("POST", "/api/users")]["Average Response Time"]) < 300),
]
agg = rows[("", "Aggregated")]
fail_rate = int(agg["Failure Count"]) / max(int(agg["Request Count"]), 1) * 100
checks.append(("TC-03", f"failure rate {fail_rate:.2f}% < 1%", fail_rate < 1))

ok = True
for tc, desc, passed in checks:
    print(f"{tc}: {desc} -> {'PASSED' if passed else 'FAILED'}")
    ok &= passed
sys.exit(0 if ok else 1)
