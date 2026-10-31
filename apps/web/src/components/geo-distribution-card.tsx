"use client";

interface RegionData { region: string; label: string; count: number; pct: number; }
interface GeoDistributionCardProps { total: number; regions: RegionData[]; topRegion: string; }

const REGION_EMOJI: Record<string, string> = {
  "us-east": "🇺🇸", "us-west": "🇺🇸", "eu-west": "🇬🇧", "eu-central": "🇩🇪", "ap-east": "🇯🇵", "ap-south": "🇮🇳",
};

export function GeoDistributionCard({ total, regions, topRegion }: GeoDistributionCardProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">🌍 Traffic Distribution</h3>
        <span className="text-xs text-gray-400">{total.toLocaleString()} requests</span>
      </div>
      <div className="flex h-5 rounded-full overflow-hidden mb-4">
        {regions.map(r => (
          <div key={r.region} className="bg-blue-500 first:bg-blue-600 last:bg-blue-300"
               style={{ width: `${r.pct}%`, opacity: r.region === topRegion ? 1 : 0.6 }}
               title={`${r.label}: ${r.pct}%`} />
        ))}
      </div>
      <div className="space-y-2">
        {regions.map(r => (
          <div key={r.region} className="flex items-center justify-between text-sm">
            <span>{REGION_EMOJI[r.region] || "🌐"} {r.label}</span>
            <span className="text-gray-500">{r.count.toLocaleString()} ({r.pct}%)</span>
          </div>
        ))}
      </div>
    </div>
  );
}
