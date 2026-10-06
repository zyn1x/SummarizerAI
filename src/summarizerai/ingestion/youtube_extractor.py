import re
import asyncio
from typing import List, Dict, Any
from summarizerai.processing.canonical import CanonicalDocument, CanonicalChunk
from summarizerai.ingestion.security import validate_ssrf_safe_url

class YouTubeExtractionError(Exception):
    pass

def format_seconds(seconds: float) -> str:
    """Format seconds into MM:SS or HH:MM:SS."""
    s = int(round(seconds))
    hrs = s // 3600
    mins = (s % 3600) // 60
    secs = s % 60
    if hrs > 0:
        return f"{hrs:02d}:{mins:02d}:{secs:02d}"
    return f"{mins:02d}:{secs:02d}"

def extract_youtube_sync(url: str) -> CanonicalDocument:
    """Extract YouTube transcript and metadata using yt-dlp synchronously."""
    try:
        import yt_dlp
    except ImportError:
        raise YouTubeExtractionError("yt-dlp library is required for YouTube extraction.")

    ydl_opts = {
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": ["en", "en-US", "en-GB", "en-orig"],
        "quiet": True,
        "no_warnings": True,
    }

    try:
        # pyrefly: ignore [bad-argument-type]
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as e:
        raise YouTubeExtractionError(f"Failed to fetch YouTube metadata: {e}")

    title = info.get("title") or "YouTube Video"
    video_id = info.get("id")
    duration = info.get("duration") or 0
    channel = info.get("uploader") or info.get("channel") or ""

    # Try to extract transcript / subtitles
    subtitles = info.get("subtitles") or {}
    auto_subs = info.get("automatic_captions") or {}
    combined_subs = {**auto_subs, **subtitles}

    # Find english subtitles or first available
    en_sub = None
    for lang in ["en", "en-US", "en-GB", "en-orig"]:
        if lang in combined_subs:
            en_sub = combined_subs[lang]
            break

    if not en_sub and combined_subs:
        # Take whatever language is available
        en_sub = next(iter(combined_subs.values()))

    transcript_segments = []
    
    if en_sub:
        # Look for json3 or vtt format
        json3_entry = next((f for f in en_sub if f.get("ext") == "json3"), None)
        vtt_entry = next((f for f in en_sub if f.get("ext") == "vtt"), None)
        sub_url = (json3_entry or vtt_entry or en_sub[0]).get("url")

        if sub_url:
            import httpx
            try:
                resp = httpx.get(sub_url, timeout=20)
                if resp.status_code == 200:
                    if json3_entry:
                        data = resp.json()
                        events = data.get("events", [])
                        for ev in events:
                            t_start = ev.get("tStartMs", 0) / 1000.0
                            d_dur = ev.get("dDurationMs", 0) / 1000.0
                            segs = ev.get("segs", [])
                            text = "".join(s.get("utf8", "") for s in segs).strip()
                            if text and text != "\n":
                                transcript_segments.append({
                                    "start": t_start,
                                    "end": t_start + d_dur,
                                    "text": text
                                })
                    else:
                        # VTT fallback parsing
                        vtt_text = resp.text
                        blocks = vtt_text.split("\n\n")
                        time_pattern = re.compile(r"(\d{2}:\d{2}(?::\d{2})?(?:\.\d+)?)\s*-->\s*(\d{2}:\d{2}(?::\d{2})?(?:\.\d+)?)")
                        for b in blocks:
                            lines = b.strip().split("\n")
                            for idx, line in enumerate(lines):
                                m = time_pattern.search(line)
                                if m and idx + 1 < len(lines):
                                    # Convert time to seconds
                                    s_parts = m.group(1).split(":")
                                    start_sec = 0.0
                                    if len(s_parts) == 3:
                                        start_sec = float(s_parts[0]) * 3600 + float(s_parts[1]) * 60 + float(s_parts[2])
                                    elif len(s_parts) == 2:
                                        start_sec = float(s_parts[0]) * 60 + float(s_parts[1])
                                    t_text = " ".join(lines[idx + 1:]).strip()
                                    if t_text:
                                        transcript_segments.append({
                                            "start": start_sec,
                                            "end": start_sec + 5.0,
                                            "text": t_text
                                        })
            except Exception:
                pass

    all_chunks: List[CanonicalChunk] = []
    full_text_list: List[str] = []
    chunk_index = 0

    if transcript_segments:
        # Group transcript segments into ~200-word chunks preserving start & end timestamps
        curr_words: List[str] = []
        chunk_t_start = transcript_segments[0]["start"]
        chunk_t_end = transcript_segments[0]["end"]

        for seg in transcript_segments:
            seg_words = seg["text"].split()
            if len(curr_words) + len(seg_words) > 180 and curr_words:
                content = " ".join(curr_words)
                formatted = format_seconds(chunk_t_start)
                all_chunks.append(
                    CanonicalChunk(
                        chunk_index=chunk_index,
                        content=content,
                        timestamp_start=chunk_t_start,
                        timestamp_end=chunk_t_end,
                        timestamp_formatted=formatted,
                        section_heading=f"Video @ {formatted}",
                        token_count=len(curr_words)
                    )
                )
                full_text_list.append(f"[{formatted}] {content}")
                chunk_index += 1
                curr_words = list(seg_words)
                chunk_t_start = seg["start"]
                chunk_t_end = seg["end"]
            else:
                curr_words.extend(seg_words)
                chunk_t_end = seg["end"]

        if curr_words:
            content = " ".join(curr_words)
            formatted = format_seconds(chunk_t_start)
            all_chunks.append(
                CanonicalChunk(
                    chunk_index=chunk_index,
                    content=content,
                    timestamp_start=chunk_t_start,
                    timestamp_end=chunk_t_end,
                    timestamp_formatted=formatted,
                    section_heading=f"Video @ {formatted}",
                    token_count=len(curr_words)
                )
            )
            full_text_list.append(f"[{formatted}] {content}")
    else:
        # Fallback to video description / chapters
        desc = info.get("description") or ""
        if not desc:
            raise YouTubeExtractionError("No transcript, captions, or description found for this YouTube video.")
        full_text_list.append(f"Description:\n{desc}")
        all_chunks.append(
            CanonicalChunk(
                chunk_index=0,
                content=desc,
                timestamp_start=0.0,
                timestamp_end=float(duration),
                timestamp_formatted="00:00",
                section_heading="Video Description",
                token_count=len(desc.split())
            )
        )

    raw_text = "\n\n".join(full_text_list)

    return CanonicalDocument(
        title=title,
        source_type="youtube",
        source_url=url,
        raw_text=raw_text,
        chunks=all_chunks,
        metadata={
            "video_id": video_id,
            "duration": duration,
            "channel": channel,
            "formatted_duration": format_seconds(duration),
        }
    )

async def extract_youtube_content(url: str) -> CanonicalDocument:
    """Async wrapper around yt-dlp extraction."""
    validate_ssrf_safe_url(url)
    return await asyncio.to_thread(extract_youtube_sync, url)
