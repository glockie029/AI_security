
from html import escape
from pathlib import Path

# 预设的不可信模型输出（模拟）
payload = (
    '<img src="missing-image.png" '
    'onerror="document.getElementById(\'status\')'
    '.textContent=\'XSS_EXECUTED\'">'
)

template = """
<!doctype html>
<meta charset="utf-8">
<p id="status">NOT_EXECUTED</p>
<div>{content}</div>
"""

out_dir = Path(__file__).parent

for name, content in [
    ("unsafe", payload),
    ("safe", escape(payload)),
]:
    file = out_dir / f"html_{name}.html"
    file.write_text(
        template.format(content=content),
        encoding="utf-8",
    )
    print(file)
