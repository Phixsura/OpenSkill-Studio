"use client";
interface Filter { subscriberId: string; eventCount: number; hasFieldFilter: boolean; }
interface WhEventFilterPanelProps { filters: Filter[]; }
export function WhEventFilterPanel({ filters }: WhEventFilterPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔍 Event Filters</h3>
        <span className="text-xs text-gray-400">{filters.length} subscribers filtered</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {filters.map(f => (
          <div key={f.subscriberId} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{f.subscriberId}</span>
            <span className="text-gray-400">{f.eventCount} events{f.hasFieldFilter ? " · field filter" : ""}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
