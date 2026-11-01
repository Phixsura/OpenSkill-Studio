"use client";

interface HelpArticleCardProps { title: string; category: string; tags: string[];
  readTimeMin: number; url: string; onClick: () => void; }

const catIcon: Record<string, string> = {
  guides: "📖", api: "🔌", faq: "❓", troubleshooting: "🔧", tutorials: "🎓",
};

export function HelpArticleCard({ title, category, tags, readTimeMin, url, onClick }: HelpArticleCardProps) {
  return (
    <button onClick={onClick}
      className="flex w-full items-start gap-3 rounded-lg border p-4 text-left hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800">
      <span className="text-2xl">{catIcon[category] ?? "📄"}</span>
      <div className="flex-1">
        <h3 className="font-semibold">{title}</h3>
        <div className="mt-1 flex items-center gap-2">
          <span className="rounded bg-gray-100 px-1.5 py-0.5 text-xs dark:bg-gray-800">{category}</span>
          <span className="text-xs text-gray-400">{readTimeMin} min read</span>
        </div>
        {tags.length > 0 && (
          <div className="mt-1.5 flex gap-1">
            {tags.map(t => (
              <span key={t} className="rounded-full bg-blue-50 px-2 py-0.5 text-[10px] text-blue-600 dark:bg-blue-900/20">{t}</span>
            ))}
          </div>
        )}
      </div>
    </button>
  );
}
