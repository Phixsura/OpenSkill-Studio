"use client";
interface VerifyCheck { check: string; status: string; durationMs: number; message: string; }
interface DeployVerifyPanelProps { success: boolean; verdict: string; checks: VerifyCheck[]; passed: number; total: number; }
export function DeployVerifyPanel({ success, verdict, checks, passed, total }: DeployVerifyPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`p-3 text-white text-center text-sm font-bold ${success ? "bg-green-500" : "bg-red-500"}`}>
        {verdict.replace("_", " ").toUpperCase()} · {passed}/{total} passed
      </div>
      <div className="divide-y dark:divide-gray-700">
        {checks.map(c => (
          <div key={c.check} className="flex justify-between px-4 py-1.5 text-xs">
            <div className="flex items-center gap-2">
              <span>{c.status === "pass" ? "✅" : "❌"}</span>
              <span>{c.check}</span>
            </div>
            <span className="text-gray-400">{c.durationMs}ms{c.message ? ` · ${c.message}` : ""}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
