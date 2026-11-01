"use client";

interface ModuleInfo { name: string; services: number; status: string; description: string; }
interface GrandSummaryDashProps { modules: ModuleInfo[]; totalServices: number;
  totalComponents: number; allOperational: boolean; }

export function GrandSummaryDash({ modules, totalServices, totalComponents, allOperational }: GrandSummaryDashProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🌐 Platform Overview</h3>
        <span className={`text-xs font-bold ${allOperational ? "text-green-600" : "text-yellow-600"}`}>
          {allOperational ? "✅ All Operational" : "⚠ Issues Detected"} · {totalServices} svcs · {totalComponents} comps
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {modules.map(m => (
          <div key={m.name} className="flex items-center justify-between px-4 py-2 text-xs">
            <div>
              <span className="font-semibold">{m.name}</span>
              <span className="text-gray-400 ml-2">{m.description}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-gray-400">{m.services} svcs</span>
              <span className={`w-2 h-2 rounded-full ${m.status === "operational" ? "bg-green-500" : "bg-yellow-500"}`} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
