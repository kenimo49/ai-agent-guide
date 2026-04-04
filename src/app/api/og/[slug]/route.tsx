import { ImageResponse } from 'next/og'
import { getArticleBySlug } from '@/lib/articles'

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ slug: string }> }
) {
  const { slug } = await params
  let title = 'AI Agent Guide'
  try {
    const article = await getArticleBySlug(slug)
    title = article.title
  } catch {}

  return new ImageResponse(
    (
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          padding: '60px',
          background: '#0f172a',
          width: '100%',
          height: '100%',
        }}
      >
        <div
          style={{
            fontSize: '16px',
            color: '#60a5fa',
            marginBottom: '24px',
            fontFamily: 'sans-serif',
          }}
        >
          AI Agent Guide
        </div>
        <div
          style={{
            fontSize: '52px',
            fontWeight: 'bold',
            color: '#f1f5f9',
            lineHeight: 1.3,
            fontFamily: 'sans-serif',
          }}
        >
          {title}
        </div>
      </div>
    ),
    { width: 1200, height: 630 }
  )
}
