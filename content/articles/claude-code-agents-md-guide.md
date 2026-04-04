---
title: "Claude Code AGENTS.mdの正しい書き方【2026年版】"
description: "AGENTS.mdはClaudeへの指示書です。何を書くべきか、どう構造化するか、実際のプロジェクトで機能する書き方を解説します。"
publishedAt: "2026-04-04"
updatedAt: "2026-04-04"
keyword: "Claude Code AGENTS.md 書き方"
cluster: "claude-code"
tags: ["Claude Code", "AGENTS.md", "AIエージェント"]
isPillar: true
---

## AGENTS.mdとは何か

Claude Codeを使うとき、最初に読ませるファイルがAGENTS.mdです。人間で言えば「入社初日に渡すマニュアル」に相当します。プロジェクトの目的、使うべきツール、守るべきルール——これを書いておくことで、Claudeは毎回同じ質問をしなくて済みます。

AGENTS.mdをきちんと書いたプロジェクトと、そうでないプロジェクトでは、生成コードの品質に雲泥の差が出ます。

## 最低限書くべき3つのこと

### 1. プロジェクトの概要（1〜2行）

```markdown
# AGENTS.md

## Overview
Next.js + TypeScriptで構築したブログサイト。
記事はMDXで管理し、Vercelにデプロイする。
```

長々と書く必要はありません。Claudeがコンテキストウィンドウを使い切る前に重要情報を把握できるよう、簡潔に書きます。

### 2. 使用技術スタック

```markdown
## Tech Stack
- Framework: Next.js 15 (App Router)
- Language: TypeScript
- Styling: Tailwind CSS
- Package Manager: npm
- Deploy: Vercel
```

「TypeScriptで書いてください」と毎回伝えなくて済みます。

### 3. 禁止事項・制約

```markdown
## Constraints
- `any`型の使用禁止（型安全を守る）
- `console.log`は本番コードに残さない
- コンポーネントは`src/components/`に配置
- ページは`src/app/`のApp Router規約に従う
```

## 実際に機能するAGENTS.mdの例

```markdown
# AGENTS.md — ai-agent-guide

## Overview
AIエージェント実装ガイドのコンテンツサイト。
ハーネスエンジニアリングで記事生成・分析・改善を自律的に回す。

## Tech Stack
- Next.js 15 (App Router, TypeScript)
- Tailwind CSS
- content/articles/ にMDXファイルで記事を管理
- Vercel でホスティング

## Directory Structure
src/
  app/         # ページルーティング
  components/  # 共通コンポーネント
  lib/         # ユーティリティ（articles.ts, ga4.ts）
content/
  articles/    # 記事MDファイル
scripts/       # 記事生成・分析Pythonスクリプト
harness/       # ハーネス設計ファイル

## Constraints
- TypeScript strict mode
- コンポーネントはsrc/components/に配置
- 記事生成スクリプトはscripts/に配置
- 記事はcontent/articles/にMD形式で保存

## Important Patterns
- 記事ページ: app/blog/[slug]/page.tsx
- 記事取得: lib/articles.ts の getAllArticles/getArticleBySlug
```

## よくある失敗パターン

**失敗1: 書きすぎる**

AGENTS.mdが5,000文字を超えると、コンテキストウィンドウを圧迫します。スキルファイル（`skills/`ディレクトリ）に詳細を切り出し、AGENTS.mdはポインター集として使います。

**失敗2: 一度書いて放置する**

プロジェクトが進むにつれて、AGENTS.mdの内容は古くなります。週1回くらいのペースで見直し、実際のコードベースと合っているか確認しましょう。

**失敗3: 禁止事項だけ書く**

「〜するな」だけでなく「〜のときは〜する」という判断基準も書くと、Claudeの判断精度が上がります。

## まとめ

AGENTS.mdに最低限書くべきことは3つです。プロジェクト概要、技術スタック、制約事項。これだけで、Claudeとの作業効率は大きく変わります。

詳細なルールはスキルファイルに切り出し、AGENTS.mdはインデックスとして小さく保つ——これがハーネスエンジニアリングの基本です。
