"use client";
interface ConnInfo { name: string; type: string; healthy: boolean; latencyMs: number; }
interface ConnHealthPanelProps { connections: ConnInfo[]; healthy: number; total: number; }
const DOT: Record<string, string> = { true: "bg-green-500", false: "bg-red-500" };
export function ConnHealthPanel({ connections, healthy, total }: ConnHealthPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔌 Connection Health</h3>
        <span className={`text-xs font-bold ${healthy === total ? "text-green-600" : "text-yellow-600"}`}>
          {healthy}/{total} healthy
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {connections.map(c => (
          <div key={c.name} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${c.healthy ? "bg-green-500" : "bg-red-500"}`} />
              <span className="font-mono">{c.name}</span>
              <span className="text-gray-400">{c.type}</span>
            </div>
            <span className="text-gray-400">{c.latencyMs}ms</span>
          </div>
        ))}
      </div>
    </div>
  );
}
