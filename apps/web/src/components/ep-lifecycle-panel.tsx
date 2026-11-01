"use client";
interface EpState { path: string; state: string; version: string; owner: string; }
interface EpLifecyclePanelProps { endpoints: EpState[]; byState: Record<string, number>; }
const STATE_DOT: Record<string, string> = { draft: "bg-gray-400", active: "bg-green-500", deprecated: "bg-yellow-500", sunset: "bg-orange-500", removed: "bg-red-500" };
export function EpLifecyclePanel({ endpoints, byState }: EpLifecyclePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔄 Endpoint Lifecycle</h3>
        <div className="flex gap-2 text-[10px]">
          {Object.entries(byState).map(([s, c]) => (
            <span key={s} className="text-gray-400">{s}: {c}</span>
          ))}
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {endpoints.map(e => (
          <div key={e.path} className="flex justify-between px-4 py-1.5 text-xs">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${STATE_DOT[e.state] ?? "bg-gray-400"}`} />
              <span className="font-mono">{e.path}</span>
            </div>
            <span className="text-gray-400">{e.state} · {e.version} · {e.owner}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
