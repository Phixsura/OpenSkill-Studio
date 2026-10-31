"use client";

interface ComponentInfo { component_id: string; name: string; status: string; }
interface Props { components: ComponentInfo[]; overallStatus: string; appName: string; }

const sColor: Record<string, string> = { operational: "bg-green-500", degraded: "bg-yellow-500", partial_outage: "bg-orange-500", major_outage: "bg-red-500", maintenance: "bg-blue-500" };
const sBanner: Record<string, string> = { operational: "bg-green-50 text-green-700 dark:bg-green-900/30", degraded: "bg-yellow-50 text-yellow-700", partial_outage: "bg-orange-50 text-orange-700", major_outage: "bg-red-50 text-red-700", maintenance: "bg-blue-50 text-blue-700" };

export default function APIDeveloperAPIApiStatusPageManagerCard({ components, overallStatus, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📡 Status Page</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
      </div>
      <div className={`mb-3 rounded-lg px-3 py-2 text-center text-[11px] font-bold ${sBanner[overallStatus] ?? ""}`}>
        {overallStatus.replace(/_/g, " ").toUpperCase()}
      </div>
      {components.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No components</p>
      ) : (
        <div className="space-y-1.5">
          {components.map((c) => (
            <div key={c.component_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{c.name}</span>
              <div className="flex items-center gap-1.5">
                <span className={`h-2 w-2 rounded-full ${sColor[c.status] ?? "bg-gray-400"}`} />
                <span className="text-gray-400">{c.status.replace(/_/g, " ")}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
