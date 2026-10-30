"use client";

interface Sandbox { id: string; name: string; status: string; rps: number; mockResponses: boolean; requestCount: number; }
interface Props { sandboxes: Sandbox[]; consumerId: string; appName: string; }

const statusColors: Record<string, string> = {
  active: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  expired: "bg-gray-200 text-gray-500 dark:bg-gray-700 dark:text-gray-400",
  destroyed: "bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400",
};

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerSandboxEnvironmentCard({ sandboxes, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🧪 Sandbox Environments</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
      </div>
      {sandboxes.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No sandboxes</p>
      ) : (
        <div className="space-y-2">
          {sandboxes.map((s) => (
            <div key={s.id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{s.name}</span>
                <span className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${statusColors[s.status] ?? ""}`}>{s.status}</span>
              </div>
              <div className="mt-0.5 text-[10px] text-gray-400">
                {s.rps} rps · {s.mockResponses ? "Mocked" : "Live"} · {s.requestCount} requests
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
