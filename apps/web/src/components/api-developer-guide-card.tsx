"use client";

interface GuideInfo { guide_id: string; title: string; category: string; step_count: number; view_count: number; }
interface Props { guides: GuideInfo[]; appName: string; }

export default function APIDeveloperGuideCard({ guides, appName }: Props) {
  const totalViews = guides.reduce((s, g) => s + g.view_count, 0);
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📚 Developer Guides</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{guides.length} guides · {totalViews} views</span>
      </div>
      {guides.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No guides</p>
      ) : (
        <div className="space-y-1">
          {guides.map((g) => (
            <div key={g.guide_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className="text-gray-700 dark:text-gray-300">{g.title}</span>
                <span className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800">{g.category}</span>
              </div>
              <span className="text-gray-400">{g.step_count} steps · {g.view_count} views</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
