"use client";

interface FeaturedApp { appId: string; name: string; description: string | null; category: string; reason?: string; iconUrl?: string | null; }

interface FeaturedAppCarouselProps { apps: FeaturedApp[]; }

const CAT_ICONS: Record<string, string> = { connector: "🔌", automation: "🤖", analytics: "📊", ui_extension: "🖥️", ecosystem_source: "🌐", content_pack: "📦", workflow_adapter: "⚡" };

export function FeaturedAppCarousel({ apps }: FeaturedAppCarouselProps) {
  if (apps.length === 0) return null;
  return (
    <div className="flex gap-4 overflow-x-auto pb-2">
      {apps.map(app => (
        <div key={app.appId} className="min-w-[250px] rounded-xl border border-gray-200 p-4 dark:border-gray-700">
          <div className="mb-2 flex items-center gap-2">
            <span className="text-2xl">{CAT_ICONS[app.category] ?? "📦"}</span>
            <h4 className="font-semibold">{app.name}</h4>
          </div>
          {app.description && <p className="mb-2 text-sm text-gray-500 line-clamp-2">{app.description}</p>}
          {app.reason && <p className="text-xs italic text-blue-600 dark:text-blue-400">⭐ {app.reason}</p>}
        </div>
      ))}
    </div>
  );
}
