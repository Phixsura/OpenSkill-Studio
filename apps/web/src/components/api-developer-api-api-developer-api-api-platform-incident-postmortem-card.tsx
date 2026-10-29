"use client";

interface PostmortemInfo { postmortem_id: string; title: string; severity: string; root_cause: string; status: string; action_item_count: number; duration_minutes: number; }
interface Props { postmortems: PostmortemInfo[]; severityCounts: Record<string, number>; appName: string; }

const sevColor: Record<string, string> = { sev1: "bg-red-100 text-red-700", sev2: "bg-orange-100 text-orange-700", sev3: "bg-yellow-100 text-yellow-700" };

export default function APIDeveloperAPIApiDeveloperApiApiPlatformIncidentPostmortemCard({ postmortems, severityCounts, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📝 Postmortems</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="flex gap-1">
          {Object.entries(severityCounts).map(([sev, count]) => (
            <span key={sev} className={`rounded px-1.5 py-0.5 text-[9px] ${sevColor[sev] ?? ""}`}>{sev}: {count}</span>
          ))}
        </div>
      </div>
      {postmortems.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No postmortems</p>
      ) : (
        <div className="space-y-2">
          {postmortems.map((p) => (
            <div key={p.postmortem_id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <div className="flex items-center gap-1.5">
                  <span className={`rounded px-1 py-0.5 text-[9px] ${sevColor[p.severity] ?? ""}`}>{p.severity}</span>
                  <span className="font-medium text-gray-700 dark:text-gray-300">{p.title}</span>
                </div>
                <span className="text-gray-400">{p.duration_minutes}m · {p.action_item_count} actions</span>
              </div>
              <p className="mt-0.5 text-[10px] text-gray-400 truncate">Root cause: {p.root_cause}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
