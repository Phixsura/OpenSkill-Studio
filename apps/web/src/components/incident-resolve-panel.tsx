"use client";
interface IncidentResolvePanelProps { incidentId: string; autoResolve: boolean;
  checks: Record<string, boolean>; passed: number; total: number; }
export function IncidentResolvePanel({ incidentId, autoResolve, checks, passed, total }: IncidentResolvePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔧 Auto-Resolve: {incidentId}</h3>
        <span className={`text-xs font-bold ${autoResolve ? "text-green-600" : "text-yellow-600"}`}>
          {autoResolve ? "✅ Ready to resolve" : `⏳ ${passed}/${total} clear`}
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {Object.entries(checks).map(([name, ok]) => (
          <div key={name} className="flex justify-between px-4 py-1.5 text-xs">
            <span>{name.replace(/_/g, " ")}</span>
            <span>{ok ? "✅" : "❌"}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
