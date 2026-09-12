import os
import sys
import subprocess
import markdown
from pygments.formatters import HtmlFormatter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_MD_PATH = os.path.join(BASE_DIR, 'docs', 'PROJECT_REPORT.md')
REPORT_HTML_PATH = os.path.join(BASE_DIR, 'docs', 'report_render.html')
OUTPUT_PDF_PATH_ROOT = os.path.join(BASE_DIR, 'LEX_REGIS_PROJECT_REPORT.pdf')
OUTPUT_PDF_PATH_DOCS = os.path.join(BASE_DIR, 'docs', 'LEX_REGIS_PROJECT_REPORT.pdf')

def build_pdf():
    print(f"Reading Markdown from: {REPORT_MD_PATH}")
    with open(REPORT_MD_PATH, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # Convert markdown to html
    extensions = [
        'extra',
        'tables',
        'fenced_code',
        'codehilite',
        'toc',
        'sane_lists',
        'nl2br'
    ]
    extension_configs = {
        'codehilite': {
            'guess_lang': False,
            'css_class': 'highlight',
            'noclasses': False
        }
    }
    
    html_body = markdown.markdown(md_text, extensions=extensions, extension_configs=extension_configs)
    pygments_css = HtmlFormatter(style='friendly').get_style_defs('.highlight')

    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>LEX REGIS - Enterprise LegalTech Project Report</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Playfair+Display:ital,wght@0,600;0,700;1,400&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>
  mermaid.initialize({{
    startOnLoad: true,
    theme: 'default',
    themeVariables: {{
      primaryColor: '#0f172a',
      primaryTextColor: '#ffffff',
      primaryBorderColor: '#c5a880',
      lineColor: '#0f172a',
      secondaryColor: '#f8fafc',
      tertiaryColor: '#f1f5f9'
    }}
  }});
</script>
<style>
  @page {{
    size: A4 portrait;
    margin: 18mm 16mm 20mm 16mm;
    @bottom-center {{
      content: "Page " counter(page) " of " counter(pages);
      font-family: 'Inter', sans-serif;
      font-size: 8.5pt;
      color: #64748b;
    }}
    @top-right {{
      content: "LEX REGIS | Project Report";
      font-family: 'Inter', sans-serif;
      font-size: 8pt;
      color: #94a3b8;
      text-transform: uppercase;
      letter-spacing: 1px;
    }}
  }}

  * {{
    box-sizing: border-box;
  }}

  body {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    color: #1e293b;
    line-height: 1.65;
    font-size: 10pt;
    margin: 0;
    padding: 0;
    background-color: #ffffff;
  }}

  /* Headings */
  h1, h2, h3, h4, h5, h6 {{
    color: #0f172a;
    font-family: 'Playfair Display', Georgia, serif;
    font-weight: 700;
    margin-top: 1.6em;
    margin-bottom: 0.6em;
    line-height: 1.25;
    page-break-after: avoid;
  }}

  h1 {{
    font-size: 20pt;
    border-bottom: 2.5px solid #c5a880;
    padding-bottom: 6px;
    margin-top: 2em;
    color: #0f172a;
  }}

  h2 {{
    font-size: 15pt;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 4px;
    margin-top: 1.8em;
    color: #1e293b;
  }}

  h3 {{
    font-size: 12pt;
    color: #334155;
  }}

  h4 {{
    font-size: 10.5pt;
    color: #475569;
  }}

  p, ul, ol {{
    margin-top: 0;
    margin-bottom: 0.9em;
    text-align: justify;
  }}

  li {{
    margin-bottom: 0.35em;
  }}

  strong {{
    color: #0f172a;
  }}

  a {{
    color: #1d4ed8;
    text-decoration: none;
  }}

  /* Cover Page Styling */
  .cover-page {{
    min-height: 90vh;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    align-items: center;
    text-align: center;
    border: 3px double #c5a880;
    padding: 40px 30px;
    margin-bottom: 40px;
    background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
    page-break-after: always;
  }}

  .cover-badge {{
    font-family: 'Inter', sans-serif;
    font-size: 9pt;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
    background-color: #0f172a;
    color: #c5a880;
    padding: 6px 18px;
    border-radius: 20px;
    display: inline-block;
    margin-bottom: 25px;
  }}

  .cover-title {{
    font-family: 'Cinzel', 'Playfair Display', Georgia, serif;
    font-size: 28pt;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: 1.5px;
    margin: 10px 0;
    line-height: 1.15;
  }}

  .cover-subtitle {{
    font-family: 'Playfair Display', serif;
    font-size: 13pt;
    color: #64748b;
    font-style: italic;
    max-width: 650px;
    margin: 15px auto 35px auto;
  }}

  .cover-divider {{
    width: 120px;
    height: 3px;
    background-color: #c5a880;
    margin: 20px auto;
  }}

  .cover-meta-grid {{
    width: 100%;
    max-width: 600px;
    margin: 30px auto;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 15px;
    text-align: left;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 18px 24px;
    font-size: 9pt;
  }}

  .cover-meta-item strong {{
    display: block;
    color: #475569;
    font-size: 7.5pt;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 2px;
  }}

  .cover-meta-item span {{
    font-weight: 600;
    color: #0f172a;
  }}

  .cover-footer {{
    font-size: 8.5pt;
    color: #64748b;
    margin-top: 30px;
  }}

  /* Tables */
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 1.4em 0;
    font-size: 8.5pt;
    page-break-inside: avoid;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  }}

  th, td {{
    padding: 8px 10px;
    border: 1px solid #cbd5e1;
    text-align: left;
    vertical-align: top;
  }}

  th {{
    background-color: #0f172a;
    color: #ffffff;
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    font-size: 8.5pt;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }}

  tr:nth-child(even) {{
    background-color: #f8fafc;
  }}

  /* Code Blocks */
  pre, code {{
    font-family: 'JetBrains Mono', Consolas, Monaco, monospace;
  }}

  code {{
    background-color: #f1f5f9;
    color: #0f172a;
    padding: 1.5px 4px;
    border-radius: 3px;
    font-size: 8.5pt;
    border: 1px solid #e2e8f0;
  }}

  pre {{
    background-color: #0f172a;
    color: #f8fafc;
    padding: 12px 16px;
    border-radius: 6px;
    overflow-x: auto;
    font-size: 8pt;
    line-height: 1.45;
    margin: 1.2em 0;
    page-break-inside: avoid;
    border-left: 4px solid #c5a880;
  }}

  pre code {{
    background-color: transparent;
    color: inherit;
    padding: 0;
    border: none;
    font-size: inherit;
  }}

  {pygments_css}

  /* Blockquotes & Callouts */
  blockquote {{
    margin: 1.4em 0;
    padding: 10px 18px;
    background-color: #f8fafc;
    border-left: 4px solid #c5a880;
    font-style: italic;
    color: #334155;
    page-break-inside: avoid;
    border-radius: 0 6px 6px 0;
  }}

  /* Mermaid Diagrams */
  .mermaid {{
    text-align: center;
    margin: 25px 0;
    page-break-inside: avoid;
    background: #ffffff;
    padding: 15px;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
  }}

  /* Chapter Breaks */
  h1 {{
    page-break-before: always;
  }}
  h1:first-of-type {{
    page-break-before: avoid;
  }}

  /* Print Media Specifics */
  @media print {{
    body {{
      background: none;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }}
    .no-print {{
      display: none;
    }}
  }}
