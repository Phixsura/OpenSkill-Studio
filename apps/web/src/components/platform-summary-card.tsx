"use client";

interface PlatformSummaryCardProps { apps: number; users: number; displayRevenue: string;
  uptime: number; growthPct: number; health: string; highlights: string[]; }

const HEALTH_COLORS: Record<string, string> = {
  excellent: "text-green-600", good: "text-blue-600", needs_attention: "text-yellow-600",
};

export function PlatformSummaryCard({ apps, users, displayRevenue, uptime, growthPct, health, highlights }: PlatformSummaryCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 Platform Summary</h3>
        <span className={`text-xs font-medium capitalize ${HEALTH_COLORS[health] ?? ""}`}>{health.replaceAll("_", " ")}</span>
      </div>
      <div className="grid grid-cols-4 gap-px bg-gray-200 dark:bg-gray-700 border-b dark:border-gray-700">
        {[{ l: "Apps", v: apps.toLocaleString() }, { l: "Users", v: users.toLocaleString() },
          { l: "Revenue", v: displayRevenue }, { l: "Uptime", v: `${uptime}%` }].map(s => (
          <div key={s.l} className="bg-white dark:bg-gray-900 p-3 text-center">
            <div className="text-sm font-bold">{s.v}</div>
            <div className="text-[10px] text-gray-400">{s.l}</div>
          </div>
        ))}
      </div>
      {highlights.length > 0 && (
        <div className="p-3">
          {highlights.map((h, i) => <div key={i} className="text-xs py-0.5">🌟 {h}</div>)}
        </div>
      )}
    </div>
  );
}
