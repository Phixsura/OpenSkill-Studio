"use client";

interface Country { code: string; region: string; requests: number; avgMs: number; errors: number; }
interface Props { countries: Country[]; byRegion: Record<string, number>; totalRequests: number; uniqueCountries: number; highestLatency: string; consumerId: string; appName: string; }

const regionColors: Record<string, string> = { NA: "bg-blue-100 text-blue-700", EU: "bg-green-100 text-green-700", APAC: "bg-purple-100 text-purple-700", LATAM: "bg-amber-100 text-amber-700", MEA: "bg-red-100 text-red-700" };

export default function APIDeveloperPlatformSDKConsumerApiEndpointGeographicAnalyticsCard({ countries, byRegion, totalRequests, uniqueCountries, highestLatency, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🌍 Geographic Analytics</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · {uniqueCountries} countries · {totalRequests.toLocaleString()} requests</p>
      </div>
      <div className="mb-3 flex flex-wrap gap-1">
        {Object.entries(byRegion).sort((a, b) => b[1] - a[1]).map(([region, count]) => (
          <span key={region} className={`rounded px-1.5 py-0.5 text-[9px] font-medium ${regionColors[region] ?? "bg-gray-200 text-gray-600"}`}>{region}: {count.toLocaleString()}</span>
        ))}
      </div>
      {countries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No geographic data</p>
      ) : (
        <div className="space-y-0.5">
          {countries.slice(0, 8).map((c) => (
            <div key={c.code} className="flex items-center justify-between text-[10px]">
              <span className="text-gray-700 dark:text-gray-300">{c.code}{c.code === highestLatency ? " 🐌" : ""}</span>
              <span className="text-gray-400">{c.requests.toLocaleString()} req · {c.avgMs}ms</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
