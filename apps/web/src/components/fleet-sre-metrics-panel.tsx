"use client";
export function FleetSreMetricsPanel({ toilPct, errorBudgetPct, onCallHappiness, sreMature }: { toilPct: number; errorBudgetPct: number; onCallHappiness: number; sreMature: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔧 SRE Metrics</h3>
    <div className="text-sm">Toil {toilPct}% · Budget {errorBudgetPct}% · 😊 {onCallHappiness}/5</div>
    <span className={`text-xs ${sreMature ? "text-green-600" : "text-yellow-600"}`}>{sreMature ? "✅ SRE Mature" : "⚠️ Needs improvement"}</span>
  </div>);
}
