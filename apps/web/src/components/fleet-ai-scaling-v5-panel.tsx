"use client";
export function FleetAiScalingV5Panel({ scalers, active, replicas, events, predAcc }: { scalers: number; active: number; replicas: number; events: number; predAcc: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📐 AI Scaling v5</h3>
    <div className="text-sm">{active}/{scalers} active · {replicas.toLocaleString()} replicas · {events} events · {predAcc}% pred</div>
  </div>);
}
