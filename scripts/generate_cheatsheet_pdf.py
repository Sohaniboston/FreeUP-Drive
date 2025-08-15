from pathlib import Path
from fpdf import FPDF
import textwrap

INPUT_MD = Path('docs/GOOGLE_DRIVE_API_CHEATSHEET.md')
OUTPUT_PDF = Path('docs/GOOGLE_DRIVE_API_CHEATSHEET.pdf')

# Very lightweight markdown-to-PDF (headings bold, code blocks monospaced)

def wrap_text(text, width, font_size):
    # crude width compensation (FPDF measures in points; assume ~0.5 char factor)
    wrapper = textwrap.TextWrapper(width=width)
    return wrapper.wrap(text)

pdf = FPDF(format='Letter')
pdf.set_auto_page_break(auto=True, margin=15)

with open(INPUT_MD, 'r', encoding='utf-8') as f:
    lines = f.readlines()

in_code = False
code_buffer = []

for line in lines:
    stripped = line.rstrip('\n')
    if stripped.startswith('```'):
        if not in_code:
            in_code = True
            code_buffer = []
        else:
            # flush code
            pdf.set_font('Courier', size=8)
            pdf.set_fill_color(245,245,245)
            for c in code_buffer:
                pdf.cell(0,5,c,ln=1)
            in_code = False
        continue
    if in_code:
        code_buffer.append(stripped)
        continue
    if stripped.startswith('#'):
        level = len(stripped) - len(stripped.lstrip('#'))
        text = stripped.lstrip('#').strip()
        pdf.set_font('Helvetica','B', 14 if level==1 else 11)
        pdf.add_page() if level==1 else None
        pdf.cell(0,8,text,ln=1)
    elif stripped.startswith('|') and '---' in stripped:
        # separator row skip
        continue
    elif stripped.startswith('|'):
        # simple table row -> split
        cols = [c.strip() for c in stripped.strip('|').split('|')]
        pdf.set_font('Helvetica','',8)
        row_text = ' | '.join(cols)
        pdf.multi_cell(0,5,row_text)
    elif stripped.startswith('- ') or stripped.startswith('* '):
        pdf.set_font('Helvetica','',9)
        bullet = '\u2022 '
        content = stripped[2:].strip()
        for w in wrap_text(content, 120, 9):
            pdf.cell(0,5, bullet + w, ln=1)
            bullet = '  '
    elif stripped == '':
        pdf.ln(4)
    else:
        pdf.set_font('Helvetica','',9)
        for w in wrap_text(stripped, 125, 9):
            pdf.multi_cell(0,5,w)

pdf.output(str(OUTPUT_PDF))
print(f"Generated {OUTPUT_PDF}")
