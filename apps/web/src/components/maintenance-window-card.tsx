"use client";

interface WindowInfo {
  window_id: string;
  title: string;
  status: "scheduled" | "active" | "completed" | "cancelled";
  duration_minutes: number;
  affected_services: string[];
  message: string;
}

interface MaintenanceWindowCardProps {
  windows: WindowInfo[];
  isInMaintenance: boolean;
  appName: string;
}

const statusStyle: Record<string, string> = {
  scheduled: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
  active: "bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300",
  completed: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
  cancelled: "bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400",
};

export default function MaintenanceWindowCard({
  windows,
  isInMaintenance,
  appName,
}: MaintenanceWindowCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            🔧 Maintenance Windows
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {isInMaintenance ? (
          <span className="rounded bg-orange-100 px-2 py-0.5 text-[11px] font-medium text-orange-700 dark:bg-orange-900 dark:text-orange-300">
            In Maintenance
          </span>
        ) : (
          <span className="text-xs text-gray-400">{windows.length} windows</span>
        )}
      </div>

      {windows.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No maintenance windows</p>
      ) : (
        <div className="space-y-2">
          {windows.map((w) => (
            <div
              key={w.window_id}
              className="rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-gray-800 dark:text-gray-200">
                  {w.title}
                </span>
                <span
                  className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${statusStyle[w.status]}`}
                >
                  {w.status}
                </span>
              </div>
              <div className="mt-1 flex items-center justify-between text-[10px] text-gray-400">
                <span>{w.duration_minutes} min</span>
                {w.affected_services.length > 0 && <span>{w.affected_services.join(", ")}</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
