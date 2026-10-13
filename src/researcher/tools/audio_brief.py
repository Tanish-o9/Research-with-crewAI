import os
import re
from typing import Optional

try:
    from gtts import gTTS
except ImportError:
    gTTS = None

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None


def extract_executive_summary_text(markdown_text: str) -> str:
    """
    Extracts the Executive Summary and Key Takeaways sections from the Markdown report
    to create a concise, listenable audio briefing.
    """
    lines = markdown_text.splitlines()
    summary_lines = []
    capture = False

    for line in lines:
        stripped = line.strip()
        # Look for Executive Summary or Key Takeaways headings
        if any(h in stripped.lower() for h in ["# executive summary", "## executive summary", "## key takeaways"]):
            capture = True
            continue
        elif capture and stripped.startswith("# ") and "executive summary" not in stripped.lower() and "key takeaways" not in stripped.lower():
            if len(summary_lines) > 5:
                break

        if capture:
            summary_lines.append(stripped)

    # If no specific section found, take first 250 words
    if not summary_lines or len(" ".join(summary_lines).split()) < 30:
        words = markdown_text.split()
        raw_text = " ".join(words[:250])
    else:
        raw_text = "\n".join(summary_lines)

    # Clean markdown formatting for speech
    clean = re.sub(r"\[.*?\]\(.*?\)", "", raw_text)  # Remove links [text](url)
    clean = re.sub(r"https?://\S+", "", clean)         # Remove raw URLs
    clean = re.sub(r"[*#_`>~-]", " ", clean)            # Remove markdown symbols
    clean = re.sub(r"\s+", " ", clean).strip()          # Clean whitespace
    return clean


def generate_audio_brief(markdown_text: str, topic: str, output_path: str, lang: str = "en") -> Optional[str]:
    """
    Generates an audio briefing (MP3) from the report summary.
    Attempts gTTS first for natural sound, with pyttsx3 offline fallback.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    brief_text = extract_executive_summary_text(markdown_text)

    if not brief_text or len(brief_text.split()) < 10:
        brief_text = f"Here is your executive intelligence briefing on {topic}. Key developments and strategic recommendations have been compiled in your full research report."

    speech_script = (
        f"Welcome to your AI research briefing on {topic}. "
        f"{brief_text} "
        f"End of executive summary briefing. Review your dashboard for full findings and citations."
    )

    # 1. Try gTTS
    if gTTS:
        try:
            tts = gTTS(text=speech_script, lang=lang, slow=False)
            tts.save(output_path)
            return output_path
        except Exception as e:
            print(f"[Audio Notice] gTTS online attempt failed ({e}), checking offline fallback...")

    # 2. Offline fallback using pyttsx3 if gTTS failed or unavailable
    if pyttsx3:
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", 175)
            # pyttsx3 saves to wav or mp3
            engine.save_to_file(speech_script, output_path)
            engine.runAndWait()
            return output_path
        except Exception as err:
            print(f"[Audio Error] pyttsx3 offline fallback failed: {err}")

    return None
