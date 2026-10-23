"use client";

interface CountryData { country_code: string; country_name: string; installs: number; pct: number; }
interface GeoAnalyticsMapProps { countries: CountryData[]; totalInstalls: number;
  uniqueCountries: number; topCountry: string | null; }

const flagEmoji = (cc: string) => cc.split("").map(c => String.fromCodePoint(127397 + c.charCodeAt(0))).join("");

export function GeoAnalyticsMap({ countries, totalInstalls, uniqueCountries, topCountry }: GeoAnalyticsMapProps) {
  const maxInstalls = Math.max(...countries.map(c => c.installs), 1);
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Geographic Distribution</h2>
        <span className="text-xs text-gray-400">{uniqueCountries} countries · {totalInstalls.toLocaleString()} installs</span>
      </div>
      <div className="space-y-1.5">
        {countries.slice(0, 10).map(c => (
          <div key={c.country_code} className="flex items-center gap-2">
            <span className="w-8 text-center">{flagEmoji(c.country_code)}</span>
            <span className="w-28 truncate text-sm">{c.country_name}</span>
            <div className="flex-1">
              <div className="h-4 rounded bg-blue-400 dark:bg-blue-600"
                style={{ width: `${(c.installs / maxInstalls) * 100}%` }}>
                <span className="px-1 text-[10px] text-white">{c.installs.toLocaleString()}</span>
              </div>
            </div>
            <span className="w-12 text-right text-xs text-gray-400">{c.pct}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}
