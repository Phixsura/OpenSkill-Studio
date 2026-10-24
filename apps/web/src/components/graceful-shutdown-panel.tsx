"use client";

interface GracefulShutdownPanelProps { state: string; activeConnections: number;
  drainSeconds: number; batches?: { batch: number; instances: string[]; size: number }[]; }

const STATE_STYLE: Record<string, string> = {
  running: "text-green-600", draining: "text-yellow-600", stopped: "text-gray-500",
};

export function GracefulShutdownPanel({ state, activeConnections, drainSeconds, batches }: GracefulShutdownPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔌 Graceful Shutdown</h3>
        <span className={`text-xs font-bold uppercase ${STATE_STYLE[state] ?? ""}`}>{state}</span>
      </div>
      <div className="grid grid-cols-2 gap-3 p-4 text-xs">
        <div><span className="text-gray-400">Active</span><div className="font-bold text-lg">{activeConnections}</div></div>
        <div><span className="text-gray-400">Drain Window</span><div className="font-bold text-lg">{drainSeconds}s</div></div>
      </div>
      {batches && batches.length > 0 && (
        <div className="border-t dark:border-gray-700 p-4">
          <div className="text-xs text-gray-400 mb-2">Rolling Restart Plan</div>
          {batches.map(b => (
            <div key={b.batch} className="text-xs font-mono mb-1">Batch {b.batch}: {b.instances.join(", ")}</div>
          ))}
        </div>
      )}
    </div>
  );
}
