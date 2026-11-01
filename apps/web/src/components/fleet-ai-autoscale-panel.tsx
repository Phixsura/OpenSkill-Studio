"use client";
export function FleetAiAutoscalePanel({ policies, active, scaleEvents, replicas, targetUtil }: { policies: number; active: number; scaleEvents: number; replicas: number; targetUtil: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📐 AI Auto-Scaling</h3>
    <div className="text-sm">{active}/{policies} active · {scaleEvents} events · {replicas} replicas · target {targetUtil}%</div>
  </div>);
}
