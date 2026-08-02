# Parses and structures Gemini responses into usable sections.
import re

def markdown_to_html(md_text: str) -> str:
    """
    Converts standard Markdown syntax into beautiful semantic HTML.
    Handles:
    - Code Blocks
    - Markdown Tables (rendered as responsive tables)
    - Headers (H1, H2, H3)
    - Formatting (Bold, Italic)
    - Bullet Points & Lists
    - Paragraph spacing
    """
    html_text = md_text

    # 1. Handle Code Blocks
    html_text = re.sub(r'```html(.*?)```', r'<div>\1</div>', html_text, flags=re.DOTALL)
    html_text = re.sub(r'```json(.*?)```', r'<pre class="bg-gray-50 p-4 rounded overflow-auto my-4 text-sm font-mono border border-gray-200 text-gray-800"><code>\1</code></pre>', html_text, flags=re.DOTALL)
    html_text = re.sub(r'```(.*?)\n(.*?)```', r'<pre class="bg-gray-50 p-4 rounded overflow-auto my-4 text-sm font-mono border border-gray-200 text-gray-800"><code>\2</code></pre>', html_text, flags=re.DOTALL)

    # 2. Convert Markdown Tables to Beautiful Styled HTML Tables
    def parse_markdown_table(match) -> str:
        table_lines = match.group(1).strip().split("\n")
        if len(table_lines) < 2:
            return match.group(1)
            
        # Parse headers
        headers = [c.strip() for c in table_lines[0].split("|")[1:-1]]
        headers_html = "".join(f"<th class='px-4 py-3 bg-indigo-50/50 text-indigo-950 font-bold border-b border-indigo-100 text-left text-xs uppercase tracking-wider'>{h}</th>" for h in headers)
        
        # Parse rows (skip separators index 1)
        rows_html = []
        for line in table_lines[2:]:
            cells = [c.strip() for c in line.split("|")[1:-1]]
            cells_html = "".join(f"<td class='px-4 py-3 border-b border-gray-100 text-sm text-gray-700'>{c}</td>" for c in cells)
            rows_html.append(f"<tr class='hover:bg-slate-50/50 transition-colors'>{cells_html}</tr>")
            
        return f"""
        <div class="my-6 overflow-hidden border border-gray-200/80 rounded-xl shadow-sm bg-white">
            <table class="min-w-full divide-y divide-gray-100">
                <thead>
                    <tr>{headers_html}</tr>
                </thead>
                <tbody class="divide-y divide-gray-100 bg-white">
                    {"".join(rows_html)}
                </tbody>
            </table>
        </div>
        """

    # Look for tabular formatted blocks starting with pipelines
    html_text = re.sub(r'((?:\|[^\n]+\|\r?\n){2,}(?:\|[^\n]+\|?))', parse_markdown_table, html_text)

    # 3. Headers Translation
    html_text = re.sub(r'^#\s+(.*?)$', r'<h1 class="text-3xl font-extrabold text-indigo-950 tracking-tight mt-8 mb-4 pb-2 border-b border-indigo-100/60">\1</h1>', html_text, flags=re.MULTILINE)
    html_text = re.sub(r'^##\s+(.*?)$', r'<h2 class="text-2xl font-bold text-indigo-900 tracking-tight mt-7 mb-3 pb-1 border-b border-indigo-50/80">\1</h2>', html_text, flags=re.MULTILINE)
    html_text = re.sub(r'^###\s+(.*?)$', r'<h3 class="text-xl font-semibold text-gray-800 mt-5 mb-2">\1</h3>', html_text, flags=re.MULTILINE)

    # 4. Bold and Italic Translation
    html_text = re.sub(r'\*\*(.*?)\*\*', r'<strong class="font-bold text-indigo-950/90">\1</strong>', html_text)
    html_text = re.sub(r'\*(.*?)\*', r'<em class="italic text-gray-600">\1</em>', html_text)

    # 5. Lists Conversion
    def parse_lists(match) -> str:
        items = match.group(1).strip().split("\n")
        li_items = []
        for it in items:
            cleaned_val = re.sub(r'^[\-\*\+]\s+', '', it).strip()
            li_items.append(f"<li class='text-gray-700 leading-relaxed text-sm py-1'>{cleaned_val}</li>")
        return f"<ul class='my-4 space-y-1 list-disc pl-5 text-gray-600'>{''.join(li_items)}</ul>"

    html_text = re.sub(r'((?:^[\-\*\+]\s+[^\n]+\r?\n?)+)', parse_lists, html_text, flags=re.MULTILINE)

    # 6. Break down block groupings into paragraphs
    content_blocks = []
    for chunk in html_text.split("\n\n"):
        chunk = chunk.strip()
        if not chunk:
            continue
        # If block is already enclosed in HTML elements, keep as is
        if chunk.startswith("<h") or chunk.startswith("<ul") or chunk.startswith("<div") or chunk.startswith("<pre") or chunk.startswith("<table"):
            content_blocks.append(chunk)
        else:
            # Wrap as a clean text paragraph
            content_blocks.append(f"<p class='text-gray-700 leading-relaxed text-base mb-4'>{chunk}</p>")

    return "\n".join(content_blocks)

# This function extracts useful information from Gemini's response.
def parse_gemini_response(response_text: str) -> dict:
    """
    Parses Markdown response outputs from the Google Gemini model.
    Segments and filters Title and Executive Summary for metadata.
    Converts remaining content block markdown to beautiful standard HTML format.
    """
    report_title = "AI Intelligence Dataset Report"
    summary_excerpt = "Analytical study generated based on the dataset properties."

    # Extract clean Title (H1 header line)
    title_pattern = re.search(r'^#\s+(.*?)$', response_text, re.MULTILINE)
    if title_pattern:
        report_title = title_pattern.group(1).strip()
        # Remove the matched title line to avoid redundant header rendering in HTML
        response_text = response_text.replace(title_pattern.group(0), "", 1)

    # Extract primary paragraph from executive summary for database metadata
    exec_summary = re.search(r'## Executive Summary\s+(.*?)(?=\n##|$)', response_text, re.DOTALL)
    if exec_summary:
        raw_summary = exec_summary.group(1).strip()
        # Grab first paragraph block
        first_para = raw_summary.split("\n\n")[0].strip()
        # Remove markdown indicators (* or #)
        first_para = re.sub(r'[\*\#\_]', '', first_para)
        if len(first_para) > 15:
            summary_excerpt = first_para

    # Parse standard markdown into semantic, styled HTML
    html_content = markdown_to_html(response_text.strip())

    return {
        "report_title": report_title,
        "summary": summary_excerpt,
        "content": html_content
    }