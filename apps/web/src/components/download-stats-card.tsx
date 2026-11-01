"use client";

interface DownloadStatsCardProps { total: number; byPlatform: Record<string, number>; byVersion: Record<string, number>; }

const PLATFORM_ICONS: Record<string, string> = { npm: "📦", pip: "🐍", brew: "🍺" };

export function DownloadStatsCard({ total, byPlatform, byVersion }: DownloadStatsCardProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h4 className="mb-2 font-semibold">📥 Downloads</h4>
      <p className="text-2xl font-bold">{total.toLocaleString()}</p>
      {Object.keys(byPlatform).length > 0 && (
        <div className="mt-3 space-y-1">
          {Object.entries(byPlatform).map(([p, c]) => (
            <div key={p} className="flex justify-between text-sm">
              <span>{PLATFORM_ICONS[p] ?? "📦"} {p}</span><span className="font-medium">{c.toLocaleString()}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
