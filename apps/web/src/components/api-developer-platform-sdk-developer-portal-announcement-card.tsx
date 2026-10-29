"use client";

interface AnnInfo { announcement_id: string; title: string; body: string; severity: string; views: number; }
interface Props { announcements: AnnInfo[]; appName: string; }

const sevBanner: Record<string, string> = { info: "bg-blue-50 border-blue-200 text-blue-700", warning: "bg-yellow-50 border-yellow-200 text-yellow-700", critical: "bg-red-50 border-red-200 text-red-700", maintenance: "bg-purple-50 border-purple-200 text-purple-700" };
const sevIcon: Record<string, string> = { info: "ℹ️", warning: "⚠️", critical: "🚨", maintenance: "🔧" };

export default function APIDeveloperPlatformSDKDeveloperPortalAnnouncementCard({ announcements, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📢 Announcements</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {announcements.length} active</p>
      </div>
      {announcements.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No announcements</p>
      ) : (
        <div className="space-y-2">
          {announcements.map((a) => (
            <div key={a.announcement_id} className={`rounded-lg border p-2 ${sevBanner[a.severity] ?? ""}`}>
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium">{sevIcon[a.severity]} {a.title}</span>
                <span className="text-[10px] opacity-60">{a.views} views</span>
              </div>
              <p className="mt-0.5 text-[10px] opacity-80 truncate">{a.body}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
