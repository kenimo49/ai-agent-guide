import { getAllArticles } from '@/lib/articles'
import Link from 'next/link'

export default async function HomePage() {
  const articles = await getAllArticles()

  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <header className="mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-3">AI Agent Guide</h1>
        <p className="text-gray-600 text-lg">
          AIエージェント実装ガイド — Claude Code、OpenAI Agents、LangChainの実践的な使い方
        </p>
      </header>

      {articles.length === 0 ? (
        <p className="text-gray-500">記事を準備中です...</p>
      ) : (
        <div className="space-y-8">
          {articles.map(article => (
            <article key={article.slug} className="border-b pb-8">
              <div className="flex gap-2 mb-2">
                {article.tags.slice(0, 3).map(tag => (
                  <span key={tag} className="text-xs bg-blue-50 text-blue-700 px-2 py-1 rounded">
                    {tag}
                  </span>
                ))}
              </div>
              <Link href={`/blog/${article.slug}`}>
                <h2 className="text-xl font-semibold text-gray-900 hover:text-blue-600 mb-2 leading-snug">
                  {article.title}
                </h2>
              </Link>
              <p className="text-gray-600 text-sm mb-2">{article.description}</p>
              <p className="text-gray-400 text-xs">
                {new Date(article.publishedAt).toLocaleDateString('ja-JP')}
              </p>
            </article>
          ))}
        </div>
      )}
    </div>
  )
}
