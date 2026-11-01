"use client";

interface Page { id: string; title: string; category: string; published: boolean; updatedAt: string; }
interface Props { pages: Page[]; appName: string; }

const catColors: Record<string, string> = {
  guide: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  reference: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  tutorial: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400",
  faq: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
};

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiDocumentationCard({ pages, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📖 API Documentation</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {pages.length} pages</p>
      </div>
      {pages.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No documentation</p>
      ) : (
        <div className="space-y-1">
          {pages.map((p) => (
            <div key={p.id} className="flex items-center justify-between rounded bg-gray-50 px-2 py-1.5 text-[11px] dark:bg-gray-800">
              <div className="flex items-center gap-2">
                <span className="text-gray-700 dark:text-gray-300">{p.title}</span>
                <span className={`rounded px-1 py-0.5 text-[9px] font-medium ${catColors[p.category] ?? ""}`}>{p.category}</span>
              </div>
              <span className={p.published ? "text-green-500" : "text-gray-400"}>{p.published ? "Published" : "Draft"}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
