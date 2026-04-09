#!/usr/bin/env python3
"""
render_email.py
---------------
papers.json（Claude Code が生成）と email_template.html から HTML メールを生成する。

Usage:
    python3 digest/render_email.py papers.json

papers.json の期待フォーマット:
{
  "date_slash": "2026/04/08",
  "papers": [
    {
      "title": "English title...",
      "pmid": "12345678",
      "authors": "Author A et al.",
      "journal": "Gastroenterology",
      "year": "2026",
      "design": "RCT",
      "background": "なぜこの研究が必要だったか...",
      "methods": "What they did...",
      "results": "Key Findings...",
      "limitations": "Limitations...",
      "so_what": "So What? 臨床へのインパクト...",
      "doi": "10.xxxx/yyyy"
    },
    ...  (3本)
  ],
  "overall_comment": "本日の総括コメント..."
}

出力: email_body.html（カレントディレクトリに生成）
"""

import json
import re
import sys
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 digest/render_email.py <papers.json>", file=sys.stderr)
        sys.exit(1)

    json_path = sys.argv[1]

    # --- papers.json を読み込み ---
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # --- テンプレートを読み込み（このスクリプトと同じフォルダの email_template.html）---
    script_dir = Path(__file__).resolve().parent
    template_path = script_dir / "email_template.html"

    if not template_path.exists():
        print(f"Error: {template_path} not found", file=sys.stderr)
        sys.exit(1)

    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()

    # --- プレースホルダー置換 ---
    html = html.replace("{{DATE_SLASH}}", data.get("date_slash", ""))

    papers = data.get("papers", [])
    for i, paper in enumerate(papers, start=1):
        n = str(i)
        html = html.replace(f"{{{{TITLE_{n}}}}}", paper.get("title", ""))
        html = html.replace(f"{{{{PMID_{n}}}}}", paper.get("pmid", ""))
        html = html.replace(f"{{{{AUTHORS_{n}}}}}", paper.get("authors", ""))
        html = html.replace(f"{{{{JOURNAL_{n}}}}}", paper.get("journal", ""))
        html = html.replace(f"{{{{YEAR_{n}}}}}", paper.get("year", ""))
        html = html.replace(f"{{{{DESIGN_{n}}}}}", paper.get("design", ""))
        html = html.replace(f"{{{{AIM_{n}}}}}", paper.get("background", ""))
        html = html.replace(f"{{{{METHODS_{n}}}}}", paper.get("methods", ""))
        html = html.replace(f"{{{{RESULTS_{n}}}}}", paper.get("results", ""))
        html = html.replace(f"{{{{CONCLUSION_{n}}}}}", paper.get("limitations", ""))
        html = html.replace(f"{{{{HIGHLIGHT_{n}}}}}", paper.get("so_what", ""))

    html = html.replace("{{OVERALL_COMMENT}}", data.get("overall_comment", ""))

    # --- 未置換プレースホルダーのチェック ---
    remaining = re.findall(r"\{\{[A-Z_0-9]+\}\}", html)
    if remaining:
        print(f"Warning: Unreplaced placeholders: {remaining}", file=sys.stderr)

    # --- email_body.html を出力（カレントディレクトリ）---
    output_path = "email_body.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Generated {output_path} ({len(html):,} bytes)")
    print(f"  Papers: {len(papers)}")
    print(f"  Unreplaced placeholders: {len(remaining)}")


if __name__ == "__main__":
    main()
