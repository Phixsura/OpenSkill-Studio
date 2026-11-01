"use client";

interface BlogPostCardProps { slug: string; title: string; excerpt: string;
  author: string; date: string; readTime: string; tags: string[];
  featured: boolean; onClick: () => void; }

export function BlogPostCard({ slug, title, excerpt, author, date, readTime, tags, featured, onClick }: BlogPostCardProps) {
  return (
    <button onClick={onClick} className={`w-full text-left rounded-xl border dark:border-gray-700 p-5 hover:shadow-lg transition ${featured ? "ring-2 ring-blue-200" : ""}`}>
      {featured && <span className="text-xs px-2 py-0.5 rounded bg-blue-100 text-blue-700 mb-2 inline-block">Featured</span>}
      <h3 className="text-lg font-bold mb-1">{title}</h3>
      <p className="text-sm text-gray-500 mb-2">{excerpt}</p>
      <div className="flex items-center gap-3 text-xs text-gray-400">
        <span>{author}</span><span>{date}</span><span>{readTime}</span>
      </div>
      {tags.length > 0 && (
        <div className="flex gap-1 mt-2">
          {tags.map(t => <span key={t} className="text-xs px-1.5 py-0.5 bg-gray-100 dark:bg-gray-800 rounded">{t}</span>)}
        </div>
      )}
    </button>
  );
}
