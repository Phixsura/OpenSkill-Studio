"use client";

interface RegionInfo { region: string; request_count: number; avg_latency_ms: number; error_rate: number; }
interface Props { regions: RegionInfo[]; totalRequests: number; appName: string; }

const rFlag: Record<string, string> = { NA: "🌎", EU: "🌍", APAC: "🌏", LATAM: "🌎", MEA: "🌍" };

export default function APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiApiRequestGeoAnalyticsCard({ regions, totalRequests, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🌍 Geo Analytics</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {totalRequests.toLocaleString()} total</p>
        </div>
      </div>
      {regions.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No geo data</p>
      ) : (
        <div className="space-y-1.5">
          {regions.map((r) => (
            <div key={r.region} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{rFlag[r.region] ?? ""} {r.region}</span>
              <span className="text-gray-400">{r.request_count.toLocaleString()} · {r.avg_latency_ms}ms{r.error_rate > 0 ? ` · ${r.error_rate}% err` : ""}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
