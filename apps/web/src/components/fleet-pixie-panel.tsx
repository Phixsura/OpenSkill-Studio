"use client";
export function FleetPixiePanel({ clusters, connected, monitoredPods, dataGb }: { clusters: number; connected: number; monitoredPods: number; dataGb: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🧚 Pixie</h3>
    <div className="text-sm">{connected}/{clusters} connected · {monitoredPods} pods · {dataGb}GB retained</div>
  </div>);
}
