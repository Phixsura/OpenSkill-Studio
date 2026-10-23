"use client";

interface TrainItem { service: string; version: string; status: string; testsPassed: boolean; }
interface ReleaseTrainTrackerProps { version: string; status: string;
  items: TrainItem[]; approved: number; total: number;
  onApprove: (service: string) => void; onRelease: () => void; }

export function ReleaseTrainTracker({ version, status, items, approved, total, onApprove, onRelease }: ReleaseTrainTrackerProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="font-semibold">🚂 Release Train</h3>
          <p className="text-xs text-gray-400">v{version} · {approved}/{total} approved</p>
        </div>
        <div className="flex gap-2">
          <span className={`text-xs px-2 py-0.5 rounded-full ${
            status === "released" ? "bg-green-100 text-green-700" :
            status === "ready" ? "bg-blue-100 text-blue-700" : "bg-gray-100 text-gray-600"
          }`}>{status}</span>
          {status === "ready" && (
            <button onClick={onRelease} className="text-xs px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700">Release All</button>
          )}
        </div>
      </div>
      <div className="space-y-2">
        {items.map(i => (
          <div key={i.service} className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded-lg px-4 py-2.5">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${i.status === "approved" || i.status === "released" ? "bg-green-500" : "bg-gray-300"}`} />
              <span className="text-sm font-medium">{i.service}</span>
              <span className="text-xs text-gray-400">v{i.version}</span>
            </div>
            {i.status === "pending" && (
              <button onClick={() => onApprove(i.service)}
                className="text-xs px-2 py-1 bg-blue-600 text-white rounded hover:bg-blue-700">Approve</button>
            )}
            {i.status !== "pending" && <span className="text-xs text-green-600">✓ {i.status}</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
