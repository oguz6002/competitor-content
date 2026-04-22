# Playground Content Hub Workflow

This workflow is built around the hub-planning dataset in:

- `C:\Users\oguzb\Downloads\Site Audit & Keyword Research - Content Hubs.csv`

That CSV is the source of truth for:

- hub research
- competitor analysis
- hub page planning
- supporting article generation

## Core Principle

Each row in the hub CSV should become:

1. one strategic content hub
2. one hub research brief
3. one hub competitor research sheet
4. one draft-queue entry for the hub page
5. several supporting article draft-queue entries derived from the supporting opportunities column

The goal is not just to write pages. The goal is to turn each hub into a cluster:

- a strong hub page
- useful supporting pages
- better structure than competing sites
- clearer intent match
- better internal linking opportunities

## Folder Structure

- `source/`
  Normalized hub data exported from the source CSV.
- `research/hub_briefs/`
  One strategic brief per content hub.
- `research/hub_competitor_sheets/`
  One competitor research sheet per content hub.
- `research/hub_outlines/`
  Working outline files for hub drafting.
- `generated/`
  Draft queues and draft exports.
- `review_queue/`
  Automated QA outputs after drafts exist.
- `approved/articles/`
  Final reviewed article markdown files.
- `prompts/`
  Reusable prompts for research, drafting, QA, and final review.

## Recommended Workflow

### 1. Build the workspace from the hub CSV

Run:

```powershell
python .\build_content_opportunity_workspace.py
```

This generates:

- `source\content_hubs.normalized.csv`
- `source\content_hubs.normalized.json`
- `research\hub_briefs\*.md`
- `research\hub_competitor_sheets\*.md`
- `research\hub_research_queue.csv`
- `generated\content_draft_queue.csv`

### 2. Research each hub

For each priority hub:

1. open the row in `research\hub_research_queue.csv`
2. complete the matching file in `research\hub_competitor_sheets\`
3. copy the best findings into the matching hub brief
4. define the hub structure and supporting pages before drafting

Use:

- `prompts\01a-competitor-research-sheet.md`
- `prompts\01-skyscraper-research.md`

### 3. Draft the hub page and supporting articles

Use `generated\content_draft_queue.csv` as the master queue.

Each row is either:

- `hub_page`
- `supporting_article`

For each row, draft using:

- the hub brief
- the completed hub competitor sheet
- the queue row context
- the source URLs from the hub CSV

Use:

- `prompts\02-skyscraper-draft.md`

### 4. Run automated QA

Once `generated\content_drafts.csv` exists, run:

```powershell
python .\qa_playground_articles.py
```

This creates:

- `review_queue\content_review_queue.csv`
- `review_queue\content_review_summary.md`

### 5. Final editorial QA

Use ChatGPT web for final review of individual finished articles.

Save approved replacements into:

```text
approved\articles\
```

### 6. Merge approved articles back

Run:

```powershell
python .\merge_approved_articles.py
```

## Best Practice Split

### Local workflow

Use local scripts for:

- normalization
- queue creation
- repeatable template generation
- automated QA
- merge-back

### ChatGPT web

Use the web model for:

- hub competitor analysis
- hub strategy refinement
- page-by-page drafting
- final editorial QA

## The Skyscraper Rule Set

Every hub and article should aim to:

- match search intent better than competitors
- cover the topic more completely
- improve the structure of the SERP norm
- create a clearer content journey across the cluster
- avoid copying competitor wording

## Suggested Lifecycle

1. `source`
2. `research`
3. `generated`
4. `review_queue`
5. `approved`
