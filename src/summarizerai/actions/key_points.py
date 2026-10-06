import re
from typing import List, Tuple
from summarizerai.models.chunk import Chunk
from summarizerai.llm.provider import LLMProvider
from summarizerai.actions.citations import extract_deterministic_citations

async def generate_key_points(
    chunks: List[Chunk],
    llm: LLMProvider
) -> Tuple[str, List[str], List[dict]]:
    """
    Extract core arguments, quantitative data, and key takeaways grounded in the document.
    """
    if not chunks:
        return "No content available.", [], []

    # Sample representative chunks across the document
    if len(chunks) > 8:
        step = len(chunks) // 8
        sampled_chunks = [chunks[i] for i in range(0, len(chunks), step)][:8]
    else:
        sampled_chunks = chunks

    context = "\n\n".join(
        f"[{c.section_heading or f'Source {c.chunk_index}'}] {c.content}"
        for c in sampled_chunks
    )

    prompt = f"""You are SummarizerAI. Extract the most important Key Points and Core Arguments from the source material below.

Instructions:
- Provide 5 to 8 essential, standalone takeaways.
- Include specific numbers, findings, or mechanisms mentioned in the text.
- Present each point as a bold statement followed by a 1-2 sentence evidence-backed explanation.
- Add a concluding section on "Strategic Implications".

Source Material:
{context}
"""
    result = await llm.generate(prompt)

    # Parse key takeaways bullet list
    takeaways = []
    for line in result.split("\n"):
        line = line.strip()
        if (line.startswith("- **") or line.startswith("* **") or re.match(r"^\d+\.\s+\*\*", line)) and len(line) > 15:
            clean = line.lstrip("-* 0123456789.").strip()
            takeaways.append(clean)

    if not takeaways:
        takeaways = [l.strip("-* ") for l in result.split("\n") if l.strip().startswith(("-", "*"))][:6]

    citations = extract_deterministic_citations(result, chunks)
    return result, takeaways, citations
