"""AutoDash: drop in a data file, get a dashboard. The AI only ever sees column names and types.

    python autodash.py data.csv                    # uses the AI set in .env (or rules if no key)
    python autodash.py data.xlsx --title "Q3 ops"
    python autodash.py data.csv --no-ai            # never contact any AI
    python autodash.py data.csv --share-categories # also share short category labels (e.g. Air/Ocean/Road)
    python autodash.py data.csv --show-ai-request  # print exactly what would be sent, then stop
"""
import argparse
import json
import os
import sys
import webbrowser
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description="Generate a dashboard from a data file.")
    ap.add_argument("file", help="CSV, Excel or JSON file")
    ap.add_argument("--out", help="output HTML path (default: <file>_dashboard.html)")
    ap.add_argument("--title", help="dashboard title")
    ap.add_argument("--no-ai", action="store_true", help="use built-in rules only; nothing leaves this computer")
    ap.add_argument("--share-categories", action="store_true",
                    help="also send labels of short category columns (<=12 values) for smarter filters")
    ap.add_argument("--show-ai-request", action="store_true", help="print what the AI would see and exit")
    ap.add_argument("--no-open", action="store_true", help="don't open the browser")
    a = ap.parse_args()
    if a.no_ai:
        os.environ["AUTODASH_NO_AI"] = "1"

    from autodash import compute, planner, profile, render
    from autodash.config import settings

    src = Path(a.file)
    print(f"Reading {src.name} ...")
    df, cols = profile.prepare(profile.load(src))
    schema = profile.schema_for_ai(df, cols, a.share_categories)
    print(f"  {len(df):,} rows, {len(cols)} columns: " + ", ".join(f"{c['name']} ({c['type']})" for c in cols))

    out = Path(a.out) if a.out else src.with_name(src.stem + "_dashboard.html")
    audit = out.with_suffix(".ai_request.json")
    if a.show_ai_request:
        print("\nThis is the ONLY data the AI would receive:\n" + json.dumps(schema, indent=2, ensure_ascii=False))
        return
    if settings.mock_mode:
        print("Planning with built-in rules (no AI used).")
    else:
        audit.write_text(json.dumps(schema, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Asking {settings.provider} to plan the dashboard. Sent ONLY the schema (saved for audit: {audit.name})")

    try:
        plan = planner.plan(schema, cols)
    except Exception as e:  # AI unavailable -> never fail, fall back to rules
        print(f"  AI planning failed ({e}); using built-in rules instead.")
        plan = planner.heuristic_plan(cols)
        plan["_planner"] = "rules (AI failed)"
    if a.title:
        plan["title"] = a.title

    res = compute.run(df, cols, plan)
    res["quality"] = [c for c in cols if c["missing_pct"] >= 5 and c["type"] != "date"][:2]
    ai_saw = ("No AI was used." if settings.mock_mode else
              f"The AI saw only {len(cols)} column names and types" + (" and short category labels." if a.share_categories else "."))
    out.write_text(render.page(res, src.name, len(df), len(cols), ai_saw), encoding="utf-8")
    for w in res["warnings"]:
        print("  note:", w)
    print(f"\nDashboard ready: {out}")
    if not a.no_open:
        webbrowser.open(out.resolve().as_uri())


if __name__ == "__main__":
    sys.exit(main())
