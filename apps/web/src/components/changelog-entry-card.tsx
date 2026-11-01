"use client";

interface ChangeCategory { type: string; items: string[]; }
interface ChangelogEntryCardProps { version: string; date: string;
  categories: ChangeCategory[]; totalChanges: number; hasBreaking: boolean; }

const typeIcon: Record<string, string> = {
  feature: "✨", fix: "🐛", improvement: "⚡", breaking: "⚠️", security: "🔒", other: "📋",
};

export function ChangelogEntryCard({ version, date, categories, totalChanges, hasBreaking }: ChangelogEntryCardProps) {
  return (
    <div className="rounded-lg border p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <div className="flex items-baseline gap-2">
          <h3 className="text-lg font-bold">v{version}</h3>
          <span className="text-xs text-gray-400">{date}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">{totalChanges} changes</span>
          {hasBreaking && <span className="rounded bg-red-100 px-1.5 py-0.5 text-xs text-red-700 dark:bg-red-900/30">Breaking</span>}
        </div>
      </div>
      <div className="mt-3 space-y-2">
        {categories.map(cat => (
          <div key={cat.type}>
            <h4 className="flex items-center gap-1 text-sm font-medium">
              <span>{typeIcon[cat.type] ?? "📋"}</span>
              <span className="capitalize">{cat.type.replace("_", " ")}</span>
            </h4>
            <ul className="ml-6 mt-0.5 list-disc space-y-0.5 text-sm text-gray-500">
              {cat.items.map((item, i) => <li key={i}>{item}</li>)}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}
