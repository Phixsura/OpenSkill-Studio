"use client";

interface Service { name: string; status: string; uptimePct: number; }
interface StatusPageCardProps { overall: string; services: Service[]; uptimePct: number; }

const STATUS_STYLES: Record<string, { icon: string; color: string }> = {
  operational: { icon: "🟢", color: "text-green-600" },
  degraded: { icon: "🟡", color: "text-yellow-600" },
  outage: { icon: "🔴", color: "text-red-600" },
};

export function StatusPageCard({ overall, services, uptimePct }: StatusPageCardProps) {
  const s = STATUS_STYLES[overall] ?? STATUS_STYLES.operational;
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="mb-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span>{s.icon}</span>
          <span className={`font-semibold capitalize ${s.color}`}>{overall}</span>
        </div>
        <span className="text-sm text-gray-500">{uptimePct}% uptime</span>
      </div>
      <div className="space-y-1">
        {services.map(svc => (
          <div key={svc.name} className="flex items-center justify-between text-sm">
            <span>{svc.name}</span>
            <span className="flex items-center gap-1">
              <span>{STATUS_STYLES[svc.status]?.icon ?? "❓"}</span>
              <span className="text-xs text-gray-400">{svc.uptimePct}%</span>
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
