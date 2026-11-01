"use client";
interface CorrelatedGroup { services: string[]; count: number; }
interface IncidentCorrPanelProps { groups: CorrelatedGroup[]; totalIncidents: number; uncorrelated: number; }
export function IncidentCorrPanel({ groups, totalIncidents, uncorrelated }: IncidentCorrPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔗 Incident Correlation</h3>
        <span className="text-xs text-gray-400">{groups.length} groups · {totalIncidents} incidents · {uncorrelated} uncorrelated</span>
      </div>
      {groups.length > 0 ? (
        <div className="divide-y dark:divide-gray-700">
          {groups.map((g, i) => (
            <div key={i} className="px-4 py-2 text-xs">
              <span className="text-red-500 font-bold">{g.count} incidents</span>
              <span className="text-gray-400 ml-2">across {g.services.join(", ")}</span>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-4 text-xs text-green-600 text-center">No correlated incidents</div>
      )}
    </div>
  );
}
