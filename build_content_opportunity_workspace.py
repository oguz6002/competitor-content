from __future__ import annotations

import csv
import json
import re
from pathlib import Path


WORKDIR = Path(__file__).resolve().parent
INPUT_CSV = Path.home() / "Downloads" / "Site Audit & Keyword Research - Content Hubs.csv"
SOURCE_DIR = WORKDIR / "source"
RESEARCH_DIR = WORKDIR / "research"
HUB_BRIEFS_DIR = RESEARCH_DIR / "hub_briefs"
HUB_COMPETITOR_SHEETS_DIR = RESEARCH_DIR / "hub_competitor_sheets"
HUB_OUTLINES_DIR = RESEARCH_DIR / "hub_outlines"
GENERATED_DIR = WORKDIR / "generated"
NORMALIZED_CSV = SOURCE_DIR / "content_hubs.normalized.csv"
NORMALIZED_JSON = SOURCE_DIR / "content_hubs.normalized.json"
HUB_RESEARCH_QUEUE_CSV = RESEARCH_DIR / "hub_research_queue.csv"
DRAFT_QUEUE_CSV = GENERATED_DIR / "content_draft_queue.csv"


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "untitled"


def clean_text(value: str) -> str:
    value = (value or "").replace("\u00a0", " ").replace("\r", "\n")
    value = re.sub(r"\n{3,}", "\n\n", value)
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r"\n[ \t]+", "\n", value)
    return value.strip()


def split_csv_list(raw: str) -> list[str]:
    raw = (raw or "").replace(";", ",")
    return [part.strip() for part in raw.split(",") if part.strip()]


def split_pipe_list(raw: str) -> list[str]:
    return [part.strip() for part in (raw or "").split("|") if part.strip()]


def split_source_urls(raw: str) -> list[str]:
    return [line.strip() for line in (raw or "").splitlines() if line.strip()]


def ensure_dirs() -> None:
    for path in [
        SOURCE_DIR,
        RESEARCH_DIR,
        HUB_BRIEFS_DIR,
        HUB_COMPETITOR_SHEETS_DIR,
        HUB_OUTLINES_DIR,
        GENERATED_DIR,
        WORKDIR / "review_queue",
        WORKDIR / "approved" / "articles",
        WORKDIR / "prompts",
    ]:
        path.mkdir(parents=True, exist_ok=True)


def supporting_deliverables(row: dict[str, str], hub_slug: str) -> list[str]:
    items = split_csv_list(row.get("Supporting Content Opportunities", ""))
    if not items:
        return []
    return items


def hub_row(index: int, row: dict[str, str]) -> dict[str, str]:
    hub = clean_text(row.get("Content Hub", ""))
    hub_slug = slugify(hub)
    representative_keyword = clean_text(row.get("Representative Keyword", ""))
    top_keywords = clean_text(row.get("Top 5 Keywords", ""))
    source_urls = split_source_urls(row.get("Source URLs", ""))
    source_urls_joined = "\n".join(source_urls)
    competitor_names = split_pipe_list(row.get("Top 3 Competitors", ""))
    supporting_items = supporting_deliverables(row, hub_slug)

    return {
        "hub_index": str(index),
        "hub_name": hub,
        "hub_slug": hub_slug,
        "hub_model": clean_text(row.get("Hub Model", "")),
        "keyword_count": clean_text(row.get("Keyword Count", "")),
        "total_cluster_volume": clean_text(row.get("Total Cluster Volume", "")),
        "representative_keyword": representative_keyword,
        "rep_volume": clean_text(row.get("Rep Volume", "")),
        "top_keywords": top_keywords,
        "primary_content_type": clean_text(row.get("Primary Content Type", "")),
        "supporting_content_opportunities": "; ".join(supporting_items),
        "serp_intent": clean_text(row.get("SERP Intent", "")),
        "dominant_ranking_format": clean_text(row.get("Dominant Ranking Format", "")),
        "top_competitors": " | ".join(competitor_names),
        "recommended_opportunity": clean_text(row.get("Recommended Opportunity", "")),
        "source_urls": source_urls_joined,
        "hub_brief_file": str((HUB_BRIEFS_DIR / f"{index:03d}-{hub_slug}.md").relative_to(WORKDIR)),
        "hub_competitor_research_file": str((HUB_COMPETITOR_SHEETS_DIR / f"{index:03d}-{hub_slug}.md").relative_to(WORKDIR)),
        "hub_outline_file": str((HUB_OUTLINES_DIR / f"{index:03d}-{hub_slug}.md").relative_to(WORKDIR)),
        "research_status": "not_started",
    }


