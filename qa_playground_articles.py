from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


WORKDIR = Path(__file__).resolve().parent
INPUT_CSV = WORKDIR / "generated" / "content_drafts.csv"
OUTPUT_DIR = WORKDIR / "review_queue"
OUTPUT_CSV = OUTPUT_DIR / "content_review_queue.csv"
OUTPUT_MD = OUTPUT_DIR / "content_review_summary.md"


@dataclass
class Issue:
    article_index: str
    title: str
    slug: str
    issue_type: str
    severity: str
    location: str
    details: str
    needs_web_review: str = "yes"


def extract_block(markdown: str, heading: str) -> str:
    pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*$\n(.*?)(?=^##\s+|\Z)", flags=re.M | re.S)
    match = pattern.search(markdown)
    return match.group(1).strip() if match else ""


def extract_faq_count(markdown: str) -> int:
    block = extract_block(markdown, "FAQ")
    return len(re.findall(r"^###\s+", block, flags=re.M)) if block else 0


def scan_article(row: dict[str, str]) -> list[Issue]:
    issues: list[Issue] = []
    markdown = row.get("article_markdown", "") or ""
    row_id = row.get("deliverable_index") or row.get("article_index", "")

    if not markdown.strip():
        return [
            Issue(
                article_index=row_id,
                title=row.get("title", ""),
                slug=row.get("slug", ""),
                issue_type="missing_article_markdown",
                severity="high",
                location="article",
                details="No article_markdown content found in generated/content_drafts.csv",
            )
        ]

    checks = [
        (r"\btrainee(s)?\b", "audience_term_trainee", "high"),
        (r"\bUse this when\b", "clinical_claim_phrase", "high"),
        (r"\bUse this for\b", "clinical_claim_phrase", "high"),
        (r"\bUse this as\b", "clinical_claim_phrase", "high"),
        (r"\b3D\b", "ui_artifact_3d", "medium"),
        (r"\bTOC\b", "ui_artifact_toc", "medium"),
    ]
    for pattern, issue_type, severity in checks:
        if re.search(pattern, markdown, flags=re.I):
            issues.append(
                Issue(
                    article_index=row_id,
                    title=row.get("title", ""),
                    slug=row.get("slug", ""),
                    issue_type=issue_type,
                    severity=severity,
                    location="article",
                    details=f"Matched pattern: {pattern}",
                )
            )

    summary_block = extract_block(markdown, "Clinician Summary")
    if not summary_block:
        issues.append(Issue(row_id, row.get("title", ""), row.get("slug", ""), "missing_clinician_summary", "high", "Clinician Summary", "Missing summary section."))
    faq_count = extract_faq_count(markdown)
    if faq_count < 3:
        issues.append(Issue(row_id, row.get("title", ""), row.get("slug", ""), "faq_count_low", "medium", "FAQ", f"Found only {faq_count} FAQ items."))

    long_paragraph_match = re.search(r"(?:(?:^|\n)(?!#|- ).{700,})(?:\n|$)", markdown, flags=re.M)
    if long_paragraph_match:
        issues.append(Issue(row_id, row.get("title", ""), row.get("slug", ""), "paragraph_too_long", "medium", "article", "Detected a very long paragraph block."))

    if not issues:
        issues.append(Issue(row_id, row.get("title", ""), row.get("slug", ""), "no_issues_found", "info", "article", "No automated QA issues detected.", "optional"))
    return issues


def main() -> None:
    if not INPUT_CSV.exists():
        raise SystemExit(f"Expected draft file at {INPUT_CSV}. Create generated/content_drafts.csv first.")

    with INPUT_CSV.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    issues: list[Issue] = []
    for row in rows:
        issues.extend(scan_article(row))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["article_index", "title", "slug", "issue_type", "severity", "location", "details", "needs_web_review"],
        )
        writer.writeheader()
        for issue in issues:
            writer.writerow(issue.__dict__)

    severity_counts = Counter(issue.severity for issue in issues if issue.issue_type != "no_issues_found")
    article_counts: dict[str, int] = defaultdict(int)
    for issue in issues:
        if issue.issue_type != "no_issues_found":
            article_counts[f"{issue.article_index}. {issue.title}"] += 1

    lines = [
        "# Content Review Summary",
        "",
        f"- Queue file: `{OUTPUT_CSV.name}`",
        f"- Total review rows: {len(issues)}",
        f"- Articles with flagged issues: {len(article_counts)}",
        "",
        "## Severity Counts",
        "",
    ]
    if severity_counts:
        for severity, count in sorted(severity_counts.items()):
            lines.append(f"- {severity}: {count}")
    else:
        lines.append("- No flagged issues.")
    OUTPUT_MD.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    print(f"Wrote review queue to {OUTPUT_CSV}")
    print(f"Wrote review summary to {OUTPUT_MD}")


if __name__ == "__main__":
    main()
