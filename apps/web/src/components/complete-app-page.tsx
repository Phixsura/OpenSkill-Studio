"use client";

interface AppInfo { name: string; icon: string; tagline: string; description: string;
  version: string; pricing: string; tags: string[]; }
interface Developer { name: string; verified: boolean; }
interface Stats { installs: number; rating: number; stars: string; reviewCount: number; }
interface Review { rating: number; title: string; author: string; }
interface SimilarApp { id: string; name: string; icon: string; }
interface ChangelogEntry { version: string; title: string; }
interface CompleteAppPageProps { app: AppInfo; developer: Developer; stats: Stats;
  topReviews: Review[]; similarApps: SimilarApp[]; recentChangelog: ChangelogEntry[];
  installed: boolean; cta: string; onInstall: () => void; onSelectSimilar: (id: string) => void; }

export function CompleteAppPage({ app, developer, stats, topReviews, similarApps,
  recentChangelog, installed, cta, onInstall, onSelectSimilar }: CompleteAppPageProps) {
  return (
    <div className="mx-auto max-w-3xl space-y-8">
      <div className="flex items-start gap-4">
        <span className="text-5xl">{app.icon}</span>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-extrabold">{app.name}</h1>
            {developer.verified && <span className="text-blue-500">✓</span>}
          </div>
          <p className="text-gray-500">{app.tagline}</p>
          <p className="text-xs text-gray-400">by {developer.name} · v{app.version}</p>
          <div className="mt-2 flex gap-3 text-sm text-gray-400">
            <span className="text-yellow-500">{stats.stars}</span>
            <span>{stats.rating} ({stats.reviewCount})</span>
            <span>{stats.installs.toLocaleString()} installs</span>
          </div>
        </div>
        <button onClick={onInstall}
          className={`shrink-0 rounded-lg px-6 py-2.5 text-sm font-medium ${installed ? "bg-gray-200 dark:bg-gray-700" : "bg-blue-600 text-white"}`}>{cta}</button>
      </div>
      <div className="flex flex-wrap gap-1.5">
        {app.tags.map(t => <span key={t} className="rounded-full border px-2.5 py-0.5 text-xs dark:border-gray-700">{t}</span>)}
      </div>
      <p className="text-sm leading-relaxed text-gray-600 dark:text-gray-300">{app.description}</p>
      {topReviews.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold mb-2">⭐ Reviews</h2>
          {topReviews.map((r, i) => (
            <div key={i} className="border-b py-2 dark:border-gray-800">
              <span className="text-yellow-500 text-xs">{"★".repeat(r.rating)}</span>
              <span className="text-sm ml-2">{r.title}</span>
              <span className="text-xs text-gray-400 ml-1">— {r.author}</span>
            </div>
          ))}
        </div>
      )}
      {recentChangelog.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold mb-2">📝 Changelog</h2>
          {recentChangelog.map((c, i) => <p key={i} className="text-sm text-gray-500">v{c.version}: {c.title}</p>)}
        </div>
      )}
      {similarApps.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold mb-2">Similar Apps</h2>
          <div className="flex gap-2">
            {similarApps.map(s => (
              <button key={s.id} onClick={() => onSelectSimilar(s.id)}
                className="flex items-center gap-2 rounded-lg border px-3 py-2 text-sm dark:border-gray-700">
                {s.icon} {s.name}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
