"use client";

interface SandboxInfo { sandbox_id: string; name: string; base_url: string; status: string; request_count: number; }
interface Props { sandboxes: SandboxInfo[]; appName: string; }

const sDot: Record<string, string> = { active: "bg-green-500", paused: "bg-yellow-500", expired: "bg-red-500" };

export default function APIDeveloperAPIApiSandboxEnvironmentCard({ sandboxes, appName }: Props) {
  const activeCount = sandboxes.filter(s => s.status === "active").length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏖️ Sandbox Environments</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {activeCount} active</p>
      </div>
      {sandboxes.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No sandboxes</p>
      ) : (
        <div className="space-y-2">
          {sandboxes.map((s) => (
            <div key={s.sandbox_id} className="rounded-lg bg-gray-50 px-3 py-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <div className="flex items-center gap-1.5">
                  <span className={`h-1.5 w-1.5 rounded-full ${sDot[s.status] ?? "bg-gray-400"}`} />
                  <span className="font-medium text-gray-700 dark:text-gray-300">{s.name}</span>
                </div>
                <span className="text-gray-400">{s.request_count} reqs</span>
              </div>
              <p className="mt-0.5 text-[10px] text-gray-400">{s.base_url}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
