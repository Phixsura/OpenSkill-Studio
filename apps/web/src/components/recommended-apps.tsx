"use client";

interface RecommendedApp { name: string; category: string; installCount: number; description?: string; }

interface RecommendedAppsProps { apps: RecommendedApp[]; title?: string; }

const ICONS: Record<string, string> = { connector: "🔌", automation: "🤖", analytics: "📊", ui_extension: "🖥️", content_pack: "📦" };

export function RecommendedApps({ apps, title = "Recommended for you" }: RecommendedAppsProps) {
  if (apps.length === 0) return null;
  return (
    <div>
      <h3 className="mb-3 font-semibold">{title}</h3>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {apps.map(app => (
          <div key={app.name} className="rounded-lg border border-gray-200 p-3 hover:border-blue-400 dark:border-gray-700">
            <div className="flex items-center gap-2">
              <span>{ICONS[app.category] ?? "📦"}</span>
              <span className="font-medium">{app.name}</span>
            </div>
            {app.description && <p className="mt-1 text-xs text-gray-500 line-clamp-2">{app.description}</p>}
            <p className="mt-1 text-xs text-gray-400">📥 {app.installCount} installs</p>
          </div>
        ))}
      </div>
    </div>
  );
}
