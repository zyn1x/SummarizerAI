import logging
from typing import List, Tuple
from summarizerai.models.chunk import Chunk
from summarizerai.llm.provider import LLMProvider
from summarizerai.actions.citations import extract_deterministic_citations

logger = logging.getLogger(__name__)

async def generate_hierarchical_summary(
    chunks: List[Chunk],
    llm: LLMProvider,
    summary_format: str = "executive"
) -> Tuple[str, List[dict]]:
    """
    Hierarchical document analysis:
    Processes chunks hierarchically and synthesizes results.
    """
    if not chunks:
        return "No content available to summarize.", []

    format_instruction = {
        "executive": "Produce a high-level C-suite Executive Summary focusing on the primary purpose, key findings, and strategic takeaways.",
        "detailed": "Produce an in-depth, thorough, and structured comprehensive summary detailing core methodology, arguments, data, and conclusions.",
        "bulleted": "Produce a structured bullet-point breakdown with clear thematic categories and concise takeaway bullet points."
    }.get(summary_format, "Produce a structured overview.")

    # If document is short (<= 5 chunks), analyze directly
    if len(chunks) <= 5:
        context_parts = []
        for c in chunks:
            prefix = ""
            if c.page_number is not None:
                prefix = f"[Page {c.page_number}]"
            elif c.timestamp_formatted:
                prefix = f"[{c.timestamp_formatted}]"
            elif c.section_heading:
                prefix = f"[{c.section_heading}]"
            context_parts.append(f"{prefix} {c.content}")
        full_context = "\n\n".join(context_parts)

        prompt = f"""You are SummarizerAI, an expert intelligence research assistant.
Analyze the following source content and generate a summary.

Instructions:
- {format_instruction}
- Ground all facts strictly in the source material.
- Use clear markdown headings and paragraphs.

Source Material:
{full_context}
"""
        result = await llm.generate(prompt)
    else:
        # Hierarchical analysis (Map-Reduce)
        # 1. Map phase: summarize batches of 4 chunks
        batch_size = 4
        intermediate_summaries = []
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            batch_text = "\n\n".join(f"[{c.section_heading or f'Chunk {c.chunk_index}'}] {c.content}" for c in batch)
            map_prompt = f"""Summarize the key information and essential facts from this document section in 2-3 concise paragraphs:

{batch_text}
"""
            inter = await llm.generate(map_prompt, max_tokens=500)
            intermediate_summaries.append(inter)

        # 2. Reduce phase: synthesize all intermediate summaries
        combined_intermediate = "\n\n---\n\n".join(intermediate_summaries)
        reduce_prompt = f"""You are SummarizerAI. Synthesize the following section summaries from a long document into a final cohesive summary.

Instructions:
- {format_instruction}
- Unify themes and eliminate redundancies across sections.
- Produce clean, professional markdown with headings.

Section Summaries:
{combined_intermediate}
"""
        result = await llm.generate(reduce_prompt, max_tokens=1500)

    # Generate backend-controlled deterministic citations
    citations = extract_deterministic_citations(result, chunks)
    return result, citations
