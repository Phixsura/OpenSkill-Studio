"use client";

interface ArticleInfo { article_id: string; title: string; category: string; views: number; helpful_votes: number; }
interface Props { articles: ArticleInfo[]; categoryCounts: Record<string, number>; appName: string; }

const catColor: Record<string, string> = { getting_started: "bg-green-100 text-green-700", api_reference: "bg-blue-100 text-blue-700", troubleshooting: "bg-orange-100 text-orange-700", best_practices: "bg-purple-100 text-purple-700", faq: "bg-gray-100 text-gray-600" };

export default function APIDeveloperPlatformSDKApiDeveloperKnowledgeBaseCard({ articles, categoryCounts, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📚 Knowledge Base</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {articles.length} articles</p>
      </div>
      <div className="mb-3 flex flex-wrap gap-1">
        {Object.entries(categoryCounts).map(([cat, count]) => (
          <span key={cat} className={`rounded px-1.5 py-0.5 text-[10px] ${catColor[cat] ?? ""}`}>{cat.replace(/_/g, " ")}: {count}</span>
        ))}
      </div>
      {articles.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No articles</p>
      ) : (
        <div className="space-y-1.5">
          {articles.slice(0, 5).map((a) => (
            <div key={a.article_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{a.title}</span>
              <span className="text-gray-400">{a.views} views</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
