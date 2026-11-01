"use client";

interface DiffInfo { diff_id: string; change_type: string; category: string; path: string; description: string; }
interface Props { fromVersion: string; toVersion: string; diffs: DiffInfo[]; breakingCount: number; appName: string; }

const ctColor: Record<string, string> = { breaking: "bg-red-100 text-red-700", non_breaking: "bg-green-100 text-green-700", deprecation: "bg-yellow-100 text-yellow-700" };

export default function APIDeveloperAPIOpenAPIDiffCheckerCard({ fromVersion, toVersion, diffs, breakingCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔀 API Diff Checker</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} · {fromVersion} → {toVersion}</p>
        </div>
        {breakingCount > 0 ? (
          <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-bold text-red-700">{breakingCount} breaking</span>
        ) : (
          <span className="rounded-full bg-green-100 px-2 py-0.5 text-[10px] text-green-700">compatible</span>
        )}
      </div>
      {diffs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No changes</p>
      ) : (
        <div className="space-y-1.5">
          {diffs.map((d) => (
            <div key={d.diff_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`rounded px-1 py-0.5 text-[9px] ${ctColor[d.change_type] ?? ""}`}>{d.change_type}</span>
                <span className="text-gray-700 dark:text-gray-300">{d.path}</span>
              </div>
              <span className="text-[10px] text-gray-400">{d.category}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
