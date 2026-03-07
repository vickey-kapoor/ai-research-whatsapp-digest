"""Generate grandma-friendly PDF reports for AI research."""

import os
import re
from datetime import datetime
from pathlib import Path

from fpdf import FPDF


def _sanitize_text_for_pdf(text: str) -> str:
    """
    Sanitize text for PDF output.

    Removes or replaces characters that might cause issues.
    """
    if not text:
        return ""

    # Replace common problematic characters
    replacements = {
        '\u2018': "'",  # Left single quote
        '\u2019': "'",  # Right single quote
        '\u201c': '"',  # Left double quote
        '\u201d': '"',  # Right double quote
        '\u2013': '-',  # En dash
        '\u2014': '-',  # Em dash
        '\u2026': '...',  # Ellipsis
        '\u00a0': ' ',  # Non-breaking space
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    # Remove other non-ASCII characters that might cause issues
    text = text.encode('latin-1', errors='replace').decode('latin-1')

    return text


class ResearchPDF(FPDF):
    """Custom PDF class for research digests."""

    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        """Add header to each page."""
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(50, 50, 50)
        self.cell(0, 10, "Daily AI Research Digest", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "I", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, datetime.now().strftime("%A, %B %d, %Y"), align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

    def footer(self):
        """Add footer to each page."""
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def generate_research_pdf(research: dict, output_dir: str = "reports") -> str:
    """
    Generate a grandma-friendly PDF report for research.

    Args:
        research: Research dictionary with title, authors, description, summary, url, source
        output_dir: Base directory for saving reports

    Returns:
        Path to the generated PDF file
    """
    # Create date-formatted folder (e.g., "06-Mar")
    date_folder = datetime.now().strftime("%d-%b")
    full_output_dir = Path(output_dir) / date_folder
    full_output_dir.mkdir(parents=True, exist_ok=True)

    # Sanitize all text inputs
    title = _sanitize_text_for_pdf(research.get("title", "Today's AI Discovery"))
    authors = _sanitize_text_for_pdf(research.get("authors", "Unknown researchers"))
    source = _sanitize_text_for_pdf(research.get("source", "Unknown"))
    # Use detailed_summary for PDF if available, fallback to short summary
    summary = _sanitize_text_for_pdf(
        research.get("detailed_summary", "") or research.get("summary", "")
    )
    description = _sanitize_text_for_pdf(research.get("description", ""))
    url = research.get("url", "")

    # Create PDF
    pdf = ResearchPDF()
    pdf.add_page()

    # Title section
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(30, 60, 120)
    pdf.multi_cell(0, 12, title, align="C")
    pdf.ln(5)

    # Authors
    pdf.set_font("Helvetica", "I", 12)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 8, f"By: {authors}", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # Source badge
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, f"Source: {source}", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)

    # Divider line
    pdf.set_draw_color(200, 200, 200)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(10)

    # "What's This About?" section - the main detailed explanation
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(50, 100, 50)
    pdf.cell(0, 10, "What's This About? (In Simple Terms)", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    # Detailed explanation (ELI5 summary) - use readable font size
    if summary:
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(40, 40, 40)
        pdf.multi_cell(0, 6, summary)
        pdf.ln(10)

    # Divider line
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(10)

    # "The Technical Bit" section (optional - original abstract) - smaller, for reference
    if description:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 8, "Original Research Abstract (Technical)", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(100, 100, 100)
        pdf.multi_cell(0, 5, description)
        pdf.ln(10)

    # Link section
    if url:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(50, 50, 50)
        pdf.cell(0, 8, "Want to learn more?", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(0, 100, 200)
        pdf.cell(0, 6, url, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(10)

    # Friendly closing
    pdf.ln(5)
    pdf.set_font("Helvetica", "I", 11)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(0, 7, "This digest is created to help you stay informed about AI research in simple, everyday language. No technical background needed!")

    # Generate filename
    safe_title = "".join(c if c.isalnum() or c in " -_" else "" for c in title[:50])
    safe_title = safe_title.strip().replace(" ", "_")
    filename = f"{safe_title}.pdf"
    filepath = full_output_dir / filename

    # Save PDF
    pdf.output(str(filepath))

    return str(filepath)


def generate_multi_research_pdf(research_items: list[dict], output_dir: str = "reports") -> str:
    """
    Generate a PDF with multiple research items.

    Args:
        research_items: List of research dictionaries
        output_dir: Base directory for saving reports

    Returns:
        Path to the generated PDF file
    """
    if not research_items:
        return ""

    # Create date-formatted folder
    date_folder = datetime.now().strftime("%d-%b")
    full_output_dir = Path(output_dir) / date_folder
    full_output_dir.mkdir(parents=True, exist_ok=True)

    # Create PDF
    pdf = ResearchPDF()

    for i, research in enumerate(research_items):
        pdf.add_page()

        # Research number
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(150, 150, 150)
        pdf.cell(0, 8, f"Research #{i + 1} of {len(research_items)}", align="R", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

        # Title
        pdf.set_font("Helvetica", "B", 18)
        pdf.set_text_color(30, 60, 120)
        title = research.get("title", "Today's AI Discovery")
        pdf.multi_cell(0, 10, title, align="C")
        pdf.ln(5)

        # Authors and source
        authors = research.get("authors", "Unknown researchers")
        source = research.get("source", "Unknown")
        pdf.set_font("Helvetica", "I", 11)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(0, 7, f"By: {authors}", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 6, f"Source: {source}", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(10)

        # Simple explanation
        summary = research.get("summary", "")
        if summary:
            pdf.set_font("Helvetica", "B", 13)
            pdf.set_text_color(50, 100, 50)
            pdf.cell(0, 10, "In Simple Terms:", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)

            pdf.set_font("Helvetica", "", 12)
            pdf.set_text_color(40, 40, 40)
            pdf.multi_cell(0, 7, summary)
            pdf.ln(8)

        # Link
        url = research.get("url", "")
        if url:
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(0, 100, 200)
            pdf.cell(0, 6, f"Read more: {url}", new_x="LMARGIN", new_y="NEXT")

    # Generate filename
    filename = f"AI_Research_Digest_{datetime.now().strftime('%Y%m%d')}.pdf"
    filepath = full_output_dir / filename

    # Save PDF
    pdf.output(str(filepath))

    return str(filepath)
