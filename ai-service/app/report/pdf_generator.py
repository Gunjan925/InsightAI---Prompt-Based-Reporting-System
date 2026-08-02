# Generates PDF reports in memory and returns the bytes.
import io
import re
import logging
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from app.exceptions.custom_exception import ReportGenerationError

logger = logging.getLogger("ai_service")

def generate_report_pdf(title: str, stats: dict, text_content: str) -> bytes:
    """
    Generates a structured PDF document binary in memory using ReportLab.
    Strips complex HTML elements to ensure compatibility with ReportLab XML parser.
    """
    try:
        buffer = io.BytesIO() # creates empty file on disk
        # Define document dimensions and margins
        doc = SimpleDocTemplate( # Creates the PDF document.
            buffer,
            pagesize=letter,
            rightMargin=45,
            leftMargin=45,
            topMargin=45,
            bottomMargin=45
        )
        
        story = [] # ReportLab builds PDFs using a list called Story Everything added to Story appears in PDF.
        styles = getSampleStyleSheet() # Loads default styles.

        # Premium Styles definition
        title_style = ParagraphStyle(
            name='PdfTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=20,
            leading=24,
            textColor=colors.HexColor('#312e81'),  # Indigo 900
            spaceAfter=15
        )
        
        section_style = ParagraphStyle(
            name='PdfSection',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=13,
            leading=16,
            textColor=colors.HexColor('#4338ca'),  # Indigo 700
            spaceBefore=15,
            spaceAfter=8,
            keepWithNext=True
        )

        body_style = ParagraphStyle(
            name='PdfBody',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=13.5,
            textColor=colors.HexColor('#334155'),  # Slate 700
            spaceAfter=6
        )

        # 1. Title Banner
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 10))

        # 2. Metadata / Profile Summary Table
        story.append(Paragraph("Dataset Overview", section_style))
        shape = stats.get("shape", [0, 0])
        meta_rows = [
            [Paragraph("<b>Total Row Count</b>", body_style), Paragraph(str(shape[0]), body_style)],
            [Paragraph("<b>Total Column Count</b>", body_style), Paragraph(str(shape[1]), body_style)],
            [Paragraph("<b>Numerical Features</b>", body_style), Paragraph(", ".join(stats.get("numerical_columns", [])), body_style)],
            [Paragraph("<b>Categorical Features</b>", body_style), Paragraph(", ".join(stats.get("categorical_columns", [])), body_style)]
        ]
        
        # Table columns widths
        profile_table = Table(meta_rows, colWidths=[140, 380])
        profile_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f8fafc')),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#1e293b')),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(profile_table)
        story.append(Spacer(1, 15))

        # 3. AI Insights Content Ingest
        story.append(Paragraph("Detailed Analytical Findings", section_style))
        
        # Clean HTML markup to comply with ReportLab's basic inline tag rules (<b>, <i>, <u>)
        cleaned_text = text_content
        # Remove paragraphs wrapping classes
        cleaned_text = re.sub(r'<p[^>]*>', '', cleaned_text)
        cleaned_text = cleaned_text.replace("</p>", "\n\n")
        # Replace list structures
        cleaned_text = re.sub(r'<ul[^>]*>', '', cleaned_text)
        cleaned_text = cleaned_text.replace("</ul>", "\n")
        cleaned_text = re.sub(r'<li[^>]*>', '  * ', cleaned_text)
        cleaned_text = cleaned_text.replace("</li>", "\n")
        # Standardize headers to bold
        cleaned_text = re.sub(r'<h[1234][^>]*>', '\n<b>', cleaned_text)
        cleaned_text = re.sub(r'</h[1234]>', '</b>\n', cleaned_text)
        # Bold and italics
        cleaned_text = cleaned_text.replace("<strong>", "<b>").replace("</strong>", "</b>")
        cleaned_text = cleaned_text.replace("<em>", "<i>").replace("</em>", "</i>")
        # Strip complex table strings from layout (PDF covers only high-level profile tables)
        cleaned_text = re.sub(r'<div class="my-6 overflow-hidden.*?>.*?</table>.*?</div>', '\n[Tabular statistics data presented in dashboard HTML]\n', cleaned_text, flags=re.DOTALL)
        cleaned_text = re.sub(r'<table[^>]*>.*?</table>', '\n[Tabular data presented in dashboard HTML]\n', cleaned_text, flags=re.DOTALL)

        # Break text content down and write line paragraphs
        for paragraph_block in cleaned_text.split("\n\n"):
            cleaned_block = paragraph_block.strip()
            if not cleaned_block:
                continue
            try:
                story.append(Paragraph(cleaned_block, body_style))
                story.append(Spacer(1, 4))
            except Exception:
                # If XML parser fails due to stray characters, load as raw string escaping HTML tags
                safe_block = re.sub(r'<[^>]*>', '', cleaned_block)
                story.append(Paragraph(safe_block, body_style))
                story.append(Spacer(1, 4))

        # Render PDF
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        logger.info("PDF document binary compiled successfully.")
        return pdf_bytes
    except Exception as e:
        logger.error(f"Failed to generate PDF byte-stream: {e}")
        raise ReportGenerationError(f"PDF compilation failed: {str(e)}")