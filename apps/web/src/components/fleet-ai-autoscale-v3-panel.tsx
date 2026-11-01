"use client";
export function FleetAiAutoscaleV3Panel({ scalers, active, replicas, events, predAcc }: { scalers: number; active: number; replicas: number; events: number; predAcc: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📐 AI Autoscaler v3</h3>
    <div className="text-sm">{active}/{scalers} active · {replicas} replicas · {events} events · {predAcc}% prediction acc</div>
  </div>);
}
