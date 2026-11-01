"use client";
interface Check { name: string; passed: boolean; durationMs: number; }
interface DeployHealthPanelProps { healthy: boolean; checks: Check[]; passed: number; failed: number; totalMs: number; recommendation: string; }
export function DeployHealthPanel({ healthy, checks, passed, failed, totalMs, recommendation }: DeployHealthPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`p-3 text-white text-center text-sm font-bold ${healthy ? "bg-green-500" : "bg-red-500"}`}>
        Post-Deploy: {healthy ? "HEALTHY ✅" : "UNHEALTHY ❌"} · {totalMs}ms · {recommendation}
      </div>
      <div className="divide-y dark:divide-gray-700">
        {checks.map(c => (
          <div key={c.name} className="flex justify-between px-4 py-1.5 text-xs">
            <div className="flex items-center gap-2">
              <span>{c.passed ? "✅" : "❌"}</span>
              <span className={c.passed ? "" : "text-red-600 font-bold"}>{c.name}</span>
            </div>
            <span className="text-gray-400">{c.durationMs}ms</span>
          </div>
        ))}
      </div>
    </div>
  );
}
