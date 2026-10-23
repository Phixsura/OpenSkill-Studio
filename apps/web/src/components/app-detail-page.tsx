"use client";

interface Header { name: string; icon: string; version: string; author: string; verified: boolean; tagline: string; }
interface Stats { installs: number; rating: number; stars: string; reviewCount: number; }
interface SimilarApp { id: string; name: string; icon: string; }
interface AppDetailPageProps { header: Header; description: string; stats: Stats;
  pricing: string; installed: boolean; cta: string; tags: string[];
  similarApps: SimilarApp[]; onInstall: () => void; onSelectSimilar: (id: string) => void; }

export function AppDetailPage({ header, description, stats, pricing, installed, cta,
  tags, similarApps, onInstall, onSelectSimilar }: AppDetailPageProps) {
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex items-start gap-4">
        <span className="text-5xl">{header.icon}</span>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-extrabold">{header.name}</h1>
            {header.verified && <span className="text-blue-500">✓</span>}
          </div>
          <p className="text-gray-500">{header.tagline}</p>
          <p className="text-xs text-gray-400">by {header.author} · v{header.version}</p>
          <div className="mt-2 flex items-center gap-3 text-sm">
            <span className="text-yellow-500">{stats.stars}</span>
            <span className="text-gray-400">{stats.rating} ({stats.reviewCount} reviews)</span>
            <span className="text-gray-400">{stats.installs.toLocaleString()} installs</span>
          </div>
        </div>
        <button onClick={onInstall}
          className={`shrink-0 rounded-lg px-6 py-2.5 text-sm font-medium ${installed ? "bg-gray-200 text-gray-600 dark:bg-gray-700" : "bg-blue-600 text-white"}`}>{cta}</button>
      </div>
      <div className="flex flex-wrap gap-1.5">
        {tags.map(t => <span key={t} className="rounded-full border px-2.5 py-0.5 text-xs dark:border-gray-700">{t}</span>)}
        <span className="text-xs font-medium text-blue-600">{pricing}</span>
      </div>
      <p className="text-sm leading-relaxed text-gray-600 dark:text-gray-300">{description}</p>
      {similarApps.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold mb-2">Similar Apps</h3>
          <div className="flex gap-2">
            {similarApps.map(s => (
              <button key={s.id} onClick={() => onSelectSimilar(s.id)}
                className="flex items-center gap-2 rounded-lg border px-3 py-2 text-sm dark:border-gray-700">
                <span>{s.icon}</span>{s.name}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
