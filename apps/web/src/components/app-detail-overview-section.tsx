"use client";

interface AppDetailOverviewSectionProps { description: string | null; category: string; developerName: string; verified: boolean; installCount: number; healthScore: number; createdAt: string; }

const ICONS: Record<string, string> = { connector: "🔌", automation: "🤖", analytics: "📊", ui_extension: "🖥️" };

export function AppDetailOverviewSection({ description, category, developerName, verified, installCount, healthScore, createdAt }: AppDetailOverviewSectionProps) {
  return (
    <div className="space-y-4">
      {description && <p className="text-gray-600 dark:text-gray-400">{description}</p>}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <div className="rounded-lg border p-3 text-center dark:border-gray-700">
          <span className="text-xl">{ICONS[category] ?? "📦"}</span>
          <p className="mt-1 text-xs capitalize text-gray-500">{category.replace(/_/g, " ")}</p>
        </div>
        <div className="rounded-lg border p-3 text-center dark:border-gray-700">
          <p className="font-bold">{installCount}</p><p className="text-xs text-gray-500">Installs</p>
        </div>
        <div className="rounded-lg border p-3 text-center dark:border-gray-700">
          <p className="font-bold">{healthScore}%</p><p className="text-xs text-gray-500">Health</p>
        </div>
        <div className="rounded-lg border p-3 text-center dark:border-gray-700">
          <p className="text-sm font-medium">{developerName} {verified ? "✓" : ""}</p><p className="text-xs text-gray-500">Developer</p>
        </div>
      </div>
      <p className="text-xs text-gray-400">Published {createdAt}</p>
    </div>
  );
}
