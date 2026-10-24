"use client";

interface DataPoint { date: string; count: number; }
interface InstallChartProps { data: DataPoint[]; growthPct: number; trend: string; peakDay?: { date: string; count: number }; }

export function InstallChart({ data, growthPct, trend, peakDay }: InstallChartProps) {
  const maxCount = Math.max(...data.map(d => d.count), 1);
  const trendConfig = { up: { icon: "📈", color: "text-green-600" }, down: { icon: "📉", color: "text-red-600" }, stable: { icon: "➡️", color: "text-gray-500" } };
  const cfg = trendConfig[trend as keyof typeof trendConfig] || trendConfig.stable;

  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Installations</h3>
        <span className={`text-sm font-medium ${cfg.color}`}>{cfg.icon} {growthPct > 0 ? "+" : ""}{growthPct}%</span>
      </div>
      <div className="mt-3 flex items-end gap-px" style={{ height: "80px" }}>
        {data.map((d, i) => {
          const h = Math.max(4, (d.count / maxCount) * 80);
          return <div key={i} className="flex-1 rounded-t bg-blue-500" style={{ height: `${h}px` }} title={`${d.date}: ${d.count}`} />;
        })}
      </div>
      <div className="mt-1 flex justify-between text-xs text-gray-400">
        <span>{data[0]?.date.slice(5)}</span>
        <span>{data[data.length - 1]?.date.slice(5)}</span>
      </div>
      {peakDay && <p className="mt-2 text-xs text-gray-400">Peak: {peakDay.count} on {peakDay.date}</p>}
    </div>
  );
}