def build_hub_rows() -> list[dict[str, str]]:
    with INPUT_CSV.open("r", encoding="utf-8-sig", newline="") as f:
        source_rows = list(csv.DictReader(f))

    return [hub_row(index, row) for index, row in enumerate(source_rows, start=1)]


def write_normalized_outputs(rows: list[dict[str, str]]) -> None:
    fieldnames = list(rows[0].keys()) if rows else []
    with NORMALIZED_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    NORMALIZED_JSON.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


def write_hub_briefs(rows: list[dict[str, str]]) -> None:
    for row in rows:
        path = WORKDIR / row["hub_brief_file"]
        supporting = row["supporting_content_opportunities"] or "(add supporting opportunities)"
        content = f"""# {row['hub_name']}

## Hub Snapshot

- Hub index: {row['hub_index']}
- Hub model: {row['hub_model'] or '(unknown)'}
- Primary content type: {row['primary_content_type'] or '(unknown)'}
- Representative keyword: {row['representative_keyword'] or '(add representative keyword)'}
- Rep volume: {row['rep_volume'] or '(unknown)'}
- Keyword count: {row['keyword_count'] or '(unknown)'}
- Total cluster volume: {row['total_cluster_volume'] or '(unknown)'}

## Search Opportunity

- SERP intent: {row['serp_intent'] or '(unknown)'}
- Dominant ranking format: {row['dominant_ranking_format'] or '(unknown)'}
- Recommended opportunity:
  {row['recommended_opportunity'] or '(add recommended opportunity)'}

## Keyword Cluster

- Top keywords: {row['top_keywords'] or '(add top keywords)'}
- Supporting content opportunities: {supporting}

## Competitor Research

- Competitor research sheet: `{row['hub_competitor_research_file']}`
- Named competitors: {row['top_competitors'] or '(add competitors)'}
- What the current SERP gets right:
- What the current SERP misses:
- What our hub should do better:

## Source Material

{row['source_urls'] or '(add source URLs)'}

## Hub Strategy

- Core conversion or education goal:
- Primary audience:
- Best page structure:
- Key sections to win:
- Internal linking targets:
- Download/tool/media opportunities:

## Deliverables

- Hub outline file: `{row['hub_outline_file']}`
- Planned hub H1:
- Planned hub H2s:
- Supporting article queue items to create from this hub:
- Notes to carry into drafting:
"""
        path.write_text(content.strip() + "\n", encoding="utf-8")


def write_hub_competitor_research_sheets(rows: list[dict[str, str]]) -> None:
    for row in rows:
        path = WORKDIR / row["hub_competitor_research_file"]
        content = f"""# Hub Competitor Research Sheet: {row['hub_name']}

## Hub Snapshot

- Hub index: {row['hub_index']}
- Hub model: {row['hub_model'] or '(unknown)'}
- Representative keyword: {row['representative_keyword'] or '(add representative keyword)'}
- Top keywords: {row['top_keywords'] or '(add top keywords)'}
- SERP intent: {row['serp_intent'] or '(unknown)'}
- Dominant ranking format: {row['dominant_ranking_format'] or '(unknown)'}
- Brief file: `{row['hub_brief_file']}`

## SERP Snapshot

- Search engine / market:
- Query used:
- Search date:
- Dominant intent:
- Dominant page type:
- Notable SERP features:
- Conversion signals present on page 1:

## Named Competitors From Source CSV

- Competitor set: {row['top_competitors'] or '(add competitors)'}

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
"""
        path.write_text(content.strip() + "\n", encoding="utf-8")


