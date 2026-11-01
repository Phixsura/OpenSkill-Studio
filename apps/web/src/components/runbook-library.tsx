"use client";

interface Runbook { slug: string; title: string; category: string;
  stepCount: number; tags: string[]; uses: number; }
interface RunbookLibraryProps { runbooks: Runbook[]; total: number;
  categories: string[]; onSelect: (slug: string) => void; }

export function RunbookLibrary({ runbooks, total, categories, onSelect }: RunbookLibraryProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📚 Runbook Library</h3>
        <span className="text-xs text-gray-400">{total} runbooks · {categories.length} categories</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {runbooks.map(r => (
          <button key={r.slug} onClick={() => onSelect(r.slug)}
            className="w-full text-left px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-800">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">{r.title}</span>
              <span className="text-xs text-gray-400">{r.stepCount} steps · {r.uses} uses</span>
            </div>
            <div className="flex gap-1 mt-1">
              <span className="px-1.5 py-0.5 text-[10px] bg-blue-50 dark:bg-blue-900/20 text-blue-600 rounded">{r.category}</span>
              {r.tags.map(t => <span key={t} className="px-1 py-0.5 text-[10px] bg-gray-100 dark:bg-gray-800 rounded">{t}</span>)}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
