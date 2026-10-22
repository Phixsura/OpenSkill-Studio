"use client";

interface RelatedApp { name: string; slug: string; category: string; installCount: number; }
interface RelatedAppsSectionProps { apps: RelatedApp[]; }

const ICONS: Record<string, string> = { connector: "🔌", automation: "🤖", analytics: "📊" };

export function RelatedAppsSection({ apps }: RelatedAppsSectionProps) {
  if (apps.length === 0) return null;
  return (
    <div>
      <h3 className="mb-3 font-semibold">Related Apps</h3>
      <div className="flex gap-3 overflow-x-auto pb-2">
        {apps.map(a => (
          <a key={a.slug} href={`/marketplace/apps/${a.slug}`} className="min-w-[180px] rounded-lg border border-gray-200 p-3 hover:border-blue-400 dark:border-gray-700">
            <span>{ICONS[a.category] ?? "📦"}</span> <span className="font-medium">{a.name}</span>
            <p className="text-xs text-gray-400">📥 {a.installCount}</p>
          </a>
        ))}
      </div>
    </div>
  );
}
