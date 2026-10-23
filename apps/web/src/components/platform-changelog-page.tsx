"use client";

interface ChangelogEntry { title: string; date: string; type: string; link: string; }
interface PlatformChangelogPageProps { entries: ChangelogEntry[]; rssUrl: string; }

const TYPE_BADGES: Record<string, { label: string; color: string }> = {
  app_update: { label: "App Update", color: "bg-blue-100 text-blue-700" },
  platform: { label: "Platform", color: "bg-purple-100 text-purple-700" },
};

export function PlatformChangelogPage({ entries, rssUrl }: PlatformChangelogPageProps) {
  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Changelog</h1>
        <a href={rssUrl} className="rounded border px-3 py-1 text-sm text-orange-600 hover:bg-orange-50">RSS</a>
      </div>
      <div className="space-y-3">
        {entries.map((e, i) => {
          const badge = TYPE_BADGES[e.type] || TYPE_BADGES.platform;
          return (
            <div key={i} className="border-l-2 border-blue-300 pl-4">
              <div className="flex items-center gap-2">
                <span className={`rounded px-1.5 py-0.5 text-xs ${badge.color}`}>{badge.label}</span>
                <span className="text-xs text-gray-400">{e.date.slice(0, 10)}</span>
              </div>
              <a href={e.link} className="mt-1 block text-sm font-semibold hover:text-blue-600">{e.title}</a>
            </div>
          );
        })}
      </div>
    </div>
  );
}
