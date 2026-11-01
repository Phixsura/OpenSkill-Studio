"use client";

interface CategoryPageHeaderProps { category: string; description: string; totalApps: number; }

const ICONS: Record<string, string> = { connector: "🔌", automation: "🤖", analytics: "📊", ui_extension: "🖥️", ecosystem_source: "🌐", content_pack: "📦", workflow_adapter: "⚡" };

export function CategoryPageHeader({ category, description, totalApps }: CategoryPageHeaderProps) {
  return (
    <div className="mb-6">
      <div className="flex items-center gap-3">
        <span className="text-4xl">{ICONS[category] ?? "📦"}</span>
        <div>
          <h1 className="text-2xl font-bold capitalize">{category.replace(/_/g, " ")}</h1>
          <p className="text-sm text-gray-500">{description}</p>
        </div>
      </div>
      <p className="mt-2 text-sm text-gray-400">{totalApps} app{totalApps !== 1 ? "s" : ""}</p>
    </div>
  );
}
