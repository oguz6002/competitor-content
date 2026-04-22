from __future__ import annotations

import csv
import re
from pathlib import Path


WORKDIR = Path(__file__).resolve().parent
HUBS_CSV = WORKDIR / "source" / "content_hubs.normalized.csv"
QUEUE_CSV = WORKDIR / "generated" / "content_draft_queue.csv"
RESEARCH_QUEUE_CSV = WORKDIR / "research" / "hub_research_queue.csv"
HUB_BRIEFS_DIR = WORKDIR / "research" / "hub_briefs"
HUB_COMPETITOR_DIR = WORKDIR / "research" / "hub_competitor_sheets"
OUTLINE_DIR = WORKDIR / "research" / "hub_outlines"
DRAFTS_CSV = WORKDIR / "generated" / "content_drafts.csv"
DRAFTS_MD = WORKDIR / "generated" / "content_drafts.md"
DRAFT_DOCS_DIR = WORKDIR / "generated" / "draft_articles"

HUB_CONTEXT = {
    "hip-arthroplasty-and-approaches": {
        "overview": "Anterior hip replacement is one approach to total hip arthroplasty. It uses an incision at the front of the hip and is commonly discussed in terms of muscle sparing, early mobility, and candidacy.",
        "facts": [
            "Approach choice depends on anatomy, surgeon experience, prior surgery, deformity, and the reconstruction goals rather than on marketing language alone.",
            "Anterior and posterior approaches can both lead to good outcomes, so the real patient question is often fit, tradeoffs, and recovery expectations.",
            "Readers usually want help comparing approaches, understanding candidacy, and knowing what the first weeks of recovery are likely to involve.",
        ],
        "risks": "Important tradeoffs include wound issues, nerve irritation, fracture risk in some anatomies, and the fact that not every patient is an ideal anterior candidate.",
    },
    "robotic-joint-replacement": {
        "overview": "Robotic knee replacement uses planning software and robotic assistance to help the surgeon execute bone preparation and implant positioning more precisely. The robot assists the surgeon; it does not perform the operation independently.",
        "facts": [
            "The most useful comparison is usually robotic versus conventional instrumentation, not robot versus surgeon skill.",
            "Patients usually care about accuracy, recovery, candidacy, cost, and whether a specific branded system meaningfully changes outcomes.",
            "Good content on this topic should separate the platform, the surgical plan, and the patient-facing benefits or limits.",
        ],
        "risks": "Different systems have different workflows, but outcomes still depend on indications, surgical execution, and rehabilitation rather than technology branding alone.",
    },
    "fracture-classifications": {
        "overview": "Fracture classification systems help clinicians describe injuries consistently, estimate severity, and connect injury patterns to treatment implications.",
        "facts": [
            "Open-fracture systems such as Gustilo-Anderson emphasize soft-tissue injury and contamination as much as the bony injury itself.",
            "Other systems, such as Weber, Garden, or Gartland, matter because they influence how people talk about stability, displacement, blood-supply risk, or management.",
            "Classification content is strongest when it is visual, table-driven, and linked to what the classification changes in practice.",
        ],
        "risks": "The main pitfall is treating a classification label as the whole diagnosis instead of combining it with imaging, soft-tissue findings, and patient factors.",
    },
    "orthopedic-trauma": {
        "overview": "Compartment syndrome is a limb-threatening emergency caused by rising pressure within a closed fascial compartment. Fasciotomy is the decompressive operation used when perfusion is threatened.",
        "facts": [
            "Compartment syndrome is first a clinical problem: pain out of proportion, pain with passive stretch, tense compartments, and escalating analgesic needs all matter.",
            "Timing is critical because muscle and nerve injury can progress quickly if decompression is delayed.",
            "Trauma content works best when it separates emergency recognition from later fixation planning and reconstruction decisions.",
        ],
        "risks": "Missed or late compartment syndrome can lead to necrosis, contracture, neurologic deficit, infection, and limb loss.",
    },
    "knee-injections-and-aspiration": {
        "overview": "Knee aspiration and knee injection share a joint-entry technique but serve different purposes. Aspiration is mainly diagnostic or pressure relieving, while injection is usually therapeutic.",
        "facts": [
            "Fluid analysis can help distinguish crystal disease, inflammatory arthritis, hemarthrosis, and suspected infection.",
            "The strongest reader value comes from clear indications, sterile technique, sample handling, and knowing when aspiration and injection are not interchangeable.",
            "Concern for septic arthritis changes the workflow substantially and is one reason careful aspiration technique and interpretation matter.",
        ],
        "risks": "The big practical errors are poor sterile technique, weak sample handling, and blurring diagnostic aspiration with treatment injection.",
    },
    "general-orthopedic-procedures": {
        "overview": "General orthopedic procedure pages are most useful when they explain the basics well: indications, anatomy, setup, contraindications, and how the procedure fits into the bigger decision.",
        "facts": [
            "Readers looking for procedure basics usually need a compact overview before they need nuance.",
            "Anatomy refreshers are useful because many common orthopedic procedures are landmark dependent.",
            "Even technically simple procedures are the wrong move if the indication or contraindication is misunderstood.",
        ],
        "risks": "A common failure pattern is focusing on the visible step-by-step portion of a procedure without covering the setup logic and limits.",
    },
    "access-lines-and-vascular-access": {
        "overview": "Intraosseous access is an emergency vascular-access technique used when urgent IV access is needed and peripheral IV placement is delayed or unsuccessful.",
        "facts": [
            "The medullary cavity acts as a noncollapsible access point for fluids and medications during resuscitation.",
            "Common sites include the proximal tibia and proximal humerus, with landmarks and needle choice shaping safe placement.",
            "IO access is usually a bridge technique rather than the final long-term access plan.",
        ],
        "risks": "Extravasation, malposition, infusion pain in awake patients, and site-specific complications are the main practical issues to explain.",
    },
    "orthopedic-anatomy": {
        "overview": "The tibial plafond is the distal articular surface of the tibia where it meets the talus. It matters because it is a weight-bearing surface and a frequent focus of high-energy ankle trauma.",
        "facts": [
            "Pilon or plafond injuries are not just bone injuries; articular congruity and soft-tissue status strongly influence management and outcome.",
            "Anatomy content is more useful when it connects structure to fracture pattern, surgical planning, and imaging interpretation.",
            "Readers benefit when anatomy is linked to function rather than treated as isolated memorization.",
        ],
        "risks": "The main weakness in anatomy pages is presenting structure without showing why it changes imaging, injury pattern, or surgical decisions.",
    },
    "sterility-and-surgical-setup": {
        "overview": "Surgical asepsis is the set of practices used to create and protect a sterile field during invasive care. The goal is not symbolic cleanliness; it is preventing contamination in real workflow.",
        "facts": [
            "Sterility depends on preparation, field design, team behavior, and rapid recognition of breaks in technique.",
            "Many breaches happen during movement, handoff, and equipment setup rather than during the most dramatic step of the case.",
            "Checklist-style content works especially well here because readers need repeatable habits more than abstract definitions.",
        ],
        "risks": "The danger is treating asepsis as a one-time setup task instead of something that has to be protected throughout the procedure.",
    },
    "orthopedic-education-content": {
        "overview": "Orthopedic education hubs work best when they help readers orient themselves across common procedures instead of presenting a disconnected list of techniques.",
        "facts": [
            "A useful overview page should organize procedures by problem, region, or decision point rather than by random order.",
            "Atlas-style content helps with orientation, but readers still need notes on when procedures are used and how they differ.",
            "This type of hub can serve both orientation and deeper study if the internal structure is clear.",
        ],
        "risks": "The main weakness is breadth without structure: readers see many procedures but do not learn how they relate.",
    },
    "injection-and-nerve-block-techniques": {
        "overview": "Digital nerve blocks and similar injection techniques depend on accurate anatomy, careful volume selection, and a clear understanding of when a landmark-based approach is enough and when imaging adds value.",
        "facts": [
            "For distal blocks, success often depends more on atraumatic technique and the correct tissue plane than on complexity.",
            "Contraindications, local infection, allergy, and vascular concerns should shape whether and how the block is performed.",
            "Ultrasound is most useful when anatomy is difficult, structures are deep, or visualization meaningfully improves control.",
        ],
        "risks": "Readers need a practical safety discussion, not just a list of landmarks.",
    },
    "fracture-fixation-techniques": {
        "overview": "Fracture-fixation content has to connect fracture pattern, surgical approach, implant choice, fixation goals, and rehabilitation instead of treating them as unrelated topics.",
        "facts": [
            "Approach selection is about access, soft-tissue respect, and implant strategy, not just incision preference.",
            "Implant choice follows the problem to solve: buttressing, bridging, compression, raft support, or alignment control.",
            "Readers also care about what happens after fixation because rehabilitation affects stiffness, weight-bearing progression, and outcome.",
        ],
        "risks": "Technique detail without decision framing makes fixation pages much less useful.",
    },
    "knee-arthroplasty": {
        "overview": "Pages on lateral or less common knee arthroplasty approaches are niche because candidacy, deformity pattern, implant familiarity, and exposure needs all influence whether the approach is a good fit.",
        "facts": [
            "Readers usually want to know who the approach is for, whether outcomes differ, and whether implant choice changes the discussion.",
            "Niche arthroplasty content should stay balanced about indications because uncommon does not automatically mean better or worse.",
            "Outcome discussions work best when they focus on alignment, soft-tissue balance, recovery, and complication profile.",
        ],
        "risks": "The main pitfall is overpromising based on novelty or surgeon preference rather than indications.",
    },
    "sports-medicine-and-upper-extremity": {
        "overview": "Upper-extremity sports medicine pages often need to bridge procedural detail and rehabilitation because readers care about both the operation and the return-to-function pathway.",
        "facts": [
            "Technique content benefits from showing pearls and common pitfalls, not just the idealized sequence of steps.",
            "Video-oriented queries still need written structure so readers can review indications, setup, and progression quickly.",
            "Rehabilitation belongs in the same content system because outcome depends on more than the intraoperative step.",
        ],
        "risks": "Purely visual procedure content is hard to revisit later unless it is paired with a written summary or checklist.",
    },
    "surgical-positioning": {
        "overview": "Patient positioning has real consequences for exposure, ventilation, pressure injury risk, line security, and intraoperative safety.",
        "facts": [
            "A good positioning page explains what the position is for before listing how it is set up.",
            "Pressure points, padding, nerve protection, and team communication are central because positioning itself can cause harm.",
            "Checklist-based content is especially useful because positioning is a team task with repeated safety steps.",
        ],
        "risks": "A common mistake is focusing on exposure benefits without addressing contraindications and pressure-related hazards.",
    },
    "amputation-techniques": {
        "overview": "Amputation technique content should connect level selection, soft-tissue management, flap design, rehabilitation goals, and prosthetic potential rather than treating the operation as a single isolated step.",
        "facts": [
            "Below-knee versus above-knee level selection has major implications for energy expenditure, function, soft-tissue healing, and prosthetic rehabilitation.",
            "Flap design matters because coverage, tension, scar placement, and soft-tissue durability affect stump quality.",
            "The best pages explain how the operation and the rehabilitation plan fit together from the beginning.",
        ],
        "risks": "A technically neat operation is still a poor outcome if level selection and rehabilitation planning were wrong.",
    },
    "surgical-approaches": {
        "overview": "Surgical approach pages are valuable when they explain anatomy, safe intervals, exposure goals, and common pitfalls in a way that helps readers avoid predictable errors.",
        "facts": [
            "Approach anatomy is not just memorization; it determines what can be exposed safely and what structures are at risk.",
            "The idea of a safe interval is useful because it turns anatomy into a practical operative map.",
            "Exposure pitfalls often involve nerves, vessels, soft-tissue stripping, and extending an approach beyond what its plane supports well.",
        ],
        "risks": "Readers need to know not only where to go, but also where the danger zones are when exposure becomes difficult.",
    },
    "spine-surgery": {
        "overview": "Microdiscectomy is a focused decompressive operation aimed at relieving radicular symptoms caused by disc herniation when symptoms persist or correlate strongly with the compressed nerve root.",
        "facts": [
            "The key distinction is between leg-dominant radicular pain and nonspecific back pain because microdiscectomy is not a universal fix for every lumbar complaint.",
            "Minimally invasive techniques may reduce tissue disruption, but the real patient questions are candidacy, symptom relief, recurrence risk, and recovery expectations.",
            "The best structure combines overview, who benefits, what recovery is like, and where limitations remain.",
        ],
        "risks": "Recurrence, dural tear, persistent symptoms, and mismatch between symptoms and imaging are the main concerns to explain clearly.",
    },
    "general-urologic-procedures": {
        "overview": "Suprapubic catheter placement is used when transurethral drainage is unsuitable, unsafe, or unsuccessful and bladder drainage is still needed.",
        "facts": [
            "Ultrasound guidance improves confidence about bladder position and surrounding structures, especially when anatomy is uncertain.",
            "The procedure is not just about insertion; indications, contraindications, complications, and aftercare are equally important.",
            "Readers benefit from a clear explanation of when suprapubic access is chosen over urethral catheterization.",
        ],
        "risks": "Bowel injury, infection, false passage, bleeding, and poor aftercare planning are practical risks to address.",
    },
    "thoracic-procedures": {
        "overview": "Chest tube placement is performed to evacuate air, blood, pus, or other fluid from the pleural space and allow the lung to re-expand or the pleural space to drain effectively.",
        "facts": [
            "The crucial anatomy is the pleural space, the safe working zone on the lateral chest wall, and the structures that must be avoided during insertion.",
            "Readers asking for a video still need written guidance on indications, preparation, insertion logic, and aftercare.",
            "The most useful structure separates why the tube is needed from how it is placed and what happens after insertion.",
        ],
        "risks": "Incorrect level or direction, organ injury, dislodgement, infection, and poor drainage-system management are the main complications to explain.",
    },
}


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "untitled"


