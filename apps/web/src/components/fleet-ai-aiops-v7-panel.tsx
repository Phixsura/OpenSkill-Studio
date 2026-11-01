"use client";
export function FleetAiAiopsV7Panel({ systems, active, autoResolved, anomalies, toil, predAcc }: { systems: number; active: number; autoResolved: number; anomalies: number; toil: number; predAcc: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🤖 AI AIOps v7</h3>
    <div className="text-sm">{active}/{systems} active · {autoResolved.toLocaleString()} auto-resolved · {anomalies} anomalies · {toil}% toil↓ · {predAcc}% pred</div>
  </div>);
}
