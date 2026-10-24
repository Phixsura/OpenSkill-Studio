"use client";

interface StatusService { name: string; status: string; }
interface PlatformStatusPageProps { overall: string; groups: Record<string, StatusService[]>;
  operational: number; total: number; }

const OVERALL_TEXT: Record<string, string> = {
  all_systems_operational: "All Systems Operational",
  degraded_performance: "Degraded Performance",
  partial_outage: "Partial Outage",
  major_outage: "Major Outage",
};
const OVERALL_STYLE: Record<string, string> = {
  all_systems_operational: "bg-green-500", degraded_performance: "bg-yellow-500",
  partial_outage: "bg-orange-500", major_outage: "bg-red-500",
};
const DOT: Record<string, string> = { operational: "bg-green-500", degraded: "bg-yellow-500", outage: "bg-red-500" };

export function PlatformStatusPage({ overall, groups, operational, total }: PlatformStatusPageProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`p-4 text-white text-center ${OVERALL_STYLE[overall] ?? "bg-gray-500"}`}>
        <h3 className="font-bold">{OVERALL_TEXT[overall] ?? overall}</h3>
        <p className="text-xs opacity-80">{operational}/{total} operational</p>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {Object.entries(groups).map(([group, svcs]) => (
          <div key={group} className="p-3">
            <div className="text-xs font-semibold text-gray-500 mb-1">{group}</div>
            {svcs.map(s => (
              <div key={s.name} className="flex items-center justify-between py-0.5 text-xs">
                <span>{s.name}</span>
                <span className={`w-2 h-2 rounded-full ${DOT[s.status] ?? "bg-gray-400"}`} />
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
