"use client";

interface DocPageInfo {
  page_id: string;
  title: string;
  section: string;
  view_count: number;
}

interface APIDocumentationCardProps {
  pages: DocPageInfo[];
  sections: string[];
  appName: string;
}

export default function APIDocumentationCard({
  pages,
  sections,
  appName,
}: APIDocumentationCardProps) {
  const totalViews = pages.reduce((s, p) => s + p.view_count, 0);

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            📖 API Documentation
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">
          {pages.length} pages · {totalViews} views
        </span>
      </div>

      {sections.length > 0 && (
        <div className="mb-3 flex flex-wrap gap-1">
          {sections.map((s) => (
            <span
              key={s}
              className="rounded bg-gray-100 px-1.5 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800"
            >
              {s}
            </span>
          ))}
        </div>
      )}

      {pages.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No documentation pages</p>
      ) : (
        <div className="space-y-1">
          {pages.map((p) => (
            <div key={p.page_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{p.title}</span>
              <span className="text-gray-400">{p.view_count} views</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
