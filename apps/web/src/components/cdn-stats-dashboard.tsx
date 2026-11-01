"use client";

interface CdnStats { totalAssets: number; totalSizeBytes: number; totalBandwidth: number; edgeLocations: number; }

function formatBytes(b: number) {
  if (b < 1024) return `${b} B`;
  if (b < 1048576) return `${(b / 1024).toFixed(1)} KB`;
  if (b < 1073741824) return `${(b / 1048576).toFixed(1)} MB`;
  return `${(b / 1073741824).toFixed(1)} GB`;
}

export function CdnStatsDashboard({ stats }: { stats: CdnStats }) {
  const metrics = [
    { label: "Assets", value: stats.totalAssets.toString(), icon: "📦" },
    { label: "Size", value: formatBytes(stats.totalSizeBytes), icon: "💾" },
    { label: "Bandwidth", value: formatBytes(stats.totalBandwidth), icon: "📡" },
    { label: "Edge PoPs", value: stats.edgeLocations.toString(), icon: "🌍" },
  ];
  return (
    <div className="space-y-3">
      <h3 className="font-bold text-sm">CDN Performance</h3>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        {metrics.map(m => (
          <div key={m.label} className="border dark:border-gray-700 rounded-xl p-3 text-center">
            <span className="text-lg block">{m.icon}</span>
            <span className="text-lg font-bold block">{m.value}</span>
            <span className="text-[10px] text-gray-500">{m.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