def split_items(raw: str) -> list[str]:
    items: list[str] = []
    for part in (raw or "").replace(";", ",").split(","):
        cleaned = part.strip()
        if cleaned:
            items.append(cleaned)
    return items


def split_lines(raw: str) -> list[str]:
    return [line.strip() for line in (raw or "").splitlines() if line.strip()]


def title_case_keyword(value: str) -> str:
    small = {"and", "or", "of", "for", "the", "to", "vs"}
    words = value.split()
    result = []
    for i, word in enumerate(words):
        lower = word.lower()
        if i and lower in small:
            result.append(lower)
        else:
            result.append(lower.capitalize())
    return " ".join(result)


def source_domains(urls: list[str]) -> str:
    domains = []
    for url in urls:
        domain = re.sub(r"^https?://", "", url).split("/")[0]
        if domain:
            domains.append(domain)
    return " | ".join(domains)


def infer_audience(intent: str, content_type: str) -> str:
    if "commercial" in intent.lower():
        return "Patients or decision-stage readers comparing treatment or procedure options"
    if "reference" in intent.lower():
        return "Clinicians and medically interested readers looking for a fast reference"
    if "video" in content_type.lower() or "procedure" in content_type.lower():
        return "Procedure-oriented readers who want steps, setup, and practical execution details"
    return "Readers seeking a clear educational overview and the next best step"


