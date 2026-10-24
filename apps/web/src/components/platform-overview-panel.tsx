"use client";
interface Module { name: string; status: string; services: number; }
interface PlatformOverviewPanelProps { overall: string; modules: Module[];
  healthPct: number; totalServices: number; totalComponents: number; }
const OV_STYLE: Record<string, string> = { operational: "bg-green-500", degraded: "bg-yellow-500", outage: "bg-red-500" };
const DOT: Record<string, string> = { operational: "bg-green-500", degraded: "bg-yellow-500", outage: "bg-red-500" };
export function PlatformOverviewPanel({ overall, modules, healthPct, totalServices, totalComponents }: PlatformOverviewPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`p-4 text-white text-center ${OV_STYLE[overall] ?? "bg-gray-500"}`}>
        <h2 className="text-lg font-black">OpenSkill Platform: {overall.toUpperCase()}</h2>
        <p className="text-xs opacity-80">{healthPct}% healthy · {totalServices} services · {totalComponents} components</p>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {modules.map(m => (
          <div key={m.name} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${DOT[m.status] ?? "bg-gray-400"}`} />
              <span>{m.name}</span>
            </div>
            <span className="text-gray-400">{m.services} svcs</span>
          </div>
        ))}
      </div>
    </div>
  );
}
