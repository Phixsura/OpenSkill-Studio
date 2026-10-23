"use client";

interface LogLine { step: string; status: string; icon: string; durationMs: number; output: string; }
interface DeployLogViewerProps { lines: LogLine[]; overall: string;
  durationDisplay: string; completed: number; totalSteps: number; }

export function DeployLogViewer({ lines, overall, durationDisplay, completed, totalSteps }: DeployLogViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📋 Deploy Log</h3>
        <div className="flex gap-2 text-xs">
          <span>{completed}/{totalSteps} steps</span>
          <span className="text-gray-400">{durationDisplay}</span>
          <span className={`px-2 py-0.5 rounded-full ${
            overall === "success" ? "bg-green-100 text-green-700" :
            overall === "failed" ? "bg-red-100 text-red-700" : "bg-blue-100 text-blue-700"
          }`}>{overall}</span>
        </div>
      </div>
      <div className="bg-gray-900 p-4 font-mono text-xs space-y-2">
        {lines.map((l, i) => (
          <div key={i}>
            <div className="flex items-center gap-2 text-gray-300">
              <span>{l.icon}</span>
              <span className="text-white font-medium">{l.step}</span>
              <span className="text-gray-500">({l.durationMs}ms)</span>
            </div>
            {l.output && <p className="text-gray-500 ml-6">{l.output}</p>}
          </div>
        ))}
      </div>
    </div>
  );
}
