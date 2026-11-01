"use client";
export function FleetAiAiopsV8Panel({ systems, active, auto, anomalies, predAcc, toil }: { systems: number; active: number; auto: number; anomalies: number; predAcc: number; toil: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🤖 AI AIOps v8</h3>
    <div className="text-sm">{active}/{systems} active · {auto.toLocaleString()} auto · {anomalies} anomalies · {predAcc}% pred · {toil}% toil↓</div>
  </div>);
}
