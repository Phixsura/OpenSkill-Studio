"use client";

interface PodInfo { name: string; status: string; restarts: number; cpuPct: number; memPct: number; }
interface PodHealthGridProps { pods: PodInfo[]; health: string; running: number;
  failed: number; totalRestarts: number; }

const STATUS_COLOR: Record<string, string> = {
  Running: "bg-green-500", Pending: "bg-yellow-500", Failed: "bg-red-500",
  CrashLoopBackOff: "bg-red-600", Error: "bg-red-500",
};

export function PodHealthGrid({ pods, health, running, failed, totalRestarts }: PodHealthGridProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">☸️ Pod Health</h3>
        <div className="flex gap-2">
          <span className="text-xs text-gray-400">{running} running · {failed} failed</span>
          <span className={`text-xs px-2 py-0.5 rounded-full ${health === "healthy" ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>{health}</span>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-2">
        {pods.map(p => (
          <div key={p.name} className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
            <div className="flex items-center gap-2 mb-1">
              <span className={`w-2 h-2 rounded-full ${STATUS_COLOR[p.status] || "bg-gray-400"}`} />
              <span className="text-xs font-mono truncate">{p.name}</span>
            </div>
            <div className="flex gap-3 text-xs text-gray-400">
              <span>CPU {p.cpuPct}%</span>
              <span>MEM {p.memPct}%</span>
              {p.restarts > 0 && <span className="text-yellow-500">↻{p.restarts}</span>}
            </div>
          </div>
        ))}
      </div>
      {totalRestarts > 0 && <p className="text-xs text-yellow-500 mt-2">{totalRestarts} total restarts</p>}
    </div>
  );
}