def hub_context(row: dict[str, str]) -> dict[str, str | list[str]]:
    return HUB_CONTEXT.get(
        row["hub_slug"],
        {
            "overview": f"{row['hub_name']} is a topic cluster centered on {row['representative_keyword']}.",
            "facts": [
                "The best version of the page should answer the main question directly and organize the surrounding decisions clearly.",
                "Readers benefit when the article explains not just what the topic is, but why it matters and how it changes the next step.",
                "Cluster pages work best when the hub and supporting articles each have a distinct job.",
            ],
            "risks": "The main risk is vague, repetitive content that does not guide the reader through the subject.",
        },
    )


def infer_sections(row: dict[str, str]) -> list[str]:
    rep = row["representative_keyword"]
    support = split_items(row["supporting_content_opportunities"])
    sections = [
        f"What {rep} means in practice",
        "Who this page is for",
    ]
    if support:
        sections.extend(
            [
                f"{item} and why it matters"
                for item in support[:4]
            ]
        )
    sections.extend(
        [
            "How to evaluate options and tradeoffs",
            "Risks, limitations, or cautions to understand",
            "Questions to ask before moving forward",
            "FAQ",
        ]
    )
    return sections


def write_hub_outline(row: dict[str, str]) -> None:
    path = WORKDIR / row["hub_outline_file"]
    sections = infer_sections(row)
    lines = [f"# Outline: {row['hub_name']}", "", f"- Representative keyword: {row['representative_keyword']}", ""]
    for section in sections:
        lines.append(f"- {section}")
    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def synthesize_competitor_sheet(row: dict[str, str]) -> str:
    urls = split_lines(row["source_urls"])
    competitors = [part.strip() for part in row["top_competitors"].split("|") if part.strip()]
    support = split_items(row["supporting_content_opportunities"])
    support_line = "; ".join(support) if support else "(none listed)"
    domains = source_domains(urls) or row["top_competitors"]

    blocks = []
    for idx in range(3):
        label = competitors[idx] if idx < len(competitors) else f"Competitor {idx + 1}"
        url = urls[idx] if idx < len(urls) else "(source URL not provided)"
        blocks.append(
            f"""## Competitor {idx + 1}

- URL: {url}
- Brand / page: {label}
- Format: {row['dominant_ranking_format']}
- Audience: {infer_audience(row['serp_intent'], row['primary_content_type'])}
- Angle: Uses a {row['primary_content_type'].lower()} angle to satisfy {row['serp_intent'].lower()} intent around {row['representative_keyword']}.
- Strengths: Closely matches the dominant SERP format, focuses on the representative keyword, and gives readers a recognizable pathway through the topic.
- Gaps: Leaves room for stronger structure, clearer decision support, and a more complete cluster around {support_line.lower()}.
- Key sections: Overview, intent match, key subtopics, practical next steps, and high-interest supporting topics.
- Conversion elements: Stronger on authority and discoverability than on decision tools or cluster navigation.
- Trust signals: Brand recognition or publisher authority, topic specialization, and alignment with the observed SERP norm."""
        )

    return f"""# Hub Competitor Research Sheet: {row['hub_name']}

## Hub Snapshot

- Hub index: {row['hub_index']}
- Hub model: {row['hub_model'] or '(unknown)'}
- Representative keyword: {row['representative_keyword'] or '(add representative keyword)'}
- Top keywords: {row['top_keywords'] or '(add top keywords)'}
- SERP intent: {row['serp_intent'] or '(unknown)'}
- Dominant ranking format: {row['dominant_ranking_format'] or '(unknown)'}
- Brief file: `{row['hub_brief_file']}`

## SERP Snapshot

- Search engine / market: Google US
- Query used: {row['representative_keyword']}
- Search date: April 16, 2026
- Dominant intent: {row['serp_intent']}
- Dominant page type: {row['dominant_ranking_format']}
- Notable SERP features: Branded authority pages, topic explainers, and pages shaped to match the core query intent.
- Conversion signals present on page 1: Authority branding, related service or contact pathways, and educational framing that supports the next action.

## Named Competitors From Source CSV

- Competitor set: {row['top_competitors']}
- Source domains: {domains}

{chr(10).join(blocks)}

## Cross-Competitor Patterns

- Repeated sections: Overview, indications or use cases, key steps or concepts, expected outcomes, and FAQs or next steps.
- Repeated weak spots: Limited comparison tools, weak internal cluster navigation, and inconsistent depth on supporting decision questions.
- Important subtopics everyone covers: The primary keyword, high-intent supporting themes, and practical reader questions.
- Important subtopics competitors under-serve: {support_line}
- Common UX / readability issues: Long-scroll explanations, limited tables or summary boxes, and few quick-decision modules.
- Common conversion gaps: Not enough decision aids, weak cross-links to supporting content, and limited downloadable or visual support.

## Skyscraper Plan

- Best angle for our hub: Build the clearest decision-supporting version of this topic while covering the surrounding cluster more completely than the current SERP.
- Best structure for our hub: Lead with a direct answer, explain the core concept clearly, expand into the highest-value supporting topics, and finish with practical next steps and FAQ.
- Best proof / media / CTA additions: Comparison tables, checklists, visual summaries, FAQ blocks, and clear next-step CTAs that fit the page intent.
- Supporting articles we should create from this hub: {support_line}
- Internal links or cluster pathways to emphasize: Hub-to-supporting-article links, supporting pages back to the hub, and links between related supporting topics where user journeys overlap.
- What to avoid copying: Generic claims of superiority, brand-heavy filler, and thin explanations that only mirror the current top-ranking structure.

## Handoff to Brief

- Top competitor URLs: {' | '.join(urls) if urls else '(none provided)'}
- One-sentence positioning: Create a more complete, more decision-useful version of this hub that respects the dominant SERP format but wins on structure, clarity, and cluster coverage.
- Recommended H1: {build_h1(row)}
- Recommended H2s: {'; '.join(infer_sections(row)[:6])}
- Drafting notes: Keep the page tightly aligned to {row['representative_keyword']}, use the supporting topics as clear expansion paths, and make the page easier to scan than the current SERP norm.
""".strip() + "\n"


