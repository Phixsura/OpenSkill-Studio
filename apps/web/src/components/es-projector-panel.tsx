"use client";
interface Projection { name: string; eventsApplied: number; }
interface EsProjectorPanelProps { projections: Projection[]; totalEvents: number; }
export function EsProjectorPanel({ projections, totalEvents }: EsProjectorPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📽️ Event Projections</h3>
        <span className="text-xs text-gray-400">{projections.length} projections · {totalEvents.toLocaleString()} events</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {projections.map(p => (
          <div key={p.name} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{p.name}</span>
            <span className="text-gray-400">{p.eventsApplied.toLocaleString()} events</span>
          </div>
        ))}
      </div>
    </div>
  );
}
