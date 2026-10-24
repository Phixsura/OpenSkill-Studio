"use client";
export function FleetAiRiskMgmtV7Panel({ systems, active, risks, mitigated, score }: { systems: number; active: number; risks: number; mitigated: number; score: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚠️ AI Risk Mgmt v7</h3>
    <div className="text-sm">{active}/{systems} active · {risks} risks · {mitigated} mitigated · score {score}</div>
  </div>);
}
