"use client";
export function FleetAiNetOptPanel({ optimizers, active, bandwidthSaved, latencyReduction, compression }: { optimizers: number; active: number; bandwidthSaved: number; latencyReduction: number; compression: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌐 AI Network Optimizer</h3>
    <div className="text-sm">{active}/{optimizers} active · {bandwidthSaved}% BW saved · {latencyReduction}% faster · {compression}x compress</div>
  </div>);
}