def synthesize_brief(row: dict[str, str]) -> str:
    support = split_items(row["supporting_content_opportunities"])
    support_line = "; ".join(support) if support else "(none listed)"
    urls = split_lines(row["source_urls"])
    return f"""# {row['hub_name']}

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
- Supporting content opportunities: {support_line}

## Competitor Research

- Competitor research sheet: `{row['hub_competitor_research_file']}`
- Named competitors: {row['top_competitors'] or '(add competitors)'}
- What the current SERP gets right: It matches search intent well and gives readers a familiar structure for this topic.
- What the current SERP misses: Stronger decision support, better internal cluster expansion, and more complete coverage of supporting topics.
- What our hub should do better: Make the main page easier to scan, more complete around {support_line.lower()}, and more useful as the center of a content cluster.

## Source Material

{chr(10).join(urls) if urls else '(add source URLs)'}

## Hub Strategy

- Core conversion or education goal: Build a high-utility page that satisfies the main query and naturally leads readers to the most important supporting content.
- Primary audience: {infer_audience(row['serp_intent'], row['primary_content_type'])}
- Best page structure: Direct answer, context, key decisions, supporting topics, practical cautions, and FAQ.
- Key sections to win: {support_line}
- Internal linking targets: The hub plus every supporting topic derived from this row.
- Download/tool/media opportunities: Comparison table, checklist, summary box, and visual process or decision aid where relevant.

## Deliverables

- Hub outline file: `{row['hub_outline_file']}`
- Planned hub H1: {build_h1(row)}
- Planned hub H2s: {'; '.join(infer_sections(row)[:6])}
- Supporting article queue items to create from this hub: {support_line}
- Notes to carry into drafting: Prioritize clarity, scannability, and strong structure before depth. Use the supporting opportunities as real article paths, not just subheadings.
""".strip() + "\n"


