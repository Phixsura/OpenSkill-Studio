"use client";

interface Props { consumerId: string; mode: string; countries: string[]; topCountries: { code: string; count: number }[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestGeoRestrictionCard({ consumerId, mode, countries, topCountries, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🌍 Geo Restriction</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
      </div>
      <div className="mb-2 flex items-center gap-2 text-[11px]">
        <span className={`rounded px-1.5 py-0.5 font-medium ${mode === "allowlist" ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400" : "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"}`}>
          {mode}
        </span>
        <span className="text-gray-400">{countries.length} countries</span>
      </div>
      <div className="mb-2 flex flex-wrap gap-1">
        {countries.slice(0, 20).map((c) => (
          <span key={c} className="rounded bg-gray-100 px-1.5 py-0.5 text-[10px] text-gray-600 dark:bg-gray-800 dark:text-gray-400">{c}</span>
        ))}
      </div>
      {topCountries.length > 0 && (
        <div className="space-y-0.5 text-[10px]">
          {topCountries.slice(0, 5).map((tc) => (
            <div key={tc.code} className="flex justify-between text-gray-500">
              <span>{tc.code}</span><span>{tc.count.toLocaleString()}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
