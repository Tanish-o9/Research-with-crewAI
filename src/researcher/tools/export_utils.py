import os
import re
from datetime import datetime
from pathlib import Path


def slugify(text: str) -> str:
    """Converts a string into a clean filename-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[-\s]+", "_", text)[:40]


def markdown_to_simple_html(md_text: str) -> str:
    """Converts common Markdown elements to HTML without external dependencies."""
    html_lines = []
    in_list = False

    for line in md_text.splitlines():
        trimmed = line.strip()

        # Handle headings
        if trimmed.startswith("### "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h3>{trimmed[4:]}</h3>")
        elif trimmed.startswith("## "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h2>{trimmed[3:]}</h2>")
        elif trimmed.startswith("# "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h1>{trimmed[2:]}</h1>")
        # Handle list items
        elif trimmed.startswith("- ") or trimmed.startswith("* "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            content = trimmed[2:]
            # Bold inline formatting
            content = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", content)
            html_lines.append(f"<li>{content}</li>")
        elif trimmed == "":
            if in_list:
                html_lines.append("</ul>")
                in_list = False
        else:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            # Bold inline formatting
            content = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", trimmed)
            html_lines.append(f"<p>{content}</p>")

    if in_list:
        html_lines.append("</ul>")

    return "\n".join(html_lines)


def export_report(markdown_content: str, topic: str, output_dir: str = "reports") -> dict:
    """
    Saves the report as both a timestamped Markdown file and an HTML document.
    Returns the paths of the saved files.
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = slugify(topic)

    md_filename = f"report_{timestamp}_{slug}.md"
    html_filename = f"report_{timestamp}_{slug}.html"
    latest_md = "latest_report.md"

    md_path = os.path.join(output_dir, md_filename)
    html_path = os.path.join(output_dir, html_filename)
    latest_path = os.path.join(output_dir, latest_md)

    # Save Markdown files
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    with open(latest_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    # Convert to HTML
    body_html = markdown_to_simple_html(markdown_content)
    now_readable = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Research Report: {topic}</title>
    <style>
        :root {{
            --bg: #0f172a;
            --card-bg: #1e293b;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent: #38bdf8;
            --border: #334155;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.7;
            background-color: var(--bg);
            color: var(--text-primary);
            margin: 0;
            padding: 2rem 1rem;
        }}
        .container {{
            max-width: 860px;
            margin: 0 auto;
            background: var(--card-bg);
            padding: 2.5rem;
            border-radius: 12px;
            border: 1px solid var(--border);
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        }}
        .header {{
            border-bottom: 2px solid var(--border);
            padding-bottom: 1.5rem;
            margin-bottom: 2rem;
        }}
        .badge {{
            display: inline-block;
            background: rgba(56, 189, 248, 0.15);
            color: var(--accent);
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 0.75rem;
        }}
        h1, h2, h3 {{
            color: #ffffff;
            line-height: 1.3;
        }}
        h1 {{ font-size: 2rem; margin-top: 0; }}
        h2 {{ font-size: 1.4rem; border-bottom: 1px solid var(--border); padding-bottom: 0.5rem; margin-top: 2rem; color: var(--accent); }}
        h3 {{ font-size: 1.15rem; margin-top: 1.5rem; }}
        p {{ color: #cbd5e1; margin-bottom: 1rem; }}
        ul {{ padding-left: 1.5rem; margin-bottom: 1.5rem; }}
        li {{ color: #cbd5e1; margin-bottom: 0.5rem; }}
        strong {{ color: #ffffff; }}
        .footer {{
            margin-top: 3rem;
            padding-top: 1.5rem;
            border-top: 1px solid var(--border);
            font-size: 0.85rem;
            color: var(--text-secondary);
            display: flex;
            justify-content: space-between;
        }}
        @media print {{
            body {{ background: white; color: black; }}
            .container {{ box-shadow: none; border: none; padding: 0; }}
            h1, h2, h3, strong, p, li {{ color: black; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <span class="badge">CrewAI Research Report</span>
            <h1>Research Report: {topic}</h1>
            <p style="color: var(--text-secondary); margin: 0;">Generated on {now_readable}</p>
        </div>
        <div class="content">
            {body_html}
        </div>
        <div class="footer">
            <span>Powered by CrewAI &amp; Multi-Agent Orchestration</span>
            <span>File: {md_filename}</span>
        </div>
    </div>
</body>
</html>"""

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(full_html)

    # 3. Export PDF
    pdf_filename = f"report_{timestamp}_{slug}.pdf"
    pdf_path = os.path.join(output_dir, pdf_filename)
    latest_pdf_path = os.path.join(output_dir, "latest_report.pdf")
    try:
        from researcher.tools.pdf_export import export_markdown_to_pdf
        export_markdown_to_pdf(markdown_content, topic=topic, output_path=pdf_path)
        # Also copy/save as latest_report.pdf
        if os.path.exists(pdf_path):
            import shutil
            shutil.copy2(pdf_path, latest_pdf_path)
    except Exception as e:
        print(f"[Warning] PDF generation skipped/failed: {e}")
        pdf_path = None
        latest_pdf_path = None

    # 4. Generate Audio Briefing
    audio_filename = f"report_{timestamp}_{slug}.mp3"
    audio_path = os.path.join(output_dir, audio_filename)
    latest_audio_path = os.path.join(output_dir, "latest_report.mp3")
    try:
        from researcher.tools.audio_brief import generate_audio_brief
        res_audio = generate_audio_brief(markdown_content, topic=topic, output_path=audio_path)
        if res_audio and os.path.exists(res_audio):
            import shutil
            shutil.copy2(res_audio, latest_audio_path)
        else:
            audio_path = None
            latest_audio_path = None
    except Exception as e:
        print(f"[Warning] Audio generation skipped/failed: {e}")
        audio_path = None
        latest_audio_path = None

    return {
        "markdown_file": md_path,
        "latest_markdown": latest_path,
        "html_file": html_path,
        "pdf_file": pdf_path,
        "latest_pdf": latest_pdf_path,
        "audio_file": audio_path,
        "latest_audio": latest_audio_path,
    }