def write_hub_research_queue(rows: list[dict[str, str]]) -> None:
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
            writer.writerow({**{key: row.get(key, "") for key in fieldnames[:-1]}, "notes": ""})


def deliverable_title(hub_name: str, supporting_topic: str) -> str:
    return f"{hub_name}: {supporting_topic}"


def build_draft_queue_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    deliverables: list[dict[str, str]] = []
    deliverable_index = 1
    for row in rows:
        hub_name = row["hub_name"]
        hub_slug = row["hub_slug"]

        deliverables.append(
            {
                "deliverable_index": str(deliverable_index),
                "hub_index": row["hub_index"],
                "hub_name": hub_name,
                "hub_slug": hub_slug,
                "deliverable_type": "hub_page",
                "title": hub_name,
                "slug": hub_slug,
                "target_keyword": row["representative_keyword"],
                "supporting_topic": "",
                "cluster_keywords": row["top_keywords"],
                "serp_intent": row["serp_intent"],
                "primary_content_type": row["primary_content_type"],
                "brief_file": row["hub_brief_file"],
                "competitor_research_file": row["hub_competitor_research_file"],
                "outline_file": row["hub_outline_file"],
                "source_urls": row["source_urls"],
                "draft_status": "not_started",
                "web_review_status": "not_started",
                "seo_title": "",
                "meta_description": "",
                "article_markdown": "",
                "faq": "",
                "notes": "",
            }
        )
        deliverable_index += 1

        for supporting_topic in split_csv_list(row["supporting_content_opportunities"]):
            supporting_slug = slugify(f"{hub_slug}-{supporting_topic}")
            deliverables.append(
                {
                    "deliverable_index": str(deliverable_index),
                    "hub_index": row["hub_index"],
                    "hub_name": hub_name,
                    "hub_slug": hub_slug,
                    "deliverable_type": "supporting_article",
                    "title": deliverable_title(hub_name, supporting_topic),
                    "slug": supporting_slug,
                    "target_keyword": supporting_topic.lower(),
                    "supporting_topic": supporting_topic,
                    "cluster_keywords": row["top_keywords"],
                    "serp_intent": row["serp_intent"],
                    "primary_content_type": "supporting article",
                    "brief_file": row["hub_brief_file"],
                    "competitor_research_file": row["hub_competitor_research_file"],
                    "outline_file": row["hub_outline_file"],
                    "source_urls": row["source_urls"],
                    "draft_status": "not_started",
                    "web_review_status": "not_started",
                    "seo_title": "",
                    "meta_description": "",
                    "article_markdown": "",
                    "faq": "",
                    "notes": "",
                }
            )
            deliverable_index += 1
    return deliverables


def write_draft_queue(rows: list[dict[str, str]]) -> int:
    deliverables = build_draft_queue_rows(rows)
    fieldnames = list(deliverables[0].keys()) if deliverables else []
    with DRAFT_QUEUE_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(deliverables)
    return len(deliverables)


def main() -> None:
    ensure_dirs()
    rows = build_hub_rows()
    if not rows:
        raise SystemExit(f"No hub rows found in {INPUT_CSV}.")
    write_normalized_outputs(rows)
    write_hub_briefs(rows)
    write_hub_competitor_research_sheets(rows)
    write_hub_research_queue(rows)
    deliverable_count = write_draft_queue(rows)
    print(f"Wrote normalized hubs to {NORMALIZED_CSV}")
    print(f"Wrote normalized hub JSON to {NORMALIZED_JSON}")
    print(f"Wrote {len(rows)} hub briefs to {HUB_BRIEFS_DIR}")
    print(f"Wrote {len(rows)} hub competitor research sheets to {HUB_COMPETITOR_SHEETS_DIR}")
    print(f"Wrote hub research queue to {HUB_RESEARCH_QUEUE_CSV}")
    print(f"Wrote draft queue with {deliverable_count} deliverables to {DRAFT_QUEUE_CSV}")


if __name__ == "__main__":
    main()
