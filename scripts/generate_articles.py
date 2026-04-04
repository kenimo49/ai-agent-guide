#!/usr/bin/env python3
"""
記事生成エージェント
キーワードリストから記事を生成し、品質チェックを通過したものをcontent/articlesに保存する
"""
import os
import re
import json
import anthropic
import datetime
from pathlib import Path

# 設定
CONTENT_DIR = Path(__file__).parent.parent / "content" / "articles"
MEMORY_DIR = Path(__file__).parent.parent / "harness" / "memory"
ARTICLES_PER_DAY = 10
MODEL = "claude-sonnet-4-5"

# AI Slopパターン
AI_SLOP_PATTERNS = [
    r"近年、.+が注目されています",
    r"この記事では.+を解説します",
    r"皆さんは.+をご存知ですか",
    r"いかがでしたか",
    r"それでは早速見ていきましょう",
    r"〜と言っても過言ではありません",
    r"ぜひ参考にしてみてください",
    r"最後までお読みいただき",
    r"この記事が.+の参考になれば幸いです",
    r"さっそく見ていきましょう",
]


def load_keywords() -> list[dict]:
    """harness/memory/keywords.jsonからキーワードを読み込む"""
    kw_file = MEMORY_DIR / "keywords.json"
    if not kw_file.exists():
        return get_default_keywords()
    with open(kw_file) as f:
        return json.load(f)


def get_default_keywords() -> list[dict]:
    """デフォルトのキーワードリスト（初期起動時）"""
    return [
        {"keyword": "Claude Code AGENTS.md 書き方", "cluster": "claude-code", "intent": "informational"},
        {"keyword": "AIエージェント ハーネス 設計", "cluster": "harness", "intent": "informational"},
        {"keyword": "CLAUDE.md 使い方 実践", "cluster": "claude-code", "intent": "informational"},
        {"keyword": "LangChain エージェント 実装 入門", "cluster": "langchain", "intent": "informational"},
        {"keyword": "OpenAI Agents SDK 使い方", "cluster": "openai", "intent": "informational"},
        {"keyword": "Claude Code hooks 設定方法", "cluster": "claude-code", "intent": "informational"},
        {"keyword": "AIエージェント フィードバックループ 実装", "cluster": "harness", "intent": "informational"},
        {"keyword": "Context Engineering とは CLAUDE.md", "cluster": "context-eng", "intent": "informational"},
        {"keyword": "AIエージェント ツール呼び出し 実装", "cluster": "implementation", "intent": "informational"},
        {"keyword": "Anthropic Claude API Python 使い方", "cluster": "implementation", "intent": "informational"},
    ]


def get_published_titles() -> list[str]:
    """既存記事のタイトル一覧を取得（重複チェック用）"""
    titles = []
    for md_file in CONTENT_DIR.glob("*.md"):
        content = md_file.read_text()
        match = re.search(r'^title:\s*"(.+)"', content, re.MULTILINE)
        if match:
            titles.append(match.group(1))
    return titles


def quality_check(content: str, title: str, keyword: str, meta_desc: str) -> tuple[bool, dict]:
    """記事の品質チェック"""
    checks = {}

    # 文字数
    checks["word_count"] = len(content) >= 3000

    # キーワードがタイトルに含まれる
    kw_parts = keyword.split()[:2]  # 最初の2単語
    checks["keyword_in_title"] = any(k in title for k in kw_parts)

    # メタディスクリプション長
    checks["meta_desc_length"] = 80 <= len(meta_desc) <= 160

    # AI Slop検出
    sentences = content.split("。")
    slop_count = sum(1 for p in AI_SLOP_PATTERNS if re.search(p, content))
    slop_density = slop_count / max(len(sentences), 1)
    checks["no_ai_slop"] = slop_density < 0.05

    # コードブロック
    checks["has_code"] = "```" in content

    passed = all(checks.values())
    return passed, checks


def generate_article(keyword_data: dict, client: anthropic.Anthropic) -> dict | None:
    """1記事を生成"""
    keyword = keyword_data["keyword"]
    cluster = keyword_data["cluster"]

    prompt = f"""あなたは技術ブログのライターです。以下のキーワードで、AIエージェント実装に興味のあるエンジニア向けの記事を書いてください。

キーワード: {keyword}
クラスタ: {cluster}

以下のJSONを返してください:
{{
  "title": "記事タイトル（32文字以内、キーワードを含む）",
  "description": "メタディスクリプション（120文字以内）",
  "tags": ["タグ1", "タグ2", "タグ3"],
  "content": "記事本文（Markdown形式、3000文字以上）"
}}

記事のルール:
- ですます調
- 1文60文字以内
- H2見出しを4〜6個使う
- コードブロックを最低1つ含める
- 冒頭で読者の課題を明示し、結論を先出しする
- 専門用語は初出時に説明する
- 禁止: 「この記事では〜を解説します」「いかがでしたか」「近年、〜が注目されています」

JSON以外のテキストは出力しないでください。"""

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=8000,
            messages=[{"role": "user", "content": prompt}]
        )
        text = response.content[0].text.strip()

        # JSONを抽出
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        data = json.loads(text)
        data["keyword"] = keyword
        data["cluster"] = cluster
        return data

    except Exception as e:
        print(f"  ❌ 生成エラー ({keyword}): {e}")
        return None


def save_article(data: dict) -> str:
    """記事をMarkdownファイルとして保存"""
    today = datetime.date.today().isoformat()
    slug = re.sub(r"[^\w\-]", "-", data["keyword"].lower().replace(" ", "-"))
    slug = re.sub(r"-+", "-", slug).strip("-")[:60]

    # 重複対策
    filename = CONTENT_DIR / f"{slug}.md"
    if filename.exists():
        slug = f"{slug}-{today}"
        filename = CONTENT_DIR / f"{slug}.md"

    frontmatter = f"""---
title: "{data['title']}"
description: "{data['description']}"
publishedAt: "{today}"
updatedAt: "{today}"
keyword: "{data['keyword']}"
cluster: "{data['cluster']}"
tags: {json.dumps(data.get('tags', []), ensure_ascii=False)}
isPillar: false
---

{data['content']}
"""
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    filename.write_text(frontmatter, encoding="utf-8")
    return slug


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY が未設定です")
        return

    client = anthropic.Anthropic(api_key=api_key)
    keywords = load_keywords()
    published = get_published_titles()

    print(f"📝 本日の記事生成開始 ({ARTICLES_PER_DAY}記事)")
    print(f"📚 既存記事数: {len(list(CONTENT_DIR.glob('*.md')))}")

    success = 0
    for kw_data in keywords[:ARTICLES_PER_DAY]:
        keyword = kw_data["keyword"]
        print(f"\n⏳ 生成中: {keyword}")

        data = generate_article(kw_data, client)
        if not data:
            continue

        passed, checks = quality_check(
            data["content"], data["title"], keyword, data["description"]
        )
        failed = [k for k, v in checks.items() if not v]

        if not passed:
            print(f"  ⚠️  品質チェック失敗: {failed}")
            continue

        slug = save_article(data)
        print(f"  ✅ 保存完了: {slug}")
        print(f"  📄 タイトル: {data['title']}")
        success += 1

    print(f"\n🎉 完了: {success}/{ARTICLES_PER_DAY} 記事生成・保存")


if __name__ == "__main__":
    main()
