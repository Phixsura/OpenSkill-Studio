"use client";

interface Dep { id: string; name: string; status: string; criticality: string; responseMs: number; }
interface Props { overall: string; dependencies: Dep[]; healthy: number; degraded: number; down: number; appName: string; }

const statusDot: Record<string, string> = { healthy: "bg-green-500", degraded: "bg-amber-500", down: "bg-red-500", unknown: "bg-gray-400" };
const critBadge: Record<string, string> = { required: "text-red-500", optional: "text-gray-400", degraded: "text-amber-500" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiServiceDependencyHealthCard({ overall, dependencies, healthy, degraded, down, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔗 Service Dependencies</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} · {healthy}↑ {degraded}~ {down}↓</p>
        </div>
        <span className={`rounded px-2 py-0.5 text-[10px] font-bold ${overall === "healthy" ? "bg-green-100 text-green-700" : overall === "degraded" ? "bg-amber-100 text-amber-700" : "bg-red-100 text-red-700"}`}>{overall}</span>
      </div>
      {dependencies.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No dependencies</p>
      ) : (
        <div className="space-y-1">
          {dependencies.map((d) => (
            <div key={d.id} className="flex items-center justify-between rounded bg-gray-50 px-2 py-1 text-[11px] dark:bg-gray-800">
              <div className="flex items-center gap-1.5">
                <span className={`h-2 w-2 rounded-full ${statusDot[d.status] ?? "bg-gray-400"}`} />
                <span className="text-gray-700 dark:text-gray-300">{d.name}</span>
                <span className={`text-[9px] ${critBadge[d.criticality] ?? ""}`}>{d.criticality}</span>
              </div>
              <span className="text-[10px] text-gray-400">{d.responseMs}ms</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
