#!/usr/bin/env python3
"""
GA4分析エージェント
Google Analytics 4 Data APIから記事パフォーマンスを取得・分析する
"""
import os
import json
import datetime
from pathlib import Path
from statistics import mean

try:
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import (
        RunReportRequest, DateRange, Dimension, Metric
    )
    GA4_AVAILABLE = True
except ImportError:
    GA4_AVAILABLE = False

MEMORY_DIR = Path(__file__).parent.parent / "harness" / "memory"
GA4_PROPERTY_ID = os.environ.get("GA4_PROPERTY_ID", "")


def fetch_article_metrics(period: str = "7daysAgo") -> list[dict]:
    """GA4 Data APIから記事メトリクスを取得"""
    if not GA4_AVAILABLE:
        print("⚠️  google-analytics-data が未インストール")
        return []
    if not GA4_PROPERTY_ID:
        print("⚠️  GA4_PROPERTY_ID が未設定")
        return []

    client = BetaAnalyticsDataClient()
    request = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        dimensions=[
            Dimension(name="pagePath"),
            Dimension(name="pageTitle"),
        ],
        metrics=[
            Metric(name="screenPageViews"),
            Metric(name="activeUsers"),
            Metric(name="averageSessionDuration"),
            Metric(name="bounceRate"),
            Metric(name="engagementRate"),
        ],
        date_ranges=[DateRange(start_date=period, end_date="today")],
    )

    response = client.run_report(request)
    articles = []
    for row in response.rows:
        path = row.dimension_values[0].value
        if not path.startswith("/blog/"):
            continue
        slug = path.replace("/blog/", "").strip("/")
        articles.append({
            "slug": slug,
            "path": path,
            "title": row.dimension_values[1].value,
            "views": int(row.metric_values[0].value),
            "users": int(row.metric_values[1].value),
            "duration": float(row.metric_values[2].value),
            "bounce_rate": float(row.metric_values[3].value),
            "engagement": float(row.metric_values[4].value),
        })

    return sorted(articles, key=lambda x: x["views"], reverse=True)


def classify_performance(article: dict) -> str:
    """パフォーマンス分類"""
    if article["views"] > 100 and article["duration"] > 120:
        return "high"
    elif article["views"] < 20 or article["duration"] < 30 or article["bounce_rate"] > 0.8:
        return "low"
    return "normal"


def analyze_success_patterns(high_performers: list[dict]) -> dict:
    """高パフォーマンス記事の成功パターンを分析"""
    if not high_performers:
        return {}
    return {
        "avg_views": mean(a["views"] for a in high_performers),
        "avg_duration": mean(a["duration"] for a in high_performers),
        "avg_engagement": mean(a["engagement"] for a in high_performers),
        "count": len(high_performers),
    }


def save_report(report: dict):
    """レポートをharness/memoryに保存"""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.date.today().isoformat()
    report_file = MEMORY_DIR / f"ga4-report-{today}.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # 低パフォーマンス記事リストを improve_queue.json に保存
    improve_queue = MEMORY_DIR / "improve_queue.json"
    low = [a["slug"] for a in report.get("low_performers", [])]
    with open(improve_queue, "w", encoding="utf-8") as f:
        json.dump({"date": today, "slugs": low}, f, ensure_ascii=False, indent=2)

    print(f"📊 レポート保存: {report_file}")


def main():
    print("📊 GA4分析開始...")

    if not GA4_AVAILABLE or not GA4_PROPERTY_ID:
        print("ℹ️  GA4未設定 — ダミーデータでテスト実行")
        articles = [
            {"slug": "claude-code-agents-md", "title": "AGENTS.md の書き方",
             "views": 150, "duration": 180, "bounce_rate": 0.3, "engagement": 0.7},
            {"slug": "ai-agent-harness", "title": "ハーネス設計入門",
             "views": 12, "duration": 25, "bounce_rate": 0.85, "engagement": 0.2},
        ]
    else:
        articles = fetch_article_metrics("7daysAgo")

    if not articles:
        print("📭 データなし（サイト公開直後は正常）")
        return

    high = [a for a in articles if classify_performance(a) == "high"]
    low = [a for a in articles if classify_performance(a) == "low"]

    report = {
        "period": "7d",
        "date": datetime.date.today().isoformat(),
        "total_articles": len(articles),
        "total_views": sum(a["views"] for a in articles),
        "high_performers": high,
        "low_performers": low,
        "top_5": articles[:5],
        "success_patterns": analyze_success_patterns(high),
    }

    print(f"\n📈 7日間レポート")
    print(f"  総記事数: {report['total_articles']}")
    print(f"  総PV: {report['total_views']:,}")
    print(f"  🟢 高パフォーマンス: {len(high)}記事")
    print(f"  🔴 低パフォーマンス: {len(low)}記事 → 改善キューへ")

    if report["top_5"]:
        print(f"\n🏆 TOP5:")
        for a in report["top_5"]:
            print(f"  {a['views']:4d}PV  {a.get('title', a['slug'])[:40]}")

    save_report(report)


if __name__ == "__main__":
    main()
