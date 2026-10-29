"use client";

interface CompInfo { name: string; status: string; }
interface Props { components: CompInfo[]; overall: string; activeIncidents: number; appName: string; }

const sDot: Record<string, string> = { operational: "bg-green-500", degraded: "bg-yellow-500", outage: "bg-red-500", maintenance: "bg-blue-500" };
const oBanner: Record<string, string> = { all_systems_operational: "bg-green-50 text-green-700 dark:bg-green-900/30 dark:text-green-300", partial_degradation: "bg-yellow-50 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300", major_outage: "bg-red-50 text-red-700 dark:bg-red-900/30 dark:text-red-300", maintenance: "bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300" };

export default function APIDeveloperAPISystemStatusCard({ components, overall, activeIncidents, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🟢 System Status</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
      </div>
      <div className={`mb-3 rounded-lg px-3 py-1.5 text-center text-xs font-medium ${oBanner[overall] ?? ""}`}>{overall.replace(/_/g, " ")}</div>
      {components.length > 0 && (
        <div className="space-y-1">
          {components.map((c) => (
            <div key={c.name} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`h-2 w-2 rounded-full ${sDot[c.status] ?? "bg-gray-400"}`} />
                <span className="text-gray-700 dark:text-gray-300">{c.name}</span>
              </div>
              <span className="text-gray-400">{c.status}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
