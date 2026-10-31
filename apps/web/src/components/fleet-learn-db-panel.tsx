"use client";
export function FleetLearnDbPanel({ totalEntries, categories, rich }: { totalEntries: number; categories: number; rich: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📚 Learnings DB</h3>
    <div className="text-sm">{totalEntries} entries · {categories} categories</div>
    {rich && <span className="text-xs text-green-600">✅ Rich knowledge base</span>}
  </div>);
}
