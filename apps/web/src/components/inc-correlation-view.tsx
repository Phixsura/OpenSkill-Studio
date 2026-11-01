"use client";

interface Correlation { tag: string; incidents: string[]; count: number; }
interface IncCorrelationViewProps { correlations: Correlation[];
  totalIncidents: number; hasCorrelations: boolean; }

export function IncCorrelationView({ correlations, totalIncidents, hasCorrelations }: IncCorrelationViewProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔗 Incident Correlation</h3>
        <span className="text-xs text-gray-400">
          {totalIncidents} incidents · {correlations.length} groups
        </span>
      </div>
      {hasCorrelations ? (
        <div className="divide-y dark:divide-gray-700">
          {correlations.map(c => (
            <div key={c.tag} className="px-4 py-2 text-xs">
              <div className="flex justify-between">
                <span className="font-medium text-blue-600">🏷️ {c.tag}</span>
                <span className="text-gray-400">{c.count} incidents</span>
              </div>
              <div className="text-[10px] text-gray-400 mt-0.5">{c.incidents.join(", ")}</div>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-4 text-center text-sm text-gray-400">✅ No correlated incidents</div>
      )}
    </div>
  );
}
