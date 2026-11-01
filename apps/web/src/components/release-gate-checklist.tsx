"use client";

interface Gate { id: string; label: string; icon: string; required: boolean; passed: boolean; status: string; }
interface ReleaseGateChecklistProps { gates: Gate[]; releaseReady: boolean; blocking: string[];
  onDeploy: () => void; }

export function ReleaseGateChecklist({ gates, releaseReady, blocking, onDeploy }: ReleaseGateChecklistProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Release Gates</h2>
        <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${releaseReady ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-red-100 text-red-700 dark:bg-red-900/30"}`}>
          {releaseReady ? "✅ Ready" : `❌ ${blocking.length} blocking`}
        </span>
      </div>
      <div className="space-y-1.5">
        {gates.map(g => (
          <div key={g.id} className={`flex items-center gap-3 rounded-lg border px-3 py-2 ${g.status === "fail" ? "border-red-200 dark:border-red-800" : "dark:border-gray-700"}`}>
            <span>{g.passed ? "✅" : g.required ? "❌" : "⏭️"}</span>
            <span className="text-lg">{g.icon}</span>
            <span className={`flex-1 text-sm ${g.passed ? "" : g.required ? "font-medium text-red-600" : "text-gray-400"}`}>
              {g.label}
            </span>
            {g.required && <span className="text-[10px] text-gray-400">Required</span>}
          </div>
        ))}
      </div>
      <button onClick={onDeploy} disabled={!releaseReady}
        className="w-full rounded-lg bg-green-600 py-2.5 text-sm font-semibold text-white disabled:opacity-50">
        {releaseReady ? "🚀 Deploy to Production" : "Fix blocking gates to deploy"}
      </button>
    </div>
  );
}
