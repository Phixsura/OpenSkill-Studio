"use client";

interface SandboxInfo { sandbox_id: string; developer_id: string; base_url: string; request_count: number; active: boolean; }
interface Props { sandboxes: SandboxInfo[]; appName: string; }

export default function APIDeveloperSandboxCard({ sandboxes, appName }: Props) {
  const active = sandboxes.filter((s) => s.active).length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🧪 Dev Sandboxes</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{active}/{sandboxes.length} active</span>
      </div>
      {sandboxes.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No sandboxes</p>
      ) : (
        <div className="space-y-1.5">
          {sandboxes.map((s) => (
            <div key={s.sandbox_id} className={`flex items-center justify-between text-[11px] ${!s.active ? "opacity-50" : ""}`}>
              <div>
                <span className="text-gray-700 dark:text-gray-300">{s.developer_id}</span>
                <p className="text-[9px] text-gray-400">{s.base_url}</p>
              </div>
              <span className="text-gray-400">{s.request_count} reqs</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