</style>
</head>
<body>

<div class="cover-page">
  <div>
    <div class="cover-badge">Enterprise Legal Technology Architecture</div>
    <div class="cover-title">LEX REGIS</div>
    <div class="cover-subtitle">Enterprise-Grade AI-Powered Legal Practice Management, Judicial Intelligence & Citizen Access Platform</div>
    <div class="cover-divider"></div>
  </div>

  <div class="cover-meta-grid">
    <div class="cover-meta-item">
      <strong>System Architecture</strong>
      <span>Modular Monolith & Layered Domain</span>
    </div>
    <div class="cover-meta-item">
      <strong>Core Technology Stack</strong>
      <span>Python 3.13 / Django 5.x / Daphne ASGI</span>
    </div>
    <div class="cover-meta-item">
      <strong>Artificial Intelligence</strong>
      <span>Groq Cloud LLM (openai/gpt-oss-120b)</span>
    </div>
    <div class="cover-meta-item">
      <strong>Real-Time Subsystem</strong>
      <span>Django Channels / Redis WebSockets</span>
    </div>
    <div class="cover-meta-item">
      <strong>Integrity & Cryptography</strong>
      <span>SHA-256 Checksums / Blockchain Receipts</span>
    </div>
    <div class="cover-meta-item">
      <strong>Jurisdiction Engine</strong>
      <span>Indian Legal Framework & Global RBAC</span>
    </div>
  </div>

  <div class="cover-footer">
    <p><strong>Document Classification:</strong> Complete Software Engineering Project Report (Ready for Submission)</p>
    <p><strong>Date:</strong> August 2026 &nbsp;|&nbsp; <strong>Release Version:</strong> 1.0.0-PROD-READY &nbsp;|&nbsp; <strong>Status:</strong> Validated & Approved</p>
  </div>
</div>

<div class="content-container">
{html_body}
</div>

</body>
</html>
"""

    print(f"Writing rendered HTML to: {REPORT_HTML_PATH}")
    with open(REPORT_HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(html_template)

    # Locate Edge or Chrome
    browsers = [
        r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
        r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
        r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
    ]
    browser_bin = None
    for b in browsers:
        if os.path.exists(b):
            browser_bin = b
            break

    if not browser_bin:
        print("Error: No Edge or Chrome executable found.")
        sys.exit(1)

    print(f"Using browser binary: {browser_bin}")
    cmd = [
        browser_bin,
        '--headless',
        '--disable-gpu',
        '--allow-file-access-from-files',
        '--run-all-compositor-stages-before-draw',
        '--virtual-time-budget=5000',
        '--no-pdf-header-footer',
        f'--print-to-pdf={OUTPUT_PDF_PATH_ROOT}',
        f'file:///{REPORT_HTML_PATH.replace(os.sep, "/")}'
    ]

    print("Running headless PDF compilation...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and os.path.exists(OUTPUT_PDF_PATH_ROOT):
        file_size = os.path.getsize(OUTPUT_PDF_PATH_ROOT)
        print(f"PDF successfully generated at: {OUTPUT_PDF_PATH_ROOT} ({file_size / 1024:.2f} KB)")
        
        # Copy to docs/ as well
        import shutil
        shutil.copy2(OUTPUT_PDF_PATH_ROOT, OUTPUT_PDF_PATH_DOCS)
        print(f"Copy placed in docs/ at: {OUTPUT_PDF_PATH_DOCS}")
    else:
        print(f"Error compiling PDF: {res.stderr}")
        sys.exit(1)

if __name__ == '__main__':
    build_pdf()
