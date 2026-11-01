"use client";
export function FleetGcfPanel({ functions, active, executions, avgDuration }: { functions: number; active: number; executions: number; avgDuration: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">☁️ Cloud Functions</h3>
    <div className="text-sm">{active}/{functions} active · {executions.toLocaleString()} exec · {avgDuration}ms avg</div>
  </div>);
}
