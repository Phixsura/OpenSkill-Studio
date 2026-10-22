"use client";

interface CountryData { country: string; count: number; }
interface GeoDistributionCardProps { countries: CountryData[]; totalInstalls: number; }

const COUNTRY_FLAGS: Record<string, string> = {
  US: "🇺🇸", DE: "🇩🇪", JP: "🇯🇵", GB: "🇬🇧", FR: "🇫🇷", CN: "🇨🇳", KR: "🇰🇷", BR: "🇧🇷",
};

export function GeoDistributionCard({ countries, totalInstalls }: GeoDistributionCardProps) {
  const top = countries.slice(0, 8);
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h3 className="font-semibold">Geographic Distribution</h3>
      <p className="mt-1 text-xs text-gray-400">{countries.length} countries · {totalInstalls.toLocaleString()} installs</p>
      <ul className="mt-3 space-y-2">
        {top.map(c => {
          const pct = Math.round((c.count / Math.max(totalInstalls, 1)) * 100);
          return (
            <li key={c.country} className="flex items-center gap-2 text-sm">
              <span className="w-6">{COUNTRY_FLAGS[c.country] || "🌍"}</span>
              <span className="w-8">{c.country}</span>
              <div className="flex-1 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
                <div className="h-full rounded-full bg-blue-500" style={{ width: `${pct}%` }} />
              </div>
              <span className="w-14 text-right text-xs text-gray-400">{c.count} ({pct}%)</span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
