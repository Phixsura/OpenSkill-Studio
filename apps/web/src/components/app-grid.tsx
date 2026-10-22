"use client";

interface GridApp { id: string; name: string; slug: string; category: string; description: string | null; installCount: number; }

interface AppGridProps { apps: GridApp[]; columns?: 2 | 3 | 4; }

const ICONS: Record<string, string> = { connector: "🔌", automation: "🤖", analytics: "📊", ui_extension: "🖥️", content_pack: "📦" };

export function AppGrid({ apps, columns = 3 }: AppGridProps) {
  if (apps.length === 0) return <p className="py-8 text-center text-sm text-gray-400">No apps to display</p>;
  const colClass = columns === 2 ? "sm:grid-cols-2" : columns === 4 ? "sm:grid-cols-2 lg:grid-cols-4" : "sm:grid-cols-2 lg:grid-cols-3";
  return (
    <div className={`grid grid-cols-1 gap-4 ${colClass}`}>
      {apps.map(app => (
        <a key={app.id} href={`/marketplace/apps/${app.slug}`} className="rounded-xl border border-gray-200 p-4 transition hover:border-blue-400 hover:shadow dark:border-gray-700">
          <div className="flex items-center gap-2">
            <span className="text-xl">{ICONS[app.category] ?? "📦"}</span>
            <h4 className="font-semibold">{app.name}</h4>
          </div>
          {app.description && <p className="mt-2 text-sm text-gray-500 line-clamp-2">{app.description}</p>}
          <p className="mt-2 text-xs text-gray-400">📥 {app.installCount} installs</p>
        </a>
      ))}
    </div>
  );
}