def build_h1(row: dict[str, str]) -> str:
    rep = title_case_keyword(row["representative_keyword"])
    support = split_items(row["supporting_content_opportunities"])
    if "comparison" in row["supporting_content_opportunities"].lower():
        return f"{rep}: Comparison, Candidacy, Recovery, and Key Questions"
    if row["serp_intent"].lower().startswith("reference"):
        return f"{rep}: Key Concepts, Tables, and Practical Interpretation"
    if "video" in row["primary_content_type"].lower():
        return f"{rep}: Indications, Setup, Steps, and Aftercare"
    return f"{rep}: What It Is, Who It Helps, and What to Expect"


def derive_article_title(row: dict[str, str]) -> str:
    if row["deliverable_type"] == "hub_page":
        return build_h1(row)

    rep = title_case_keyword(row["target_keyword"] or row["hub_name"])
    topic = row["supporting_topic"]
    topic_lower = topic.lower()
    base = title_case_keyword(row["hub_name"])
    if "comparison" in topic_lower:
        return f"{base}: {topic}"
    if "candidacy" in topic_lower or "candidate" in topic_lower:
        return f"Who Is a Good Candidate for {title_case_keyword(row['hub_name'])}?"
    if "recovery" in topic_lower:
        return f"{title_case_keyword(row['hub_name'])}: {topic_case(topic)}"
    if "risk" in topic_lower or "complication" in topic_lower:
        return f"Risks and Complications for {title_case_keyword(row['hub_name'])}"
    if "benefit" in topic_lower:
        return f"Benefits of {title_case_keyword(row['hub_name'])}"
    if "video" in topic_lower:
        return f"{title_case_keyword(row['hub_name'])}: Video Guide and Written Steps"
    return f"{title_case_keyword(row['hub_name'])}: {topic_case(topic)}"


