"use client";
interface TimeoutStep { service: string; timeoutMs: number; cumulativeMs: number; }
interface DepTimeoutPanelProps { chainTimeoutMs: number; steps: TimeoutStep[]; depth: number; valid: boolean; }
export function DepTimeoutPanel({ chainTimeoutMs, steps, depth, valid }: DepTimeoutPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⏱️ Chain Timeouts</h3>
        <span className={`text-xs font-bold ${valid ? "text-green-600" : "text-red-500"}`}>
          {chainTimeoutMs}ms total · depth {depth} · {valid ? "✅ valid" : "❌ invalid"}
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {steps.map(s => (
          <div key={s.service} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{s.service}</span>
            <span className="text-gray-400">{s.timeoutMs}ms (cumulative: {s.cumulativeMs}ms)</span>
          </div>
        ))}
      </div>
    </div>
  );
}
