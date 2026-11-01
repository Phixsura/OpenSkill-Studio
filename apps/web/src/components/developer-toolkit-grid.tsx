"use client";

interface Tool { id: string; name: string; icon: string; category: string; description: string; }
interface DeveloperToolkitGridProps { tools: Tool[]; categories: string[];
  onToolClick: (id: string) => void; }

const catColor: Record<string, string> = {
  development: "border-blue-200 dark:border-blue-800",
  security: "border-red-200 dark:border-red-800",
  performance: "border-green-200 dark:border-green-800",
  debugging: "border-yellow-200 dark:border-yellow-800",
};

export function DeveloperToolkitGrid({ tools, categories, onToolClick }: DeveloperToolkitGridProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold">🧰 Developer Toolkit</h2>
        <span className="text-xs text-gray-400">{tools.length} tools</span>
      </div>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {tools.map(t => (
          <button key={t.id} onClick={() => onToolClick(t.id)}
            className={`rounded-xl border p-4 text-left hover:shadow-md ${catColor[t.category] ?? "dark:border-gray-700"}`}>
            <span className="text-3xl">{t.icon}</span>
            <h3 className="mt-2 font-bold">{t.name}</h3>
            <p className="mt-1 text-xs text-gray-400">{t.description}</p>
            <span className="mt-2 inline-block rounded-full bg-gray-100 px-2 py-0.5 text-[10px] capitalize dark:bg-gray-800">
              {t.category}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}