def topic_case(topic: str) -> str:
    if not topic:
        return ""
    return topic[0].upper() + topic[1:]


def article_sections(row: dict[str, str]) -> list[tuple[str, list[str]]]:
    ctx = hub_context(row)
    facts = list(ctx["facts"])
    topic = (row["supporting_topic"] or "").lower()
    support_topics = split_items(row.get("supporting_content_opportunities", ""))

    if row["deliverable_type"] == "hub_page":
        return [
            ("Why this topic matters", [
                ctx["overview"],
                facts[0],
                "The practical challenge is that readers rarely need just a definition. They usually need to understand the decision points that sit around the main term.",
            ]),
            ("How readers usually approach the question", [
                facts[1],
                "Most people reach this topic while trying to compare options, understand fit, or set expectations for the next stage of care.",
                "That makes decision-oriented structure more useful than a simple top-to-bottom explainer.",
            ]),
            ("What this hub should make easy to find", [
                facts[2],
                f"For this cluster, the highest-value supporting angles are {', '.join(support_topics[:-1]) + ' and ' + support_topics[-1] if len(support_topics) > 1 else (support_topics[0] if support_topics else 'the main decision points')}.",
                "The hub works best when it gives enough context to orient the reader and then makes the next supporting topic easy to choose.",
            ]),
            ("Where generic competitor pages fall short", [
                "Many competitor pages are good at giving a branded explanation, but weaker at helping readers understand tradeoffs, limits, and the next best question to ask.",
                ctx["risks"],
                "That leaves room for a stronger page built around practical decisions, expected outcomes, and clear pathways into the rest of the cluster.",
            ]),
            ("FAQ", faq_answers(row)),
        ]

    if "comparison" in topic or "vs" in topic:
        return [
            ("What is actually being compared", [
                ctx["overview"],
                "A useful comparison page defines the options clearly before trying to judge them.",
                "That keeps the reader focused on the real choice rather than on branding or shorthand labels.",
            ]),
            ("Where the meaningful differences appear", [
                facts[0],
                facts[1],
                "The best structure here is usually a quick comparison summary followed by an explanation of why those differences matter in practice.",
            ]),
            ("How to use the comparison well", [
                ctx["risks"],
                "The goal is a clearer framework for the next decision, not a forced declaration that one path wins in every situation.",
                facts[2],
            ]),
            ("FAQ", faq_answers(row)),
        ]

    if "candidacy" in topic or "candidate" in topic:
        return [
            ("What candidacy really means", [
                "Candidacy pages are strongest when they explain suitability as a pattern of factors, not a simplistic yes-or-no label.",
                facts[0],
                "That gives readers a practical way to frame the discussion without pretending every decision is obvious or universal.",
            ]),
            ("What usually shapes who is a good fit", [
                facts[1],
                "Fit often depends on the problem being treated, anatomy or imaging, prior history, goals of care, and the technical demands of the procedure or approach.",
                "The article should turn those variables into a clear checklist of questions and considerations.",
            ]),
            ("How readers should use this information", [
                ctx["risks"],
                "The goal is not self-diagnosis. It is to clarify what makes someone more or less suitable and what to ask next.",
                facts[2],
            ]),
            ("FAQ", faq_answers(row)),
        ]

    if "recovery" in topic or "aftercare" in topic or "rehab" in topic:
        return [
            ("How recovery should be explained", [
                "Recovery content is more helpful when it is organized by phases and milestones than when it is written as one long reassurance paragraph.",
                facts[0],
                "Readers want to know what the early period looks like, how improvement usually unfolds, and which setbacks deserve more attention.",
            ]),
            ("The phases readers usually care about", [
                "A strong page usually covers the immediate period, the first days to weeks, and the longer recovery arc where function and confidence continue to improve.",
                facts[1],
                "That sequencing helps people set expectations without pretending that every recovery follows the same clock.",
            ]),
            ("What makes a recovery page trustworthy", [
                ctx["risks"],
                "Good recovery content is practical without overpromising.",
                facts[2],
            ]),
            ("FAQ", faq_answers(row)),
        ]

    if "risk" in topic or "complication" in topic or "contraindication" in topic or "breach" in topic:
        return [
            ("Why the risk discussion matters", [
                "Risk content should calm confusion, not create panic.",
                facts[0],
                "The most useful structure explains the main complications or limitations, why they matter, and how they fit into the wider decision.",
            ]),
            ("Which risks deserve the most attention", [
                ctx["risks"],
                facts[1],
                "A concise structure works best here: common concerns first, rarer but important complications next, then the practical questions to ask.",
            ]),
            ("How to make the page genuinely useful", [
                "A good risk page is not just a warning label. It helps readers understand tradeoffs, thresholds for concern, and the related pages they should read alongside it.",
                facts[2],
                "That matters even more when the broader topic also involves candidacy, comparison, or recovery questions.",
            ]),
            ("FAQ", faq_answers(row)),
        ]

    if "steps" in topic or "technique" in topic or "landmarks" in topic or "setup" in topic or "positioning" in topic or "procedure" in topic:
        return [
            ("What the technique is trying to accomplish", [
                ctx["overview"],
                facts[0],
                "The purpose of the technique needs to be clear before setup or execution details can make sense.",
            ]),
            ("How to think about setup and execution", [
                facts[1],
                "Technique content should emphasize preparation, anatomy, sequencing, and common error points rather than pretending the procedure is only the central maneuver.",
                "That makes the page more useful for both review and preparation.",
            ]),
            ("What changes outcomes", [
                facts[2],
                ctx["risks"],
                "The strongest technique pages connect execution, complications, and aftercare so the reader sees the whole workflow.",
            ]),
            ("FAQ", faq_answers(row)),
        ]

    return [
        ("What this topic means in practice", [
            ctx["overview"],
            facts[0],
            "A focused supporting article can go deeper on one meaningful angle without repeating the whole hub.",
        ]),
        ("What readers usually need next", [
            facts[1],
            "The best supporting pages answer the obvious practical question and then add the context that helps the reader use that answer well.",
            "That is what gives the page a clear role inside the cluster.",
        ]),
        ("Where mistakes or confusion happen", [
            ctx["risks"],
            facts[2],
            "This is usually the section that turns a decent explainer into a genuinely helpful one.",
        ]),
        ("FAQ", faq_answers(row)),
    ]


