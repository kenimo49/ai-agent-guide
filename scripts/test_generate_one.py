#!/usr/bin/env python3
"""1記事だけ生成してテスト"""
import os, re, json, datetime, anthropic
from pathlib import Path

CONTENT_DIR = Path(__file__).parent.parent / "content" / "articles"
MODEL = "claude-sonnet-4-5"

AI_SLOP_PATTERNS = [
    r"近年、.+が注目されています",
    r"この記事では.+を解説します",
    r"いかがでしたか",
    r"それでは早速見ていきましょう",
]

def quality_check(content, title, keyword, meta_desc):
    checks = {
        "word_count": len(content) >= 3000,
        "keyword_in_title": any(k in title for k in keyword.split()[:2]),
        "meta_desc_length": 80 <= len(meta_desc) <= 160,
        "no_ai_slop": sum(1 for p in AI_SLOP_PATTERNS if re.search(p, content)) / max(len(content.split("。")), 1) < 0.05,
        "has_code": "```" in content,
    }
    return all(checks.values()), checks

api_key = os.environ.get("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=api_key)

keyword = "Claude Code AGENTS.md 書き方"
cluster = "claude-code"

print(f"⏳ 生成中: {keyword}")

response = client.messages.create(
    model=MODEL,
    max_tokens=8000,
    messages=[{"role": "user", "content": f"""あなたは技術ブログのライターです。以下のキーワードで、AIエージェント実装に興味のあるエンジニア向けの記事を書いてください。

キーワード: {keyword}

以下のJSONを返してください:
{{"title": "タイトル（32文字以内）", "description": "メタディスクリプション（120文字以内）", "tags": ["タグ1","タグ2","タグ3"], "content": "記事本文（Markdown、3000文字以上、H2見出し4-6個、コードブロック必須）"}}

ルール: ですます調、禁止「いかがでしたか」「この記事では〜を解説します」「近年、〜が注目されています」
JSON以外のテキストは出力しないでください。"""}]
)

text = response.content[0].text.strip()
if "```json" in text:
    text = text.split("```json")[1].split("```")[0].strip()
elif "```" in text:
    text = text.split("```")[1].split("```")[0].strip()

data = json.loads(text)
passed, checks = quality_check(data["content"], data["title"], keyword, data["description"])
failed = [k for k, v in checks.items() if not v]

print(f"✅ タイトル: {data['title']}")
print(f"📏 文字数: {len(data['content'])}")
print(f"🔍 品質チェック: {'PASS' if passed else 'FAIL ' + str(failed)}")

if passed:
    today = datetime.date.today().isoformat()
    slug = re.sub(r"[^\w\-]", "-", keyword.lower().replace(" ", "-"))
    slug = re.sub(r"-+", "-", slug).strip("-")[:60]
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    filename = CONTENT_DIR / f"{slug}.md"
    filename.write_text(f"""---
title: "{data['title']}"
description: "{data['description']}"
publishedAt: "{today}"
updatedAt: "{today}"
keyword: "{keyword}"
cluster: "{cluster}"
tags: {json.dumps(data.get('tags', []), ensure_ascii=False)}
isPillar: false
---

{data['content']}
""", encoding="utf-8")
    print(f"💾 保存: content/articles/{slug}.md")
