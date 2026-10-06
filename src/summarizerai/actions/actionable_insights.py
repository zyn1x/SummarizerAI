from typing import List, Tuple, Optional
from summarizerai.models.chunk import Chunk
from summarizerai.llm.provider import LLMProvider
from summarizerai.actions.citations import extract_deterministic_citations

GOAL_PROMPTS = {
    "study_exam": """GOAL: STUDY FOR AN EXAM
Deconstruct this source into an intense, high-yield examination study guide:
1. **Core Terminology & Definitions**: Essential terms to define verbatim.
2. **Key Concepts & Theories**: The primary mechanisms and principles you must memorize.
3. **High-Yield Formulas / Numerical Data**: Crucial figures, metrics, and relationships.
4. **Potential Exam Questions & Model Answers**: 3 challenging sample questions (short answer / analytical) with precise source-grounded answers.
5. **Quick-Recall Mnemonics / Memory Hooks**: Summarized anchors for rapid review.""",

    "understand_topic": """GOAL: UNDERSTAND THE TOPIC FROM FIRST PRINCIPLES
Build an intuitive, crystal-clear conceptual mental model:
1. **The 'Explain Like I'm Five' (ELI5) Analogy**: A relatable metaphor that demystifies the core thesis.
2. **Foundational Architecture**: Why this matters and what foundational problem it solves.
3. **Step-by-Step Breakdown**: Walk through the logical progression from origin to outcome.
4. **Common Misconceptions**: Pitfalls or inaccurate assumptions beginners frequently make.
5. **Key Takeaway in One Sentence**: The single most critical concept to retain.""",

    "implement_method": """GOAL: IMPLEMENT THE METHOD (ENGINEERING / EXECUTION)
Translate the theoretical findings into an actionable technical implementation playbook:
1. **System Prerequisites & Dependencies**: Libraries, environment variables, tooling, and data requirements.
2. **Step-by-Step Execution Algorithm**: Numbered procedural steps to execute or reproduce the method.
3. **Code / Workflow Blueprint**: Concrete pseudo-code or configuration schemas detailing the exact logic.
4. **Edge Cases & Failure Modes**: Specific boundary conditions where the method fails or requires fallbacks.
5. **Verification & Testing Protocol**: How to validate that your implementation produces the expected results.""",

    "apply_project": """GOAL: APPLY TO A REAL-WORLD PROJECT
Create an architectural integration blueprint for adapting this material into a production project:
1. **Value Proposition & Use Cases**: Where this yields the highest ROI or competitive advantage in a product.
2. **Architecture Integration Plan**: How this plugs into existing pipelines, data stores, or frontend/backend stacks.
3. **Resource & Performance Budget**: Expected compute costs, latency considerations, and scalability bottlenecks.
4. **Implementation Roadmap**: 30-60-90 day milestone rollout plan.
5. **Risk Matrix & Mitigation**: Security, compliance, latency, or data quality risks and defenses.""",

    "find_research_gaps": """GOAL: FIND RESEARCH GAPS & NOVEL DIRECTIONS
Perform a critical scientific review of this paper/source to identify unexplored avenues:
1. **Underlying Assumptions**: Unstated or fragile premises upon which the arguments depend.
2. **Methodological Limitations**: Dataset biases, scope boundaries, or missing benchmark comparisons.
3. **Unresolved Contradictions / Open Questions**: Ambiguities or conflicting findings left unanswered.
4. **Proposed Research Hypotheses**: 3 concrete, testable novel research questions for future investigation.
5. **Interdisciplinary Opportunities**: Novel connections with adjacent domains or emergent methodologies.""",

    "prepare_presentation": """GOAL: PREPARE AN IMPACTFUL PRESENTATION
Transform this content into an executive-ready presentation structure:
1. **Slide 1: Hook & Core Problem Statement** (Slide title, 3 key bullet points, Speaker talking notes).
2. **Slide 2: Proposed Methodology / Core Framework** (Slide title, 3 key bullet points, Speaker talking notes).
3. **Slide 3: Evidence, Data & Key Findings** (Slide title, 3 key bullet points, Speaker talking notes).
4. **Slide 4: Strategic Impact & Real-World Implications** (Slide title, 3 key bullet points, Speaker talking notes).
5. **Slide 5: Action Items & Q&A Preparation** (Anticipated difficult audience questions and vetted answers)."""
}

async def generate_actionable_insights(
    chunks: List[Chunk],
    llm: LLMProvider,
    user_goal: str,
    custom_context: Optional[str] = None
) -> Tuple[str, List[dict]]:
    """
    Generate deeply tailored, goal-specific actionable insights strictly grounded in the document source.
    """
    if not chunks:
        return "No content available to generate actionable insights.", []

    goal_template = GOAL_PROMPTS.get(
        user_goal,
        f"Analyze the source to provide actionable execution insights tailored specifically to: {user_goal}."
    )

    # Sample chunks if large
    if len(chunks) > 10:
        step = len(chunks) // 10
        sampled = [chunks[i] for i in range(0, len(chunks), step)][:10]
    else:
        sampled = chunks

    context = "\n\n".join(
        f"[{c.section_heading or f'Source {c.chunk_index}'}] {c.content}"
        for c in sampled
    )

    custom_note = f"\nUser Custom Context / Focus Area: {custom_context}\n" if custom_context else ""

    prompt = f"""You are SummarizerAI, an elite research and actionable intelligence system.
Generate an actionable intelligence deliverable based strictly on the provided source material.

{goal_template}
{custom_note}

Strict Grounding Rules:
- Only cite facts, numbers, or methods actually supported by the source text.
- Do not fabricate benchmarks, API endpoints, or results not found in the source.
- Format with professional markdown, headers, tables, and bullet points.

Source Material:
{context}
"""
    result = await llm.generate(prompt, max_tokens=2048)
    citations = extract_deterministic_citations(result, chunks)
    return result, citations
