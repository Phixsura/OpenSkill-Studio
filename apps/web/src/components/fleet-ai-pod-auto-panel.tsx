"use client";
export function FleetAiPodAutoPanel({ scalers, active, pods, targetCpu, scaleEvents }: { scalers: number; active: number; pods: number; targetCpu: number; scaleEvents: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📐 AI Pod Autoscaler</h3>
    <div className="text-sm">{active}/{scalers} active · {pods} pods · target {targetCpu}% CPU · {scaleEvents} events</div>
  </div>);
}
