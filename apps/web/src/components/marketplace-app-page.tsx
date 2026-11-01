"use client";

interface AppInfo { name: string; icon: string; tagline: string; description: string;
  version: string; pricing: string; tags: string[]; }
interface Developer { name: string; verified: boolean; appCount: number; }
interface AppStats { installs: number; rating: number; stars: string; reviewCount: number; }
interface MarketplaceAppPageProps { app: AppInfo; developer: Developer; stats: AppStats;
  installed: boolean; cta: string; onInstall: () => void; }

export function MarketplaceAppPage({ app, developer, stats, installed, cta, onInstall }: MarketplaceAppPageProps) {
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex items-start gap-4">
        <span className="text-5xl">{app.icon}</span>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-extrabold">{app.name}</h1>
            {developer.verified && <span className="text-blue-500">✓</span>}
          </div>
          <p className="text-gray-500">{app.tagline}</p>
          <p className="text-xs text-gray-400">by {developer.name} · v{app.version} · {developer.appCount} apps</p>
          <div className="mt-2 flex items-center gap-3 text-sm">
            <span className="text-yellow-500">{stats.stars}</span>
            <span className="text-gray-400">{stats.rating} ({stats.reviewCount})</span>
            <span className="text-gray-400">{stats.installs.toLocaleString()} installs</span>
          </div>
        </div>
        <button onClick={onInstall}
          className={`shrink-0 rounded-lg px-6 py-2.5 text-sm font-medium ${installed ? "bg-gray-200 dark:bg-gray-700 text-gray-600" : "bg-blue-600 text-white"}`}>{cta}</button>
      </div>
      <div className="flex flex-wrap gap-1.5">
        {app.tags.map(t => <span key={t} className="rounded-full border px-2.5 py-0.5 text-xs dark:border-gray-700">{t}</span>)}
        <span className="text-xs text-blue-600 font-medium">{app.pricing}</span>
      </div>
      <p className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed">{app.description}</p>
    </div>
  );
}
