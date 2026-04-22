from __future__ import annotations

import argparse
import csv
from pathlib import Path


WORKDIR = Path(__file__).resolve().parent
SOURCE_CSV = WORKDIR / "source" / "content_hubs.normalized.csv"
RESEARCH_DIR = WORKDIR / "research"
HUB_BRIEFS_DIR = RESEARCH_DIR / "hub_briefs"
HUB_COMPETITOR_SHEETS_DIR = RESEARCH_DIR / "hub_competitor_sheets"
HUB_RESEARCH_QUEUE_CSV = RESEARCH_DIR / "hub_research_queue.csv"


def load_rows() -> list[dict[str, str]]:
    if not SOURCE_CSV.exists():
        raise SystemExit(
            f"Expected normalized hubs at {SOURCE_CSV}. "
            "Run build_content_opportunity_workspace.py first."
        )
    with SOURCE_CSV.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def resolve_competitor_sheet_path(row: dict[str, str]) -> str:
    existing = (row.get("hub_competitor_research_file") or "").strip()
    if existing:
        return existing
    hub_index = int(row.get("hub_index", "0"))
    hub_slug = row.get("hub_slug", "untitled") or "untitled"
    return f"research/hub_competitor_sheets/{hub_index:03d}-{hub_slug}.md"


def competitor_sheet_content(row: dict[str, str]) -> str:
    return f"""# Hub Competitor Research Sheet: {row.get('hub_name', '')}

## Hub Snapshot

- Hub index: {row.get('hub_index', '')}
- Hub model: {row.get('hub_model') or '(unknown)'}
- Representative keyword: {row.get('representative_keyword') or '(add representative keyword)'}
- Top keywords: {row.get('top_keywords') or '(add top keywords)'}
- SERP intent: {row.get('serp_intent') or '(unknown)'}
- Dominant ranking format: {row.get('dominant_ranking_format') or '(unknown)'}
- Brief file: `{row.get('hub_brief_file', '')}`

## SERP Snapshot

- Search engine / market:
- Query used:
- Search date:
- Dominant intent:
- Dominant page type:
- Notable SERP features:
- Conversion signals present on page 1:

## Named Competitors From Source CSV

- Competitor set: {row.get('top_competitors') or '(add competitors)'}

## Competitor 1

- URL:
- Brand / page:
- Format:
- Audience:
- Angle:
- Strengths:
- Gaps:
- Key sections:
- Conversion elements:
- Trust signals:

## Competitor 2

- URL:
- Brand / page:
- Format:
- Audience:
- Angle:
- Strengths:
- Gaps:
- Key sections:
- Conversion elements:
- Trust signals:

## Competitor 3

- URL:
- Brand / page:
- Format:
- Audience:
- Angle:
- Strengths:
- Gaps:
- Key sections:
- Conversion elements:
- Trust signals:

## Cross-Competitor Patterns

- Repeated sections:
- Repeated weak spots:
- Important subtopics everyone covers:
- Important subtopics competitors under-serve:
- Common UX / readability issues:
- Common conversion gaps:

## Skyscraper Plan

- Best angle for our hub:
- Best structure for our hub:
- Best proof / media / CTA additions:
- Supporting articles we should create from this hub:
- Internal links or cluster pathways to emphasize:
- What to avoid copying:

## Handoff to Brief

- Top competitor URLs:
- One-sentence positioning:
- Recommended H1:
- Recommended H2s:
- Drafting notes:
""".strip() + "\n"


def build_sheets(rows: list[dict[str, str]], force: bool) -> tuple[int, int]:
    HUB_COMPETITOR_SHEETS_DIR.mkdir(parents=True, exist_ok=True)
    created = 0
    skipped = 0
    for row in rows:
        rel_path = resolve_competitor_sheet_path(row)
        target = WORKDIR / rel_path
        if target.exists() and not force:
            skipped += 1
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(competitor_sheet_content(row), encoding="utf-8")
        created += 1
    return created, skipped


def sync_briefs(rows: list[dict[str, str]]) -> int:
    updated = 0
    for row in rows:
        brief_rel = (row.get("hub_brief_file") or "").strip()
        if not brief_rel:
            continue
        brief_path = WORKDIR / brief_rel
        if not brief_path.exists():
            continue

        expected_line = f"- Competitor research sheet: `{resolve_competitor_sheet_path(row)}`"
        content = brief_path.read_text(encoding="utf-8")
        if expected_line in content:
            continue
        marker = "## Competitor Research\n\n"
        if marker not in content:
            continue
        content = content.replace(marker, marker + expected_line + "\n", 1)
        brief_path.write_text(content, encoding="utf-8")
        updated += 1
    return updated


def build_queue(rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "hub_index",
        "hub_name",
        "hub_slug",
        "hub_model",
        "representative_keyword",
        "rep_volume",
        "keyword_count",
        "total_cluster_volume",
        "serp_intent",
        "dominant_ranking_format",
        "top_competitors",
        "hub_competitor_research_file",
        "hub_brief_file",
        "hub_outline_file",
        "research_status",
        "notes",
    ]
    with HUB_RESEARCH_QUEUE_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "hub_index": row.get("hub_index", ""),
                    "hub_name": row.get("hub_name", ""),
                    "hub_slug": row.get("hub_slug", ""),
                    "hub_model": row.get("hub_model", ""),
                    "representative_keyword": row.get("representative_keyword", ""),
                    "rep_volume": row.get("rep_volume", ""),
                    "keyword_count": row.get("keyword_count", ""),
                    "total_cluster_volume": row.get("total_cluster_volume", ""),
                    "serp_intent": row.get("serp_intent", ""),
                    "dominant_ranking_format": row.get("dominant_ranking_format", ""),
                    "top_competitors": row.get("top_competitors", ""),
                    "hub_competitor_research_file": resolve_competitor_sheet_path(row),
                    "hub_brief_file": row.get("hub_brief_file", ""),
                    "hub_outline_file": row.get("hub_outline_file", ""),
                    "research_status": row.get("research_status", "not_started") or "not_started",
                    "notes": "",
                }
            )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Overwrite existing hub competitor research sheets.")
    args = parser.parse_args()

    rows = load_rows()
    created, skipped = build_sheets(rows, force=args.force)
    build_queue(rows)
    updated_briefs = sync_briefs(rows)
    print(f"Wrote hub research queue to {HUB_RESEARCH_QUEUE_CSV}")
    print(f"Hub competitor research sheets created: {created}")
    print(f"Hub competitor research sheets skipped: {skipped}")
    print(f"Hub briefs updated with competitor sheet link: {updated_briefs}")


if __name__ == "__main__":
    main()
