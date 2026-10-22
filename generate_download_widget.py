import base64
import os

pdf_path = r"C:\Users\Admin\.gemini\antigravity\scratch\smart-city-traffic-analytics\Smart_City_Traffic_Analytics_Report.pdf"
out_html = r"C:\Users\Admin\.gemini\antigravity\brain\31f81685-557a-469d-9f4a-f3c7e5467b7f\download_report.html"

with open(pdf_path, "rb") as f:
    pdf_bytes = f.read()

b64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")

html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
</head>
<body class="bg-transparent text-[var(--foreground)] antialiased p-3">
  <div class="bg-[var(--card)] text-[var(--foreground)] border border-[var(--border)] rounded-2xl p-5 shadow-lg max-w-xl mx-auto">
    <div class="flex items-start justify-between gap-4">
      <div class="flex items-center gap-3">
        <div class="w-12 h-12 rounded-xl bg-red-500/10 border border-red-500/30 flex items-center justify-center text-red-500 font-bold text-xl shadow-inner">
          PDF
        </div>
        <div>
          <h2 class="text-[var(--foreground)] font-bold text-base tracking-tight">Smart_City_Traffic_Analytics_Report.pdf</h2>
          <p class="text-[var(--muted-foreground)] text-xs mt-0.5">VTU Mini-Project Report • 24 Pages • 2.08 MB • Official Standard Format</p>
        </div>
      </div>
      <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-600 border border-emerald-500/20">
        Ready
      </span>
    </div>

    <div class="mt-4 grid grid-cols-3 gap-2 py-3 px-3.5 bg-[var(--background)]/60 rounded-xl border border-[var(--border)] text-xs">
      <div>
        <span class="text-[var(--muted-foreground)] block">Author:</span>
        <span class="font-medium text-[var(--foreground)]">Shreya G Poojari</span>
      </div>
      <div>
        <span class="text-[var(--muted-foreground)] block">USN:</span>
        <span class="font-medium text-[var(--foreground)]">1VI23IS100</span>
      </div>
      <div>
        <span class="text-[var(--muted-foreground)] block">Institution:</span>
        <span class="font-medium text-[var(--foreground)]">Vemana IT, Bengaluru</span>
      </div>
    </div>

    <div class="mt-4 flex items-center gap-3">
      <button id="dlBtn" onclick="downloadReport()" class="flex-1 bg-blue-600 hover:bg-blue-700 active:scale-[0.98] transition-all text-white font-medium text-sm py-2.5 px-4 rounded-xl shadow-md flex items-center justify-center gap-2 cursor-pointer">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
        </svg>
        Download PDF Now
      </button>
      <a href="file:///{pdf_path.replace(os.sep, '/')}" target="_blank" class="px-3.5 py-2.5 rounded-xl border border-[var(--border)] hover:bg-[var(--accent)] text-xs font-medium text-[var(--muted-foreground)] hover:text-[var(--foreground)] transition-colors">
        Open File
      </a>
    </div>
  </div>

  <script>
    const b64Data = '{b64_pdf}';
    function downloadReport() {{
      const btn = document.getElementById('dlBtn');
      btn.innerHTML = 'Downloading...';
      try {{
        const byteCharacters = atob(b64Data);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {{
          byteNumbers[i] = byteCharacters.charCodeAt(i);
        }}
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], {{ type: 'application/pdf' }});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'Smart_City_Traffic_Analytics_Report.pdf';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        setTimeout(() => {{
          btn.innerHTML = '✓ Download Complete';
          setTimeout(() => {{
            btn.innerHTML = 'Download PDF Again';
          }}, 2500);
        }}, 500);
      }} catch (err) {{
        console.error(err);
        btn.innerHTML = 'Error - Open Directly';
      }}
    }}
  </script>
</body>
</html>"""

os.makedirs(os.path.dirname(out_html), exist_ok=True)
with open(out_html, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Generated HTML download widget: {out_html} ({round(os.path.getsize(out_html)/1024, 1)} KB)")
