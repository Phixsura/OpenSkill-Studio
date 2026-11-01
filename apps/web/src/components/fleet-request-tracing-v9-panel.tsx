"use client";
export function FleetRequestTracingV9Panel({ traces, errors }: { traces: number; errors: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔍 Request Tracing v9</h3>
    <div className="text-sm">{traces} traces · {errors} errors</div>
  </div>);
}
