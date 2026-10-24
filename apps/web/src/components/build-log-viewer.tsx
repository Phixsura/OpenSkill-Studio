"use client";

interface BuildStep { name: string; status: string; icon: string; durationDisplay: string; outputLines: number; }
interface BuildLogViewerProps { steps: BuildStep[]; overall: string; totalDisplay: string; failedStep: string | null; }

const stepStatus: Record<string, string> = {
  success: "text-green-600", failed: "text-red-600", running: "text-blue-600 animate-pulse", skipped: "text-gray-400",
};

export function BuildLogViewer({ steps, overall, totalDisplay, failedStep }: BuildLogViewerProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Build Log</h3>
        <div className="flex items-center gap-2">
          <span className={`h-2 w-2 rounded-full ${overall === "success" ? "bg-green-500" : "bg-red-500"}`} />
          <span className="text-xs text-gray-400">{totalDisplay}</span>
        </div>
      </div>
      {failedStep && <p className="text-xs text-red-600">❌ Failed at: {failedStep}</p>}
      <div className="space-y-1">
        {steps.map((s, i) => (
          <div key={i} className="flex items-center justify-between rounded-lg border px-4 py-2 dark:border-gray-700">
            <div className="flex items-center gap-2">
              <span>{s.icon}</span>
              <span className="text-sm font-medium">{s.name}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-400">{s.durationDisplay}</span>
              <span className={`text-xs font-medium ${stepStatus[s.status] ?? ""}`}>{s.status}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
