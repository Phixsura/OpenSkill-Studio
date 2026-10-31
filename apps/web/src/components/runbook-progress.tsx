"use client";

interface RunbookStep { index: number; title: string; command: string; status: string; output: string; }
interface RunbookProgressProps { name: string; steps: RunbookStep[]; status: string;
  completed: number; total: number; onExecute: (index: number) => void; }

const STEP_ICON: Record<string, string> = { pending: "⬜", passed: "✅", failed: "❌" };

export function RunbookProgress({ name, steps, status, completed, total, onExecute }: RunbookProgressProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">📋 {name}</h3>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">{completed}/{total}</span>
          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
            status === "completed" ? "bg-green-100 text-green-700" :
            status === "failed" ? "bg-red-100 text-red-700" :
            status === "in_progress" ? "bg-blue-100 text-blue-700" : "bg-gray-100 text-gray-600"
          }`}>{status.replace("_", " ")}</span>
        </div>
      </div>
      <div className="space-y-2">
        {steps.map(s => (
          <div key={s.index} className="flex items-center gap-3 bg-gray-50 dark:bg-gray-800 rounded-lg px-3 py-2">
            <span>{STEP_ICON[s.status] || "⬜"}</span>
            <div className="flex-1">
              <p className="text-sm font-medium">{s.title}</p>
              {s.command && <p className="text-xs font-mono text-gray-400">{s.command}</p>}
              {s.output && <p className="text-xs text-gray-500 mt-0.5">{s.output}</p>}
            </div>
            {s.status === "pending" && (
              <button onClick={() => onExecute(s.index)}
                className="text-xs px-2 py-1 bg-blue-600 text-white rounded hover:bg-blue-700">Run</button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
