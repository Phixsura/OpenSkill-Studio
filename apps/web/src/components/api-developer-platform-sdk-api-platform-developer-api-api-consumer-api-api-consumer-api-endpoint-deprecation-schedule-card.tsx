"use client";

interface Entry { id: string; path: string; status: string; deprecatedAt: string; sunsetAt: string; replacement: string | null; }
interface Props { entries: Entry[]; appName: string; }

const statusColors: Record<string, string> = {
  active: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  deprecated: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
  sunset: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
};

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointDeprecationScheduleCard({ entries, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📅 Deprecation Schedule</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {entries.length} endpoints</p>
      </div>
      {entries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No deprecations scheduled</p>
      ) : (
        <div className="space-y-2">
          {entries.map((e) => (
            <div key={e.id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <code className="font-medium text-gray-700 dark:text-gray-300">{e.path}</code>
                <span className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${statusColors[e.status] ?? ""}`}>{e.status}</span>
              </div>
              <div className="mt-0.5 text-[10px] text-gray-400">
                Deprecated: {e.deprecatedAt} · Sunset: {e.sunsetAt}
                {e.replacement && <span> · Replace with <code className="text-blue-500">{e.replacement}</code></span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
