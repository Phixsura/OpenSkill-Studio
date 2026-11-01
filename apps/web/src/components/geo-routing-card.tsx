"use client";

interface GeoRegionInfo {
  region_id: string;
  name: string;
  endpoint: string;
  countries: string[];
  request_count: number;
  active: boolean;
}

interface GeoRoutingCardProps {
  regions: GeoRegionInfo[];
  defaultRegion: string;
  appName: string;
}

function formatNum(n: number): string {
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toString();
}

export default function GeoRoutingCard({ regions, defaultRegion, appName }: GeoRoutingCardProps) {
  const activeCount = regions.filter((r) => r.active).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Geo Routing</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">
          {activeCount}/{regions.length} active
        </span>
      </div>

      {regions.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No regions configured</p>
      ) : (
        <div className="space-y-2">
          {regions.map((r) => (
            <div
              key={r.region_id}
              className={`rounded-lg border px-3 py-2 ${
                r.active
                  ? "border-gray-100 dark:border-gray-800"
                  : "border-gray-100 opacity-50 dark:border-gray-800"
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span
                    className={`h-2 w-2 rounded-full ${r.active ? "bg-green-500" : "bg-gray-300"}`}
                  />
                  <span className="text-sm font-medium text-gray-800 dark:text-gray-200">
                    {r.name}
                  </span>
                  {r.region_id === defaultRegion && (
                    <span className="text-[10px] text-blue-600 dark:text-blue-400">default</span>
                  )}
                </div>
                <span className="text-[11px] text-gray-400">{formatNum(r.request_count)} req</span>
              </div>
              <div className="mt-1 flex flex-wrap gap-1">
                {r.countries.slice(0, 8).map((c) => (
                  <span
                    key={c}
                    className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800"
                  >
                    {c}
                  </span>
                ))}
                {r.countries.length > 8 && (
                  <span className="text-[9px] text-gray-400">+{r.countries.length - 8}</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