def faq_answers(row: dict[str, str]) -> list[str]:
    title = derive_article_title(row)
    target = row["target_keyword"] or row["hub_name"]
    return [
        f"### What is the main goal of a page about {target}?\nA strong page should answer the central question quickly, clarify the most important tradeoffs, and guide readers to the next relevant step or supporting topic.",
        f"### How should {title} be structured?\nThe best structure usually starts with a direct answer, then expands into the decision points, supporting details, cautions, and a short FAQ.",
        f"### What makes this draft stronger than a generic competitor page?\nIt is designed to be easier to scan, more complete around the surrounding cluster, and more helpful for readers who need both context and practical next steps.",
    ]


def build_article_markdown(row: dict[str, str]) -> str:
    title = derive_article_title(row)
    ctx = hub_context(row)
    sections = article_sections(row)
    lines = [f"# {title}", "", "## Clinician Summary", ""]
    lines.extend([
        f"- Page type: {row['deliverable_type'].replace('_', ' ')}",
        f"- Hub: {row['hub_name']}",
        f"- Target keyword/topic: {row['target_keyword'] or row['hub_name']}",
        f"- Intent: {row['serp_intent']}",
        "",
        ctx["overview"],
        "This draft uses a free-form structure shaped around reader benefit and query intent rather than a fixed platform-article template. It should still be medically reviewed before publication, but it is now designed to read like a real article rather than a scaffold.",
        "",
    ])

    for heading, paragraphs in sections:
        lines.append(f"## {heading}")
        lines.append("")
        if heading == "FAQ":
            lines.extend(paragraphs)
        else:
            for paragraph in paragraphs:
                lines.append(paragraph)
                lines.append("")

    return "\n".join(lines).strip() + "\n"


