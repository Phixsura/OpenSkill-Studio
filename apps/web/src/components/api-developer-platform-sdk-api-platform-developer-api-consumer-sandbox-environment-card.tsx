"use client";

interface SandboxInfo { sandbox_id: string; consumer_id: string; status: string; request_count: number; request_limit: number; data_seeded: boolean; reset_count: number; }
interface Props { sandboxes: SandboxInfo[]; appName: string; }

const statusStyle: Record<string, string> = { active: "text-green-600 dark:text-green-400", paused: "text-yellow-600 dark:text-yellow-400", expired: "text-red-600 dark:text-red-400" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerSandboxEnvironmentCard({ sandboxes, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏖️ Sandboxes</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {sandboxes.length} environments</p>
      </div>
      {sandboxes.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No sandboxes</p>
      ) : (
        <div className="space-y-2">
          {sandboxes.map((s) => (
            <div key={s.sandbox_id} className="text-[11px]">
              <div className="flex items-center justify-between">
                <span className="text-gray-700 dark:text-gray-300">{s.consumer_id} / {s.sandbox_id}</span>
                <span className={statusStyle[s.status] ?? "text-gray-400"}>{s.status}</span>
              </div>
              <div className="mt-0.5 flex justify-between text-[10px] text-gray-400">
                <span>{s.request_count.toLocaleString()}/{s.request_limit.toLocaleString()} reqs</span>
                <span>{s.data_seeded ? "🌱 seeded" : "empty"} · {s.reset_count}× reset</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
