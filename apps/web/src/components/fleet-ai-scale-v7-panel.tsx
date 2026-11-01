"use client";
export function FleetAiScaleV7Panel({ systems, active, peakRps, gpus, dataPb, users }: { systems: number; active: number; peakRps: number; gpus: number; dataPb: number; users: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📐 AI Scale v7</h3>
    <div className="text-sm">{active}/{systems} active · {peakRps.toLocaleString()} RPS · {gpus.toLocaleString()} GPUs · {dataPb}PB · {users.toLocaleString()} users</div>
  </div>);
}
