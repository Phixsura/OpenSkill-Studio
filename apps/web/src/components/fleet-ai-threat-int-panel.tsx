"use client";
export function FleetAiThreatIntPanel({ feeds, active, indicators, threats, mitigated }: { feeds: number; active: number; indicators: number; threats: number; mitigated: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🛡️ AI Threat Intelligence</h3>
    <div className="text-sm">{active}/{feeds} active · {indicators.toLocaleString()} IoCs · {threats} threats · {mitigated} mitigated</div>
  </div>);
}
