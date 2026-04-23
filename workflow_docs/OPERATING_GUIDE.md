# Competitor Content Operations Guide

This document is the shared operating guide for the competitor-content repo.

Use it as the front door.
Use the repo workflow and prompt files as the detailed instructions.

## Quick Links

- [Workflow overview](./WORKFLOW.md)
- [Competitor research sheet prompt](../prompts/01a-competitor-research-sheet.md)
- [Hub strategy prompt](../prompts/01-skyscraper-research.md)
- [Skyscraper draft prompt](../prompts/02-skyscraper-draft.md)
- [Article QA prompt](../prompts/03-article-qa.md)
- [Final publish QA prompt](../prompts/04-final-publish-qa.md)
- [Web article draft prompt](../prompts/05-web-article-draft-prompt.md)

## What This Guide Is For

Use this guide to answer 3 questions quickly:

1. What stage am I in?
2. Which prompt should I use?
3. What file should I update next?

## Shared Production Model

This repo follows this working model:

`source -> research -> generation -> QA -> approved full-article rewrites -> merge`

This means the team should treat work as a staged pipeline rather than drafting directly from scratch without process context.

## Step Map

## 1. Source

Related links:

- [Workflow: Build the workspace from the hub CSV](./WORKFLOW.md#1-build-the-workspace-from-the-hub-csv)

Goal:

- normalize the planning dataset into reusable research and drafting inputs

What happens here:

- import the planning CSV
- generate normalized source files
- generate research and draft queues

Main output:

- normalized source files
- research queue
- draft queue

## 2. Research

Related links:

- [Workflow: Research each hub](./WORKFLOW.md#2-research-each-hub)
- [Competitor research sheet prompt](../prompts/01a-competitor-research-sheet.md)
- [Hub strategy prompt](../prompts/01-skyscraper-research.md)

Goal:

- turn hub opportunities into practical research briefs and competitor analysis

What happens here:

- complete competitor research sheets
- summarize SERP intent and competitor structure
- identify gaps and differentiators
- define the hub and supporting-page strategy

Main output:

- completed competitor sheets
- refined hub briefs

## 3. Generation

Related links:

- [Workflow: Draft the hub page and supporting articles](./WORKFLOW.md#3-draft-the-hub-page-and-supporting-articles)
- [Skyscraper draft prompt](../prompts/02-skyscraper-draft.md)
- [Web article draft prompt](../prompts/05-web-article-draft-prompt.md)

Goal:

- create original, useful drafts that outperform competitors in structure and usefulness

What happens here:

- draft hub pages and supporting articles
- follow the queue row context
- use competitor analysis for coverage and structure, not wording

Main output:

- generated article drafts

## 4. Editorial Checks

Related links:

- [Workflow: Run automated QA](./WORKFLOW.md#4-run-automated-qa)
- [Article QA prompt](../prompts/03-article-qa.md)

Goal:

- improve readability, originality, and competitiveness before final publishing review

What happens here:

- run automated QA
- review flagged drafts
- tighten headings, structure, and readability
- fix weak sections, weak SERP intent match, and thin FAQ content where appropriate

Main output:

- corrected draft ready for final publish review

## 5. Before Publishing Review

Related links:

- [Workflow: Final editorial QA](./WORKFLOW.md#5-final-editorial-qa)
- [Final publish QA prompt](../prompts/04-final-publish-qa.md)

Goal:

- finalize one article at a time for publication

What happens here:

- run final wording and structure review
- remove repetitive phrasing
- improve title and heading quality
- keep the article aligned to source support and competitive intent
- save the final approved article as a full Markdown replacement

Main output:

- final approved article in `approved/articles/`

## 6. Merge

Related links:

- [Workflow: Merge approved articles back](./WORKFLOW.md#6-merge-approved-articles-back)

Goal:

- merge approved replacements back into the master outputs

Main output:

- merged CSV
- merged Markdown

## Team Rules

- Use the repo workflow and prompt files as the source of process truth.
- Do not treat old copied chat prompts as canonical.
- Do not copy competitor wording.
- Do not invent unsupported claims.
- Approved article files must always be full replacement articles, not patch notes.

## Recommended Team Handoff Method

Use the same handoff stages for each article or hub:

- `Source ready`
- `Research complete`
- `Generation complete`
- `QA complete`
- `Ready for publishing review`
- `Approved`
- `Merged`

## Suggested Usage Pattern

1. Start with this guide.
2. Open the workflow overview.
3. Use the prompt that matches the current stage.
4. Save approved articles as full replacements.
5. Merge approved work back into the master outputs.
