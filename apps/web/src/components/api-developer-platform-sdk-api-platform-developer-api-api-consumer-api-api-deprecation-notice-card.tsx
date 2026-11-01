"use client";

interface NoticeInfo { notice_id: string; endpoint: string; method: string; urgency: string; message: string; sunset_date: string; acknowledged_count: number; }
interface Props { notices: NoticeInfo[]; urgentCount: number; appName: string; }

const urgencyStyle: Record<string, string> = { info: "text-blue-600 dark:text-blue-400", warning: "text-yellow-600 dark:text-yellow-400", urgent: "text-orange-600 dark:text-orange-400", final: "text-red-600 dark:text-red-400" };
const urgencyEmoji: Record<string, string> = { info: "ℹ️", warning: "⚠️", urgent: "🔶", final: "🔴" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiDeprecationNoticeCard({ notices, urgentCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📢 Deprecation Notices</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {notices.length} notices</p>
        </div>
        {urgentCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">🔴 {urgentCount} urgent</span>}
      </div>
      {notices.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No deprecation notices</p>
      ) : (
        <div className="space-y-1.5">
          {notices.map((n) => (
            <div key={n.notice_id} className="text-[11px]">
              <div className="flex items-center justify-between">
                <span className="text-gray-700 dark:text-gray-300">{urgencyEmoji[n.urgency]} {n.method} {n.endpoint}</span>
                <span className={urgencyStyle[n.urgency] ?? "text-gray-400"}>sunset: {n.sunset_date}</span>
              </div>
              <div className="text-[10px] text-gray-400">{n.message}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
