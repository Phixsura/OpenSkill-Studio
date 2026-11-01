"use client";
interface SvcStatus { service: string; consensus: string; reports: number; }
interface SvcStatusAggPanelProps { services: SvcStatus[]; healthy: number; unhealthy: number; }
const CON_STYLE: Record<string, string> = { healthy: "text-green-600", degraded: "text-yellow-600", down: "text-red-500" };
export function SvcStatusAggPanel({ services, healthy, unhealthy }: SvcStatusAggPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 Service Status</h3>
        <span className="text-xs text-gray-400">{healthy} healthy · {unhealthy} unhealthy</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {services.map(s => (
          <div key={s.service} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{s.service}</span>
            <span className={CON_STYLE[s.consensus] ?? ""}>{s.consensus} ({s.reports} sources)</span>
          </div>
        ))}
      </div>
    </div>
  );
}
