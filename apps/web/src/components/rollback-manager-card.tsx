"use client";

interface RollbackRecordInfo {
  rollback_id: string;
  from_version: string;
  to_version: string;
  reason: string;
  status: "pending" | "in_progress" | "completed" | "failed";
  initiated_by: string;
}

interface RollbackManagerCardProps {
  currentVersion: string | null;
  rollbacks: RollbackRecordInfo[];
  appName: string;
}

const statusStyle: Record<string, string> = {
  pending: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
  in_progress: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
  completed: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
  failed: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
};

export default function RollbackManagerCard({
  currentVersion,
  rollbacks,
  appName,
}: RollbackManagerCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            ⏪ Rollback Manager
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {currentVersion && (
          <span className="rounded bg-gray-100 px-2 py-0.5 font-mono text-xs text-gray-700 dark:bg-gray-800 dark:text-gray-300">
            {currentVersion}
          </span>
        )}
      </div>

      {rollbacks.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No rollbacks</p>
      ) : (
        <div className="space-y-2">
          {rollbacks.map((r) => (
            <div
              key={r.rollback_id}
              className="rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-700 dark:text-gray-300">
                  {r.from_version} → {r.to_version}
                </span>
                <span
                  className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${statusStyle[r.status] ?? ""}`}
                >
                  {r.status.replace("_", " ")}
                </span>
              </div>
              <div className="mt-0.5 flex justify-between text-[10px] text-gray-400">
                {r.reason && <span>{r.reason}</span>}
                {r.initiated_by && <span>by {r.initiated_by}</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
