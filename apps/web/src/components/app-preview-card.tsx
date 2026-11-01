"use client";

interface AppPreviewCardProps {
  name: string; slug: string; category: string; description: string | null;
  installCount: number; healthScore: number; developerName: string; verified: boolean;
}

const ICONS: Record<string, string> = { connector: "🔌", automation: "🤖", analytics: "📊", ui_extension: "🖥️", content_pack: "📦" };

export function AppPreviewCard({ name, slug, category, description, installCount, healthScore, developerName, verified }: AppPreviewCardProps) {
  return (
    <a href={`/marketplace/apps/${slug}`} className="block rounded-xl border border-gray-200 p-4 transition hover:border-blue-400 hover:shadow-md dark:border-gray-700">
      <div className="mb-2 flex items-center gap-2">
        <span className="text-2xl">{ICONS[category] ?? "📦"}</span>
        <div className="flex-1">
          <h4 className="font-semibold">{name}</h4>
          <p className="text-xs text-gray-500">{developerName} {verified ? "✓" : ""}</p>
        </div>
        <span className={`text-sm font-bold ${healthScore >= 90 ? "text-green-600" : "text-yellow-600"}`}>{healthScore}</span>
      </div>
      {description && <p className="mb-2 text-sm text-gray-500 line-clamp-2">{description}</p>}
      <div className="flex items-center justify-between text-xs text-gray-400">
        <span className="capitalize">{category.replace(/_/g, " ")}</span>
        <span>📥 {installCount}</span>
      </div>
    </a>
  );
}
