"use client";

interface IntInfo { integration_id: string; name: string; provider: string; status: string; event_count: number; }
interface Props { integrations: IntInfo[]; appName: string; }

const sDot: Record<string, string> = { connected: "bg-green-500", disconnected: "bg-gray-400", error: "bg-red-500" };

export default function APIDeveloperAPIIntegrationHubCard({ integrations, appName }: Props) {
  const connected = integrations.filter((i) => i.status === "connected").length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔌 Integration Hub</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{connected}/{integrations.length} connected</span>
      </div>
      {integrations.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No integrations</p>
      ) : (
        <div className="space-y-1">
          {integrations.map((i) => (
            <div key={i.integration_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`h-2 w-2 rounded-full ${sDot[i.status] ?? "bg-gray-400"}`} />
                <span className="text-gray-700 dark:text-gray-300">{i.name}</span>
                <span className="rounded bg-gray-100 px-1 py-0.5 text-[8px] text-gray-500 dark:bg-gray-800">{i.provider}</span>
              </div>
              <span className="text-gray-400">{i.event_count} events</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
