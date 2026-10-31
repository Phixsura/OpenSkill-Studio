"use client";
export function FleetTritonPanel({ servers, ready, modelsLoaded, inferencesPerSec }: { servers: number; ready: number; modelsLoaded: number; inferencesPerSec: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🟢 Triton</h3>
    <div className="text-sm">{ready}/{servers} ready · {modelsLoaded} models · {inferencesPerSec.toLocaleString()} inf/s</div>
  </div>);
}
