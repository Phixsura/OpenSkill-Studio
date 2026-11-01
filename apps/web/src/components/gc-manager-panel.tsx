"use client";
interface GcItem { id: string; type: string; sizeMb: number; }
interface GcManagerPanelProps { items: GcItem[]; reclaimableMb: number; stale: number; orphaned: number; }
export function GcManagerPanel({ items, reclaimableMb, stale, orphaned }: GcManagerPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🧹 Garbage Collector</h3>
        <span className="text-xs text-gray-400">{stale} stale · {orphaned} orphaned · {reclaimableMb}MB reclaimable</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {items.map(i => (
          <div key={i.id} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{i.id} <span className="text-gray-400">({i.type})</span></span>
            <span className="text-gray-400">{i.sizeMb}MB</span>
          </div>
        ))}
      </div>
    </div>
  );
}
