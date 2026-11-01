"use client";

interface AnalyticsInfo { total_views: number; unique_viewers: number; total_reactions: number; total_comments: number; total_bookmarks: number; engagement_rate: number; most_viewed_version: string; }
interface Props { analytics: AnalyticsInfo; appName: string; }

export default function APIDeveloperChangelogAnalyticsCard({ analytics: a, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Changelog Analytics</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-sm font-bold text-blue-600">{a.engagement_rate}% engagement</span>
      </div>
      <div className="grid grid-cols-3 gap-2 text-center">
        {[
          { l: "Views", v: a.total_views.toLocaleString() },
          { l: "Viewers", v: a.unique_viewers },
          { l: "Reactions", v: a.total_reactions },
          { l: "Comments", v: a.total_comments },
          { l: "Bookmarks", v: a.total_bookmarks },
          { l: "Top Version", v: a.most_viewed_version || "—" },
        ].map((m) => (
          <div key={m.l} className="rounded-lg bg-gray-50 py-1 dark:bg-gray-800">
            <p className="text-xs font-bold text-gray-900 dark:text-gray-100">{m.v}</p>
            <p className="text-[8px] text-gray-500">{m.l}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
