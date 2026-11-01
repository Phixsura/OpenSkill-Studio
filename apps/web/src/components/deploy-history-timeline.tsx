"use client";

interface DeployEntry { version: string; commit: string; deployer: string; status: string;
  index: number; rollbackFrom?: string; }
interface DeployHistoryTimelineProps { entries: DeployEntry[]; current: string | null;
  onRollback: (index: number) => void; }

const STATUS_STYLE: Record<string, string> = {
  active: "border-green-500 bg-green-50 dark:bg-green-900/20",
  superseded: "border-gray-300 dark:border-gray-600",
  rolled_back: "border-red-300 dark:border-red-700",
};

export function DeployHistoryTimeline({ entries, current, onRollback }: DeployHistoryTimelineProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">🚀 Deploy History</h3>
        {current && <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">Current: {current}</span>}
      </div>
      <div className="space-y-3">
        {entries.map(e => (
          <div key={e.index} className={`border-l-4 rounded-r-lg p-3 ${STATUS_STYLE[e.status] || ""}`}>
            <div className="flex items-center justify-between">
              <div>
                <span className="font-mono text-sm font-bold">v{e.version}</span>
                <span className="text-xs text-gray-400 ml-2">{e.commit.slice(0, 7)}</span>
                <span className="text-xs text-gray-400 ml-2">by {e.deployer}</span>
              </div>
              {e.status !== "active" && (
                <button onClick={() => onRollback(e.index)}
                  className="text-xs px-2 py-1 bg-yellow-100 text-yellow-700 rounded hover:bg-yellow-200">
                  Rollback
                </button>
              )}
            </div>
            {e.rollbackFrom && <p className="text-xs text-gray-400 mt-1">↩ Rolled back from {e.rollbackFrom}</p>}
          </div>
        ))}
      </div>
    </div>
  );
}
