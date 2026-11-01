"use client";

interface Service { name: string; status: string; uptimePct: number; }
interface StatusPageData { title: string; overall: string; services: Service[]; updatedAt: number; }

const statusConfig: Record<string, { bg: string; text: string; label: string }> = {
  operational: { bg: "bg-green-500", text: "text-green-600", label: "Operational" },
  degraded: { bg: "bg-yellow-500", text: "text-yellow-600", label: "Degraded" },
  partial_outage: { bg: "bg-orange-500", text: "text-orange-600", label: "Partial Outage" },
  major_outage: { bg: "bg-red-500", text: "text-red-600", label: "Major Outage" },
  maintenance: { bg: "bg-blue-500", text: "text-blue-600", label: "Maintenance" },
};

export function StatusPageComponent({ page }: { page: StatusPageData }) {
  const overall = statusConfig[page.overall] || statusConfig.operational;
  return (
    <div className="space-y-4">
      <div className={`${overall.bg} rounded-xl p-4 text-white text-center`}>
        <h2 className="font-bold text-lg">{page.title}</h2>
        <span className="text-sm opacity-90">{overall.label}</span>
      </div>
      <div className="space-y-1">
        {page.services.map(s => {
          const cfg = statusConfig[s.status] || statusConfig.operational;
          return (
            <div key={s.name} className="flex items-center justify-between border dark:border-gray-700 rounded-lg p-2.5">
              <div className="flex items-center gap-2">
                <span className={`w-2.5 h-2.5 rounded-full ${cfg.bg}`} />
                <span className="text-sm">{s.name}</span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <span className={cfg.text}>{cfg.label}</span>
                <span className="text-gray-400">{s.uptimePct}%</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
