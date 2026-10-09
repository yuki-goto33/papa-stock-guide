#!/usr/bin/env python3
"""papa-stock-guide の構造チェック。仕様逸脱があれば exit 1。"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = ["index.html", "stage-c.html", "stage-b.html", "stage-a.html",
         "advanced.html", "glossary.html"]
STAGE_PAGES = ["stage-c.html", "stage-b.html", "stage-a.html"]
DISCLAIMER_PAGES = ["stage-b.html", "stage-a.html", "advanced.html"]
errors = []


class Collector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.hrefs, self.classes = set(), [], []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if "id" in d:
            self.ids.add(d["id"])
        if tag in ("a", "link") and d.get("href"):
            self.hrefs.append(d["href"])
        if tag == "script" and d.get("src"):
            self.hrefs.append(d["src"])
        if "class" in d:
            self.classes.extend(d["class"].split())


docs = {}
for page in PAGES:
    path = ROOT / page
    if not path.exists():
        errors.append(f"{page}: ファイルがない")
        continue
    text = path.read_text(encoding="utf-8")
    c = Collector()
    c.feed(text)
    docs[page] = (text, c)

for page, (text, c) in docs.items():
    if '<html lang="ja">' not in text:
        errors.append(f'{page}: <html lang="ja"> がない')
    if "viewport" not in text:
        errors.append(f"{page}: viewport meta がない")
    if 'href="style.css"' not in text:
        errors.append(f"{page}: style.css を読み込んでいない")
    # 内部リンク切れ
    for href in c.hrefs:
        if href.startswith(("http://", "https://", "mailto:")):
            continue
        target, _, frag = href.partition("#")
        if target and not (ROOT / target).exists():
            errors.append(f"{page}: リンク切れ {href}")
        elif frag:
            ref = docs.get(target or page)
            if ref and frag not in ref[1].ids:
                errors.append(f"{page}: アンカー切れ {href}")

for page in STAGE_PAGES:
    if page not in docs:
        continue
    text, c = docs[page]
    for cls in ["progress-bar", "goal-card", "steps", "check-box", "qa", "screen-mock"]:
        if cls not in c.classes:
            errors.append(f"{page}: .{cls} がない")
    if 'data-save="' not in text:
        errors.append(f"{page}: 保存つきチェックリストがない")

for page in DISCLAIMER_PAGES:
    if page in docs and "投資判断はご自身の責任で" not in docs[page][0]:
        errors.append(f"{page}: 免責文がない")

for page, (text, _) in docs.items():
    if re.search(r'(src|href)="https?://(?!github\.com|claude\.ai|docs\.github\.com)', text):
        errors.append(f"{page}: 外部リソース読み込みの疑い")

if errors:
    print("NG:")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print(f"PASS: {len(docs)} ページ検証 OK")
