"use client";

interface SummaryInfo { summary_id: string; version: string; summary: string; key_points: string[]; }
interface Props { summaries: SummaryInfo[]; appName: string; }

export default function APIDeveloperChangelogAISummaryCard({ summaries, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🤖 AI Summaries</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{summaries.length} generated</span>
      </div>
      {summaries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No AI summaries</p>
      ) : (
        <div className="space-y-2">
          {summaries.map((s) => (
            <div key={s.summary_id} className="rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-gray-800 dark:text-gray-200">{s.version}</span>
                <span className="text-[9px] text-purple-500">AI generated</span>
              </div>
              <p className="mt-0.5 text-[10px] text-gray-500">{s.summary}</p>
              {s.key_points.length > 0 && (
                <div className="mt-1 flex flex-wrap gap-1">
                  {s.key_points.map((p) => (
                    <span key={p} className="rounded bg-purple-50 px-1 py-0.5 text-[8px] text-purple-600 dark:bg-purple-900/30 dark:text-purple-300">{p}</span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
