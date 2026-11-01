"use client";

interface AnnInfo { announcement_id: string; title: string; body: string; severity: string; active: boolean; }
interface Props { announcements: AnnInfo[]; appName: string; }

const sevBg: Record<string, string> = {
  info: "bg-blue-50 border-blue-200 dark:bg-blue-900/20 dark:border-blue-800",
  warning: "bg-yellow-50 border-yellow-200 dark:bg-yellow-900/20 dark:border-yellow-800",
  critical: "bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-800",
};

export default function APIPlatformAnnouncementCard({ announcements, appName }: Props) {
  const active = announcements.filter((a) => a.active);
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📢 Announcements</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{active.length} active</span>
      </div>
      {active.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No active announcements</p>
      ) : (
        <div className="space-y-2">
          {active.map((a) => (
            <div key={a.announcement_id} className={`rounded-lg border px-3 py-2 ${sevBg[a.severity] ?? ""}`}>
              <p className="text-xs font-medium text-gray-800 dark:text-gray-200">{a.title}</p>
              <p className="mt-0.5 text-[10px] text-gray-600 dark:text-gray-400">{a.body}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
