"use client";
interface HealthDashAggPanelProps { status: string; score: number; checks: Record<string, boolean>; passing: number; totalChecks: number; }
const STATUS_COLOR: Record<string, string> = { healthy: "bg-green-500", degraded: "bg-yellow-500", critical: "bg-red-500" };
export function HealthDashAggPanel({ status, score, checks, passing, totalChecks }: HealthDashAggPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`p-4 text-white text-center ${STATUS_COLOR[status] ?? "bg-gray-500"}`}>
        <div className="text-3xl font-black">{score}</div>
        <div className="text-sm">{status.toUpperCase()} — {passing}/{totalChecks} checks passing</div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {Object.entries(checks).map(([name, ok]) => (
          <div key={name} className="flex justify-between px-4 py-1.5 text-xs">
            <span>{name.replace("_", " ")}</span>
            <span>{ok ? "✅" : "❌"}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
