"use client";

interface ChangeEntry { service: string; type: string; title: string; date: string; version: string; }
interface PlatformChangelogFeedProps { entries: ChangeEntry[]; total: number;
  byType: Record<string, number>; }

const TYPE_ICON: Record<string, string> = { feat: "✨", fix: "🐛", perf: "⚡", docs: "📝", changed: "🔄" };
const TYPE_BADGE: Record<string, string> = {
  feat: "bg-green-100 text-green-700", fix: "bg-red-100 text-red-700",
  perf: "bg-blue-100 text-blue-700", docs: "bg-purple-100 text-purple-700",
};

export function PlatformChangelogFeed({ entries, total, byType }: PlatformChangelogFeedProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📋 Platform Changelog</h3>
        <div className="flex gap-2 text-xs">
          {Object.entries(byType).map(([t, c]) => (
            <span key={t} className={`px-1.5 py-0.5 rounded ${TYPE_BADGE[t] || "bg-gray-100"}`}>{t}: {c}</span>
          ))}
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700 max-h-96 overflow-y-auto">
        {entries.map((e, i) => (
          <div key={i} className="flex items-start gap-3 px-4 py-3">
            <span className="text-lg">{TYPE_ICON[e.type] || "📌"}</span>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">{e.title}</span>
                <span className="text-xs text-gray-400">{e.service} v{e.version}</span>
              </div>
              <p className="text-xs text-gray-400">{e.date}</p>
            </div>
          </div>
        ))}
      </div>
      <div className="px-4 py-2 text-xs text-gray-400 border-t dark:border-gray-700">{total} changes total</div>
    </div>
  );
}
