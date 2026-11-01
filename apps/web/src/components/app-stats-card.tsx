"use client";

interface Metric { label: string; display: string; icon: string; }
interface AppStatsCardProps { name: string; icon: string; metrics: Metric[]; health: string; }

const healthDot: Record<string, string> = { good: "bg-green-500", ok: "bg-yellow-500", poor: "bg-red-500" };

export function AppStatsCard({ name, icon, metrics, health }: AppStatsCardProps) {
  return (
    <div className="rounded-xl border p-4 dark:border-gray-700">
      <div className="flex items-center gap-2 mb-3">
        <span className="text-2xl">{icon}</span>
        <h3 className="text-sm font-bold">{name}</h3>
        <span className={`ml-auto h-2.5 w-2.5 rounded-full ${healthDot[health] ?? ""}`} title={health} />
      </div>
      <div className="grid grid-cols-4 gap-2">
        {metrics.map(m => (
          <div key={m.label} className="text-center">
            <span className="text-xs">{m.icon}</span>
            <p className="text-sm font-bold">{m.display}</p>
            <p className="text-xs text-gray-400">{m.label}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
