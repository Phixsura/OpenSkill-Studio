"use client";
interface Requirement { name: string; category: string; met: boolean; severity: string; }
interface OpsReadyPanelProps { ready: boolean; score: number; met: number; total: number;
  blocking: string[]; requirements: Requirement[]; }
export function OpsReadyPanel({ ready, score, met, total, blocking, requirements }: OpsReadyPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`p-4 text-white text-center ${ready ? "bg-green-500" : "bg-red-500"}`}>
        <div className="text-2xl font-black">{score}%</div>
        <div className="text-sm">{ready ? "✅ OPERATIONALLY READY" : "❌ NOT READY"} · {met}/{total}</div>
      </div>
      {blocking.length > 0 && (
        <div className="px-4 py-2 text-xs text-red-600 bg-red-50 dark:bg-red-950">
          Blocking: {blocking.join(", ")}
        </div>
      )}
      <div className="divide-y dark:divide-gray-700">
        {requirements.map(r => (
          <div key={r.name} className="flex justify-between px-4 py-1 text-xs">
            <div className="flex items-center gap-1">
              <span>{r.met ? "✅" : "❌"}</span>
              <span className={r.met ? "" : r.severity === "required" ? "text-red-600" : "text-gray-400"}>{r.name}</span>
            </div>
            <span className="text-gray-400">{r.category} · {r.severity}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
