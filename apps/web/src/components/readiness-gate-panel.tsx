"use client";
interface Check { name: string; ready: boolean; critical: boolean; }
interface ReadinessGatePanelProps { checks: Check[]; ready: boolean; passed: number; total: number; }
export function ReadinessGatePanel({ checks, ready, passed, total }: ReadinessGatePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🚦 Readiness Gate</h3>
        <span className={`text-xs font-bold ${ready ? "text-green-600" : "text-red-500"}`}>
          {ready ? "✅ Ready" : "❌ Not Ready"} · {passed}/{total}
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {checks.map(c => (
          <div key={c.name} className="flex justify-between px-4 py-1.5 text-xs">
            <div className="flex items-center gap-2">
              <span>{c.ready ? "✅" : "❌"}</span>
              <span className={!c.ready && c.critical ? "text-red-600 font-bold" : ""}>{c.name}</span>
            </div>
            <span className="text-gray-400">{c.critical ? "critical" : "optional"}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
