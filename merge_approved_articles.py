from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


WORKDIR = Path(__file__).resolve().parent
INPUT_CSV = WORKDIR / "generated" / "content_drafts.csv"
APPROVED_DIR = WORKDIR / "approved" / "articles"
OUTPUT_DIR = WORKDIR / "generated"
OUTPUT_CSV = OUTPUT_DIR / "content_drafts.approved.csv"
OUTPUT_MD = OUTPUT_DIR / "content_drafts.approved.md"


def load_rows() -> list[dict[str, str]]:
    with INPUT_CSV.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def approved_map(rows: list[dict[str, str]]) -> dict[int, Path]:
    slug_to_index = {row["slug"]: index for index, row in enumerate(rows, start=1)}
    row_id_to_index = {}
    for index, row in enumerate(rows, start=1):
        row_id = row.get("deliverable_index") or row.get("article_index")
        if row_id:
            row_id_to_index[str(row_id)] = index
    result: dict[int, Path] = {}
    for path in sorted(APPROVED_DIR.glob("*.md")):
        stem = path.stem
        match = re.match(r"^(?P<index>\d{1,3})[-_](?P<slug>.+)$", stem)
        if match:
            matched_index = match.group("index").lstrip("0") or "0"
            result[row_id_to_index.get(matched_index, int(match.group("index")))] = path
        elif stem in slug_to_index:
            result[slug_to_index[stem]] = path
    return result


def rebuild_md(rows: list[dict[str, str]]) -> str:
    parts = ["# Content Drafts", ""]
    for index, row in enumerate(rows, start=1):
        parts.extend(["---", f"## {index}. {row['title']}", "", (row.get("article_markdown", "") or "").strip(), ""])
    return "\n".join(parts).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--in-place", action="store_true")
    args = parser.parse_args()

    if not INPUT_CSV.exists():
        raise SystemExit(f"Expected {INPUT_CSV} to exist before merging approved articles.")

    rows = load_rows()
    mapping = approved_map(rows)
    updated = 0
    for index, row in enumerate(rows, start=1):
        approved = mapping.get(index)
        if not approved:
            continue
        row["article_markdown"] = approved.read_text(encoding="utf-8").strip() + "\n"
        row["web_review_status"] = "approved"
        updated += 1

    csv_target = INPUT_CSV if args.in_place else OUTPUT_CSV
    md_target = WORKDIR / "generated" / ("content_drafts.md" if args.in_place else "content_drafts.approved.md")

    csv_target.parent.mkdir(parents=True, exist_ok=True)
    with csv_target.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else [])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    md_target.write_text(rebuild_md(rows), encoding="utf-8")

    print(f"Merged {updated} approved article(s).")
    print(f"Wrote CSV to {csv_target}")
    print(f"Wrote Markdown to {md_target}")


if __name__ == "__main__":
    main()
