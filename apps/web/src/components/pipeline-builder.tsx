"use client";

interface PipelineStep { name: string; action: string; field?: string; }
interface PipelineBuilderProps { name: string; steps: PipelineStep[]; status: string;
  inputCount: number; outputCount: number; onRun: () => void; }

const ACTION_ICONS: Record<string, string> = {
  filter: "🔍", map: "🔄", sort: "↕️", aggregate: "📊", passthrough: "➡️",
};

export function PipelineBuilder({ name, steps, status, inputCount, outputCount, onRun }: PipelineBuilderProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <div>
          <h3 className="font-semibold text-sm">🔧 {name}</h3>
          <div className="text-xs text-gray-400 mt-0.5">{steps.length} steps · {inputCount} → {outputCount} records</div>
        </div>
        <button onClick={onRun} className={`px-3 py-1 text-xs rounded-lg ${status === "completed" ? "bg-green-500" : "bg-blue-500"} text-white`}>
          {status === "completed" ? "✓ Done" : "Run"}
        </button>
      </div>
      <div className="p-4">
        <div className="flex items-center gap-2 flex-wrap">
          {steps.map((s, i) => (
            <div key={i} className="flex items-center gap-1">
              <span className="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-800 rounded-lg border dark:border-gray-700">
                {ACTION_ICONS[s.action] ?? "⚙️"} {s.name}
              </span>
              {i < steps.length - 1 && <span className="text-gray-400">→</span>}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
