"use client";

interface Article { slug: string; title: string; category: string; views: number; }
interface KnowledgeBaseBrowserProps { articles: Article[]; categories: string[];
  totalArticles: number; onSelect: (slug: string) => void; }

const CAT_ICON: Record<string, string> = { guides: "📖", faq: "❓", tutorials: "🎓", reference: "📚" };

export function KnowledgeBaseBrowser({ articles, categories, totalArticles, onSelect }: KnowledgeBaseBrowserProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📚 Knowledge Base</h3>
        <span className="text-xs text-gray-400">{totalArticles} articles</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {articles.map(a => (
          <button key={a.slug} onClick={() => onSelect(a.slug)}
            className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-gray-50 dark:hover:bg-gray-800">
            <div className="flex items-center gap-2">
              <span>{CAT_ICON[a.category] || "📄"}</span>
              <span className="text-sm font-medium">{a.title}</span>
              <span className="text-xs text-gray-400 capitalize">{a.category}</span>
            </div>
            <span className="text-xs text-gray-400">{a.views} views</span>
          </button>
        ))}
      </div>
    </div>
  );
}
