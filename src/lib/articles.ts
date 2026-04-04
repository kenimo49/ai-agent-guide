import fs from 'fs'
import path from 'path'
import matter from 'gray-matter'
import { remark } from 'remark'
import html from 'remark-html'

const articlesDirectory = path.join(process.cwd(), 'content/articles')

export interface Article {
  slug: string
  title: string
  description: string
  publishedAt: string
  updatedAt: string
  keyword: string
  cluster: string
  tags: string[]
  isPillar: boolean
  content: string
  wordCount: number
}

export function getAllSlugs(): string[] {
  if (!fs.existsSync(articlesDirectory)) return []
  return fs
    .readdirSync(articlesDirectory)
    .filter(f => f.endsWith('.md'))
    .map(f => f.replace('.md', ''))
}

export async function getArticleBySlug(slug: string): Promise<Article> {
  const fullPath = path.join(articlesDirectory, `${slug}.md`)
  const fileContents = fs.readFileSync(fullPath, 'utf8')
  const { data, content } = matter(fileContents)

  const processedContent = await remark().use(html).process(content)
  const contentHtml = processedContent.toString()

  return {
    slug,
    title: data.title || '',
    description: data.description || '',
    publishedAt: data.publishedAt || '',
    updatedAt: data.updatedAt || data.publishedAt || '',
    keyword: data.keyword || '',
    cluster: data.cluster || 'general',
    tags: data.tags || [],
    isPillar: data.isPillar || false,
    content: contentHtml,
    wordCount: content.length,
  }
}

export async function getAllArticles(): Promise<Article[]> {
  const slugs = getAllSlugs()
  const articles = await Promise.all(slugs.map(getArticleBySlug))
  return articles.sort(
    (a, b) => new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime()
  )
}

export async function getArticlesByCluster(cluster: string): Promise<Article[]> {
  const all = await getAllArticles()
  return all.filter(a => a.cluster === cluster)
}
