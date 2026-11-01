"use client";

interface Container { name: string; cpuPct: number; memoryPct: number;
  restartCount: number; healthy: boolean; issues: string[]; }
interface ContainerHealthGridProps { containers: Container[]; healthy: number;
  unhealthy: number; avgCpu: number; }

export function ContainerHealthGrid({ containers, healthy, unhealthy, avgCpu }: ContainerHealthGridProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🐳 Container Health</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-green-600">{healthy}✓</span>
          {unhealthy > 0 && <span className="text-red-500">{unhealthy}✗</span>}
          <span className="text-gray-400">avg CPU {avgCpu}%</span>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {containers.map(c => (
          <div key={c.name} className="px-4 py-2.5">
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2">
                <span className={`w-2 h-2 rounded-full ${c.healthy ? "bg-green-500" : "bg-red-500"}`} />
                <span className="text-sm font-mono">{c.name}</span>
              </div>
              <div className="flex gap-3 text-xs text-gray-400">
                <span>CPU {c.cpuPct}%</span>
                <span>Mem {c.memoryPct}%</span>
                <span>↻{c.restartCount}</span>
              </div>
            </div>
            {c.issues.length > 0 && c.issues.map((issue, i) => (
              <div key={i} className="text-[10px] text-red-500 pl-4">⚠ {issue}</div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
