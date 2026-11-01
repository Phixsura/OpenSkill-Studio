"use client";

interface RunbookStep { index: number; title: string; description: string; type: string; status: string; }
interface RunbookExecutorViewProps { name: string; steps: RunbookStep[];
  progressPct: number; status: string; onExecuteStep: (index: number) => void; }

const STEP_ICONS: Record<string, string> = {
  pending: "⬜", success: "✅", failed: "❌", skipped: "⏭️",
};

export function RunbookExecutorView({ name, steps, progressPct, status, onExecuteStep }: RunbookExecutorViewProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <div>
          <h3 className="font-semibold text-sm">📋 {name}</h3>
          <div className="text-xs text-gray-400 mt-0.5 capitalize">{status} · {progressPct}%</div>
        </div>
        <div className="w-20 h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
          <div className={`h-full rounded-full ${progressPct === 100 ? "bg-green-500" : "bg-blue-500"}`}
            style={{ width: `${progressPct}%` }} />
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {steps.map(s => (
          <div key={s.index} className="flex items-center justify-between px-4 py-2.5">
            <div className="flex items-center gap-2">
              <span>{STEP_ICONS[s.status] ?? "⬜"}</span>
              <div>
                <div className="text-sm">{s.title}</div>
                <div className="text-[10px] text-gray-400">{s.type}</div>
              </div>
            </div>
            {s.status === "pending" && (
              <button onClick={() => onExecuteStep(s.index)}
                className="px-2 py-1 text-xs bg-blue-500 text-white rounded">▶ Run</button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
