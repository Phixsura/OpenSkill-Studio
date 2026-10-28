"use client";

interface WindowInfo {
  window_id: string;
  title: string;
  status: "scheduled" | "active" | "completed" | "cancelled";
  start_at: string;
  end_at: string;
  affected_services: string[];
}

interface MaintenanceWindowCardProps {
  windows: WindowInfo[];
  inMaintenance: boolean;
  appName: string;
}

const STATUS_STYLES: Record<string, { icon: string; text: string }> = {
  scheduled: { icon: "📅", text: "text-blue-600 dark:text-blue-400" },
  active: { icon: "🔧", text: "text-yellow-600 dark:text-yellow-400" },
  completed: { icon: "✅", text: "text-green-600 dark:text-green-400" },
  cancelled: { icon: "🚫", text: "text-gray-400" },
};

function formatTime(iso: string): string {
  return new Date(iso).toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function MaintenanceWindowCard({
  windows,
  inMaintenance,
  appName,
}: MaintenanceWindowCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Maintenance</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {inMaintenance ? (
          <span className="rounded-full bg-yellow-100 px-2 py-0.5 text-xs font-medium text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400">
            🔧 In Progress
          </span>
        ) : (
          <span className="text-xs text-gray-400">{windows.length} windows</span>
        )}
      </div>

      {windows.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No maintenance windows</p>
      ) : (
        <div className="space-y-2">
          {windows.map((w) => {
            const st = STATUS_STYLES[w.status] ?? STATUS_STYLES.scheduled;
            return (
              <div
                key={w.window_id}
                className={`rounded-lg border px-3 py-2 ${
                  w.status === "active"
                    ? "border-yellow-200 bg-yellow-50/50 dark:border-yellow-900/50 dark:bg-yellow-950/10"
                    : "border-gray-100 dark:border-gray-800"
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span>{st.icon}</span>
                    <span className="text-sm text-gray-800 dark:text-gray-200">{w.title}</span>
                  </div>
                  <span className={`text-xs font-medium capitalize ${st.text}`}>{w.status}</span>
                </div>
                <div className="mt-1 text-[11px] text-gray-400">
                  {formatTime(w.start_at)} – {formatTime(w.end_at)}
                </div>
                {w.affected_services.length > 0 && (
                  <div className="mt-1 flex flex-wrap gap-1">
                    {w.affected_services.map((s) => (
                      <span
                        key={s}
                        className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800"
                      >
                        {s}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
