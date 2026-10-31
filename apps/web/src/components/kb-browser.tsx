"use client";

interface Article { slug: string; title: string; category: string; tags: string[]; helpfulPct?: number; }
interface KbBrowserProps { articles: Article[]; categories: string[];
  total: number; onSelect: (slug: string) => void; }

export function KbBrowser({ articles, categories, total, onSelect }: KbBrowserProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📚 Knowledge Base</h3>
        <span className="text-xs text-gray-400">{total} articles · {categories.length} categories</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {articles.map(a => (
          <button key={a.slug} onClick={() => onSelect(a.slug)}
            className="w-full text-left px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-800">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">{a.title}</span>
              <span className="text-[10px] text-gray-400">{a.category}</span>
            </div>
            <div className="flex gap-1 mt-1">
              {a.tags.map(t => (
                <span key={t} className="px-1 py-0.5 text-[10px] bg-gray-100 dark:bg-gray-800 rounded">{t}</span>
              ))}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
