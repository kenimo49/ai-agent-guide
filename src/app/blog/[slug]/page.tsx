import { getAllSlugs, getArticleBySlug } from '@/lib/articles'
import { Metadata } from 'next'
import Link from 'next/link'

const BASE_URL = process.env.NEXT_PUBLIC_BASE_URL || 'https://ai-agent-guide.vercel.app'
const SITE_NAME = 'AI Agent Guide'

export async function generateStaticParams() {
  const slugs = getAllSlugs()
  return slugs.map(slug => ({ slug }))
}

export async function generateMetadata(
  { params }: { params: Promise<{ slug: string }> }
): Promise<Metadata> {
  const { slug } = await params
  const article = await getArticleBySlug(slug)
  return {
    title: `${article.title} | ${SITE_NAME}`,
    description: article.description,
    alternates: { canonical: `${BASE_URL}/blog/${slug}` },
    openGraph: {
      title: article.title,
      description: article.description,
      url: `${BASE_URL}/blog/${slug}`,
      siteName: SITE_NAME,
      images: [{ url: `${BASE_URL}/api/og/${slug}`, width: 1200, height: 630 }],
      type: 'article',
      publishedTime: article.publishedAt,
    },
  }
}

export default async function ArticlePage(
  { params }: { params: Promise<{ slug: string }> }
) {
  const { slug } = await params
  const article = await getArticleBySlug(slug)

  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <Link href="/" className="text-sm text-blue-600 hover:underline mb-6 block">
        ← トップに戻る
      </Link>
      <div className="mb-6">
        <div className="flex gap-2 mb-3">
          {article.tags.map(tag => (
            <span key={tag} className="text-xs bg-blue-50 text-blue-700 px-2 py-1 rounded">
              {tag}
            </span>
          ))}
        </div>
        <h1 className="text-3xl font-bold text-gray-900 mb-3 leading-snug">
          {article.title}
        </h1>
        <p className="text-gray-500 text-sm">
          {new Date(article.publishedAt).toLocaleDateString('ja-JP')}
          {article.updatedAt !== article.publishedAt && (
            <span className="ml-2 text-gray-400">
              (更新: {new Date(article.updatedAt).toLocaleDateString('ja-JP')})
            </span>
          )}
        </p>
      </div>
      <div
        className="prose prose-lg max-w-none prose-headings:font-bold prose-a:text-blue-600 prose-code:bg-gray-100 prose-code:px-1 prose-code:rounded"
        dangerouslySetInnerHTML={{ __html: article.content }}
      />
    </div>
  )
}
