"use client";

interface RecoveryStep { step: number; action: string; status: string; }
interface CrashRecoveryPanelProps { crashType: string; steps: RecoveryStep[];
  autoRecovery: boolean; onExecuteStep: (step: number) => void; onRollback: () => void; }

const crashIcon: Record<string, string> = {
  oom: "💾", deadlock: "🔒", unresponsive: "⏳", boot_failure: "🔴",
};

export function CrashRecoveryPanel({ crashType, steps, autoRecovery, onExecuteStep, onRollback }: CrashRecoveryPanelProps) {
  return (
    <div className="space-y-4 rounded-lg border border-red-300 p-5 dark:border-red-700">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-2xl">{crashIcon[crashType] ?? "💥"}</span>
          <div>
            <h2 className="text-lg font-semibold text-red-600">Crash Recovery</h2>
            <p className="text-xs text-gray-400 capitalize">{crashType.replace("_", " ")} detected</p>
          </div>
        </div>
        {autoRecovery && <span className="rounded bg-blue-100 px-2 py-0.5 text-xs text-blue-700 dark:bg-blue-900/30">Auto</span>}
      </div>
      <div className="space-y-2">
        {steps.map(s => (
          <div key={s.step} className="flex items-center justify-between rounded border px-3 py-2 dark:border-gray-700">
            <div className="flex items-center gap-2">
              <span className={`flex h-6 w-6 items-center justify-center rounded-full text-xs font-bold ${s.status === "completed" ? "bg-green-500 text-white" : "border dark:border-gray-600"}`}>
                {s.status === "completed" ? "✓" : s.step}
              </span>
              <span className="text-sm">{s.action}</span>
            </div>
            {s.status === "pending" && (
              <button onClick={() => onExecuteStep(s.step)} className="rounded bg-blue-600 px-2 py-1 text-xs text-white">Execute</button>
            )}
          </div>
        ))}
      </div>
      <button onClick={onRollback} className="w-full rounded border border-orange-300 py-2 text-sm text-orange-600">
        ⏪ Rollback to Previous Version
      </button>
    </div>
  );
}
