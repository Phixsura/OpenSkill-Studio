"use client";

interface NoticeInfo { notice_id: string; method: string; path: string; message: string; sunset_date: string; replacement: string; acknowledged_count: number; }
interface Props { notices: NoticeInfo[]; appName: string; }

export default function APIEndpointDeprecationNoticeCard({ notices, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⚠️ Deprecation Notices</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{notices.length} notices</span>
      </div>
      {notices.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No deprecation notices</p>
      ) : (
        <div className="space-y-2">
          {notices.map((n) => (
            <div key={n.notice_id} className="rounded-lg border border-yellow-200 bg-yellow-50 px-3 py-2 dark:border-yellow-800 dark:bg-yellow-900/20">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  <span className="rounded bg-gray-200 px-1 py-0.5 text-[9px] text-gray-600 dark:bg-gray-700">{n.method}</span>
                  <span className="font-mono text-xs text-gray-700 dark:text-gray-300">{n.path}</span>
                </div>
                <span className="text-[10px] text-orange-600">sunset {n.sunset_date}</span>
              </div>
              {n.replacement && <p className="mt-0.5 text-[10px] text-gray-500">→ {n.replacement}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