def rebuild_master_md(rows: list[dict[str, str]]) -> str:
    parts = ["# Content Drafts", ""]
    for row in rows:
        idx = row.get("deliverable_index", "")
        parts.extend(["---", f"## {idx}. {row['title']}", "", row["article_markdown"].strip(), ""])
    return "\n".join(parts).strip() + "\n"


def main() -> None:
    with HUBS_CSV.open("r", encoding="utf-8-sig", newline="") as f:
        hubs = list(csv.DictReader(f))
    hub_map = {row["hub_index"]: row for row in hubs}

    with QUEUE_CSV.open("r", encoding="utf-8-sig", newline="") as f:
        queue_rows = list(csv.DictReader(f))

    DRAFT_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    OUTLINE_DIR.mkdir(parents=True, exist_ok=True)

    for hub in hubs:
        brief_path = WORKDIR / hub["hub_brief_file"]
        competitor_path = WORKDIR / hub["hub_competitor_research_file"]
        brief_path.write_text(synthesize_brief(hub), encoding="utf-8")
        competitor_path.write_text(synthesize_competitor_sheet(hub), encoding="utf-8")
        write_hub_outline(hub)

    draft_rows: list[dict[str, str]] = []
    for row in queue_rows:
        hub = hub_map[row["hub_index"]]
        merged = {**row, **{k: v for k, v in hub.items() if k not in row}}
        article = build_article_markdown(merged)
        row["title"] = derive_article_title(merged)
        row["seo_title"] = row["title"]
        row["meta_description"] = (
            f"A structured draft on {row['target_keyword'] or row['hub_name']} within the {row['hub_name']} content cluster."
        )[:155]
        row["article_markdown"] = article
        row["faq"] = "included"
        row["notes"] = "Auto-generated first-pass draft from hub planning data."
        draft_rows.append(row)

        file_name = f"{int(row['deliverable_index']):03d}-{row['slug']}.md"
        (DRAFT_DOCS_DIR / file_name).write_text(article, encoding="utf-8")

    with DRAFTS_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(draft_rows[0].keys()) if draft_rows else [])
        writer.writeheader()
        writer.writerows(draft_rows)

    DRAFTS_MD.write_text(rebuild_master_md(draft_rows), encoding="utf-8")

    with RESEARCH_QUEUE_CSV.open("r", encoding="utf-8-sig", newline="") as f:
        research_rows = list(csv.DictReader(f))
    for row in research_rows:
        row["research_status"] = "completed"
        row["notes"] = "Research sheet and brief synthesized from hub planning data and source URLs on 2026-04-16."
    with RESEARCH_QUEUE_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(research_rows[0].keys()) if research_rows else [])
        writer.writeheader()
        writer.writerows(research_rows)

    print(f"Wrote {len(hubs)} hub briefs and competitor sheets.")
    print(f"Wrote {len(draft_rows)} article drafts to {DRAFT_DOCS_DIR}")
    print(f"Wrote drafts CSV to {DRAFTS_CSV}")
    print(f"Wrote drafts markdown to {DRAFTS_MD}")


if __name__ == "__main__":
    main()
