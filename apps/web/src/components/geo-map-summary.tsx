"use client";

interface GeoEntry { country: string; count: number; }
interface GeoMapSummaryProps { distribution: GeoEntry[]; totalIps: number; countries: number; }

const flags: Record<string, string> = {
  US: "🇺🇸", AU: "🇦🇺", GB: "🇬🇧", DE: "🇩🇪", JP: "🇯🇵", FR: "🇫🇷",
  CA: "🇨🇦", BR: "🇧🇷", IN: "🇮🇳", SG: "🇸🇬",
};

export function GeoMapSummary({ distribution, totalIps, countries }: GeoMapSummaryProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Geographic Distribution</h3>
        <span className="text-xs text-gray-400">{countries} countries · {totalIps} IPs</span>
      </div>
      <div className="space-y-1">
        {distribution.map(g => {
          const pct = Math.round((g.count / Math.max(totalIps, 1)) * 100);
          return (
            <div key={g.country} className="flex items-center gap-2">
              <span className="w-6 text-center">{flags[g.country] ?? "🌍"}</span>
              <span className="w-8 text-xs font-medium">{g.country}</span>
              <div className="flex-1 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
                <div className="h-full rounded-full bg-blue-500" style={{ width: `${pct}%` }} />
              </div>
              <span className="w-12 text-right text-xs text-gray-400">{g.count} ({pct}%)</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
