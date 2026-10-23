"use client";

interface BlogPostCardProps { title: string; excerpt: string; category: string; date: string; readTime: number; slug: string; author: string; }

const CAT_COLORS: Record<string, string> = {
  tutorial: "bg-green-100 text-green-700", announcement: "bg-blue-100 text-blue-700",
  case_study: "bg-purple-100 text-purple-700", engineering: "bg-orange-100 text-orange-700",
  community: "bg-pink-100 text-pink-700",
};

export function BlogPostCard({ title, excerpt, category, date, readTime, slug, author }: BlogPostCardProps) {
  return (
    <a href={`/blog/${slug}`} className="block rounded-lg border border-gray-200 p-4 transition hover:shadow-md dark:border-gray-700">
      <div className="flex items-center gap-2">
        <span className={`rounded px-2 py-0.5 text-xs ${CAT_COLORS[category] || "bg-gray-100"}`}>{category}</span>
        <span className="text-xs text-gray-400">{date}</span>
        <span className="text-xs text-gray-400">· {readTime} min read</span>
      </div>
      <h3 className="mt-2 text-lg font-semibold">{title}</h3>
      <p className="mt-1 text-sm text-gray-500 line-clamp-2">{excerpt}</p>
      <p className="mt-2 text-xs text-gray-400">By {author}</p>
    </a>
  );
}
