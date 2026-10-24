"use client";

interface StatusComponent { name: string; status: string; uptimePct: number; }
interface StatusPageViewProps { title: string; components: StatusComponent[];
  overall: string; avgUptime: number; incidentCount: number; }

const STATUS_STYLE: Record<string, { icon: string; color: string }> = {
  operational: { icon: "🟢", color: "text-green-600" },
  degraded: { icon: "🟡", color: "text-yellow-600" },
  outage: { icon: "🔴", color: "text-red-600" },
  maintenance: { icon: "🔵", color: "text-blue-600" },
};

export function StatusPageView({ title, components, overall, avgUptime, incidentCount }: StatusPageViewProps) {
  const s = STATUS_STYLE[overall] ?? STATUS_STYLE.operational;
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`p-6 text-center border-b dark:border-gray-700 ${overall === "operational" ? "bg-green-50 dark:bg-green-900/10" : overall === "outage" ? "bg-red-50 dark:bg-red-900/10" : "bg-yellow-50 dark:bg-yellow-900/10"}`}>
        <h2 className="text-lg font-bold">{title}</h2>
        <div className={`text-sm mt-1 ${s.color} font-medium capitalize`}>{s.icon} {overall}</div>
        <div className="text-xs text-gray-400 mt-1">{avgUptime}% uptime · {incidentCount} incidents</div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {components.map(c => {
          const cs = STATUS_STYLE[c.status] ?? STATUS_STYLE.operational;
          return (
            <div key={c.name} className="flex items-center justify-between px-4 py-3">
              <span className="text-sm">{c.name}</span>
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-400">{c.uptimePct}%</span>
                <span className={`text-xs capitalize ${cs.color}`}>{cs.icon} {c.status}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
